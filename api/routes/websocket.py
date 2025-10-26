"""
WebSocket routes for real-time streaming
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
from loguru import logger
import asyncio
import json
from datetime import datetime

from api.utils.websocket_manager import manager
from api.utils.elasticsearch_client import es_client
from api.config import ES_INDEX_PATTERN

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/logs")
async def websocket_logs(
    websocket: WebSocket,
    service: Optional[str] = Query(None),
    level: Optional[str] = Query(None)
):
    """
    WebSocket endpoint for real-time log streaming
    
    Query parameters:
    - service: Filter by service name
    - level: Filter by log level (INFO, WARN, ERROR, etc.)
    
    Example: ws://localhost:8000/ws/logs?service=payment-service&level=ERROR
    """
    await manager.connect(websocket, "logs")
    
    # Set filters if provided
    filters = {}
    if service:
        filters["service"] = service
    if level:
        filters["level"] = level
    
    if filters:
        manager.set_filters(websocket, filters)
        await websocket.send_json({
            "type": "connection",
            "message": f"Connected with filters: {filters}",
            "timestamp": datetime.now().isoformat()
        })
    else:
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to live log stream",
            "timestamp": datetime.now().isoformat()
        })
    
    try:
        # Start streaming recent logs first
        await stream_recent_logs(websocket, service, level)
        
        # Keep connection alive and wait for client messages
        while True:
            data = await websocket.receive_text()
            
            # Handle client commands
            message = json.loads(data)
            if message.get("command") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            elif message.get("command") == "update_filters":
                new_filters = message.get("filters", {})
                manager.set_filters(websocket, new_filters)
                await websocket.send_json({
                    "type": "filters_updated",
                    "filters": new_filters,
                    "timestamp": datetime.now().isoformat()
                })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "logs")
        logger.info("Client disconnected from log stream")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, "logs")


@router.websocket("/ws/metrics")
async def websocket_metrics(websocket: WebSocket):
    """
    WebSocket endpoint for real-time metrics updates
    
    Sends metrics updates every 5 seconds
    """
    await manager.connect(websocket, "metrics")
    
    await websocket.send_json({
        "type": "connection",
        "message": "Connected to live metrics stream",
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        while True:
            # Get current metrics
            try:
                metrics = await get_current_metrics()
                await websocket.send_json({
                    "type": "metrics",
                    "data": metrics,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"Error getting metrics: {e}")
            
            # Wait 5 seconds before next update
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "metrics")
        logger.info("Client disconnected from metrics stream")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, "metrics")


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket endpoint for real-time alert notifications
    
    Receives alerts as they are triggered
    """
    await manager.connect(websocket, "alerts")
    
    await websocket.send_json({
        "type": "connection",
        "message": "Connected to live alert stream",
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            
            # Handle ping
            message = json.loads(data)
            if message.get("command") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, "alerts")
        logger.info("Client disconnected from alert stream")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, "alerts")


@router.get("/ws/stats")
async def websocket_stats():
    """
    Get WebSocket connection statistics
    """
    return manager.get_stats()


async def stream_recent_logs(
    websocket: WebSocket,
    service: Optional[str] = None,
    level: Optional[str] = None,
    limit: int = 10
):
    """
    Stream recent logs to new connection
    
    Args:
        websocket: WebSocket connection
        service: Optional service filter
        level: Optional level filter
        limit: Number of recent logs to send
    """
    try:
        # Build query
        must_clauses = []
        if service:
            must_clauses.append({"term": {"service": service}})
        if level:
            must_clauses.append({"term": {"level": level}})
        
        query = {
            "query": {
                "bool": {"must": must_clauses}
            } if must_clauses else {"match_all": {}},
            "size": limit,
            "sort": [{"timestamp": "desc"}]
        }
        
        response, _ = es_client.search(index=ES_INDEX_PATTERN, body=query)
        
        # Send recent logs
        for hit in reversed(response["hits"]["hits"]):
            log = hit["_source"]
            log["id"] = hit["_id"]
            
            await websocket.send_json({
                "type": "log",
                "data": log
            })
            await asyncio.sleep(0.1)  # Small delay between messages
            
    except Exception as e:
        logger.error(f"Error streaming recent logs: {e}")


async def get_current_metrics() -> dict:
    """Get current system metrics"""
    try:
        query = {
            "query": {"match_all": {}},
            "size": 0,
            "aggs": {
                "by_level": {
                    "terms": {"field": "level", "size": 10}
                },
                "by_service": {
                    "terms": {"field": "service", "size": 10}
                }
            }
        }
        
        response, _ = es_client.search(index=ES_INDEX_PATTERN, body=query)
        
        total = response["hits"]["total"]["value"]
        by_level = {
            bucket["key"]: bucket["doc_count"]
            for bucket in response["aggregations"]["by_level"]["buckets"]
        }
        by_service = {
            bucket["key"]: bucket["doc_count"]
            for bucket in response["aggregations"]["by_service"]["buckets"]
        }
        
        return {
            "total_logs": total,
            "by_level": by_level,
            "by_service": by_service
        }
        
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return {}
