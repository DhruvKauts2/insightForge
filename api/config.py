"""
Configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "LogFlow"
    ENVIRONMENT: str = "development"
    
    # API
    API_TITLE: str = "LogFlow API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "Distributed Log Aggregation System"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_RAW_LOGS: str = "logs-raw"
    
    # Elasticsearch
    ELASTICSEARCH_HOSTS: str = "http://localhost:9200"
    ES_INDEX_PATTERN: str = "logs"
    ELASTICSEARCH_INDEX_PREFIX: str = "logs"
    
    # PostgreSQL
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "logflow"
    POSTGRES_PASSWORD: str = "logflow123"
    POSTGRES_DB: str = "logflow"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Authentication
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Export commonly used variables
API_TITLE = settings.API_TITLE
API_VERSION = settings.API_VERSION
API_DESCRIPTION = settings.API_DESCRIPTION
API_HOST = settings.API_HOST
API_PORT = settings.API_PORT
ES_INDEX_PATTERN = settings.ES_INDEX_PATTERN

# Build database URL
DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
