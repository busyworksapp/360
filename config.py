import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', '').replace('mysql://', 'mysql+pymysql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    REDIS_URL = os.getenv('REDIS_URL')
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL')
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
    
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
