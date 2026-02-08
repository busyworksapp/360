import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # SECURITY: SECRET_KEY must be set in production
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("CRITICAL SECURITY ERROR: SECRET_KEY environment variable must be set!")
    if SECRET_KEY == 'dev-secret-key':
        raise ValueError("CRITICAL SECURITY ERROR: Change SECRET_KEY from default value!")
    
    # Handle DATABASE_URL with proper format conversion
    _db_url = os.getenv('DATABASE_URL', '')
    print(f"[DEBUG] DATABASE_URL from env: {_db_url[:50] if _db_url else 'NOT SET'}...")  # Debug
    if _db_url:
        # Replace mysql:// with mysql+pymysql:// if needed
        if _db_url.startswith('mysql://'):
            SQLALCHEMY_DATABASE_URI = _db_url.replace('mysql://', 'mysql+pymysql://', 1)
            print(f"[DEBUG] Converted to: {SQLALCHEMY_DATABASE_URI[:50]}...")  # Debug
        else:
            SQLALCHEMY_DATABASE_URI = _db_url
    else:
        # Fallback for development
        SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
        print("[WARNING] Using SQLite fallback - DATABASE_URL not set!")  # Debug
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Cache Configuration - Use Redis if available, fallback to simple cache
    REDIS_URL = os.getenv('REDIS_URL')
    if REDIS_URL:
        CACHE_TYPE = 'redis'
        CACHE_REDIS_URL = REDIS_URL
    else:
        CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    PAYFAST_MERCHANT_ID = os.getenv('PAYFAST_MERCHANT_ID')
    PAYFAST_MERCHANT_KEY = os.getenv('PAYFAST_MERCHANT_KEY')
    PAYFAST_PASSPHRASE = os.getenv('PAYFAST_PASSPHRASE')
    PAYFAST_MODE = os.getenv('PAYFAST_MODE', 'sandbox')
    
    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_FROM_ADDRESS = os.getenv(
        'MAIL_FROM_ADDRESS',
        'noreply@360degreesupply.co.za'
    )
    MAIL_FROM_NAME = os.getenv(
        'MAIL_FROM_NAME',
        '360Degree Supply'
    )
    CONTACT_EMAIL = os.getenv(
        'CONTACT_EMAIL',
        'info@360degreesupply.co.za'
    )
    ADMIN_EMAIL = os.getenv(
        'ADMIN_EMAIL',
        'admin@360degreesupply.co.za'
    )
    SEND_EMAILS = os.getenv('SEND_EMAILS', 'True') == 'True'
    
    # BANK-LEVEL File Upload Security
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max (reduced for security)
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}  # Removed gif
    ALLOWED_POP_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/png', 'image/webp', 'application/pdf'
    }
    FILE_SCAN_ENABLED = True  # Enable virus scanning if available
    
    # BANK-LEVEL Session Security
    is_production = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_SECURE = True  # Always enforce HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'  # Strict for maximum security
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes (reduced)
    SESSION_COOKIE_NAME = '__Host-session' if is_production else 'session'
    SESSION_REFRESH_EACH_REQUEST = True  # Auto-refresh session
    
    # BANK-LEVEL Remember Me Security
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 1  # 1 day only (reduced for security)
    REMEMBER_COOKIE_NAME = '__Host-remember' if is_production else 'remember'
    REMEMBER_COOKIE_SAMESITE = 'Strict'
    
    # BANK-LEVEL CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour limit
    WTF_CSRF_SSL_STRICT = True  # Always enforce SSL
    WTF_CSRF_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    # BANK-LEVEL Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_DEFAULT = '100 per hour, 20 per minute'
    RATELIMIT_LOGIN = '5 per minute'
    RATELIMIT_API = '60 per minute'
    
    # OCR settings
    OCR_CONFIDENCE_THRESHOLD = 0.75  # Auto-verify if confidence >= 75%
    PAYMENT_VALIDATION_TOLERANCE = 0.01  # 1% tolerance for amount matching
    
    # Production Optimizations
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    PREFERRED_URL_SCHEME = 'https' if is_production else 'http'
    PROPAGATE_EXCEPTIONS = is_production
    
    # OPTIMIZED Performance Settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', '20')),  # Increased
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '1800')),  # Reduced
        'pool_pre_ping': True,
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '40')),  # Increased
        'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '10')),  # Reduced
        'echo': False,  # Disable SQL logging for speed
        'connect_args': {'connect_timeout': 5}  # Fast connection timeout
    }
    
    # Monitoring and Health Checks
    HEALTH_CHECK_ENABLED = True
    METRICS_ENABLED = os.getenv('METRICS_ENABLED', 'True') == 'True'
    
    # BANK-LEVEL Security Settings
    SECURITY_PASSWORD_SALT = os.getenv('SECURITY_PASSWORD_SALT', SECRET_KEY)
    SECURITY_TRACKABLE = True
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_PASSWORD_SCHEMES = ['pbkdf2_sha512', 'bcrypt']
    
    # Advanced Security
    FORCE_2FA_FOR_ADMIN = True
    AUTO_LOGOUT_INACTIVE_MINUTES = 15
    MAX_LOGIN_ATTEMPTS = 3
    LOCKOUT_DURATION_MINUTES = 60
    PASSWORD_EXPIRY_DAYS = 90
    
    # Performance Optimization
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year cache for static files
    TEMPLATES_AUTO_RELOAD = False if is_production else True
    JSON_SORT_KEYS = False  # Faster JSON serialization
    JSONIFY_PRETTYPRINT_REGULAR = False  # Compact JSON
