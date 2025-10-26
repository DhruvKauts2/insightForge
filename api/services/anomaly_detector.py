"""
Anomaly detection service using statistical methods and ML
"""
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
from loguru import logger

from api.utils.elasticsearch_client import es_client
from api.config import ES_INDEX_PATTERN
from api.models.anomaly import (
    AnomalyScore, DetectedAnomaly, AnomalyBaseline,
    AnomalyDetectionConfig
)


class AnomalyDetector:
    """Detect anomalies in log metrics using multiple methods"""
    
    def __init__(self):
        self.config = AnomalyDetectionConfig()
        self.config.min_samples = 5  # Lower for sparse time-series data
        self.config.sensitivity = 1.0  # Lower threshold for better detection
        self.baselines: Dict[str, AnomalyBaseline] = {}
        logger.info(f"Anomaly detector initialized: min_samples={self.config.min_samples}, sensitivity={self.config.sensitivity}")
    
    async def detect_log_volume_anomalies(
        self,
        service: Optional[str] = None,
        window_minutes: int = 60
    ) -> List[DetectedAnomaly]:
        """
        Detect anomalies in log volume
        
        Args:
            service: Optional service to check
            window_minutes: Time window for detection
            
        Returns:
            List of detected anomalies
        """
        try:
            time_series = await self._get_log_volume_timeseries(
                service=service,
                window_minutes=window_minutes
            )
            
            logger.info(f"Got {len(time_series)} time series points for anomaly detection")
            
            if len(time_series) < self.config.min_samples:
                logger.debug(f"Not enough samples: {len(time_series)} < {self.config.min_samples}")
                return []
            
            anomalies = []
            
            # Z-Score method
            zscore_anomalies = self._detect_zscore_anomalies(
                time_series,
                metric_name="log_volume",
                service=service
            )
            logger.info(f"Z-Score found {len(zscore_anomalies)} anomalies")
            anomalies.extend(zscore_anomalies)
            
            # Moving average method
            ma_anomalies = self._detect_moving_average_anomalies(
                time_series,
                metric_name="log_volume",
                service=service,
                window=min(5, len(time_series) // 3)
            )
            logger.info(f"Moving Average found {len(ma_anomalies)} anomalies")
            anomalies.extend(ma_anomalies)
            
            # Isolation Forest (if enough data)
            if len(time_series) >= 20:
                if_anomalies = self._detect_isolation_forest_anomalies(
                    time_series,
                    metric_name="log_volume",
                    service=service
                )
                logger.info(f"Isolation Forest found {len(if_anomalies)} anomalies")
                anomalies.extend(if_anomalies)
            
            anomalies = self._deduplicate_anomalies(anomalies)
            logger.info(f"Total unique anomalies: {len(anomalies)}")
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Error detecting log volume anomalies: {e}")
            return []
    
    async def detect_error_rate_anomalies(
        self,
        service: Optional[str] = None,
        window_minutes: int = 60
    ) -> List[DetectedAnomaly]:
        """Detect anomalies in error rates"""
        try:
            time_series = await self._get_error_rate_timeseries(
                service=service,
                window_minutes=window_minutes
            )
            
            if len(time_series) < self.config.min_samples:
                return []
            
            anomalies = self._detect_zscore_anomalies(
                time_series,
                metric_name="error_rate",
                service=service
            )
            
            return self._deduplicate_anomalies(anomalies)
            
        except Exception as e:
            logger.error(f"Error detecting error rate anomalies: {e}")
            return []
    
    def _detect_zscore_anomalies(
        self,
        time_series: List[Tuple[str, float]],
        metric_name: str,
        service: Optional[str] = None
    ) -> List[DetectedAnomaly]:
        """Detect anomalies using Z-Score method"""
        anomalies = []
        
        try:
            values = np.array([v for _, v in time_series])
            timestamps = [t for t, _ in time_series]
            
            mean = np.mean(values)
            std = np.std(values)
            
            logger.debug(f"Z-Score: mean={mean:.2f}, std={std:.2f}")
            
            if std == 0:
                logger.debug("Standard deviation is 0, no anomalies")
                return []
            
            z_scores = np.abs((values - mean) / std)
            
            threshold = self.config.sensitivity
            anomaly_indices = np.where(z_scores > threshold)[0]
            
            logger.debug(f"Found {len(anomaly_indices)} points above threshold {threshold}")
            logger.debug(f"Z-scores: {z_scores}")
            logger.debug(f"Anomaly indices: {anomaly_indices}")
            
            for idx in anomaly_indices:
                actual_value = values[idx]
                z_score = z_scores[idx]
                
                if z_score > 4:
                    severity = "critical"
                elif z_score > 3:
                    severity = "high"
                elif z_score > 2.5:
                    severity = "medium"
                elif z_score > 1.5:
                    severity = "medium"
                else:
                    severity = "low"
                
                anomaly_type = "spike" if actual_value > mean else "drop"
                deviation_percent = ((actual_value - mean) / mean * 100) if mean != 0 else 0
                
                anomaly = DetectedAnomaly(
                    detected_at=timestamps[idx],
                    metric_name=metric_name,
                    service=service,
                    anomaly_type=anomaly_type,
                    description=f"{metric_name} {anomaly_type}: {actual_value:.2f} (expected ~{mean:.2f})",
                    score=float(z_score),
                    severity=severity,
                    actual_value=float(actual_value),
                    expected_value=float(mean),
                    deviation_percent=float(deviation_percent)
                )
                anomalies.append(anomaly)
                logger.debug(f"Detected anomaly: {anomaly_type} at {timestamps[idx]}, score={z_score:.2f}")
            
        except Exception as e:
            logger.error(f"Error in Z-Score detection: {e}")
        
        return anomalies
    
    def _detect_moving_average_anomalies(
        self,
        time_series: List[Tuple[str, float]],
        metric_name: str,
        service: Optional[str] = None,
        window: int = 5
    ) -> List[DetectedAnomaly]:
        """Detect anomalies using Moving Average method"""
        anomalies = []
        
        try:
            if len(time_series) < window:
                return []
            
            values = np.array([v for _, v in time_series])
            timestamps = [t for t, _ in time_series]
            
            moving_avg = np.convolve(values, np.ones(window)/window, mode='valid')
            moving_std = np.array([
                np.std(values[max(0, i-window):i+1])
                for i in range(len(values))
            ])
            
            for i in range(window, len(values)):
                if moving_std[i] == 0:
                    continue
                
                deviation = abs(values[i] - moving_avg[i-window])
                threshold = self.config.sensitivity * moving_std[i]
                
                if deviation > threshold:
                    z_score = deviation / moving_std[i]
                    
                    if z_score > 2:
                        severity = "high" if z_score > 3 else "medium"
                        anomaly_type = "spike" if values[i] > moving_avg[i-window] else "drop"
                        
                        anomaly = DetectedAnomaly(
                            detected_at=timestamps[i],
                            metric_name=metric_name,
                            service=service,
                            anomaly_type=anomaly_type,
                            description=f"{metric_name} MA {anomaly_type}: {values[i]:.2f}",
                            score=float(z_score),
                            severity=severity,
                            actual_value=float(values[i]),
                            expected_value=float(moving_avg[i-window]),
                            deviation_percent=float((deviation / moving_avg[i-window] * 100) if moving_avg[i-window] != 0 else 0)
                        )
                        anomalies.append(anomaly)
            
        except Exception as e:
            logger.error(f"Error in Moving Average detection: {e}")
        
        return anomalies
    
    def _detect_isolation_forest_anomalies(
        self,
        time_series: List[Tuple[str, float]],
        metric_name: str,
        service: Optional[str] = None
    ) -> List[DetectedAnomaly]:
        """Detect anomalies using Isolation Forest ML algorithm"""
        anomalies = []
        
        try:
            values = np.array([v for _, v in time_series]).reshape(-1, 1)
            timestamps = [t for t, _ in time_series]
            
            clf = IsolationForest(
                contamination=0.1,
                random_state=42
            )
            predictions = clf.fit_predict(values)
            scores = clf.score_samples(values)
            
            anomaly_indices = np.where(predictions == -1)[0]
            
            for idx in anomaly_indices:
                score = abs(scores[idx])
                actual_value = values[idx][0]
                mean_value = np.mean(values)
                
                if score > 0.6:
                    severity = "critical"
                elif score > 0.5:
                    severity = "high"
                elif score > 0.4:
                    severity = "medium"
                else:
                    severity = "low"
                
                anomaly_type = "pattern_change"
                if actual_value > mean_value * 1.5:
                    anomaly_type = "spike"
                elif actual_value < mean_value * 0.5:
                    anomaly_type = "drop"
                
                anomaly = DetectedAnomaly(
                    detected_at=timestamps[idx],
                    metric_name=metric_name,
                    service=service,
                    anomaly_type=anomaly_type,
                    description=f"{metric_name} IF anomaly: {actual_value:.2f}",
                    score=float(score),
                    severity=severity,
                    actual_value=float(actual_value),
                    expected_value=float(mean_value),
                    deviation_percent=float(((actual_value - mean_value) / mean_value * 100) if mean_value != 0 else 0)
                )
                anomalies.append(anomaly)
            
        except Exception as e:
            logger.error(f"Error in Isolation Forest detection: {e}")
        
        return anomalies
    
    def _deduplicate_anomalies(self, anomalies: List[DetectedAnomaly]) -> List[DetectedAnomaly]:
        """Remove duplicate anomalies and keep highest severity"""
        if not anomalies:
            return []
        
        grouped: Dict[str, List[DetectedAnomaly]] = {}
        
        for anomaly in anomalies:
            key = f"{anomaly.detected_at}_{anomaly.metric_name}"
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(anomaly)
        
        deduplicated = []
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        
        for key, group in grouped.items():
            best = max(group, key=lambda x: (severity_order.get(x.severity, 0), x.score))
            deduplicated.append(best)
        
        return sorted(deduplicated, key=lambda x: x.detected_at, reverse=True)
    
    async def _get_log_volume_timeseries(
        self,
        service: Optional[str] = None,
        window_minutes: int = 60
    ) -> List[Tuple[str, float]]:
        """Get log volume time series data"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=window_minutes)
            
            query: Dict[str, Any] = {
                "query": {
                    "range": {
                        "timestamp": {
                            "gte": start_time.isoformat(),
                            "lte": end_time.isoformat()
                        }
                    }
                },
                "size": 0,
                "aggs": {
                    "time_buckets": {
                        "date_histogram": {
                            "field": "timestamp",
                            "fixed_interval": "1m"
                        }
                    }
                }
            }
            
            if service:
                query["query"] = {
                    "bool": {
                        "must": [
                            query["query"],
                            {"term": {"service.keyword": service}}
                        ]
                    }
                }
            
            response, _ = es_client.search(index=ES_INDEX_PATTERN, body=query)
            
            time_series = []
            for bucket in response["aggregations"]["time_buckets"]["buckets"]:
                timestamp = bucket["key_as_string"]
                count = bucket["doc_count"]
                time_series.append((timestamp, float(count)))
            
            return time_series
            
        except Exception as e:
            logger.error(f"Error getting log volume time series: {e}")
            return []
    
    async def _get_error_rate_timeseries(
        self,
        service: Optional[str] = None,
        window_minutes: int = 60
    ) -> List[Tuple[str, float]]:
        """Get error rate time series data"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=window_minutes)
            
            query: Dict[str, Any] = {
                "query": {
                    "range": {
                        "timestamp": {
                            "gte": start_time.isoformat(),
                            "lte": end_time.isoformat()
                        }
                    }
                },
                "size": 0,
                "aggs": {
                    "time_buckets": {
                        "date_histogram": {
                            "field": "timestamp",
                            "fixed_interval": "1m"
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
            
            if service:
                query["query"] = {
                    "bool": {
                        "must": [
                            query["query"],
                            {"term": {"service.keyword": service}}
                        ]
                    }
                }
            
            response, _ = es_client.search(index=ES_INDEX_PATTERN, body=query)
            
            time_series = []
            for bucket in response["aggregations"]["time_buckets"]["buckets"]:
                timestamp = bucket["key_as_string"]
                total = bucket["doc_count"]
                errors = bucket["errors"]["doc_count"]
                error_rate = (errors / total * 100) if total > 0 else 0
                time_series.append((timestamp, float(error_rate)))
            
            return time_series
            
        except Exception as e:
            logger.error(f"Error getting error rate time series: {e}")
            return []


# Global anomaly detector instance
anomaly_detector = AnomalyDetector()
