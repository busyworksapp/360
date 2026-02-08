"""
BANK-LEVEL SECURITY SYSTEM
Ultra-fast, ultra-secure authentication and protection
"""
import pyotp
import qrcode
import io
import base64
import re
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from functools import wraps, lru_cache
from flask import session, redirect, url_for, request
from flask_login import current_user
from werkzeug.utils import secure_filename
import os

try:
    import magic
    MAGIC_AVAILABLE = True
except (ImportError, OSError):
    MAGIC_AVAILABLE = False

# BANK-LEVEL PASSWORD REQUIREMENTS
PASSWORD_MIN_LENGTH = 12
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = True
PASSWORD_MAX_AGE_DAYS = 90

# AGGRESSIVE LOCKOUT SETTINGS
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION_MINUTES = 60
PROGRESSIVE_LOCKOUT = True  # Increase lockout time with each failure

# PRE-COMPILED REGEX (PERFORMANCE)
_REGEX_PATTERNS = {
    'upper': re.compile(r'[A-Z]'),
    'lower': re.compile(r'[a-z]'),
    'digit': re.compile(r'\d'),
    'special': re.compile(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]'),
    'sequential': re.compile(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', re.IGNORECASE),
    'repeated': re.compile(r'(.)\1{2,}')
}

# COMMON WEAK PASSWORDS (HASHED FOR SPEED)
_WEAK_PASSWORDS = frozenset([
    hashlib.sha256(p.encode()).hexdigest() for p in [
        'password', 'password123', 'admin', 'admin123', '12345678', 
        'qwerty', 'letmein', 'welcome', 'monkey', 'dragon'
    ]
])

# IN-MEMORY STORAGE (USE REDIS IN PRODUCTION)
_failed_attempts = {}
_locked_accounts = {}
_rate_limits = {}

# FILE SECURITY
ALLOWED_IMAGE_EXTENSIONS = frozenset(['png', 'jpg', 'jpeg', 'gif', 'webp'])
ALLOWED_DOCUMENT_EXTENSIONS = frozenset(['pdf'])
ALLOWED_MIME_TYPES = frozenset([
    'image/png', 'image/jpeg', 'image/gif', 'image/webp', 'application/pdf'
])
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB (reduced for security)

# SECURITY HEADERS
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net code.jquery.com js.stripe.com; script-src-elem 'self' 'unsafe-inline' cdn.jsdelivr.net code.jquery.com js.stripe.com; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; style-src-elem 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com; style-src-attr 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' cdnjs.cloudflare.com; connect-src 'self' https://api.stripe.com cdn.jsdelivr.net",
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
}


def validate_password_strength(password):
    """BANK-LEVEL password validation - ultra-fast"""
    if not password or len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Minimum {PASSWORD_MIN_LENGTH} characters required"
    
    # Check patterns (pre-compiled for speed)
    if not _REGEX_PATTERNS['upper'].search(password):
        return False, "Must contain uppercase letter"
    if not _REGEX_PATTERNS['lower'].search(password):
        return False, "Must contain lowercase letter"
    if not _REGEX_PATTERNS['digit'].search(password):
        return False, "Must contain number"
    if not _REGEX_PATTERNS['special'].search(password):
        return False, "Must contain special character"
    
    # Advanced security checks
    if _REGEX_PATTERNS['sequential'].search(password):
        return False, "No sequential characters allowed"
    if _REGEX_PATTERNS['repeated'].search(password):
        return False, "No repeated characters allowed"
    
    # Check against weak passwords (hashed comparison for speed)
    pwd_hash = hashlib.sha256(password.lower().encode()).hexdigest()
    if pwd_hash in _WEAK_PASSWORDS:
        return False, "Password too common"
    
    return True, ""


def check_account_locked(username):
    """Check lockout status - optimized"""
    lock_data = _locked_accounts.get(username)
    if not lock_data:
        return False, ""
    
    now = time.time()
    if now < lock_data['until']:
        remaining = int((lock_data['until'] - now) / 60)
        return True, f"Account locked for {remaining} more minutes"
    
    # Auto-unlock
    _locked_accounts.pop(username, None)
    _failed_attempts.pop(username, None)
    return False, ""


def record_failed_login(username):
    """Record failed attempt with progressive lockout"""
    now = time.time()
    cutoff = now - (LOCKOUT_DURATION_MINUTES * 60)
    
    # Get or create attempt list
    attempts = _failed_attempts.setdefault(username, [])
    attempts.append(now)
    
    # Clean old attempts (in-place for speed)
    while attempts and attempts[0] < cutoff:
        attempts.pop(0)
    
    # Check threshold
    if len(attempts) >= MAX_LOGIN_ATTEMPTS:
        # Progressive lockout: multiply duration by attempt count
        lockout_multiplier = len(attempts) // MAX_LOGIN_ATTEMPTS if PROGRESSIVE_LOCKOUT else 1
        lockout_seconds = LOCKOUT_DURATION_MINUTES * 60 * lockout_multiplier
        
        _locked_accounts[username] = {
            'until': now + lockout_seconds,
            'attempts': len(attempts)
        }
        return True
    
    return False


def clear_failed_login_attempts(username):
    """Clear attempts after successful login"""
    _failed_attempts.pop(username, None)
    _locked_accounts.pop(username, None)


