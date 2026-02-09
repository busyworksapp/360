# Master Admin System - Setup Guide

## Overview
The Master Admin system provides IT and system administrators with full oversight and control of the application, including:
- System monitoring & debugging
- Database access & management
- User management
- Security & threat detection
- Change tracking & auditing

## Installation Steps

### 1. Import Models in app.py
Add to your imports:
```python
from models.master_admin import MasterAdmin, AuditLog, SecurityEvent, SystemLog, UserActivity
```

### 2. Register Blueprint in app.py
Add after other blueprints:
```python
from master_admin_routes import master_admin_bp
app.register_blueprint(master_admin_bp)
```

### 3. Create Database Tables
```bash
python init_master_admin.py
```

### 4. Promote User to Master Admin
```bash
python create_master_admin.py admin@360degreesupply.co.za
```

## Features

### 1. Dashboard (/master-admin/dashboard)
- System health metrics
- Unresolved security events
- Recent audit logs
- System errors

### 2. User Management (/master-admin/users)
- View all users
- User details with activity history
- Security events per user

### 3. Database Browser (/master-admin/database)
- View all database tables
- Browse table data (read-only, first 100 records)
- All access is logged

### 4. Audit Logs (/master-admin/audit-logs)
- Complete audit trail
- Track all critical actions
- Filter by severity

### 5. Security Events (/master-admin/security-events)
- Monitor suspicious activity
- Failed login attempts
- Unauthorized access attempts
- Resolve events

### 6. System Logs (/master-admin/system-logs)
- Application errors
- System events
- Debug information

## Security Features

### Access Control
- Requires `@require_master_admin` decorator
- Only users with `master_admin_profile` can access
- All unauthorized attempts are logged

### Audit Logging
Every action is logged with:
- User ID
- Action performed
- Table/record affected
- Old and new values
- IP address
- User agent
- Timestamp
- Severity level

### Security Event Tracking
Monitors:
- Failed login attempts
- Unauthorized access attempts
- Suspicious activity patterns
- Database access

## Usage Examples

### Log an Audit Event
```python
from utils.master_admin_utils import log_audit

log_audit(
    user_id=current_user.id,
    action='updated_product',
    table_name='products',
    record_id=product.id,
    old_value={'price': 100},
    new_value={'price': 150},
    severity='info'
)
```

### Log Security Event
```python
from utils.master_admin_utils import log_security_event

log_security_event(
    user_id=user.id,
    event_type='failed_login',
    description='Multiple failed login attempts',
    severity='high'
)
```

### Log User Activity
```python
from utils.master_admin_utils import log_user_activity

log_user_activity(
    user_id=current_user.id,
    action='viewed_dashboard',
    details='Accessed admin dashboard'
)
```

### Protect Route with Master Admin
```python
from utils.master_admin_utils import require_master_admin

@app.route('/sensitive-operation')
@login_required
@require_master_admin
def sensitive_operation():
    # Only master admins can access
    pass
```

## Database Schema

### master_admins
- id, user_id, is_active, mfa_enabled, mfa_secret, last_login, last_ip, created_at

### audit_logs
- id, user_id, action, table_name, record_id, old_value, new_value, ip_address, user_agent, timestamp, severity

### security_events
- id, user_id, event_type, description, ip_address, user_agent, severity, resolved, resolved_by, resolved_at, timestamp

### system_logs
- id, level, message, module, function, line_number, exception, timestamp

### user_activities
- id, user_id, action, details, ip_address, user_agent, timestamp

## Best Practices

1. **Limit Master Admin Access**: Only grant to IT/system administrators
2. **Enable MFA**: Implement multi-factor authentication for master admins
3. **Regular Audits**: Review audit logs regularly
4. **Monitor Security Events**: Address unresolved events promptly
5. **Database Access**: Use database browser sparingly, prefer application logic
6. **Log Everything**: All critical operations should be logged

## Maintenance

### View Recent Security Events
```bash
# In Python shell
from models.master_admin import SecurityEvent
events = SecurityEvent.query.filter_by(resolved=False).all()
```

### Clean Old Logs (Optional)
```python
# Delete logs older than 90 days
from datetime import datetime, timedelta
cutoff = datetime.utcnow() - timedelta(days=90)
AuditLog.query.filter(AuditLog.timestamp < cutoff).delete()
db.session.commit()
```

## Troubleshooting

### Can't Access Master Admin Dashboard
1. Verify user is promoted: `python create_master_admin.py <email>`
2. Check `master_admins` table: `SELECT * FROM master_admins;`
3. Ensure `is_active = 1`

### Audit Logs Not Appearing
1. Check database connection
2. Verify `audit_logs` table exists
3. Check for exceptions in system logs

### Security Events Not Logging
1. Verify `security_events` table exists
2. Check `log_security_event` function is called
3. Review system logs for errors

## Future Enhancements

- [ ] MFA implementation
- [ ] Real-time dashboard updates
- [ ] Email alerts for critical events
- [ ] Advanced database query builder
- [ ] User suspension/activation
- [ ] Bulk user operations
- [ ] Export audit logs to CSV
- [ ] Security event analytics
- [ ] Performance metrics
- [ ] API access logs
