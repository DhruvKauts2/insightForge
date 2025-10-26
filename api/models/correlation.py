"""
Log correlation models
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class ServiceCall(BaseModel):
    """Individual service call in a trace"""
    service: str
    timestamp: str
    duration_ms: Optional[float] = None
    status: Optional[str] = None
    log_id: str
    message: str
    level: str


class RequestFlow(BaseModel):
    """Complete request flow across services"""
    correlation_id: str
    start_time: str
    end_time: Optional[str] = None
    duration_ms: Optional[float] = None
    services: List[str]
    total_calls: int
    service_calls: List[ServiceCall]
    error_count: int
    
    
class ServiceDependency(BaseModel):
    """Service dependency information"""
    from_service: str
    to_service: str
    call_count: int
    avg_duration_ms: float
    error_rate: float


class DependencyGraph(BaseModel):
    """Service dependency graph"""
    services: List[str]
    dependencies: List[ServiceDependency]
    total_services: int
    total_dependencies: int


class CorrelatedLog(BaseModel):
    """Log with correlation context"""
    log_id: str
    timestamp: str
    level: str
    service: str
    message: str
    correlation_id: Optional[str] = None
    request_id: Optional[str] = None
    related_logs_count: int = 0
    position_in_flow: Optional[int] = None
