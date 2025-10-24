"""
Log search routes with rate limiting
"""
from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional
from loguru import logger

from api.models.log import LogSearchResponse, LogEntry
from api.utils.elasticsearch_client import es_client
from api.utils.rate_limiter import limiter
from api.config import ES_INDEX_PATTERN

router = APIRouter(prefix="/api/v1/logs", tags=["Logs"])


@router.get("/search", response_model=LogSearchResponse)
@limiter.limit("50/minute")  # More restrictive for search
async def search_logs(
    request: Request,
    query: Optional[str] = Query(None, description="Search query"),
    service: Optional[str] = Query(None, description="Filter by service name"),
    level: Optional[str] = Query(None, description="Filter by log level"),
    limit: int = Query(100, ge=1, le=1000, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Search logs with filters (rate limited: 50/minute)
    """
    try:
        must_clauses = []
        
        if query:
            must_clauses.append({
                "query_string": {
                    "query": query,
                    "default_field": "message"
                }
            })
        
        if service:
            must_clauses.append({"term": {"service": service}})
        
        if level:
            must_clauses.append({"term": {"level": level}})
        
        es_query = {
            "query": {
                "bool": {"must": must_clauses}
            } if must_clauses else {"match_all": {}},
            "size": limit,
            "from": offset,
            "sort": [{"timestamp": "desc"}]
        }
        
        es_response, query_time = es_client.search(
            index=ES_INDEX_PATTERN,
            body=es_query
        )
        
        logs = [
            LogEntry(**hit["_source"], id=hit["_id"])
            for hit in es_response["hits"]["hits"]
        ]
        
        return LogSearchResponse(
            total=es_response["hits"]["total"]["value"],
            logs=logs,
            query_time_ms=query_time
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/recent", response_model=LogSearchResponse)
@limiter.limit("100/minute")
async def get_recent_logs(
    request: Request,
    limit: int = Query(100, ge=1, le=1000)
):
    """
    Get recent logs (rate limited: 100/minute)
    """
    try:
        es_query = {
            "query": {"match_all": {}},
            "size": limit,
            "sort": [{"timestamp": "desc"}]
        }
        
        es_response, query_time = es_client.search(
            index=ES_INDEX_PATTERN,
            body=es_query
        )
        
        logs = [
            LogEntry(**hit["_source"], id=hit["_id"])
            for hit in es_response["hits"]["hits"]
        ]
        
        return LogSearchResponse(
            total=es_response["hits"]["total"]["value"],
            logs=logs,
            query_time_ms=query_time
        )
        
    except Exception as e:
        logger.error(f"Recent logs error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent logs: {str(e)}")


@router.get("/{log_id}", response_model=LogEntry)
@limiter.limit("200/minute")
async def get_log_by_id(request: Request, log_id: str):
    """
    Get a specific log by ID (rate limited: 200/minute)
    """
    try:
        es_response = es_client.get_by_id(ES_INDEX_PATTERN, log_id)
        
        if not es_response:
            raise HTTPException(status_code=404, detail="Log not found")
        
        return LogEntry(**es_response["_source"], id=es_response["_id"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get log error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get log: {str(e)}")
