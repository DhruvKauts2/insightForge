"""
API Configuration
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from config import settings as app_settings
    
    # API specific settings
    API_TITLE = "LogFlow API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = """
    LogFlow API provides endpoints for searching, filtering, and analyzing logs.
    
    ## Features
    
    * **Search logs** - Full-text search with filters
    * **Aggregations** - Statistics and metrics
    * **Real-time** - Query live data from Elasticsearch
    """
    
    # Elasticsearch
    ES_HOSTS = [app_settings.elasticsearch_hosts] if isinstance(app_settings.elasticsearch_hosts, str) else app_settings.elasticsearch_hosts
    ES_INDEX_PATTERN = "logs-*"
    
    # API Server
    API_HOST = app_settings.api_host
    API_PORT = app_settings.api_port
    
except ImportError:
    # Fallback if config not available
    API_TITLE = "LogFlow API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "Log aggregation and search API"
    ES_HOSTS = ["http://localhost:9200"]
    ES_INDEX_PATTERN = "logs-*"
    API_HOST = "0.0.0.0"
    API_PORT = 8000
