"""
Alert notification handler with WebSocket support
"""
from loguru import logger
import requests
from typing import Dict, Any
import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class AlertNotifier:
    """Handle alert notifications to various channels"""
    
    def __init__(self):
        self.websocket_manager = None
    
    def set_websocket_manager(self, manager):
        """Set WebSocket manager for broadcasting"""
        self.websocket_manager = manager
    
    async def notify(self, alert_data: Dict[str, Any], channel: str, config: Dict[str, Any]):
        """
        Send alert notification
        
        Args:
            alert_data: Alert information
            channel: Notification channel (console, webhook, email, websocket)
            config: Channel-specific configuration
        """
        logger.info(f"Sending notification via {channel}")
        
        try:
            if channel == "console":
                await self._notify_console(alert_data)
            elif channel == "webhook":
                await self._notify_webhook(alert_data, config)
            elif channel == "email":
                await self._notify_email(alert_data, config)
            elif channel == "websocket":
                await self._notify_websocket(alert_data)
            else:
                logger.warning(f"Unknown notification channel: {channel}")
                
        except Exception as e:
            logger.error(f"Notification failed for channel {channel}: {e}")
    
    async def _notify_console(self, alert_data: Dict[str, Any]):
        """Print alert to console"""
        logger.warning(f"🚨 ALERT TRIGGERED: {alert_data['rule_name']}")
        logger.warning(f"   Condition: {alert_data['condition']}")
        logger.warning(f"   Current Value: {alert_data['current_value']}")
        logger.warning(f"   Threshold: {alert_data['threshold']}")
        logger.warning(f"   Time: {alert_data['triggered_at']}")
    
    async def _notify_webhook(self, alert_data: Dict[str, Any], config: Dict[str, Any]):
        """Send alert via webhook"""
        url = config.get("url")
        if not url:
            logger.error("Webhook URL not configured")
            return
        
        try:
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: requests.post(
                    url,
                    json=alert_data,
                    timeout=5
                )
            )
            logger.info(f"Webhook notification sent to {url}")
            
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
    
    async def _notify_email(self, alert_data: Dict[str, Any], config: Dict[str, Any]):
        """Send alert via email (placeholder)"""
        # TODO: Implement email notification
        logger.info("Email notification (not implemented)")
        logger.info(f"Would send to: {config.get('recipients', [])}")
    
    async def _notify_websocket(self, alert_data: Dict[str, Any]):
        """Broadcast alert via WebSocket"""
        if self.websocket_manager:
            await self.websocket_manager.broadcast(
                {
                    "type": "alert",
                    "data": alert_data
                },
                "alerts"
            )
            logger.info("Alert broadcast via WebSocket")
        else:
            logger.warning("WebSocket manager not available")


# Global notifier instance
notifier = AlertNotifier()
