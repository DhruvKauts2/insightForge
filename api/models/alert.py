"""
Pydantic models for alerts
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AlertRuleCreate(BaseModel):
    """Model for creating an alert rule"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    query: str = Field(default="", description="Elasticsearch query string")
    condition: str = Field(..., pattern="^(greater_than|less_than|equals|greater_than_or_equal|less_than_or_equal)$")
    threshold: float
    time_window: int = Field(default=5, ge=1, le=1440, description="Time window in minutes")
    services: Optional[List[str]] = None
    levels: Optional[List[str]] = None
    notification_channel: str = Field(..., pattern="^(console|webhook|email|slack)$")
    notification_config: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "High Error Rate",
                "description": "Alert when error count exceeds 100",
                "query": "",
                "condition": "greater_than",
                "threshold": 100,
                "time_window": 5,
                "services": ["payment-service"],
                "levels": ["ERROR"],
                "notification_channel": "webhook",
                "notification_config": {
                    "url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
                },
                "is_active": True
            }
        }


class AlertRuleUpdate(BaseModel):
    """Model for updating an alert rule"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    query: Optional[str] = None
    condition: Optional[str] = Field(None, pattern="^(greater_than|less_than|equals|greater_than_or_equal|less_than_or_equal)$")
    threshold: Optional[float] = None
    time_window: Optional[int] = Field(None, ge=1, le=1440)
    services: Optional[List[str]] = None
    levels: Optional[List[str]] = None
    notification_channel: Optional[str] = Field(None, pattern="^(console|webhook|email|slack)$")
    notification_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AlertRuleResponse(BaseModel):
    """Model for alert rule response"""
    id: int
    name: str
    description: Optional[str]
    query: str
    condition: str
    threshold: float
    time_window: int
    services: Optional[List[str]]
    levels: Optional[List[str]]
    notification_channel: str
    notification_config: Dict[str, Any]
    is_active: bool
    last_triggered: Optional[datetime]
    trigger_count: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TriggeredAlertResponse(BaseModel):
    """Model for triggered alert response"""
    id: int
    rule_id: int
    rule_name: Optional[str] = None
    triggered_at: datetime
    value: float
    threshold: float
    log_count: Optional[int]
    sample_logs: Optional[List[Dict[str, Any]]]
    status: str
    acknowledged_at: Optional[datetime]
    acknowledged_by: Optional[int]
    resolved_at: Optional[datetime]
    notes: Optional[str]


class AlertAcknowledge(BaseModel):
    """Model for acknowledging an alert"""
    notes: Optional[str] = None


class AlertResolve(BaseModel):
    """Model for resolving an alert"""
    notes: Optional[str] = None
