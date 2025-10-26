"""
WebSocket connection manager
"""
from fastapi import WebSocket
from typing import Dict, List, Set
from loguru import logger
import asyncio
import json


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        # Active connections by type
        self.active_connections: Dict[str, List[WebSocket]] = {
            "logs": [],
            "metrics": [],
            "alerts": []
        }
        
        # Connection filters (for filtered streams)
        self.connection_filters: Dict[WebSocket, dict] = {}
        
    async def connect(self, websocket: WebSocket, stream_type: str):
        """
        Accept new WebSocket connection
        
        Args:
            websocket: WebSocket connection
            stream_type: Type of stream (logs, metrics, alerts)
        """
        await websocket.accept()
        
        if stream_type not in self.active_connections:
            self.active_connections[stream_type] = []
        
        self.active_connections[stream_type].append(websocket)
        logger.info(f"WebSocket connected: {stream_type} (total: {len(self.active_connections[stream_type])})")
    
    def disconnect(self, websocket: WebSocket, stream_type: str):
        """
        Remove WebSocket connection
        
        Args:
            websocket: WebSocket connection
            stream_type: Type of stream
        """
        if stream_type in self.active_connections:
            if websocket in self.active_connections[stream_type]:
                self.active_connections[stream_type].remove(websocket)
                logger.info(f"WebSocket disconnected: {stream_type} (total: {len(self.active_connections[stream_type])})")
        
        # Remove filters
        if websocket in self.connection_filters:
            del self.connection_filters[websocket]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def broadcast(self, message: dict, stream_type: str):
        """
        Broadcast message to all connections of a stream type
        
        Args:
            message: Message to broadcast (will be JSON serialized)
            stream_type: Type of stream
        """
        if stream_type not in self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections[stream_type]:
            try:
                # Check if connection has filters
                if connection in self.connection_filters:
                    filters = self.connection_filters[connection]
                    if not self._matches_filters(message, filters):
                        continue
                
                await connection.send_text(message_json)
            except Exception as e:
                logger.error(f"Error broadcasting to {stream_type}: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, stream_type)
    
    def set_filters(self, websocket: WebSocket, filters: dict):
        """
        Set filters for a connection
        
        Args:
            websocket: WebSocket connection
            filters: Filter dictionary (e.g., {"service": "payment-service", "level": "ERROR"})
        """
        self.connection_filters[websocket] = filters
        logger.info(f"Filters set for connection: {filters}")
    
    def _matches_filters(self, message: dict, filters: dict) -> bool:
        """
        Check if message matches connection filters
        
        Args:
            message: Message to check
            filters: Filter criteria
            
        Returns:
            True if message matches filters
        """
        for key, value in filters.items():
            if key not in message:
                return False
            if message[key] != value:
                return False
        return True
    
    def get_stats(self) -> dict:
        """Get connection statistics"""
        return {
            "total_connections": sum(len(conns) for conns in self.active_connections.values()),
            "by_type": {
                stream_type: len(connections)
                for stream_type, connections in self.active_connections.items()
            }
        }


# Global connection manager
manager = ConnectionManager()
