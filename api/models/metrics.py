"""
Pydantic models for metrics and aggregations
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class TimeRangeMetrics(BaseModel):
    """Metrics for a specific time range"""
    time_range: str
    total_logs: int
    logs_per_minute: float
    by_level: Dict[str, int]
    by_service: Dict[str, int]
    error_rate: float = Field(description="Percentage of ERROR logs")


class TopError(BaseModel):
    """Top error message"""
    message: str
    count: int
    service: str
    last_seen: str


class ServiceMetrics(BaseModel):
    """Metrics for a specific service"""
    service: str
    total_logs: int
    by_level: Dict[str, int]
    error_rate: float
    top_errors: List[TopError]


class SystemMetrics(BaseModel):
    """Overall system metrics"""
    timestamp: str
    total_logs: int
    total_services: int
    time_range: str
    metrics_by_service: List[ServiceMetrics]
    overall_by_level: Dict[str, int]
    logs_per_second: float


class TimeSeriesPoint(BaseModel):
    """Single point in time series"""
    timestamp: str
    count: int
    by_level: Optional[Dict[str, int]] = None


class TimeSeriesResponse(BaseModel):
    """Time series data response"""
    interval: str
    data: List[TimeSeriesPoint]
    total_points: int
