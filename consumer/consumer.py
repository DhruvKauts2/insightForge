"""
Kafka consumer - reads logs from Kafka and indexes to Elasticsearch
"""
import json
from kafka import KafkaConsumer
from elasticsearch import Elasticsearch
from loguru import logger
import sys

# Configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_TOPIC = 'logs-raw'
ELASTICSEARCH_HOSTS = ['http://localhost:9200']
ELASTICSEARCH_INDEX = 'logs'

def main():
    logger.info("Starting Kafka consumer...")
    
    # Connect to Elasticsearch
    try:
        es = Elasticsearch(ELASTICSEARCH_HOSTS)
        es.info()
        logger.info(f"Connected to Elasticsearch at {ELASTICSEARCH_HOSTS}")
    except Exception as e:
        logger.error(f"Failed to connect to Elasticsearch: {e}")
        sys.exit(1)
    
    # Connect to Kafka
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='logflow-consumer'
        )
        logger.info(f"Connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
        logger.info(f"Consuming from topic: {KAFKA_TOPIC}")
    except Exception as e:
        logger.error(f"Failed to connect to Kafka: {e}")
        sys.exit(1)
    
    # Process messages
    try:
        count = 0
        for message in consumer:
            log_entry = message.value
            
            # Index to Elasticsearch
            try:
                es.index(index=ELASTICSEARCH_INDEX, document=log_entry)
                count += 1
                
                if count % 100 == 0:
                    logger.info(f"Indexed {count} logs")
                
            except Exception as e:
                logger.error(f"Failed to index log: {e}")
                
    except KeyboardInterrupt:
        logger.info("\nStopping consumer...")
    finally:
        consumer.close()
        logger.info(f"Consumer stopped. Total logs indexed: {count}")

if __name__ == "__main__":
    main()
