"""
Metrics and aggregation routes
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from loguru import logger
from datetime import datetime

from api.models.metrics import (
    TimeRangeMetrics, 
    ServiceMetrics, 
    SystemMetrics,
    TopError,
    TimeSeriesResponse,
    TimeSeriesPoint
)
from api.utils.elasticsearch_client import es_client
from api.config import ES_INDEX_PATTERN

router = APIRouter(prefix="/api/v1/metrics", tags=["Metrics"])


@router.get("/overview", response_model=TimeRangeMetrics)
async def get_metrics_overview():
    """
    Get metrics overview for all logs
    
    Returns aggregated metrics including:
    - Total logs
    - Distribution by level
    - Distribution by service
    - Error rate
    """
    try:
        # Simple query without time filter
        es_query = {
            "query": {"match_all": {}},
            "size": 0,
            "aggs": {
                "by_level": {
                    "terms": {"field": "level", "size": 10}
                },
                "by_service": {
                    "terms": {"field": "service", "size": 50}
                }
            }
        }
        
        es_response, query_time = es_client.search(
            index=ES_INDEX_PATTERN,
            body=es_query
        )
        
        total_logs = es_response["hits"]["total"]["value"]
        
        by_level = {
            bucket["key"]: bucket["doc_count"]
            for bucket in es_response["aggregations"]["by_level"]["buckets"]
        }
        
        by_service = {
            bucket["key"]: bucket["doc_count"]
            for bucket in es_response["aggregations"]["by_service"]["buckets"]
        }
        
        # Calculate metrics
        error_count = by_level.get("ERROR", 0)
        error_rate = round((error_count / total_logs * 100), 2) if total_logs > 0 else 0
        
        # Estimate logs per minute (assuming data from last hour)
        logs_per_minute = round(total_logs / 60, 2) if total_logs > 0 else 0
        
        return TimeRangeMetrics(
            time_range="all",
            total_logs=total_logs,
            logs_per_minute=logs_per_minute,
            by_level=by_level,
            by_service=by_service,
            error_rate=error_rate
        )
        
    except Exception as e:
        logger.error(f"Metrics overview error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/service/{service_name}", response_model=ServiceMetrics)
async def get_service_metrics(service_name: str):
    """
    Get metrics for a specific service
    
    Returns detailed metrics for a single service including:
    - Total logs
    - Distribution by level
    - Error rate
    - Top error messages
    """
    try:
        # Query for service metrics
        es_query = {
            "query": {
                "term": {"service": service_name}
            },
            "size": 0,
            "aggs": {
                "by_level": {
                    "terms": {"field": "level", "size": 10}
                },
                "top_errors": {
                    "filter": {"term": {"level": "ERROR"}},
                    "aggs": {
                        "error_messages": {
                            "terms": {
                                "field": "message.keyword",
                                "size": 10
                            },
                            "aggs": {
                                "latest": {
                                    "top_hits": {
                                        "size": 1,
                                        "sort": [{"timestamp": "desc"}],
                                        "_source": ["timestamp"]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        es_response, _ = es_client.search(
            index=ES_INDEX_PATTERN,
            body=es_query
        )
        
        total_logs = es_response["hits"]["total"]["value"]
        
        if total_logs == 0:
            raise HTTPException(status_code=404, detail=f"No logs found for service: {service_name}")
        
        by_level = {
            bucket["key"]: bucket["doc_count"]
            for bucket in es_response["aggregations"]["by_level"]["buckets"]
        }
        
        error_count = by_level.get("ERROR", 0)
        error_rate = round((error_count / total_logs * 100), 2) if total_logs > 0 else 0
        
        # Parse top errors
        top_errors = []
        error_buckets = es_response["aggregations"]["top_errors"]["error_messages"]["buckets"]
        for bucket in error_buckets[:10]:
            if bucket["latest"]["hits"]["hits"]:
                latest_hit = bucket["latest"]["hits"]["hits"][0]
                top_errors.append(TopError(
                    message=bucket["key"],
                    count=bucket["doc_count"],
                    service=service_name,
                    last_seen=latest_hit["_source"]["timestamp"]
                ))
        
        return ServiceMetrics(
            service=service_name,
            total_logs=total_logs,
            by_level=by_level,
            error_rate=error_rate,
            top_errors=top_errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service metrics error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get service metrics: {str(e)}")


@router.get("/system", response_model=SystemMetrics)
async def get_system_metrics():
    """
    Get comprehensive system metrics
    
    Returns system-wide metrics including:
    - Overall statistics
    - Per-service breakdown
    - Performance metrics
    """
    try:
        # Query for all services
        es_query = {
            "query": {"match_all": {}},
            "size": 0,
            "aggs": {
                "by_level": {
                    "terms": {"field": "level", "size": 10}
                },
                "by_service": {
                    "terms": {"field": "service", "size": 50},
                    "aggs": {
                        "by_level": {
                            "terms": {"field": "level", "size": 10}
                        },
                        "top_errors": {
                            "filter": {"term": {"level": "ERROR"}},
                            "aggs": {
                                "messages": {
                                    "terms": {"field": "message.keyword", "size": 5},
                                    "aggs": {
                                        "latest": {
                                            "top_hits": {
                                                "size": 1,
                                                "sort": [{"timestamp": "desc"}],
                                                "_source": ["timestamp"]
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        es_response, _ = es_client.search(
            index=ES_INDEX_PATTERN,
            body=es_query
        )
        
        total_logs = es_response["hits"]["total"]["value"]
        
        # Overall level distribution
        overall_by_level = {
            bucket["key"]: bucket["doc_count"]
            for bucket in es_response["aggregations"]["by_level"]["buckets"]
        }
        
        # Per-service metrics
        service_buckets = es_response["aggregations"]["by_service"]["buckets"]
        metrics_by_service = []
        
        for service_bucket in service_buckets:
            service_name = service_bucket["key"]
            service_total = service_bucket["doc_count"]
            
            service_by_level = {
                bucket["key"]: bucket["doc_count"]
                for bucket in service_bucket["by_level"]["buckets"]
            }
            
            error_count = service_by_level.get("ERROR", 0)
            error_rate = round((error_count / service_total * 100), 2) if service_total > 0 else 0
            
            # Top errors for this service
            top_errors = []
            error_messages = service_bucket["top_errors"]["messages"]["buckets"]
            for msg_bucket in error_messages[:5]:
                if msg_bucket["latest"]["hits"]["hits"]:
                    latest_hit = msg_bucket["latest"]["hits"]["hits"][0]
                    top_errors.append(TopError(
                        message=msg_bucket["key"],
                        count=msg_bucket["doc_count"],
                        service=service_name,
                        last_seen=latest_hit["_source"]["timestamp"]
                    ))
            
            metrics_by_service.append(ServiceMetrics(
                service=service_name,
                total_logs=service_total,
                by_level=service_by_level,
                error_rate=error_rate,
                top_errors=top_errors
            ))
        
        # Estimate logs per second (assuming recent data)
        logs_per_second = round(total_logs / 3600, 2) if total_logs > 0 else 0
        
        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            total_logs=total_logs,
            total_services=len(service_buckets),
            time_range="all",
            metrics_by_service=metrics_by_service,
            overall_by_level=overall_by_level,
            logs_per_second=logs_per_second
        )
        
    except Exception as e:
        logger.error(f"System metrics error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")


@router.get("/timeseries", response_model=TimeSeriesResponse)
async def get_time_series(
    interval: str = Query("5m", regex="^(1m|5m|15m|30m|1h)$"),
    service: Optional[str] = Query(None)
):
    """
    Get time series data for visualization
    
    Returns log counts over time with specified interval.
    """
    try:
        # Build query
        if service:
            query = {"term": {"service": service}}
        else:
            query = {"match_all": {}}
        
        es_query = {
            "query": query,
            "size": 0,
            "aggs": {
                "over_time": {
                    "date_histogram": {
                        "field": "timestamp",
                        "fixed_interval": interval,
                        "format": "yyyy-MM-dd HH:mm:ss"
                    },
                    "aggs": {
                        "by_level": {
                            "terms": {"field": "level"}
                        }
                    }
                }
            }
        }
        
        es_response, _ = es_client.search(
            index=ES_INDEX_PATTERN,
            body=es_query
        )
        
        # Parse time series data
        time_series_data = []
        for bucket in es_response["aggregations"]["over_time"]["buckets"]:
            by_level = {
                level_bucket["key"]: level_bucket["doc_count"]
                for level_bucket in bucket["by_level"]["buckets"]
            }
            
            time_series_data.append(TimeSeriesPoint(
                timestamp=bucket["key_as_string"],
                count=bucket["doc_count"],
                by_level=by_level
            ))
        
        return TimeSeriesResponse(
            interval=interval,
            data=time_series_data,
            total_points=len(time_series_data)
        )
        
    except Exception as e:
        logger.error(f"Time series error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get time series: {str(e)}")
