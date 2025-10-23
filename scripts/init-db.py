"""
Initialize database with tables and seed data
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.utils.database import init_db, get_db, drop_db
from api.models.database import User, SystemConfig
from passlib.context import CryptContext
from loguru import logger

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_admin_user():
    """Create default admin user"""
    with get_db() as db:
        # Check if admin exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            logger.info("Admin user already exists")
            return
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@logflow.local",
            hashed_password=pwd_context.hash("admin123"),  # Change in production!
            full_name="System Administrator",
            is_active=True,
            is_admin=True
        )
        db.add(admin)
        db.commit()
        logger.info("✅ Created admin user (username: admin, password: admin123)")


def create_default_config():
    """Create default system configuration"""
    with get_db() as db:
        configs = [
            SystemConfig(
                key="alert_check_interval",
                value={"seconds": 60},
                description="How often to check alert rules (in seconds)"
            ),
            SystemConfig(
                key="max_alerts_per_rule",
                value={"count": 100},
                description="Maximum number of triggered alerts to keep per rule"
            ),
            SystemConfig(
                key="log_retention_days",
                value={"days": 30},
                description="How long to keep logs in Elasticsearch"
            )
        ]
        
        for config in configs:
            existing = db.query(SystemConfig).filter(SystemConfig.key == config.key).first()
            if not existing:
                db.add(config)
        
        db.commit()
        logger.info("✅ Created default system configuration")


def main():
    """Main initialization"""
    logger.info("🚀 Initializing LogFlow database...")
    
    # Create tables
    init_db()
    
    # Seed data
    create_admin_user()
    create_default_config()
    
    logger.info("✅ Database initialization complete!")
    logger.info("")
    logger.info("Default admin credentials:")
    logger.info("  Username: admin")
    logger.info("  Password: admin123")
    logger.info("  ⚠️  Change this password in production!")


if __name__ == "__main__":
    main()
