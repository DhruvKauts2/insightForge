"""
Elasticsearch client with Prometheus metrics
"""
from elasticsearch import Elasticsearch
from loguru import logger
import time
from typing import Optional, Tuple, Dict, Any

from config import settings
from api.utils.prometheus_metrics import (
    elasticsearch_queries_total,
    elasticsearch_query_duration_seconds
)


class ElasticsearchClient:
    """Elasticsearch client wrapper with metrics"""
    
    def __init__(self):
        self._client = None
        self._connected = False
        self._initialize()
    
    def _initialize(self):
        """Initialize Elasticsearch connection"""
        try:
            hosts = settings.elasticsearch_hosts.split(',')
            self._client = Elasticsearch(hosts=hosts)
            
            # Test connection
            info = self._client.info()
            self._connected = True
            logger.info(f"✅ Connected to Elasticsearch {info['version']['number']}")
            
        except Exception as e:
            logger.error(f"Elasticsearch connection failed: {e}")
            self._connected = False
    
    def is_connected(self) -> bool:
        """Check if Elasticsearch is connected"""
        return self._connected
    
    def search(self, index: str, body: dict) -> Tuple[Dict[Any, Any], float]:
        """
        Search Elasticsearch with metrics
        
        Returns:
            Tuple of (response, query_time_ms)
        """
        start_time = time.time()
        
        try:
            response = self._client.search(index=index, body=body)
            query_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Record metrics
            elasticsearch_queries_total.labels(operation='search').inc()
            elasticsearch_query_duration_seconds.labels(operation='search').observe(time.time() - start_time)
            
            return response, query_time
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            elasticsearch_queries_total.labels(operation='search_error').inc()
            raise
    
    def index(self, index: str, document: dict, doc_id: Optional[str] = None):
        """Index a document with metrics"""
        start_time = time.time()
        
        try:
            if doc_id:
                response = self._client.index(index=index, id=doc_id, document=document)
            else:
                response = self._client.index(index=index, document=document)
            
            # Record metrics
            elasticsearch_queries_total.labels(operation='index').inc()
            elasticsearch_query_duration_seconds.labels(operation='index').observe(time.time() - start_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Index error: {e}")
            elasticsearch_queries_total.labels(operation='index_error').inc()
            raise
    
    def get_by_id(self, index: str, doc_id: str) -> Optional[dict]:
        """Get document by ID with metrics"""
        start_time = time.time()
        
        try:
            response = self._client.get(index=index, id=doc_id)
            
            # Record metrics
            elasticsearch_queries_total.labels(operation='get').inc()
            elasticsearch_query_duration_seconds.labels(operation='get').observe(time.time() - start_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Get by ID error: {e}")
            elasticsearch_queries_total.labels(operation='get_error').inc()
            return None
    
    def health(self) -> dict:
        """Get Elasticsearch health"""
        if not self._connected:
            return {"status": "disconnected"}
        
        try:
            health = self._client.cluster.health()
            return health
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return {"status": "error", "error": str(e)}


# Global Elasticsearch client instance
es_client = ElasticsearchClient()
