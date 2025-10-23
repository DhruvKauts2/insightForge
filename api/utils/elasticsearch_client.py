"""
Elasticsearch client utilities
"""
from elasticsearch import Elasticsearch
from api.config import ES_HOSTS
from loguru import logger
import time


class ESClient:
    """Singleton Elasticsearch client"""
    _instance = None
    _es = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ESClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Elasticsearch connection"""
        try:
            # Get first host if it's a list
            es_host = ES_HOSTS[0] if isinstance(ES_HOSTS, list) else ES_HOSTS
            
            self._es = Elasticsearch(
                es_host,
                request_timeout=30
            )
            
            if self._es.ping():
                info = self._es.info()
                logger.info(f"Connected to Elasticsearch {info['version']['number']}")
            else:
                logger.error("Elasticsearch ping failed")
                
        except Exception as e:
            logger.error(f"Failed to connect to Elasticsearch: {e}")
            raise
    
    @property
    def client(self):
        """Get Elasticsearch client"""
        return self._es
    
    def search(self, index, body):
        """Execute search query"""
        start_time = time.time()
        try:
            response = self._es.search(index=index, body=body)
            query_time = (time.time() - start_time) * 1000  # Convert to ms
            return response, query_time
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise
    
    def count(self, index, body=None):
        """Count documents"""
        try:
            response = self._es.count(index=index, body=body)
            return response['count']
        except Exception as e:
            logger.error(f"Count error: {e}")
            raise
    
    def health(self):
        """Check Elasticsearch health"""
        try:
            if self._es.ping():
                cluster_health = self._es.cluster.health()
                return {
                    "status": cluster_health['status'],
                    "nodes": cluster_health['number_of_nodes']
                }
            return {"status": "down"}
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {"status": "error", "error": str(e)}


# Singleton instance
es_client = ESClient()
