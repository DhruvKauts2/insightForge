from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Application
    app_name: str = "LogFlow"
    environment: str = "development"
    
    # Kafka - Changed to string, will split in code if needed
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_raw_logs: str = "logs-raw"
    
    # Elasticsearch - Changed to string
    elasticsearch_hosts: str = "http://localhost:9200"
    elasticsearch_index_prefix: str = "logs"
    
    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "logflow"
    postgres_password: str = "logflow123"
    postgres_db: str = "logflow"
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4  # ADDED THIS
    
    # Auth
    secret_key: str = "your-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Logging
    log_level: str = "INFO"
    
    # Helper methods to get lists
    def get_kafka_servers(self) -> List[str]:
        return [s.strip() for s in self.kafka_bootstrap_servers.split(',')]
    
    def get_elasticsearch_hosts(self) -> List[str]:
        return [s.strip() for s in self.elasticsearch_hosts.split(',')]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
