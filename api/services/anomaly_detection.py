"""
Anomaly detection service using statistical methods
"""
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from loguru import logger

from api.utils.elasticsearch_client import es_client
from api.config import ES_INDEX_PATTERN
from api.models.anomaly import (
    AnomalyScore, TimeSeriesAnomaly, ServiceAnomaly,
    AnomalyReport, BaselineStats
)


class AnomalyDetectionService:
    """ML-based anomaly detection for logs"""
    
    def __init__(self):
        self.baselines: Dict[str, BaselineStats] = {}
    
    async def detect_log_volume_anomalies(
        self,
        service: Optional[str] = None,
        time_window_hours: int = 24,
        interval_minutes: int = 5,
        threshold: float = 3.0  # Z-score threshold
    ) -> TimeSeriesAnomaly:
        """
        Detect anomalies in log volume using statistical methods
        
        Args:
            service: Optional service name to analyze
            time_window_hours: Time window for analysis
            interval_minutes: Bucket interval for time series
            threshold: Z-score threshold (default 3.0 = 99.7%)
            
        Returns:
            TimeSeriesAnomaly with detected anomalies
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_window_hours)
            
            # Build query
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"range": {"timestamp": {
                                "gte": start_time.isoformat(),
                                "lte": end_time.isoformat()
                            }}}
                        ]
                    }
                },
                "size": 0,
                "aggs": {
                    "over_time": {
                        "date_histogram": {
                            "field": "timestamp",
                            "fixed_interval": f"{interval_minutes}m",
                            "min_doc_count": 0
                        }
                    }
                }
            }
            
            if service:
                query["query"]["bool"]["must"].append({"term": {"service.keyword": service}})
            
            response, _ = es_client.search(index=ES_INDEX_PATTERN, body=query)
            
            # Extract time series data
            buckets = response["aggregations"]["over_time"]["buckets"]
            timestamps = [bucket["key_as_string"] for bucket in buckets]
            values = np.array([bucket["doc_count"] for bucket in buckets])
            
            if len(values) < 3:
                return TimeSeriesAnomaly(
                    metric_name="log_volume",
                    time_range_hours=time_window_hours,
                    total_points=len(values),
                    anomalies_detected=0,
                    anomaly_rate=0.0,
                    scores=[]
                )
            
            # Calculate Z-scores
            mean = np.mean(values)
            std = np.std(values)
            
            if std == 0:
                std = 1  # Avoid division by zero
            
            z_scores = np.abs((values - mean) / std)
            
            # Detect anomalies
            scores = []
            anomalies_count = 0
            
            for i, (timestamp, value, z_score) in enumerate(zip(timestamps, values, z_scores)):
                is_anomaly = z_score > threshold
                if is_anomaly:
                    anomalies_count += 1
                
                scores.append(AnomalyScore(
                    timestamp=timestamp,
                    value=float(value),
                    score=float(z_score),
                    is_anomaly=is_anomaly,
                    threshold=threshold
                ))
            
            return TimeSeriesAnomaly(
                metric_name="log_volume",
                time_range_hours=time_window_hours,
                total_points=len(values),
                anomalies_detected=anomalies_count,
                anomaly_rate=anomalies_count / len(values) if len(values) > 0 else 0.0,
                scores=scores
            )
            
        except Exception as e:
            logger.error(f"Error detecting log volume anomalies: {e}")
            return TimeSeriesAnomaly(
                metric_name="log_volume",
                time_range_hours=time_window_hours,
                total_points=0,
                anomalies_detected=0,
                anomaly_rate=0.0,
                scores=[]
            )
    
    async def detect_error_rate_anomalies(
        self,
        time_window_hours: int = 24,
        interval_minutes: int = 15
    ) -> List[ServiceAnomaly]:
        """
        Detect anomalies in error rates per service
        
        Uses Isolation Forest algorithm for multivariate anomaly detection
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_window_hours)
            
            # Get error rates by service over time
            query = {
                "query": {
                    "range": {"timestamp": {
                        "gte": start_time.isoformat(),
                        "lte": end_time.isoformat()
                    }}
                },
                "size": 0,
                "aggs": {
                    "by_service": {
                        "terms": {
                            "field": "service.keyword",
                            "size": 50
                        },
                        "aggs": {
                            "over_time": {
                                "date_histogram": {
                                    "field": "timestamp",
                                    "fixed_interval": f"{interval_minutes}m"
                                },
                                "aggs": {
                                    "errors": {
                                        "filter": {
                                            "terms": {"level": ["ERROR", "CRITICAL"]}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
            
            response, _ = es_client.search(index=ES_INDEX_PATTERN, body=query)
            
            anomalies = []
            
            for service_bucket in response["aggregations"]["by_service"]["buckets"]:
                service = service_bucket["key"]
                time_buckets = service_bucket["over_time"]["buckets"]
                
                if len(time_buckets) < 5:
                    continue
                
                # Extract error rates
                error_rates = []
                timestamps = []
                
                for bucket in time_buckets:
                    total = bucket["doc_count"]
                    errors = bucket["errors"]["doc_count"]
                    error_rate = (errors / total * 100) if total > 0 else 0
                    error_rates.append(error_rate)
                    timestamps.append(bucket["key_as_string"])
                
                # Use Isolation Forest for anomaly detection
                if len(error_rates) >= 5:
                    X = np.array(error_rates).reshape(-1, 1)
                    
                    iso_forest = IsolationForest(
                        contamination=0.1,  # Expected 10% anomalies
                        random_state=42
                    )
                    predictions = iso_forest.fit_predict(X)
                    
                    # Calculate expected value (moving average)
                    window_size = min(5, len(error_rates))
                    expected_values = np.convolve(
                        error_rates,
                        np.ones(window_size) / window_size,
                        mode='same'
                    )
                    
                    # Find anomalies
                    for i, (pred, timestamp, current, expected) in enumerate(
                        zip(predictions, timestamps, error_rates, expected_values)
                    ):
                        if pred == -1:  # Anomaly detected
                            deviation = abs(current - expected)
                            
                            # Determine severity
                            if deviation > 20:
                                severity = "high"
                            elif deviation > 10:
                                severity = "medium"
                            else:
                                severity = "low"
                            
                            anomalies.append(ServiceAnomaly(
                                service=service,
                                timestamp=timestamp,
                                metric="error_rate",
                                current_value=current,
                                expected_value=expected,
                                deviation=deviation,
                                severity=severity,
                                description=f"Error rate spike detected: {current:.2f}% (expected {expected:.2f}%)"
                            ))
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting error rate anomalies: {e}")
            return []
    
    async def generate_anomaly_report(
        self,
        time_window_hours: int = 24
    ) -> AnomalyReport:
        """
        Generate comprehensive anomaly report
        
        Combines multiple anomaly detection methods
        """
        try:
            # Detect error rate anomalies
            anomalies = await self.detect_error_rate_anomalies(time_window_hours)
            
            # Count by service
            by_service: Dict[str, int] = {}
            for anomaly in anomalies:
                by_service[anomaly.service] = by_service.get(anomaly.service, 0) + 1
            
            # Count by severity
            by_severity: Dict[str, int] = {
                "low": 0,
                "medium": 0,
                "high": 0
            }
            for anomaly in anomalies:
                by_severity[anomaly.severity] += 1
            
            return AnomalyReport(
                generated_at=datetime.now().isoformat(),
                time_window_hours=time_window_hours,
                total_anomalies=len(anomalies),
                by_service=by_service,
                by_severity=by_severity,
                anomalies=sorted(anomalies, key=lambda x: x.deviation, reverse=True)
            )
            
        except Exception as e:
            logger.error(f"Error generating anomaly report: {e}")
            return AnomalyReport(
                generated_at=datetime.now().isoformat(),
                time_window_hours=time_window_hours,
                total_anomalies=0,
                by_service={},
                by_severity={"low": 0, "medium": 0, "high": 0},
                anomalies=[]
            )
    
    async def calculate_baseline(
        self,
        metric_name: str,
        service: Optional[str] = None,
        lookback_days: int = 7
    ) -> BaselineStats:
        """
        Calculate baseline statistics for a metric
        
        Used for threshold adaptation
        """
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=lookback_days)
            
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"range": {"timestamp": {
                                "gte": start_time.isoformat(),
                                "lte": end_time.isoformat()
                            }}}
                        ]
                    }
                },
                "size": 0,
                "aggs": {
                    "over_time": {
                        "date_histogram": {
                            "field": "timestamp",
                            "fixed_interval": "1h"
                        }
                    }
                }
            }
            
            if service:
                query["query"]["bool"]["must"].append({"term": {"service.keyword": service}})
            
            response, _ = es_client.search(index=ES_INDEX_PATTERN, body=query)
            
            buckets = response["aggregations"]["over_time"]["buckets"]
            values = [bucket["doc_count"] for bucket in buckets]
            
            if not values:
                return BaselineStats(
                    metric_name=metric_name,
                    service=service,
                    mean=0.0,
                    std_dev=0.0,
                    min_value=0.0,
                    max_value=0.0,
                    sample_count=0,
                    last_updated=datetime.now().isoformat()
                )
            
            return BaselineStats(
                metric_name=metric_name,
                service=service,
                mean=float(np.mean(values)),
                std_dev=float(np.std(values)),
                min_value=float(np.min(values)),
                max_value=float(np.max(values)),
                sample_count=len(values),
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Error calculating baseline: {e}")
            return BaselineStats(
                metric_name=metric_name,
                service=service,
                mean=0.0,
                std_dev=0.0,
                min_value=0.0,
                max_value=0.0,
                sample_count=0,
                last_updated=datetime.now().isoformat()
            )


# Global anomaly detection service instance
anomaly_service = AnomalyDetectionService()
