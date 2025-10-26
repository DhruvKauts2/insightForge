"""
Request tracing models
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class RequestTrace(BaseModel):
    """Request trace information"""
    request_id: str
    correlation_id: str
    method: str
    path: str
    status_code: Optional[int] = None
    duration_ms: Optional[float] = None
    timestamp: str
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    
class TraceContext(BaseModel):
    """Trace context for responses"""
    request_id: str
    correlation_id: str
    timestamp: str = datetime.now().isoformat()


class DebugTrace(BaseModel):
    """Detailed debug trace"""
    request_id: str
    correlation_id: str
    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, Any]
    body: Optional[Dict[str, Any]] = None
    timestamp: str
    user: Optional[str] = None
