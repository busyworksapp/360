"""
ADVANCED SECURITY MIDDLEWARE
Real-time threat detection and prevention
"""
from flask import request, abort, g
from functools import wraps
import time
import re
from security_utils import (
    rate_limit_check, get_client_ip, log_security_event,
    detect_suspicious_activity, SECURITY_HEADERS
)

# ATTACK PATTERNS (PRE-COMPILED)
_SQL_INJECTION = re.compile(r"(\bunion\b|\bselect\b|\binsert\b|\bupdate\b|\bdelete\b|\bdrop\b|\b--|\b;)", re.IGNORECASE)
_XSS_PATTERNS = re.compile(r"(<script|javascript:|onerror=|onload=|<iframe)", re.IGNORECASE)
_PATH_TRAVERSAL = re.compile(r"(\.\./|\.\.\\|%2e%2e)")
_COMMAND_INJECTION = re.compile(r"(;|\||&|`|\$\(|\${)")

# BLOCKED USER AGENTS
_BLOCKED_AGENTS = frozenset(['sqlmap', 'nikto', 'nmap', 'masscan', 'metasploit'])


def security_middleware(app):
    """Apply security middleware to Flask app"""
    
    @app.before_request
    def before_request_security():
        """Run before every request"""
        g.request_start_time = time.time()
        ip = get_client_ip()
        
        # 1. Rate limiting
        if not rate_limit_check(f"ip_{ip}", max_requests=100, window_seconds=60):
            log_security_event('rate_limit_exceeded', details=f'IP: {ip}', ip_address=ip)
            abort(429, "Too many requests")
        
        # 2. Block malicious user agents
        user_agent = request.headers.get('User-Agent', '').lower()
        if any(agent in user_agent for agent in _BLOCKED_AGENTS):
            log_security_event('blocked_user_agent', details=user_agent, ip_address=ip)
            abort(403, "Forbidden")
        
        # 3. Check for attack patterns in URL
        if _SQL_INJECTION.search(request.url) or _XSS_PATTERNS.search(request.url) or _PATH_TRAVERSAL.search(request.url):
            log_security_event('attack_detected', details=f'URL: {request.url}', ip_address=ip)
            abort(400, "Bad request")
        
        # 4. Check request body for attacks
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                if request.is_json:
                    data = str(request.get_json())
                else:
                    data = str(request.form)
                
                if _SQL_INJECTION.search(data) or _XSS_PATTERNS.search(data) or _COMMAND_INJECTION.search(data):
                    log_security_event('attack_detected', details='Malicious payload', ip_address=ip)
                    abort(400, "Bad request")
            except:
                pass
        
        # 5. Validate content length
        if request.content_length and request.content_length > 20 * 1024 * 1024:  # 20MB
            abort(413, "Payload too large")
    
    @app.after_request
    def after_request_security(response):
        """Add security headers to every response"""
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value
        
        # Add timing header for monitoring
        if hasattr(g, 'request_start_time'):
            duration = int((time.time() - g.request_start_time) * 1000)
            response.headers['X-Response-Time'] = f"{duration}ms"
        
        return response
    
    @app.errorhandler(429)
    def rate_limit_handler(e):
        return {"error": "Rate limit exceeded"}, 429
    
    @app.errorhandler(403)
    def forbidden_handler(e):
        return {"error": "Forbidden"}, 403
    
    @app.errorhandler(400)
    def bad_request_handler(e):
        return {"error": "Bad request"}, 400


def require_secure_connection(f):
    """Decorator to require HTTPS"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.is_secure and not request.headers.get('X-Forwarded-Proto') == 'https':
            abort(403, "HTTPS required")
        return f(*args, **kwargs)
    return decorated


def ip_whitelist(allowed_ips):
    """Decorator to restrict access to specific IPs"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            ip = get_client_ip()
            if ip not in allowed_ips:
                log_security_event('ip_blocked', details=f'IP: {ip}')
                abort(403, "Access denied")
            return f(*args, **kwargs)
        return decorated
    return decorator
