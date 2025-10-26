"""
Anomaly detection API routes
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from loguru import logger

from api.models.anomaly import DetectedAnomaly, AnomalyReport
from api.services.anomaly_detector import anomaly_detector

router = APIRouter(prefix="/api/v1/anomaly", tags=["Anomaly Detection"])


@router.get("/detect/log-volume", response_model=list[DetectedAnomaly])
async def detect_log_volume_anomalies(
    service: Optional[str] = Query(None, description="Service to analyze"),
    window_minutes: int = Query(60, ge=10, le=1440, description="Time window in minutes")
):
    """
    Detect anomalies in log volume
    
    Uses multiple ML methods:
    - Z-Score (statistical)
    - Moving Average
    - Isolation Forest (ML)
    """
    try:
        anomalies = await anomaly_detector.detect_log_volume_anomalies(
            service=service,
            window_minutes=window_minutes
        )
        return anomalies
        
    except Exception as e:
        logger.error(f"Error detecting log volume anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detect/error-rate", response_model=list[DetectedAnomaly])
async def detect_error_rate_anomalies(
    service: Optional[str] = Query(None, description="Service to analyze"),
    window_minutes: int = Query(60, ge=10, le=1440, description="Time window in minutes")
):
    """
    Detect anomalies in error rates
    
    Identifies unusual spikes or drops in error percentage
    """
    try:
        anomalies = await anomaly_detector.detect_error_rate_anomalies(
            service=service,
            window_minutes=window_minutes
        )
        return anomalies
        
    except Exception as e:
        logger.error(f"Error detecting error rate anomalies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report", response_model=AnomalyReport)
async def get_anomaly_report(
    service: Optional[str] = Query(None),
    window_minutes: int = Query(60, ge=10, le=1440)
):
    """
    Get comprehensive anomaly report
    
    Includes all detected anomalies with statistics
    """
    try:
        from datetime import datetime, timedelta
        
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=window_minutes)
        
        # Detect all types of anomalies
        log_volume_anomalies = await anomaly_detector.detect_log_volume_anomalies(
            service=service,
            window_minutes=window_minutes
        )
        
        error_rate_anomalies = await anomaly_detector.detect_error_rate_anomalies(
            service=service,
            window_minutes=window_minutes
        )
        
        # Combine all anomalies
        all_anomalies = log_volume_anomalies + error_rate_anomalies
        
        # Statistics
        anomalies_by_severity = {}
        anomalies_by_service = {}
        
        for anomaly in all_anomalies:
            # By severity
            severity = anomaly.severity
            anomalies_by_severity[severity] = anomalies_by_severity.get(severity, 0) + 1
            
            # By service
            if anomaly.service:
                service_name = anomaly.service
                anomalies_by_service[service_name] = anomalies_by_service.get(service_name, 0) + 1
        
        return AnomalyReport(
            period_start=start_time.isoformat(),
            period_end=end_time.isoformat(),
            total_anomalies=len(all_anomalies),
            anomalies=all_anomalies,
            anomalies_by_severity=anomalies_by_severity,
            anomalies_by_service=anomalies_by_service
        )
        
    except Exception as e:
        logger.error(f"Error generating anomaly report: {e}")
        raise HTTPException(status_code=500, detail=str(e))
