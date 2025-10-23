"""
Pydantic models for logs
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class LogSource(BaseModel):
    """Log source information"""
    hostname: str
    file: str


class LogDocument(BaseModel):
    """Log document model"""
    timestamp: str
    level: str
    service: str
    message: str
    source: LogSource
    ingested_at: str
    shipper_timestamp: Optional[float] = None
    extra_fields: Optional[Dict[str, Any]] = None
    raw_log: Optional[str] = None


class SearchRequest(BaseModel):
    """Search request model"""
    query: Optional[str] = Field(None, description="Full-text search query")
    services: Optional[List[str]] = Field(None, description="Filter by services")
    levels: Optional[List[str]] = Field(None, description="Filter by log levels")
    start_time: Optional[str] = Field(None, description="Start timestamp (YYYY-MM-DD HH:MM:SS)")
    end_time: Optional[str] = Field(None, description="End timestamp (YYYY-MM-DD HH:MM:SS)")
    limit: int = Field(50, ge=1, le=1000, description="Number of results to return")
    offset: int = Field(0, ge=0, description="Offset for pagination")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "database timeout",
                "services": ["payment-service"],
                "levels": ["ERROR", "WARN"],
                "start_time": "2025-10-23 10:00:00",
                "end_time": "2025-10-23 20:00:00",
                "limit": 50,
                "offset": 0
            }
        }


class SearchResponse(BaseModel):
    """Search response model"""
    total: int = Field(description="Total number of matching logs")
    logs: List[LogDocument] = Field(description="List of log documents")
    aggregations: Optional[Dict[str, Any]] = Field(None, description="Aggregation results")
    query_time_ms: Optional[float] = Field(None, description="Query execution time in milliseconds")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    services: Dict[str, str]
