"""
Elasticsearch client with retry logic
"""
from elasticsearch import Elasticsearch, exceptions
from typing import Dict, Any, Tuple, Optional
from loguru import logger

from api.config import settings


class ElasticsearchClient:
    """Elasticsearch client with connection management"""
    
    def __init__(self):
        self.client: Optional[Elasticsearch] = None
        self.index_pattern = settings.ES_INDEX_PATTERN
        self._initialize()
    
    def _initialize(self):
        """Initialize Elasticsearch connection"""
        try:
            self.client = Elasticsearch(
                [settings.ELASTICSEARCH_HOSTS],
                request_timeout=30,
                max_retries=3,
                retry_on_timeout=True
            )
            
            # Test connection
            info = self.client.info()
            logger.info(f"✅ Connected to Elasticsearch {info['version']['number']}")
            
        except Exception as e:
            logger.error(f"Elasticsearch connection failed: {e}")
            self.client = None
    
    def search(
        self,
        index: str,
        body: Dict[str, Any],
        size: Optional[int] = None
    ) -> Tuple[Dict[str, Any], int]:
        """Execute search query"""
        if not self.client:
            raise exceptions.ConnectionError("Elasticsearch not connected")
        
        try:
            if size is not None:
                body['size'] = size
            
            response = self.client.search(index=index, body=body)
            query_time = response.get('took', 0)
            
            return response, query_time
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise
    
    def index_document(
        self,
        index: str,
        document: Dict[str, Any],
        doc_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Index a document"""
        if not self.client:
            raise exceptions.ConnectionError("Elasticsearch not connected")
        
        try:
            if doc_id:
                response = self.client.index(index=index, id=doc_id, document=document)
            else:
                response = self.client.index(index=index, document=document)
            
            return response
            
        except Exception as e:
            logger.error(f"Indexing error: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check if Elasticsearch is healthy"""
        if not self.client:
            return False
        
        try:
            health = self.client.cluster.health()
            return health['status'] in ['yellow', 'green']
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


# Global Elasticsearch client instance
es_client = ElasticsearchClient()
