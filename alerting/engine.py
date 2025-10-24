"""
Alert Engine - Main alerting service that runs continuously
"""
from loguru import logger
from datetime import datetime
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from alerting.alert_evaluator import AlertEvaluator
from alerting.notifier import Notifier
from api.utils.database import get_db
from api.models.database import AlertRule, TriggeredAlert, User


class AlertEngine:
    """Main alerting engine that evaluates rules periodically"""
    
    def __init__(self, check_interval: int = 60):
        """
        Initialize alert engine
        
        Args:
            check_interval: Seconds between rule checks
        """
        self.check_interval = check_interval
        self.evaluator = AlertEvaluator()
        self.notifier = Notifier()
        self.running = False
    
    def start(self):
        """Start the alert engine"""
        self.running = True
        logger.info(f"🚨 Alert Engine started (checking every {self.check_interval}s)")
        
        try:
            while self.running:
                self._check_all_rules()
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("Alert Engine stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"Alert Engine error: {e}")
            self.running = False
    
    def stop(self):
        """Stop the alert engine"""
        self.running = False
        logger.info("Alert Engine stopping...")
    
    def _check_all_rules(self):
        """Check all active alert rules"""
        try:
            with get_db() as db:
                # Get all active alert rules
                rules = db.query(AlertRule).filter(AlertRule.is_active == True).all()
                
                if not rules:
                    logger.debug("No active alert rules to check")
                    return
                
                logger.info(f"Checking {len(rules)} active alert rules...")
                
                for rule in rules:
                    self._check_rule(db, rule)
                    
        except Exception as e:
            logger.error(f"Error checking rules: {e}")
    
    def _check_rule(self, db, rule: AlertRule):
        """Check a single alert rule"""
        try:
            # Convert SQLAlchemy model to dict for evaluator
            rule_dict = {
                "id": rule.id,
                "name": rule.name,
                "query": rule.query,
                "condition": rule.condition,
                "threshold": rule.threshold,
                "time_window": rule.time_window,
                "services": rule.services,
                "levels": rule.levels
            }
            
            # Evaluate the rule
            result = self.evaluator.evaluate_rule(rule_dict)
            
            if result:
                # Rule triggered - create triggered alert
                triggered_alert = TriggeredAlert(
                    rule_id=rule.id,
                    triggered_at=datetime.utcnow(),
                    value=result["value"],
                    threshold=result["threshold"],
                    log_count=result["log_count"],
                    sample_logs=result["sample_logs"],
                    status="triggered"
                )
                
                db.add(triggered_alert)
                
                # Update rule stats
                rule.last_triggered = datetime.utcnow()
                rule.trigger_count += 1
                
                db.commit()
                
                # Send notification
                notification_sent = self.notifier.send_notification(result, rule_dict)
                
                if notification_sent:
                    logger.info(f"✅ Alert '{rule.name}' triggered and notification sent")
                else:
                    logger.warning(f"⚠️ Alert '{rule.name}' triggered but notification failed")
            
        except Exception as e:
            logger.error(f"Error checking rule '{rule.name}': {e}")
            db.rollback()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='LogFlow Alert Engine')
    parser.add_argument('--interval', type=int, default=60,
                        help='Check interval in seconds (default: 60)')
    
    args = parser.parse_args()
    
    engine = AlertEngine(check_interval=args.interval)
    engine.start()
