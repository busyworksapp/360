"""
Phase 2 Security Enhancements
- 2FA for admin accounts
- Account lockout after failed logins
- Enhanced audit logging
- Password strength enforcement
- Secure file upload validation
"""

import pyotp
import qrcode
import io
import base64
import re
from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, request, flash
from flask_login import current_user
from werkzeug.utils import secure_filename
import os

try:
    import magic
    MAGIC_AVAILABLE = True
except (ImportError, OSError):
    MAGIC_AVAILABLE = False
    print("Warning: python-magic not available. File type validation will be limited.")

# Password strength requirements
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = True

# Account lockout settings
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30

# Failed login tracking (in-memory, could be moved to database/Redis)
failed_login_attempts = {}
locked_accounts = {}

# Allowed file types for uploads
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx'}
ALLOWED_MIME_TYPES = {
    'image/png', 'image/jpeg', 'image/gif', 'image/webp',
    'application/pdf', 'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_password_strength(password):
    """
    Validate password meets security requirements
    Returns: (bool, str) - (is_valid, error_message)
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
    
    if PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character (!@#$%^&*...)"
    
    return True, ""


def check_account_locked(username):
    """Check if account is locked due to failed login attempts"""
    if username in locked_accounts:
        lock_time = locked_accounts[username]
        if datetime.utcnow() < lock_time:
            remaining = (lock_time - datetime.utcnow()).total_seconds() / 60
            return True, f"Account locked. Try again in {int(remaining)} minutes."
        else:
            # Unlock account
            del locked_accounts[username]
            if username in failed_login_attempts:
                del failed_login_attempts[username]
    return False, ""


def record_failed_login(username):
    """Record a failed login attempt and lock account if threshold exceeded"""
    if username not in failed_login_attempts:
        failed_login_attempts[username] = []
    
    # Add timestamp of failed attempt
    failed_login_attempts[username].append(datetime.utcnow())
    
    # Remove attempts older than lockout duration
    cutoff = datetime.utcnow() - timedelta(minutes=LOCKOUT_DURATION_MINUTES)
    failed_login_attempts[username] = [
        attempt for attempt in failed_login_attempts[username] 
        if attempt > cutoff
    ]
    
    # Check if threshold exceeded
    if len(failed_login_attempts[username]) >= MAX_LOGIN_ATTEMPTS:
        locked_accounts[username] = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        return True  # Account now locked
    
    return False


def clear_failed_login_attempts(username):
    """Clear failed login attempts after successful login"""
    if username in failed_login_attempts:
        del failed_login_attempts[username]
    if username in locked_accounts:
        del locked_accounts[username]


def generate_2fa_secret():
    """Generate a new 2FA secret key"""
    return pyotp.random_base32()


def get_2fa_qr_code(username, secret, issuer_name="360Degree Supply"):
    """
    Generate QR code for 2FA setup
    Returns: base64 encoded image
    """
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=username, issuer_name=issuer_name)
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"


def verify_2fa_token(secret, token):
    """Verify a 2FA token"""
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)  # Allow 1 window back/forward for clock skew


def require_2fa(f):
    """Decorator to require 2FA verification for admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        # Check if user is admin and has 2FA enabled
        if hasattr(current_user, 'is_admin') and current_user.is_admin:
            if hasattr(current_user, 'two_factor_secret') and current_user.two_factor_secret:
                # Check if 2FA is verified in this session
                if not session.get('2fa_verified', False):
                    return redirect(url_for('verify_2fa', next=request.url))
        
        return f(*args, **kwargs)
    return decorated_function


def secure_file_upload(file, allowed_extensions=None, max_size=MAX_FILE_SIZE):
    """
    Comprehensive file upload validation
    
    Args:
        file: FileStorage object from request.files
        allowed_extensions: Set of allowed extensions (defaults to images + documents)
        max_size: Maximum file size in bytes
    
    Returns:
        (bool, str, str) - (is_valid, error_message, secure_filename)
    """
    if not file or file.filename == '':
        return False, "No file selected", None
    
    # Get secure filename
    filename = secure_filename(file.filename)
    if not filename:
        return False, "Invalid filename", None
    
    # Check file extension
    if '.' not in filename:
        return False, "File must have an extension", None
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if allowed_extensions is None:
        allowed_extensions = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_DOCUMENT_EXTENSIONS
    
    if ext not in allowed_extensions:
        return False, f"File type .{ext} not allowed. Allowed types: {', '.join(allowed_extensions)}", None
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        return False, f"File too large. Maximum size: {max_mb}MB", None
    
    if file_size == 0:
        return False, "File is empty", None
    
    # Validate MIME type using python-magic (if available)
    if MAGIC_AVAILABLE:
        try:
            file_content = file.read(2048)  # Read first 2KB for magic number detection
            file.seek(0)
            
            mime = magic.from_buffer(file_content, mime=True)
            
            if mime not in ALLOWED_MIME_TYPES:
                return False, f"File type {mime} not allowed for security reasons", None
        except Exception as e:
            # If magic fails, just check extension
            print(f"Magic detection failed: {e}")
    
    return True, "", filename


def log_security_event(event_type, user_id=None, username=None, details=None, ip_address=None):
    """
    Log security events for audit trail
    
    Args:
        event_type: Type of event (login_success, login_failed, 2fa_enabled, etc.)
        user_id: User ID if available
        username: Username if available
        details: Additional details about the event
        ip_address: IP address of request
    """
    from models import db, AuditLog
    
    log_entry = AuditLog(
        event_type=event_type,
        user_id=user_id,
        username=username,
        details=details,
        ip_address=ip_address or request.remote_addr,
        user_agent=request.headers.get('User-Agent', ''),
        timestamp=datetime.utcnow()
    )
    
    try:
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        print(f"Failed to log security event: {e}")
        db.session.rollback()


def get_client_ip():
    """Get real client IP address (handles proxies and Cloudflare)
    
    Priority order:
    1. CF-Connecting-IP (Cloudflare's real visitor IP)
    2. X-Forwarded-For (standard proxy header)
    3. X-Real-IP (alternative proxy header)
    4. request.remote_addr (direct connection)
    """
    # Cloudflare provides the real visitor IP
    cf_ip = request.headers.get('CF-Connecting-IP')
    if cf_ip:
        return cf_ip
    
    # Standard proxy headers
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # Direct connection
    return request.remote_addr
