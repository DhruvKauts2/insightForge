"""
Search routes for log queries
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from loguru import logger

from api.models.log import SearchRequest, SearchResponse, LogDocument, LogSource
from api.utils.elasticsearch_client import es_client
from api.config import ES_INDEX_PATTERN

router = APIRouter(prefix="/api/v1", tags=["Search"])


def build_es_query(request: SearchRequest) -> dict:
    """Build Elasticsearch query from search request"""
    must_clauses = []
    
    if request.query:
        must_clauses.append({
            "match": {
                "message": {
                    "query": request.query,
                    "operator": "and"
                }
            }
        })
    
    if request.services:
        must_clauses.append({
            "terms": {"service": request.services}
        })
    
    if request.levels:
        must_clauses.append({
            "terms": {"level": request.levels}
        })
    
    if request.start_time or request.end_time:
        range_query = {"range": {"timestamp": {}}}
        if request.start_time:
            range_query["range"]["timestamp"]["gte"] = request.start_time
        if request.end_time:
            range_query["range"]["timestamp"]["lte"] = request.end_time
        must_clauses.append(range_query)
    
    if must_clauses:
        query = {"bool": {"must": must_clauses}}
    else:
        query = {"match_all": {}}
    
    es_query = {
        "query": query,
        "from": request.offset,
        "size": request.limit,
        "sort": [{"timestamp": {"order": "desc"}}],
        "aggs": {
            "by_level": {
                "terms": {"field": "level", "size": 10}
            },
            "by_service": {
                "terms": {"field": "service", "size": 20}
            }
        }
    }
    
    return es_query


def parse_es_response(es_response, query_time_ms) -> SearchResponse:
    """Parse Elasticsearch response into SearchResponse model"""
    logs = []
    for hit in es_response["hits"]["hits"]:
        source = hit["_source"]
        
        log_doc = LogDocument(
            timestamp=source.get("timestamp"),
            level=source.get("level"),
            service=source.get("service"),
            message=source.get("message"),
            source=LogSource(
                hostname=source.get("source", {}).get("hostname", "unknown"),
                file=source.get("source", {}).get("file", "unknown")
            ),
            ingested_at=source.get("ingested_at"),
            shipper_timestamp=source.get("shipper_timestamp"),
            extra_fields=source.get("extra_fields"),
            raw_log=source.get("raw_log")
        )
        logs.append(log_doc)
    
    aggregations = {}
    if "aggregations" in es_response:
        aggs = es_response["aggregations"]
        
        if "by_level" in aggs:
            aggregations["by_level"] = {
                bucket["key"]: bucket["doc_count"]
                for bucket in aggs["by_level"]["buckets"]
            }
        
        if "by_service" in aggs:
            aggregations["by_service"] = {
                bucket["key"]: bucket["doc_count"]
                for bucket in aggs["by_service"]["buckets"]
            }
    
    return SearchResponse(
        total=es_response["hits"]["total"]["value"],
        logs=logs,
        aggregations=aggregations,
        query_time_ms=query_time_ms
    )


@router.post("/logs/search", response_model=SearchResponse)
async def search_logs(request: SearchRequest):
    """Search logs with filters"""
    try:
        es_query = build_es_query(request)
        logger.debug(f"ES Query: {es_query}")
        
        es_response, query_time = es_client.search(
            index=ES_INDEX_PATTERN,
            body=es_query
        )
        
        response = parse_es_response(es_response, query_time)
        logger.info(f"Search returned {response.total} results in {query_time:.2f}ms")
        
        return response
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# IMPORTANT: /logs/recent must come BEFORE /logs/{log_id}
# Otherwise FastAPI will match "recent" as a log_id
@router.get("/logs/recent", response_model=SearchResponse)
async def get_recent_logs(
    limit: int = Query(50, ge=1, le=500),
    level: Optional[str] = Query(None)
):
    """Get recent logs"""
    try:
        if level:
            query = {"term": {"level": level.upper()}}
        else:
            query = {"match_all": {}}
        
        es_query = {
            "query": query,
            "size": limit,
            "sort": [{"timestamp": {"order": "desc"}}]
        }
        
        logger.info(f"Recent logs query: {es_query}")
        
        es_response, query_time = es_client.search(
            index=ES_INDEX_PATTERN,
            body=es_query
        )
        
        logger.info(f"ES response hits: {es_response['hits']['total']['value']}")
        
        if es_response["hits"]["total"]["value"] == 0:
            return SearchResponse(
                total=0,
                logs=[],
                query_time_ms=query_time
            )
        
        logs = []
        for hit in es_response["hits"]["hits"]:
            source = hit["_source"]
            logs.append(LogDocument(
                timestamp=source.get("timestamp"),
                level=source.get("level"),
                service=source.get("service"),
                message=source.get("message"),
                source=LogSource(
                    hostname=source.get("source", {}).get("hostname", "unknown"),
                    file=source.get("source", {}).get("file", "unknown")
                ),
                ingested_at=source.get("ingested_at"),
                shipper_timestamp=source.get("shipper_timestamp"),
                extra_fields=source.get("extra_fields"),
                raw_log=source.get("raw_log")
            ))
        
        return SearchResponse(
            total=es_response["hits"]["total"]["value"],
            logs=logs,
            query_time_ms=query_time
        )
        
    except Exception as e:
        logger.error(f"Recent logs error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to get recent logs: {str(e)}")


@router.get("/logs/{log_id}", response_model=LogDocument)
async def get_log_by_id(log_id: str):
    """Get a specific log by ID"""
    try:
        es_query = {
            "query": {
                "ids": {"values": [log_id]}
            }
        }
        
        es_response, _ = es_client.search(
            index=ES_INDEX_PATTERN,
            body=es_query
        )
        
        if es_response["hits"]["total"]["value"] == 0:
            raise HTTPException(status_code=404, detail="Log not found")
        
        source = es_response["hits"]["hits"][0]["_source"]
        
        return LogDocument(
            timestamp=source.get("timestamp"),
            level=source.get("level"),
            service=source.get("service"),
            message=source.get("message"),
            source=LogSource(
                hostname=source.get("source", {}).get("hostname", "unknown"),
                file=source.get("source", {}).get("file", "unknown")
            ),
            ingested_at=source.get("ingested_at"),
            shipper_timestamp=source.get("shipper_timestamp"),
            extra_fields=source.get("extra_fields"),
            raw_log=source.get("raw_log")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get log error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get log: {str(e)}")
