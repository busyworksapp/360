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
    if _db_url:
        # Replace mysql:// with mysql+pymysql:// if needed
        if _db_url.startswith('mysql://'):
            SQLALCHEMY_DATABASE_URI = _db_url.replace('mysql://', 'mysql+pymysql://', 1)
        else:
            SQLALCHEMY_DATABASE_URI = _db_url
    else:
        # Fallback for development
        SQLALCHEMY_DATABASE_URI = 'sqlite:///dev.db'
    
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
    
    # File Upload Security
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ALLOWED_POP_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
    ALLOWED_MIME_TYPES = {
        'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/pdf'
    }
    
    # Session Security
    # Only enforce secure cookies in production
    is_production = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_SECURE = is_production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    # Use __Host- prefix only in production (requires HTTPS)
    SESSION_COOKIE_NAME = '__Host-session' if is_production else 'session'
    
    # Remember Me Security
    REMEMBER_COOKIE_SECURE = is_production
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 7  # Days
    # Use __Host- prefix only in production (requires HTTPS)
    REMEMBER_COOKIE_NAME = '__Host-remember' if is_production else 'remember'
    
    # CSRF Protection
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None  # No time limit
    # Only enforce SSL strict in production
    WTF_CSRF_SSL_STRICT = os.getenv('FLASK_ENV') == 'production'
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')
    RATELIMIT_STRATEGY = 'fixed-window'
    
    # OCR settings
    OCR_CONFIDENCE_THRESHOLD = 0.75  # Auto-verify if confidence >= 75%
    PAYMENT_VALIDATION_TOLERANCE = 0.01  # 1% tolerance for amount matching
    
    # Production Optimizations
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    PREFERRED_URL_SCHEME = 'https' if is_production else 'http'
    PROPAGATE_EXCEPTIONS = is_production
    
    # Performance Settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
        'pool_recycle': int(os.getenv('DB_POOL_RECYCLE', '3600')),
        'pool_pre_ping': True,
        'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20')),
        'pool_timeout': int(os.getenv('DB_POOL_TIMEOUT', '30')),
    }
    
    # Monitoring and Health Checks
    HEALTH_CHECK_ENABLED = True
    METRICS_ENABLED = os.getenv('METRICS_ENABLED', 'True') == 'True'
