"""
Advanced Security Middleware with IP Blocking and Deep Monitoring
"""

from flask import request, jsonify, render_template, session
from functools import wraps
from datetime import datetime
import json
import time
import traceback
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'models'))
from security_models import BlockedIP, SystemControl, UserPermission, DetailedLog
from models import db

def get_client_ip():
    """Get real client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr

def is_ip_blocked(ip_address):
    """Check if IP is blocked"""
    blocked = BlockedIP.query.filter_by(ip_address=ip_address).first()
    if not blocked:
        return False, None
    
    # Check if temporary block has expired
    if not blocked.is_permanent and blocked.expires_at:
        if datetime.utcnow() > blocked.expires_at:
            db.session.delete(blocked)
            db.session.commit()
            return False, None
    
    # Update last attempt
    blocked.last_attempt = datetime.utcnow()
    blocked.block_count += 1
    db.session.commit()
    
    return True, blocked.reason

def is_system_active():
    """Check if system is active"""
    control = SystemControl.query.first()
    if not control:
        return True, None
    
    if not control.is_system_active:
        return False, control.shutdown_reason or "System is currently unavailable"
    
    if control.maintenance_mode:
        return False, control.maintenance_message or "System is under maintenance"
    
    return True, None

def check_user_permissions(user):
    """Check if user has required permissions"""
    if not user or not user.is_authenticated:
        return True, None
    
    # Check for User model
    from models import User, Customer
    if isinstance(user, User):
        perms = UserPermission.query.filter_by(user_id=user.id).first()
    elif isinstance(user, Customer):
        perms = UserPermission.query.filter_by(customer_id=user.id).first()
    else:
        return True, None
    
    if not perms:
        return True, None
    
    if perms.is_blocked:
        return False, perms.block_reason or "Your account has been blocked"
    
    # Check path-specific permissions
    path = request.path.lower()
    
    if '/products' in path and not perms.can_access_products:
        return False, "You don't have permission to access products"
    if '/services' in path and not perms.can_access_services:
        return False, "You don't have permission to access services"
    if '/cart' in path and not perms.can_access_cart:
        return False, "You don't have permission to access cart"
    if '/orders' in path and not perms.can_access_orders:
        return False, "You don't have permission to access orders"
    if '/invoices' in path and not perms.can_access_invoices:
        return False, "You don't have permission to access invoices"
    if '/transactions' in path and not perms.can_access_transactions:
        return False, "You don't have permission to access transactions"
    if '/profile' in path and not perms.can_access_profile:
        return False, "You don't have permission to access profile"
    
    return True, None

def log_detailed_request(app, start_time, response=None, error=None):
    """Log detailed request information"""
    try:
        from flask_login import current_user
        
        # Calculate response time
        response_time = (time.time() - start_time) * 1000  # milliseconds
        
        # Get user info
        user_id = None
        customer_id = None
        username = None
        
        if current_user and current_user.is_authenticated:
            from models import User, Customer
            if isinstance(current_user, User):
                user_id = current_user.id
                username = current_user.email
            elif isinstance(current_user, Customer):
                customer_id = current_user.id
                username = current_user.email
        
        # Parse user agent
        user_agent = request.headers.get('User-Agent', '')
        device_type = 'mobile' if 'Mobile' in user_agent else 'desktop'
        browser = 'unknown'
        if 'Chrome' in user_agent:
            browser = 'Chrome'
        elif 'Firefox' in user_agent:
            browser = 'Firefox'
        elif 'Safari' in user_agent:
            browser = 'Safari'
        elif 'Edge' in user_agent:
            browser = 'Edge'
        
        # Determine severity
        severity = 'info'
        is_suspicious = False
        
        if error:
            severity = 'error'
            is_suspicious = True
        elif response and response.status_code >= 500:
            severity = 'critical'
        elif response and response.status_code >= 400:
            severity = 'warning'
            if response.status_code == 403 or response.status_code == 401:
                is_suspicious = True
        
        # Get request data
        request_data = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if request.is_json:
                    request_data = json.dumps(request.get_json())
                elif request.form:
                    # Don't log passwords
                    form_data = {k: v for k, v in request.form.items() if 'password' not in k.lower()}
                    request_data = json.dumps(form_data)
            except:
                pass
        
        # Create log entry
        log = DetailedLog(
            log_type='request',
            severity=severity,
            user_id=user_id,
            customer_id=customer_id,
            username=username,
            ip_address=get_client_ip(),
            user_agent=user_agent,
            request_method=request.method,
            request_path=request.path,
            request_data=request_data,
            response_status=response.status_code if response else None,
            response_time=response_time,
            error_message=str(error) if error else None,
            error_traceback=traceback.format_exc() if error else None,
            session_id=session.get('_id'),
            referrer=request.referrer,
            device_type=device_type,
            browser=browser,
            is_suspicious=is_suspicious
        )
        
        db.session.add(log)
        db.session.commit()
        
    except Exception as e:
        app.logger.error(f"Error logging detailed request: {str(e)}")

def advanced_security_middleware(app):
    """Apply advanced security middleware"""
    
    @app.before_request
    def check_security():
        """Check security before each request"""
        # Skip for static files and health checks
        if request.path.startswith('/static/') or request.path in ['/health', '/metrics', '/status']:
            return None
        
        # Check if IP is blocked
        ip = get_client_ip()
        is_blocked, reason = is_ip_blocked(ip)
        if is_blocked:
            app.logger.warning(f"Blocked IP attempt: {ip} - {reason}")
            return jsonify({
                'error': 'Access Denied',
                'message': 'Your IP address has been blocked',
                'reason': reason
            }), 403
        
        # Check if system is active
        is_active, message = is_system_active()
        if not is_active:
            # Allow master admin access during shutdown
            from flask_login import current_user
            from utils.master_admin_utils import is_master_admin
            
            if not (current_user.is_authenticated and is_master_admin(current_user)):
                if request.path.startswith('/api/'):
                    return jsonify({
                        'error': 'System Unavailable',
                        'message': message
                    }), 503
                return render_template('maintenance.html', message=message), 503
        
        # Check user permissions
        from flask_login import current_user
        if current_user.is_authenticated:
            has_permission, perm_message = check_user_permissions(current_user)
            if not has_permission:
                if request.path.startswith('/api/'):
                    return jsonify({
                        'error': 'Permission Denied',
                        'message': perm_message
                    }), 403
                from flask import flash, redirect, url_for
                flash(perm_message, 'danger')
                return redirect(url_for('index'))
        
        # Store start time for logging
        request.start_time = time.time()
    
    @app.after_request
    def log_request(response):
        """Log request after completion"""
        if hasattr(request, 'start_time'):
            log_detailed_request(app, request.start_time, response)
        return response
    
    @app.errorhandler(Exception)
    def handle_error(error):
        """Handle and log errors"""
        if hasattr(request, 'start_time'):
            log_detailed_request(app, request.start_time, error=error)
        
        app.logger.error(f"Unhandled error: {str(error)}")
        app.logger.error(traceback.format_exc())
        
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Internal Server Error',
                'message': str(error)
            }), 500
        
        return render_template('error.html', error=str(error)), 500

def require_permission(permission_name):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask_login import current_user
            from flask import flash, redirect, url_for
            
            if not current_user.is_authenticated:
                flash('Please login to continue', 'warning')
                return redirect(url_for('login'))
            
            from models import User, Customer
            if isinstance(current_user, User):
                perms = UserPermission.query.filter_by(user_id=current_user.id).first()
            elif isinstance(current_user, Customer):
                perms = UserPermission.query.filter_by(customer_id=current_user.id).first()
            else:
                return f(*args, **kwargs)
            
            if not perms:
                return f(*args, **kwargs)
            
            # Check specific permission
            if not getattr(perms, permission_name, True):
                flash('You don\'t have permission to access this feature', 'danger')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
