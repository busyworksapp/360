from flask import request
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from models import db, AuditLog
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'models'))
from master_admin import SecurityEvent, UserActivity, SystemLog
import json

def log_audit(user_id, action, table_name=None, record_id=None, old_value=None, new_value=None, severity='info'):
    try:
        audit = AuditLog(
            user_id=user_id,
            event_type=action,
            details=json.dumps({'table': table_name, 'record_id': record_id, 'old': old_value, 'new': new_value}),
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None
        )
        db.session.add(audit)
        db.session.commit()
    except Exception as e:
        print(f"Audit log error: {e}")

def log_security_event(user_id, event_type, description, severity='low'):
    try:
        event = SecurityEvent(
            user_id=user_id,
            event_type=event_type,
            description=description,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None,
            severity=severity
        )
        db.session.add(event)
        db.session.commit()
    except Exception as e:
        print(f"Security log error: {e}")

def log_user_activity(user_id, action, details=None):
    try:
        activity = UserActivity(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=request.remote_addr if request else None,
            user_agent=request.headers.get('User-Agent') if request else None
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        print(f"Activity log error: {e}")

def is_master_admin(user):
    if not user or not user.is_authenticated:
        return False
    return hasattr(user, 'master_admin_profile') and user.master_admin_profile and user.master_admin_profile.is_active

def require_master_admin(f):
    from functools import wraps
    from flask import abort
    from flask_login import current_user
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_master_admin(current_user):
            log_security_event(
                current_user.id if current_user.is_authenticated else None,
                'unauthorized_access_attempt',
                f'Attempted to access: {f.__name__}',
                severity='high'
            )
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
