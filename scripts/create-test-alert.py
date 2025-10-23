"""
Create a test alert rule
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.utils.database import get_db
from api.models.database import AlertRule, User
from loguru import logger


def create_test_alert():
    """Create a test alert rule"""
    with get_db() as db:
        # Get admin user
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            logger.error("Admin user not found")
            return
        
        # Check if test alert already exists
        existing = db.query(AlertRule).filter(AlertRule.name == "Test Error Alert").first()
        if existing:
            logger.info("Test alert already exists")
            return
        
        # Create test alert rule
        alert = AlertRule(
            name="Test Error Alert",
            description="Triggers when ERROR log count exceeds 10",
            query="",  # Empty query means match all
            condition="greater_than",
            threshold=10,
            time_window=5,  # 5 minutes (not used in current implementation)
            services=None,  # All services
            levels=["ERROR"],  # Only ERROR logs
            notification_channel="console",
            notification_config={},
            is_active=True,
            owner_id=admin.id
        )
        
        db.add(alert)
        db.commit()
        
        logger.info(f"✅ Created test alert rule (ID: {alert.id})")
        logger.info(f"   Name: {alert.name}")
        logger.info(f"   Condition: ERROR logs > 10")
        logger.info(f"   Channel: console")


if __name__ == "__main__":
    create_test_alert()
