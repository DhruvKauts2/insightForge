"""
SQLAlchemy database models
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    alert_rules = relationship("AlertRule", back_populates="owner")
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"


class AlertRule(Base):
    """Alert rule configuration"""
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Rule configuration
    query = Column(Text, nullable=False)  # Elasticsearch query
    condition = Column(String(50), nullable=False)  # "greater_than", "less_than", "equals"
    threshold = Column(Float, nullable=False)
    time_window = Column(Integer, nullable=False)  # Minutes
    
    # Filters
    services = Column(JSON)  # List of services to monitor
    levels = Column(JSON)  # List of log levels
    
    # Actions
    notification_channel = Column(String(50), nullable=False)  # "email", "slack", "webhook"
    notification_config = Column(JSON)  # Channel-specific configuration
    
    # Status
    is_active = Column(Boolean, default=True)
    last_triggered = Column(DateTime, nullable=True)
    trigger_count = Column(Integer, default=0)
    
    # Metadata
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="alert_rules")
    triggered_alerts = relationship("TriggeredAlert", back_populates="rule")
    
    def __repr__(self):
        return f"<AlertRule(name='{self.name}', active={self.is_active})>"


class TriggeredAlert(Base):
    """History of triggered alerts"""
    __tablename__ = "triggered_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.id"), nullable=False)
    
    # Alert details
    triggered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    value = Column(Float, nullable=False)  # The value that triggered the alert
    threshold = Column(Float, nullable=False)  # Threshold at time of trigger
    
    # Context
    log_count = Column(Integer)
    sample_logs = Column(JSON)  # Sample logs that triggered the alert
    
    # Status
    status = Column(String(20), default="triggered")  # "triggered", "acknowledged", "resolved"
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    notes = Column(Text)
    
    # Relationships
    rule = relationship("AlertRule", back_populates="triggered_alerts")
    
    def __repr__(self):
        return f"<TriggeredAlert(rule_id={self.rule_id}, status='{self.status}')>"


class SystemConfig(Base):
    """System-wide configuration"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(JSON, nullable=False)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<SystemConfig(key='{self.key}')>"
