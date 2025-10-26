"""
Metrics service for log analytics
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger

from api.utils.elasticsearch_client import es_client
from api.config import ES_INDEX_PATTERN


class MetricsService:
    """Service for calculating log metrics"""
    
    async def get_overview(self) -> Dict[str, Any]:
        """Get overview metrics"""
        try:
            # Get total count using search with size 0
            count_query = {"query": {"match_all": {}}, "size": 0}
            count_response, _ = es_client.search(index=ES_INDEX_PATTERN, body=count_query)
            total_logs = count_response["hits"]["total"]["value"]
            
            # Get logs in last hour
            one_hour_ago = (datetime.now() - timedelta(hours=1)).isoformat()
            
            query = {
                "query": {
                    "range": {
                        "timestamp": {
                            "gte": one_hour_ago
                        }
                    }
                },
                "size": 0,
                "aggs": {
                    "by_level": {
                        "terms": {
                            "field": "level.keyword",
                            "size": 10
                        }
                    },
                    "by_service": {
                        "terms": {
                            "field": "service.keyword",
                            "size": 20
                        }
                    }
                }
            }
            
            response, _ = es_client.search(index=ES_INDEX_PATTERN, body=query)
            
            logs_last_hour = response["hits"]["total"]["value"]
            logs_per_minute = logs_last_hour / 60 if logs_last_hour > 0 else 0
            
            # Calculate error rate
            level_buckets = response["aggregations"]["by_level"]["buckets"]
            total_in_hour = sum(b["doc_count"] for b in level_buckets)
            error_count = sum(
                b["doc_count"] 
                for b in level_buckets 
                if b["key"] in ["ERROR", "CRITICAL"]
            )
            error_rate = (error_count / total_in_hour * 100) if total_in_hour > 0 else 0
            
            # Service count
            services_count = len(response["aggregations"]["by_service"]["buckets"])
            
            return {
                "total_logs": total_logs,
                "logs_last_hour": logs_last_hour,
                "logs_per_minute": round(logs_per_minute, 2),
                "error_rate": round(error_rate, 2),
                "services_count": services_count,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting metrics overview: {e}")
            raise
    
    async def get_service_metrics(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get metrics by service"""
        try:
            start_time = (datetime.now() - timedelta(minutes=minutes)).isoformat()
            
            query = {
                "query": {
                    "range": {
                        "timestamp": {
                            "gte": start_time
                        }
                    }
                },
                "size": 0,
                "aggs": {
                    "by_service": {
                        "terms": {
                            "field": "service.keyword",
                            "size": 50
                        },
                        "aggs": {
                            "by_level": {
                                "terms": {
                                    "field": "level.keyword",
                                    "size": 10
                                }
                            }
                        }
                    }
                }
            }
            
            response, _ = es_client.search(index=ES_INDEX_PATTERN, body=query)
            
            service_metrics = []
            for bucket in response["aggregations"]["by_service"]["buckets"]:
                service = bucket["key"]
                total_logs = bucket["doc_count"]
                
                # Count errors
                level_buckets = bucket["by_level"]["buckets"]
                error_count = sum(
                    b["doc_count"]
                    for b in level_buckets
                    if b["key"] in ["ERROR", "CRITICAL"]
                )
                error_rate = (error_count / total_logs * 100) if total_logs > 0 else 0
                
                service_metrics.append({
                    "service": service,
                    "total_logs": total_logs,
                    "error_count": error_count,
                    "error_rate": round(error_rate, 2),
                    "logs_per_minute": round(total_logs / minutes, 2)
                })
            
            return sorted(service_metrics, key=lambda x: x["total_logs"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting service metrics: {e}")
            raise
    
    async def get_log_volume(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Get log volume over time"""
        try:
            start_time = (datetime.now() - timedelta(minutes=minutes)).isoformat()
            
            query = {
                "query": {
                    "range": {
                        "timestamp": {
                            "gte": start_time
                        }
                    }
                },
                "size": 0,
                "aggs": {
                    "over_time": {
                        "date_histogram": {
                            "field": "timestamp",
                            "fixed_interval": "1m"
                        },
                        "aggs": {
                            "by_level": {
                                "terms": {
                                    "field": "level.keyword",
                                    "size": 10
                                }
                            }
                        }
                    }
                }
            }
            
            response, _ = es_client.search(index=ES_INDEX_PATTERN, body=query)
            
            volume_data = []
            for bucket in response["aggregations"]["over_time"]["buckets"]:
                timestamp = bucket["key_as_string"]
                total = bucket["doc_count"]
                
                # Get counts by level
                levels = {}
                for level_bucket in bucket["by_level"]["buckets"]:
                    levels[level_bucket["key"]] = level_bucket["doc_count"]
                
                volume_data.append({
                    "timestamp": timestamp,
                    "total": total,
                    **levels
                })
            
            return volume_data
            
        except Exception as e:
            logger.error(f"Error getting log volume: {e}")
            raise


# Global metrics service instance
metrics_service = MetricsService()
