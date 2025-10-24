"""
Notification Handler - Sends alert notifications via various channels
"""
from loguru import logger
from typing import Dict, Any
import json


class Notifier:
    """Handles sending notifications for triggered alerts"""
    
    def send_notification(self, alert: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """
        Send notification for triggered alert
        
        Args:
            alert: Alert data
            rule: Alert rule configuration
            
        Returns:
            True if sent successfully, False otherwise
        """
        channel = rule.get("notification_channel", "console")
        config = rule.get("notification_config", {})
        
        try:
            if channel == "console":
                return self._send_console(alert, rule)
            elif channel == "webhook":
                return self._send_webhook(alert, rule, config)
            elif channel == "email":
                return self._send_email(alert, rule, config)
            elif channel == "slack":
                return self._send_slack(alert, rule, config)
            else:
                logger.warning(f"Unknown notification channel: {channel}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send notification via {channel}: {e}")
            return False
    
    def _send_console(self, alert: Dict[str, Any], rule: Dict[str, Any]) -> bool:
        """Send notification to console (for testing)"""
        logger.info("=" * 60)
        logger.info("🚨 ALERT TRIGGERED")
        logger.info(f"Rule: {alert['rule_name']}")
        logger.info(f"Condition: {alert['value']} {alert['condition']} {alert['threshold']}")
        logger.info(f"Log Count: {alert['log_count']}")
        logger.info(f"Sample Logs:")
        for i, log in enumerate(alert['sample_logs'][:3], 1):
            logger.info(f"  {i}. [{log.get('level')}] {log.get('message', '')[:80]}")
        logger.info("=" * 60)
        return True
    
    def _send_webhook(self, alert: Dict[str, Any], rule: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """Send notification via webhook"""
        import requests
        
        url = config.get("url")
        if not url:
            logger.error("Webhook URL not configured")
            return False
        
        payload = {
            "alert_id": alert["rule_id"],
            "rule_name": alert["rule_name"],
            "triggered_at": datetime.now().isoformat(),
            "condition": f"{alert['value']} {alert['condition']} {alert['threshold']}",
            "log_count": alert["log_count"],
            "sample_logs": alert["sample_logs"][:3]
        }
        
        headers = config.get("headers", {})
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            logger.info(f"Webhook notification sent to {url}")
            return True
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
            return False
    
    def _send_email(self, alert: Dict[str, Any], rule: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """Send notification via email (placeholder)"""
        logger.info(f"Email notification (not implemented): {alert['rule_name']}")
        # TODO: Implement email sending (SMTP, SendGrid, etc.)
        return True
    
    def _send_slack(self, alert: Dict[str, Any], rule: Dict[str, Any], config: Dict[str, Any]) -> bool:
        """Send notification via Slack (placeholder)"""
        logger.info(f"Slack notification (not implemented): {alert['rule_name']}")
        # TODO: Implement Slack webhook
        return True