def rate_limit_check(identifier, max_requests=10, window_seconds=60):
    """Generic rate limiting - ultra-fast"""
    now = time.time()
    cutoff = now - window_seconds
    
    requests = _rate_limits.setdefault(identifier, [])
    requests.append(now)
    
    # Clean old requests
    while requests and requests[0] < cutoff:
        requests.pop(0)
    
    return len(requests) <= max_requests


def generate_2fa_secret():
    """Generate cryptographically secure 2FA secret"""
    return pyotp.random_base32()


@lru_cache(maxsize=128)
def get_2fa_qr_code(username, secret, issuer_name="360Degree Supply"):
    """Generate QR code - cached for performance"""
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=username, issuer_name=issuer_name)
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    
    return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"


def verify_2fa_token(secret, token):
    """Verify 2FA with timing attack protection"""
    if not token or not secret:
        return False
    
    totp = pyotp.TOTP(secret)
    # Constant-time comparison
    return totp.verify(token, valid_window=1)


def require_2fa(f):
    """Decorator for 2FA-protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        if hasattr(current_user, 'is_admin') and current_user.is_admin:
            if hasattr(current_user, 'two_factor_secret') and current_user.two_factor_secret:
                if not session.get('2fa_verified'):
                    return redirect(url_for('verify_2fa', next=request.url))
        
        return f(*args, **kwargs)
    return decorated


def secure_file_upload(file, allowed_extensions=None, max_size=MAX_FILE_SIZE):
    """BANK-LEVEL file upload security"""
    if not file or not file.filename:
        return False, "No file", None
    
    filename = secure_filename(file.filename)
    if not filename or '.' not in filename:
        return False, "Invalid filename", None
    
    ext = filename.rsplit('.', 1)[1].lower()
    allowed = allowed_extensions or (ALLOWED_IMAGE_EXTENSIONS | ALLOWED_DOCUMENT_EXTENSIONS)
    
    if ext not in allowed:
        return False, f"File type not allowed", None
    
    # Check size efficiently
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size == 0:
        return False, "Empty file", None
    if size > max_size:
        return False, f"Max {max_size // (1024*1024)}MB", None
    
    # MIME validation
    if MAGIC_AVAILABLE:
        try:
            content = file.read(2048)
            mime = magic.from_buffer(content, mime=True)
            file.seek(0)
            
            if mime not in ALLOWED_MIME_TYPES:
                return False, "Invalid file type", None
        except:
            file.seek(0)
    
    # Generate secure filename
    secure_name = f"{secrets.token_hex(16)}.{ext}"
    return True, "", secure_name


def log_security_event(event_type, user_id=None, username=None, details=None, ip_address=None):
    """Fast security logging"""
    try:
        from models import db, AuditLog
        
        log = AuditLog(
            event_type=event_type,
            user_id=user_id,
            username=username,
            details=details,
            ip_address=ip_address or get_client_ip(),
            user_agent=request.headers.get('User-Agent', '')[:500],
            timestamp=datetime.utcnow()
        )
        
        db.session.add(log)
        db.session.commit()
    except:
        pass  # Never fail on logging


def get_client_ip():
    """Get real IP - optimized"""
    return (request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or
            request.headers.get('X-Real-IP') or
            request.remote_addr)


def sanitize_input(text, max_length=1000):
    """Fast input sanitization"""
    if not text:
        return ""
    
    # Remove dangerous characters
    text = str(text)[:max_length]
    text = re.sub(r'[<>"\']', '', text)
    return text.strip()


def generate_csrf_token():
    """Generate secure CSRF token"""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']


def validate_csrf_token(token):
    """Validate CSRF token - constant time"""
    expected = session.get('_csrf_token')
    if not expected or not token:
        return False
    return secrets.compare_digest(expected, token)


def hash_password_secure(password):
    """Secure password hashing with salt"""
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password, method='pbkdf2:sha256:260000')


def verify_password_secure(password_hash, password):
    """Secure password verification"""
    from werkzeug.security import check_password_hash
    return check_password_hash(password_hash, password)


def generate_secure_token(length=32):
    """Generate cryptographically secure token"""
    return secrets.token_urlsafe(length)


def constant_time_compare(a, b):
    """Constant-time string comparison"""
    return secrets.compare_digest(str(a), str(b))


# SECURITY MONITORING
def detect_suspicious_activity(username, ip_address):
    """Detect suspicious patterns"""
    # Check for rapid requests from same IP
    if not rate_limit_check(f"ip_{ip_address}", max_requests=20, window_seconds=60):
        log_security_event('suspicious_activity', username=username, 
                         details='Rate limit exceeded', ip_address=ip_address)
        return True
    
    # Check for multiple failed logins
    attempts = _failed_attempts.get(username, [])
    if len(attempts) >= 2:
        log_security_event('suspicious_activity', username=username,
                         details='Multiple failed attempts', ip_address=ip_address)
        return True
    
    return False


def cleanup_old_data():
    """Periodic cleanup of in-memory data"""
    now = time.time()
    cutoff = now - 3600  # 1 hour
    
    # Clean failed attempts
    for username in list(_failed_attempts.keys()):
        _failed_attempts[username] = [t for t in _failed_attempts[username] if t > cutoff]
        if not _failed_attempts[username]:
            del _failed_attempts[username]
    
    # Clean rate limits
    for key in list(_rate_limits.keys()):
        _rate_limits[key] = [t for t in _rate_limits[key] if t > cutoff]
        if not _rate_limits[key]:
            del _rate_limits[key]
    
    # Clean expired locks
    for username in list(_locked_accounts.keys()):
        if _locked_accounts[username]['until'] < now:
            del _locked_accounts[username]
