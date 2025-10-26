"""
Log correlation service - FIXED for keyword fields
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from loguru import logger

from api.utils.elasticsearch_client import es_client
from api.config import ES_INDEX_PATTERN
from api.models.correlation import (
    ServiceCall, RequestFlow, ServiceDependency, 
    DependencyGraph, CorrelatedLog
)


class CorrelationService:
    """Service for correlating logs across services"""
    
    async def get_request_flow(self, correlation_id: str) -> Optional[RequestFlow]:
        """Get complete request flow for a correlation ID"""
        try:
            query = {
                "query": {
                    "match": {"correlation_id": correlation_id}
                },
                "size": 1000,
                "sort": [{"timestamp": "asc"}]
            }
            
            response, _ = es_client.search(index=ES_INDEX_PATTERN, body=query)
            
            if response["hits"]["total"]["value"] == 0:
                return None
            
            service_calls = []
            services_set = set()
            error_count = 0
            
            for hit in response["hits"]["hits"]:
                log = hit["_source"]
                service = log.get("service", "unknown")
                services_set.add(service)
                
                if log.get("level") in ["ERROR", "CRITICAL"]:
                    error_count += 1
                
                service_call = ServiceCall(
                    service=service,
                    timestamp=log.get("timestamp"),
                    log_id=hit["_id"],
                    message=log.get("message", ""),
                    level=log.get("level", "INFO"),
                    status=log.get("status"),
                    duration_ms=log.get("duration_ms")
                )
                service_calls.append(service_call)
            
            if service_calls:
                start_time = service_calls[0].timestamp
                end_time = service_calls[-1].timestamp
                
                try:
                    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                    duration_ms = (end_dt - start_dt).total_seconds() * 1000
                except:
                    duration_ms = None
            else:
                start_time = None
                end_time = None
                duration_ms = None
            
            return RequestFlow(
                correlation_id=correlation_id,
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                services=sorted(list(services_set)),
                total_calls=len(service_calls),
                service_calls=service_calls,
                error_count=error_count
            )
            
        except Exception as e:
            logger.error(f"Error getting request flow: {e}")
            return None
    
    async def get_related_logs(self, log_id: str, time_window_seconds: int = 60) -> List[CorrelatedLog]:
        """Get logs related to a specific log"""
        try:
            original_log = es_client.get_by_id(ES_INDEX_PATTERN, log_id)
            if not original_log:
                return []
            
            log_data = original_log["_source"]
            service = log_data.get("service")
            timestamp = log_data.get("timestamp")
            correlation_id = log_data.get("correlation_id")
            
            try:
                log_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                return []
            
            start_time = (log_time - timedelta(seconds=time_window_seconds)).isoformat()
            end_time = (log_time + timedelta(seconds=time_window_seconds)).isoformat()
            
            must_clauses = [
                {"range": {"timestamp": {"gte": start_time, "lte": end_time}}}
            ]
            
            if correlation_id:
                must_clauses.append({"match": {"correlation_id": correlation_id}})
            else:
                must_clauses.append({"term": {"service": service}})
            
            query = {
                "query": {
                    "bool": {
                        "must": must_clauses,
                        "must_not": [{"term": {"_id": log_id}}]
                    }
                },
                "size": 100,
                "sort": [{"timestamp": "asc"}]
            }
            
            response, _ = es_client.search(index=ES_INDEX_PATTERN, body=query)
            
            related_logs = []
            for i, hit in enumerate(response["hits"]["hits"]):
                log = hit["_source"]
                related_logs.append(CorrelatedLog(
                    log_id=hit["_id"],
                    timestamp=log.get("timestamp"),
                    level=log.get("level", "INFO"),
                    service=log.get("service", "unknown"),
                    message=log.get("message", ""),
                    correlation_id=log.get("correlation_id"),
                    request_id=log.get("request_id"),
                    position_in_flow=i + 1
                ))
            
            return related_logs
            
        except Exception as e:
            logger.error(f"Error getting related logs: {e}")
            return []
    
    async def get_service_dependencies(self, time_window_hours: int = 24) -> DependencyGraph:
        """Analyze service dependencies - FIXED to use keyword fields"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_window_hours)
            
            # Use keyword fields for aggregations
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"exists": {"field": "correlation_id"}},
                            {"range": {"timestamp": {
                                "gte": start_time.isoformat(),
                                "lte": end_time.isoformat()
                            }}}
                        ]
                    }
                },
                "size": 0,
                "aggs": {
                    "by_correlation": {
                        "terms": {
                            "field": "correlation_id.keyword",
                            "size": 1000
                        },
                        "aggs": {
                            "services": {
                                "terms": {
                                    "field": "service.keyword",  # Use keyword!
                                    "size": 50
                                }
                            }
                        }
                    }
                }
            }
            
            response, _ = es_client.search(index=ES_INDEX_PATTERN, body=query)
            
            dependency_map: Dict[tuple, Dict[str, Any]] = {}
            services_set = set()
            
            for bucket in response["aggregations"]["by_correlation"]["buckets"]:
                services = [s["key"] for s in bucket["services"]["buckets"]]
                
                for i in range(len(services) - 1):
                    from_service = services[i]
                    to_service = services[i + 1]
                    
                    services_set.add(from_service)
                    services_set.add(to_service)
                    
                    key = (from_service, to_service)
                    
                    if key not in dependency_map:
                        dependency_map[key] = {
                            "count": 0,
                            "errors": 0,
                            "durations": []
                        }
                    
                    dependency_map[key]["count"] += 1
            
            dependencies = []
            for (from_service, to_service), data in dependency_map.items():
                avg_duration = (
                    sum(data["durations"]) / len(data["durations"])
                    if data["durations"] else 0
                )
                error_rate = (
                    data["errors"] / data["count"]
                    if data["count"] > 0 else 0
                )
                
                dependencies.append(ServiceDependency(
                    from_service=from_service,
                    to_service=to_service,
                    call_count=data["count"],
                    avg_duration_ms=avg_duration,
                    error_rate=error_rate
                ))
            
            return DependencyGraph(
                services=sorted(list(services_set)),
                dependencies=dependencies,
                total_services=len(services_set),
                total_dependencies=len(dependencies)
            )
            
        except Exception as e:
            logger.error(f"Error getting service dependencies: {e}")
            return DependencyGraph(
                services=[],
                dependencies=[],
                total_services=0,
                total_dependencies=0
            )
    
    async def find_correlation_ids_by_service(self, service: str, limit: int = 100) -> List[str]:
        """Find recent correlation IDs for a service - FIXED to use keyword field"""
        try:
            query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {"service.keyword": service}},  # Use keyword!
                            {"exists": {"field": "correlation_id"}}
                        ]
                    }
                },
                "size": 0,
                "aggs": {
                    "correlation_ids": {
                        "terms": {
                            "field": "correlation_id.keyword",
                            "size": limit
                        }
                    }
                }
            }
            
            response, _ = es_client.search(index=ES_INDEX_PATTERN, body=query)
            
            correlation_ids = [
                bucket["key"]
                for bucket in response["aggregations"]["correlation_ids"]["buckets"]
            ]
            
            return correlation_ids
            
        except Exception as e:
            logger.error(f"Error finding correlation IDs: {e}")
            return []


# Global correlation service instance
correlation_service = CorrelationService()
