"""
Log Processor - Consumes from Kafka and indexes to Elasticsearch
Parses raw log lines and stores structured data in Elasticsearch
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from loguru import logger
import uuid
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure loguru
logger.remove()
logger.add(sys.stderr, level="INFO")


class LogProcessor:
    def __init__(self, kafka_servers, es_hosts, kafka_topic='logs-raw', consumer_group='log-processor-group'):
        """
        Initialize the log processor
        
        Args:
            kafka_servers: List of Kafka bootstrap servers
            es_hosts: Elasticsearch host (string) or list of hosts
            kafka_topic: Kafka topic to consume from
            consumer_group: Consumer group ID
        """
        self.kafka_servers = kafka_servers
        self.es_hosts = es_hosts
        self.kafka_topic = kafka_topic
        self.consumer_group = consumer_group
        
        # Regex pattern for parsing text logs
        # Format: YYYY-MM-DD HH:MM:SS LEVEL [service] message
        self.log_pattern = re.compile(
            r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+'
            r'(?P<level>\w+)\s+'
            r'\[(?P<service>[\w-]+)\]\s+'
            r'(?P<message>.*)'
        )
        
        self.logs_processed = 0
        self.logs_failed = 0
        self.batch = []
        self.batch_size = 100  # Batch index operations for efficiency
        self.created_indices = set()  # Track created indices
        
        # Connect to services
        self._connect_elasticsearch()
        self._connect_kafka()
    
    def _connect_elasticsearch(self):
        """Connect to Elasticsearch with retries (v9.x compatible)"""
        max_retries = 5
        retry_delay = 3
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Connecting to Elasticsearch at {self.es_hosts} (attempt {attempt + 1}/{max_retries})")
                
                # Elasticsearch 9.x connection syntax
                # Convert list to string if needed
                if isinstance(self.es_hosts, list):
                    es_host = self.es_hosts[0] if len(self.es_hosts) == 1 else self.es_hosts[0]
                else:
                    es_host = self.es_hosts
                
                self.es = Elasticsearch(
                    es_host,
                    request_timeout=30
                )
                
                # Test connection
                if self.es.ping():
                    logger.success("✅ Connected to Elasticsearch successfully")
                    
                    # Get cluster info
                    info = self.es.info()
                    logger.info(f"Elasticsearch version: {info['version']['number']}")
                    logger.info(f"Cluster name: {info['cluster_name']}")
                    return
                else:
                    raise Exception("Elasticsearch ping returned False")
                    
            except Exception as e:
                logger.error(f"Failed to connect to Elasticsearch: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error("Max retries reached. Make sure Elasticsearch is running:")
                    logger.error("  docker compose ps elasticsearch")
                    logger.error("  curl http://localhost:9200")
                    raise
    
    def _connect_kafka(self):
        """Connect to Kafka consumer"""
        try:
            logger.info(f"Connecting to Kafka at {self.kafka_servers}")
            self.consumer = KafkaConsumer(
                self.kafka_topic,
                bootstrap_servers=self.kafka_servers,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id=self.consumer_group,
                auto_offset_reset='earliest',  # Start from beginning if no offset
                enable_auto_commit=True,
                auto_commit_interval_ms=5000,
                max_poll_records=500  # Process up to 500 records per poll
            )
            logger.success(f"✅ Connected to Kafka successfully")
            logger.info(f"Subscribed to topic: {self.kafka_topic}")
            logger.info(f"Consumer group: {self.consumer_group}")
            
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise
    
    def _ensure_index_exists(self, index_name):
        """Create index if it doesn't exist"""
        if index_name in self.created_indices:
            return
        
        try:
            if not self.es.indices.exists(index=index_name):
                # Create index with mapping
                self.es.indices.create(
                    index=index_name,
                    body={
                        "settings": {
                            "number_of_shards": 1,
                            "number_of_replicas": 0
                        },
                        "mappings": {
                            "properties": {
                                "timestamp": {"type": "date", "format": "yyyy-MM-dd HH:mm:ss"},
                                "level": {"type": "keyword"},
                                "service": {"type": "keyword"},
                                "message": {"type": "text"},
                                "source": {
                                    "properties": {
                                        "hostname": {"type": "keyword"},
                                        "file": {"type": "keyword"}
                                    }
                                },
                                "ingested_at": {"type": "date"},
                                "shipper_timestamp": {"type": "float"},
                                "raw_log": {"type": "text"}
                            }
                        }
                    }
                )
                logger.info(f"Created index: {index_name}")
            
            self.created_indices.add(index_name)
            
        except Exception as e:
            logger.warning(f"Could not create index {index_name}: {e}")
    
    def parse_log(self, raw_log):
        """
        Parse raw log line into structured format
        
        Args:
            raw_log: Raw log line as string
            
        Returns:
            Dictionary with parsed fields, or None if parsing fails
        """
        match = self.log_pattern.match(raw_log)
        if not match:
            return None
        
        parsed = match.groupdict()
        
        # Extract additional fields from message if present
        message = parsed['message']
        extra_fields = {}
        
        # Look for key=value patterns in message
        kv_pattern = re.compile(r'(\w+)=(\S+)')
        for match in kv_pattern.finditer(message):
            key, value = match.groups()
            extra_fields[key] = value
            # Remove from message
            message = message.replace(f'{key}={value}', '').strip()
        
        parsed['message'] = message
        parsed['extra_fields'] = extra_fields
        
        return parsed
    
    def create_document(self, kafka_message):
        """
        Create Elasticsearch document from Kafka message
        
        Args:
            kafka_message: Message from Kafka with raw_log and metadata
            
        Returns:
            Dictionary ready for Elasticsearch indexing
        """
        raw_log = kafka_message.get('raw_log', '')
        metadata = kafka_message.get('metadata', {})
        
        # Parse the raw log
        parsed = self.parse_log(raw_log)
        if not parsed:
            logger.warning(f"Failed to parse log: {raw_log[:100]}")
            return None
        
        # Create document (without _id in the document itself)
        doc = {
            'timestamp': parsed['timestamp'],
            'level': parsed['level'],
            'service': parsed['service'],
            'message': parsed['message'],
            'source': {
                'hostname': metadata.get('source', 'unknown'),
                'file': metadata.get('file_path', 'unknown')
            },
            'ingested_at': datetime.now().isoformat(),
            'shipper_timestamp': metadata.get('shipper_timestamp'),
            'raw_log': raw_log  # Keep original for reference
        }
        
        # Add extra fields if any
        if parsed.get('extra_fields'):
            doc['extra_fields'] = parsed['extra_fields']
        
        # Return document with ID separate
        return {
            'id': str(uuid.uuid4()),
            'doc': doc,
            'date': parsed['timestamp'][:10]  # YYYY-MM-DD
        }
    
    def index_batch(self):
        """Index a batch of documents using bulk API (ES 9.x compatible)"""
        if not self.batch:
            return
        
        try:
            # Ensure all indices exist first
            indices_needed = set(f"logs-{item['date']}" for item in self.batch if item)
            for index_name in indices_needed:
                self._ensure_index_exists(index_name)
            
            # Prepare bulk actions - ES 9.x format
            actions = []
            for item in self.batch:
                if item:
                    index_name = f"logs-{item['date']}"
                    
                    # Use 'create' op_type to avoid data stream issues
                    actions.append({
                        '_op_type': 'create',
                        '_index': index_name,
                        '_id': item['id'],
                        '_source': item['doc']
                    })
            
            # Execute bulk index
            if actions:
                success, failed = bulk(self.es, actions, raise_on_error=False)
                self.logs_processed += success
                
                if failed:
                    self.logs_failed += len(failed)
                    logger.warning(f"Failed to index {len(failed)} documents")
                    # Log first few failures for debugging
                    for failure in failed[:3]:
                        logger.debug(f"Failure: {failure}")
            
            # Clear batch
            self.batch = []
            
        except Exception as e:
            logger.error(f"Bulk indexing error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.batch = []
    
    def run(self):
        """Main processing loop"""
        logger.info("🚀 Starting log processor...")
        logger.info(f"📥 Consuming from Kafka topic: {self.kafka_topic}")
        logger.info(f"📤 Indexing to Elasticsearch")
        logger.info(f"\nPress Ctrl+C to stop\n")
        
        try:
            for message in self.consumer:
                try:
                    # Create document from Kafka message
                    doc_item = self.create_document(message.value)
                    
                    if doc_item:
                        # Add to batch
                        self.batch.append(doc_item)
                        
                        # Index batch when it reaches batch_size
                        if len(self.batch) >= self.batch_size:
                            self.index_batch()
                            logger.info(f"✓ Processed {self.logs_processed} logs (failed: {self.logs_failed})")
                    else:
                        self.logs_failed += 1
                        
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    self.logs_failed += 1
                    
        except KeyboardInterrupt:
            logger.info(f"\n\n✅ Shutting down gracefully...")
            # Index remaining batch
            if self.batch:
                logger.info("Indexing remaining batch...")
                self.index_batch()
            self._shutdown()
            
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            self._shutdown()
            raise
    
    def _shutdown(self):
        """Clean shutdown"""
        logger.info(f"📊 Final stats:")
        logger.info(f"   Processed: {self.logs_processed}")
        logger.info(f"   Failed: {self.logs_failed}")
        
        if self.consumer:
            logger.info("Closing Kafka consumer...")
            self.consumer.close()
            logger.info("✅ Kafka consumer closed")


if __name__ == "__main__":
    import argparse
    
    # Try to import settings
    try:
        from config import settings
        default_kafka = settings.kafka_bootstrap_servers
        default_es = settings.elasticsearch_hosts
        default_topic = settings.kafka_topic_raw_logs
    except ImportError:
        default_kafka = "localhost:9092"
        default_es = "http://localhost:9200"
        default_topic = "logs-raw"
    
    parser = argparse.ArgumentParser(description='Process logs from Kafka to Elasticsearch')
    parser.add_argument('--kafka-servers', default=default_kafka,
                        help=f'Kafka servers (default: {default_kafka})')
    parser.add_argument('--es-hosts', default=default_es,
                        help=f'Elasticsearch hosts (default: {default_es})')
    parser.add_argument('--topic', default=default_topic,
                        help=f'Kafka topic (default: {default_topic})')
    parser.add_argument('--consumer-group', default='log-processor-group',
                        help='Kafka consumer group (default: log-processor-group)')
    
    args = parser.parse_args()
    
    # Parse servers - handle string or list
    if isinstance(args.kafka_servers, str):
        kafka_servers = [s.strip() for s in args.kafka_servers.split(',')]
    else:
        kafka_servers = args.kafka_servers
    
    # Keep ES hosts as is (string or list)
    es_hosts = args.es_hosts
    
    processor = LogProcessor(
        kafka_servers=kafka_servers,
        es_hosts=es_hosts,
        kafka_topic=args.topic,
        consumer_group=args.consumer_group
    )
    
    processor.run()
