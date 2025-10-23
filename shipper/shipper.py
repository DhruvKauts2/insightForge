"""
Log Shipper - Tails log files and sends to Kafka
Monitors log files for new entries and ships them to Kafka for processing
"""

import json
import time
import socket
import sys
from pathlib import Path
from kafka import KafkaProducer
from kafka.errors import KafkaError
from loguru import logger

# Add parent directory to path so we can import config
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure loguru
logger.remove()
logger.add(sys.stderr, level="INFO")


class LogShipper:
    def __init__(self, kafka_servers, log_file_path, topic='logs-raw'):
        """
        Initialize the log shipper
        
        Args:
            kafka_servers: List of Kafka bootstrap servers
            log_file_path: Path to log file to tail
            topic: Kafka topic to send logs to
        """
        self.kafka_servers = kafka_servers
        self.log_file_path = Path(log_file_path)
        self.topic = topic
        self.hostname = socket.gethostname()
        self.producer = None
        self.logs_sent = 0
        
        # Verify log file exists or can be created
        if not self.log_file_path.exists():
            logger.warning(f"Log file {self.log_file_path} does not exist. Will wait for it to be created.")
            self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Connect to Kafka
        self._connect_kafka()
    
    def _connect_kafka(self):
        """Connect to Kafka with retry logic"""
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Connecting to Kafka at {self.kafka_servers} (attempt {attempt + 1}/{max_retries})")
                self.producer = KafkaProducer(
                    bootstrap_servers=self.kafka_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    acks='all',  # Wait for all replicas to acknowledge
                    retries=3,
                    max_in_flight_requests_per_connection=5,
                    compression_type='gzip'  # Compress messages
                )
                logger.success("✅ Connected to Kafka successfully")
                return
            except KafkaError as e:
                logger.error(f"Failed to connect to Kafka: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    logger.error("Max retries reached. Exiting.")
                    raise
    
    def _send_to_kafka(self, raw_log):
        """
        Send log line to Kafka
        
        Args:
            raw_log: Raw log line as string
        """
        message = {
            "raw_log": raw_log,
            "metadata": {
                "source": self.hostname,
                "file_path": str(self.log_file_path),
                "shipper_timestamp": time.time(),
                "service": self.log_file_path.stem  # filename without extension
            }
        }
        
        try:
            # Send message to Kafka
            future = self.producer.send(self.topic, value=message)
            
            # Wait for confirmation (with timeout)
            record_metadata = future.get(timeout=10)
            
            self.logs_sent += 1
            
            if self.logs_sent % 100 == 0:
                logger.info(f"✓ Sent {self.logs_sent} logs to Kafka (topic: {record_metadata.topic}, partition: {record_metadata.partition})")
            
            return True
            
        except KafkaError as e:
            logger.error(f"Failed to send log to Kafka: {e}")
            logger.debug(f"Failed log: {raw_log[:100]}...")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending to Kafka: {e}")
            return False
    
    def tail_file(self):
        """
        Tail log file and send new lines to Kafka
        Similar to 'tail -f' command
        """
        logger.info(f"🚀 Starting to tail {self.log_file_path}")
        logger.info(f"📤 Sending logs to Kafka topic: {self.topic}")
        logger.info(f"📍 Source hostname: {self.hostname}")
        logger.info(f"\nPress Ctrl+C to stop\n")
        
        # Wait for file to exist
        while not self.log_file_path.exists():
            logger.warning(f"Waiting for {self.log_file_path} to be created...")
            time.sleep(2)
        
        try:
            with open(self.log_file_path, 'r') as f:
                # Move to end of file to start tailing new content
                f.seek(0, 2)  # 2 = end of file
                logger.info("📖 Positioned at end of file, watching for new logs...")
                
                while True:
                    line = f.readline()
                    
                    if line:
                        # New line available
                        line = line.strip()
                        if line:  # Skip empty lines
                            self._send_to_kafka(line)
                    else:
                        # No new data, wait a bit
                        time.sleep(0.1)
                        
        except KeyboardInterrupt:
            logger.info(f"\n\n✅ Shutting down gracefully...")
            logger.info(f"📊 Total logs sent: {self.logs_sent}")
            self._shutdown()
        except Exception as e:
            logger.error(f"Error while tailing file: {e}")
            self._shutdown()
            raise
    
    def _shutdown(self):
        """Clean shutdown - flush remaining messages"""
        if self.producer:
            logger.info("Flushing remaining messages to Kafka...")
            self.producer.flush(timeout=10)
            self.producer.close()
            logger.info("✅ Kafka producer closed")


if __name__ == "__main__":
    import argparse
    
    # Try to import settings, but use defaults if not available
    try:
        from config import settings
        default_kafka = settings.kafka_bootstrap_servers
        default_topic = settings.kafka_topic_raw_logs
    except ImportError:
        default_kafka = "localhost:9092"
        default_topic = "logs-raw"
    
    parser = argparse.ArgumentParser(description='Ship logs from file to Kafka')
    parser.add_argument('--log-file', default='sample_logs/app.log',
                        help='Path to log file to tail (default: sample_logs/app.log)')
    parser.add_argument('--kafka-servers', default=default_kafka,
                        help=f'Kafka servers (default: {default_kafka})')
    parser.add_argument('--topic', default=default_topic,
                        help=f'Kafka topic (default: {default_topic})')
    
    args = parser.parse_args()
    
    # Parse kafka servers (handle both string and list)
    if isinstance(args.kafka_servers, str):
        kafka_servers = [s.strip() for s in args.kafka_servers.split(',')]
    else:
        kafka_servers = args.kafka_servers
    
    shipper = LogShipper(
        kafka_servers=kafka_servers,
        log_file_path=args.log_file,
        topic=args.topic
    )
    
    shipper.tail_file()
