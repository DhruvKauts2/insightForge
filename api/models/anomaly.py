"""
Anomaly detection models
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class AnomalyScore(BaseModel):
    """Anomaly score for a metric"""
    timestamp: str
    metric_name: str
    actual_value: float
    expected_value: float
    anomaly_score: float
    is_anomaly: bool
    confidence: float
    severity: str  # low, medium, high, critical


class DetectedAnomaly(BaseModel):
    """Detected anomaly"""
    id: Optional[str] = None
    detected_at: str
    metric_name: str
    service: Optional[str] = None
    anomaly_type: str  # spike, drop, pattern_change
    description: str
    score: float
    severity: str
    actual_value: float
    expected_value: float
    deviation_percent: float
    
    
class AnomalyBaseline(BaseModel):
    """Baseline for anomaly detection"""
    metric_name: str
    service: Optional[str] = None
    mean: float
    std_dev: float
    min_value: float
    max_value: float
    sample_count: int
    last_updated: str


class AnomalyDetectionConfig(BaseModel):
    """Configuration for anomaly detection"""
    enabled: bool = True
    sensitivity: float = 1.5  # Standard deviations for threshold
    min_samples: int = 100  # Minimum samples for baseline
    detection_window_minutes: int = 5
    methods: List[str] = ["zscore", "isolation_forest", "moving_average"]


class AnomalyReport(BaseModel):
    """Anomaly detection report"""
    period_start: str
    period_end: str
    total_anomalies: int
    anomalies: List[DetectedAnomaly]
    anomalies_by_severity: dict
    anomalies_by_service: dict
