# Database Quick Reference

## Connection Details

| Context | Host | Port | User | Password | Database |
|---------|------|------|------|----------|----------|
| External (Python/API) | 127.0.0.1 | 5432 | logflow | logflow123 | logflow |
| Internal (Docker) | postgres | 5432 | logflow | logflow123 | logflow |

## Schema

### users
```sql
id, username, email, hashed_password, full_name, 
is_active, is_admin, created_at, updated_at
```

### alert_rules
```sql
id, name, description, query, condition, threshold, time_window,
services, levels, notification_channel, notification_config,
is_active, last_triggered, trigger_count, owner_id,
created_at, updated_at
```

### triggered_alerts
```sql
id, rule_id, triggered_at, value, threshold, log_count, sample_logs,
status, acknowledged_at, acknowledged_by, resolved_at, notes
```

### system_config
```sql
id, key, value, description, updated_at
```

## Common Operations

### View Data
```sql
-- List all users
SELECT username, email, is_admin FROM users;

-- List active alert rules
SELECT name, condition, threshold, is_active FROM alert_rules WHERE is_active = true;

-- Recent triggered alerts
SELECT r.name, a.triggered_at, a.status 
FROM triggered_alerts a 
JOIN alert_rules r ON a.rule_id = r.id 
ORDER BY a.triggered_at DESC 
LIMIT 10;

-- System configuration
SELECT key, value FROM system_config;
```

### Modify Data
```sql
-- Update admin password (use bcrypt hash)
UPDATE users SET hashed_password = '$2b$12$...' WHERE username = 'admin';

-- Disable an alert rule
UPDATE alert_rules SET is_active = false WHERE id = 1;

-- Acknowledge an alert
UPDATE triggered_alerts 
SET status = 'acknowledged', acknowledged_at = NOW(), acknowledged_by = 1 
WHERE id = 5;
```

## Management Scripts
```bash
./scripts/manage-db.sh init    # Initialize database
./scripts/manage-db.sh shell   # Open psql shell
./scripts/manage-db.sh backup  # Create backup
./scripts/manage-db.sh reset   # Reset (delete all data)
```

## Password Hashing

To generate a bcrypt password hash in Python:
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("your_password")
print(hashed)
```
