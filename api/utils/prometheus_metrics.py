"""
Prometheus metrics collection
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from loguru import logger

# Application info
app_info = Info('logflow_app', 'LogFlow application information')
app_info.info({
    'version': '1.0.0',
    'name': 'LogFlow'
})

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Business metrics
logs_processed_total = Counter(
    'logs_processed_total',
    'Total number of logs processed'
)

logs_indexed_total = Counter(
    'logs_indexed_total',
    'Total number of logs indexed to Elasticsearch',
    ['service', 'level']
)

elasticsearch_queries_total = Counter(
    'elasticsearch_queries_total',
    'Total Elasticsearch queries',
    ['operation']
)

elasticsearch_query_duration_seconds = Histogram(
    'elasticsearch_query_duration_seconds',
    'Elasticsearch query duration in seconds',
    ['operation']
)

# Alert metrics
alerts_triggered_total = Counter(
    'alerts_triggered_total',
    'Total alerts triggered',
    ['rule_name']
)

alerts_checked_total = Counter(
    'alerts_checked_total',
    'Total alert rule checks performed'
)

# Cache metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_key_prefix']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_key_prefix']
)

# Database metrics
database_queries_total = Counter(
    'database_queries_total',
    'Total database queries',
    ['operation']
)

database_connections = Gauge(
    'database_connections',
    'Current number of database connections'
)

# Auth metrics
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['result']
)

users_registered_total = Counter(
    'users_registered_total',
    'Total users registered'
)

# Rate limit metrics
rate_limit_exceeded_total = Counter(
    'rate_limit_exceeded_total',
    'Total rate limit exceeded events',
    ['endpoint']
)

# System metrics
active_sessions = Gauge(
    'active_sessions',
    'Number of active user sessions'
)

logger.info("✅ Prometheus metrics initialized")
