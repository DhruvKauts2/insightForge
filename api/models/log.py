"""
Log entry models
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class LogEntry(BaseModel):
    """Individual log entry"""
    id: Optional[str] = None
    timestamp: str
    level: str
    service: str
    message: str
    correlation_id: Optional[str] = None
    request_id: Optional[str] = None
    transaction_position: Optional[int] = None
    transaction_total: Optional[int] = None
    metadata: Optional[dict] = None
    
    class Config:
        from_attributes = True


class LogSearchResponse(BaseModel):
    """Response model for log search"""
    total: int
    logs: List[LogEntry]
    query_time_ms: Optional[float] = None


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    services: dict
