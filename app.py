from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_cors import CORS
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import os
from datetime import datetime, timedelta
from config import Config
from models import (
    db, User, SiteSettings, CompanyInfo, Service, Product, HeroSection,
    ContentSection, PaymentMethod, PaymentTerm, Transaction,
    ContactSubmission, MenuItem, Testimonial, Customer, Cart, CartItem,
    Order, OrderItem, Invoice, InvoicePayment, InvoiceItem, ProofOfPayment, AuditLog,
    HomePageSettings
)
from email_service import EmailService
import json
import secrets
from werkzeug.utils import secure_filename
from payments import StripePayment, PayFastPayment
from email_service import EmailService
from geolocation import geolocation_service
from pricing import pricing_service
from ocr_service import OCRService
from s3_storage import storage_service
import bleach
from security_utils import (
    validate_password_strength, check_account_locked, record_failed_login,
    clear_failed_login_attempts, generate_2fa_secret, get_2fa_qr_code,
    verify_2fa_token, require_2fa, secure_file_upload, log_security_event,
    get_client_ip, cleanup_old_data
)
from security_middleware import security_middleware
from performance import optimize_db_connection, optimize_static_files, optimize_templates

app = Flask(__name__)
app.config.from_object(Config)

# APPLY BANK-LEVEL SECURITY MIDDLEWARE
security_middleware(app)

# APPLY PERFORMANCE OPTIMIZATIONS
optimize_db_connection(app)
optimize_static_files(app)
optimize_templates(app)

# Initialize logging FIRST for early error catching
from logging_config import setup_logging, log_request
setup_logging(app)
log_request(app)

app.logger.info("🚀 Initializing 360Degree Supply Application")
app.logger.info("🔒 Bank-level security enabled")
app.logger.info("⚡ Performance optimizations applied")

# Version: 2.3.0 - Production Optimization with Gunicorn and Monitoring

db.init_app(app)
migrate = Migrate(app, db)
cache = Cache(app)
CORS(app)

# CSRF Protection
csrf = CSRFProtect(app)

# Rate Limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://')
)

# HTTPS and Security Headers
csp = {
    'default-src': ["'self'"],
    'script-src': [
        "'self'",
        "'unsafe-inline'",
        "'unsafe-eval'",
        'cdn.jsdelivr.net',
        'code.jquery.com',
        'js.stripe.com'
    ],
    'script-src-elem': [
        "'self'",
        "'unsafe-inline'",
        'cdn.jsdelivr.net',
        'code.jquery.com',
        'js.stripe.com'
    ],
    'style-src': [
        "'self'",
        "'unsafe-inline'",
        'cdn.jsdelivr.net',
        'cdnjs.cloudflare.com'
    ],
    'style-src-elem': [
        "'self'",
        "'unsafe-inline'",
        'cdn.jsdelivr.net',
        'cdnjs.cloudflare.com'
    ],
    'style-src-attr': ["'unsafe-inline'"],
    'img-src': ["'self'", 'data:', 'https:'],
    'font-src': ["'self'", 'cdnjs.cloudflare.com'],
    'connect-src': ["'self'", 'https://api.stripe.com']
}

# Only enable Talisman in production (Railway deployment)
# Check for Railway environment or explicit production flag
is_railway = os.getenv('RAILWAY_ENVIRONMENT') is not None
is_production = os.getenv('FLASK_ENV') == 'production'
enable_https = os.getenv('ENABLE_HTTPS') == 'True'

# HTTPS Redirect Middleware - Force all traffic to HTTPS in production
@app.before_request
def force_https():
    """Force HTTPS in production by redirecting HTTP to HTTPS
    
    Supports both direct Railway access and Cloudflare proxy:
    - X-Forwarded-Proto: Standard proxy header (Railway, Cloudflare)
    - CF-Visitor: Cloudflare-specific header with JSON {"scheme":"https"}
    """
    if is_railway or is_production:
        # Check multiple headers for HTTPS detection (Cloudflare compatibility)
        forwarded_proto = request.headers.get('X-Forwarded-Proto', 'http')
        cf_visitor = request.headers.get('CF-Visitor', '{}')
        
        # Cloudflare sends CF-Visitor with scheme info
        is_https_cloudflare = '"scheme":"https"' in cf_visitor
        is_https = request.is_secure or forwarded_proto == 'https' or is_https_cloudflare
        
        if not is_https:
            # Exclude health check endpoints from redirect
            if request.path not in ['/health', '/health/detailed', '/metrics', '/status']:
                url = request.url.replace('http://', 'https://', 1)
                app.logger.info(f"🔒 Redirecting HTTP to HTTPS: {request.url} -> {url}")
                return redirect(url, code=301)

# Apply security in production - Manual implementation without Talisman
if is_production or enable_https:
    print("🔒 HTTPS enforcement enabled (Production)")
    
    # Manual HTTPS redirect is already handled by force_https() function above
    # No Talisman needed
else:
    print("⚠️  HTTPS enforcement disabled (Local development)")
    # Still apply CSP without HTTPS enforcement for local testing
    @app.after_request
    def add_csp_header(response):
        # Build CSP header manually with ALL directives including style-src-attr
        csp_header = "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net code.jquery.com js.stripe.com",
            "script-src-elem 'self' 'unsafe-inline' cdn.jsdelivr.net code.jquery.com js.stripe.com",
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com",
            "style-src-elem 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com",
            "style-src-attr 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' cdnjs.cloudflare.com",
            "connect-src 'self' https://api.stripe.com cdn.jsdelivr.net"
        ])
        response.headers['Content-Security-Policy'] = csp_header
        return response

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Initialize Email Service
email_service = EmailService(
    smtp_server=app.config.get('MAIL_SERVER'),
    smtp_port=app.config.get('MAIL_PORT'),
    sender_email=app.config.get('MAIL_USERNAME'),
    sender_password=app.config.get('MAIL_PASSWORD'),
    use_tls=app.config.get('MAIL_USE_TLS'),
    reply_to=os.getenv('MAIL_REPLY_TO', 'support@360degreesupply.co.za')
)

@login_manager.user_loader
def load_user(user_id):
    # Try to load as admin user first
    admin = db.session.get(User, int(user_id))
    if admin:
        return admin
    # Try to load as customer user
    customer = db.session.get(Customer, int(user_id))
    if customer:
        return customer
    return None

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# =====================================================
# SECURITY FUNCTIONS
# =====================================================

@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    # Prevent MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Enable XSS filter
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions policy
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    # HSTS for production
    if is_production or enable_https:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # CSP - Override any previous CSP headers
    if is_production or enable_https:
        csp_header = "; ".join([
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net code.jquery.com js.stripe.com",
            "script-src-elem 'self' 'unsafe-inline' cdn.jsdelivr.net code.jquery.com js.stripe.com",
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com",
            "style-src-elem 'self' 'unsafe-inline' cdn.jsdelivr.net cdnjs.cloudflare.com",
            "style-src-attr 'unsafe-inline'",
            "img-src 'self' data: https:",
            "font-src 'self' cdnjs.cloudflare.com",
            "connect-src 'self' https://api.stripe.com cdn.jsdelivr.net"
        ])
        response.headers['Content-Security-Policy'] = csp_header
    
    return response

def validate_password_strength(password):
    """Enforce strong password policy"""
    import re
    
    if len(password) < 12:
        return False, "Password must be at least 12 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain an uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain a lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain a number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain a special character"
    
    # Check against common passwords
    common_passwords = ['password123', 'admin123', '12345678', 'password', 'admin']
    if password.lower() in common_passwords:
        return False, "Password is too common"
    
    return True, "Password is strong"

def secure_file_upload(file):
    """Enhanced file upload security"""
    if not file:
        return None, "No file provided"
    
    # Check file size
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset
    
    if size > app.config['MAX_CONTENT_LENGTH']:
        return None, "File too large (max 16MB)"
    
    if size == 0:
        return None, "File is empty"
    
    # Sanitize filename
    filename = secure_filename(file.filename)
    if not filename:
        return None, "Invalid filename"
    
    # Check extension
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    if ext not in app.config['ALLOWED_EXTENSIONS']:
        return None, f"File type .{ext} not allowed"
    
    # Generate unique filename to prevent overwrite attacks
    unique_filename = f"{secrets.token_hex(16)}.{ext}"
    
    # Save file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)
    
    # Set restrictive permissions
    try:
        os.chmod(filepath, 0o644)
    except:
        pass  # Windows doesn't support chmod
    
    return unique_filename, None

def sanitize_input(text, max_length=1000):
    """Sanitize user input to prevent XSS"""
    if not text:
        return ""
    
    # Remove HTML tags and limit length
    clean_text = bleach.clean(str(text), tags=[], strip=True)
    return clean_text[:max_length]


# Custom decorator to require customer login
def customer_required(f):
    """Decorator to require customer authentication"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            # Check if this is an AJAX request
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': 'Please log in to add items to cart.',
                    'redirect': url_for('customer_login')
                }), 401
            
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('customer_login'))
        
        if not isinstance(current_user, Customer):
            # Check if this is an AJAX request
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': 'This feature is only accessible to customers.'
                }), 403
            
            flash('This page is only accessible to customers.', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in \
           app.config['ALLOWED_EXTENSIONS']


def save_upload_file(file):
    """Save uploaded file to S3 cloud storage for persistence across deployments"""
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    # Upload to S3 cloud storage
    file_url, error = storage_service.upload_file(
        file,
        folder='uploads',
        allowed_extensions=app.config['ALLOWED_EXTENSIONS']
    )
    
    if error:
        print(f"S3 Upload error: {error}")
        return None
    
    return file_url  # Returns full S3 URL (https://t3.storageapi.dev/bucket/uploads/filename)


def send_payment_email(transaction):
    """Send payment confirmation email to customer."""
    if not app.config.get('SEND_EMAILS'):
        return False

    company = CompanyInfo.query.first()
    if not company:
        return False

    return email_service.send_payment_confirmation(
        recipient_email=transaction.customer_email,
        recipient_name=transaction.customer_name or 'Valued Customer',
        transaction_id=transaction.transaction_id,
        amount=transaction.amount,
        currency=transaction.currency,
        payment_method=transaction.payment_method or
            transaction.payment_gateway,
        company_name=company.company_name,
        company_email=company.email,
        company_phone=company.phone
    )


@app.route('/')
@cache.cached(timeout=300)
def index():
    hero_sections = HeroSection.query.filter_by(
        is_active=True
    ).order_by(HeroSection.order_position).all()
    services = Service.query.filter_by(
        is_active=True
    ).order_by(Service.order_position).all()
    testimonials = Testimonial.query.filter_by(
        is_active=True
    ).order_by(Testimonial.order_position).limit(3).all()
    company_info = CompanyInfo.query.first()
    content_sections = ContentSection.query.filter_by(
        is_active=True
    ).order_by(ContentSection.order_position).all()
    menu_items = MenuItem.query.filter_by(
        is_active=True, parent_id=None
    ).order_by(MenuItem.order_position).all()
    # Get featured products (first 6 active products)
    products = Product.query.filter_by(
        is_active=True
    ).limit(6).all()

    return render_template('index.html',
                         hero_sections=hero_sections,
                         services=services,
                         testimonials=testimonials,
                         company_info=company_info,
                         content_sections=content_sections,
                         menu_items=menu_items,
                         products=products)

@app.route('/services')
@cache.cached(timeout=300)
def services():
    services = Service.query.filter_by(is_active=True).order_by(Service.order_position).all()
    company_info = CompanyInfo.query.first()
    menu_items = MenuItem.query.filter_by(is_active=True, parent_id=None).order_by(MenuItem.order_position).all()
    
    return render_template('services.html', 
                         services=services,
                         company_info=company_info,
                         menu_items=menu_items)

@app.route('/products')
@cache.cached(timeout=300)
def products():
    products = Product.query.filter_by(is_active=True).order_by(
        Product.order_position
    ).all()
    company_info = CompanyInfo.query.first()
    menu_items = MenuItem.query.filter_by(
        is_active=True, parent_id=None
    ).order_by(MenuItem.order_position).all()
    
    # Get unique categories
    categories = db.session.query(Product.category).filter(
        Product.is_active == True,
        Product.category.isnot(None),
        Product.category != ''
    ).distinct().order_by(Product.category).all()
    categories = [cat[0] for cat in categories if cat[0]]
    
    # Get pricing context for current customer
    pricing_ctx = pricing_service.get_product_list_context(products)
    
    return render_template('products.html',
                         products=products,
                         pricing_context=pricing_ctx,
                         categories=categories,
                         company_info=company_info,
                         menu_items=menu_items)

@app.route('/payment')
@cache.cached(timeout=300)
def payment():
    payment_methods = PaymentMethod.query.filter_by(is_active=True).order_by(PaymentMethod.order_position).all()
    payment_terms = PaymentTerm.query.filter_by(is_active=True).order_by(PaymentTerm.order_position).all()
    company_info = CompanyInfo.query.first()
    menu_items = MenuItem.query.filter_by(is_active=True, parent_id=None).order_by(MenuItem.order_position).all()
    
    return render_template('payment.html', 
                         payment_methods=payment_methods,
                         payment_terms=payment_terms,
                         company_info=company_info,
                         menu_items=menu_items,
                         stripe_public_key=app.config.get('STRIPE_PUBLIC_KEY', ''))

@app.route('/contact')
def contact():
    company_info = CompanyInfo.query.first()
    menu_items = MenuItem.query.filter_by(is_active=True, parent_id=None).order_by(MenuItem.order_position).all()
    
    return render_template('contact.html', 
                         company_info=company_info,
                         menu_items=menu_items)

@app.route('/api/contact', methods=['POST'])
@limiter.limit("10 per minute")  # Increased from 3 to 10
def submit_contact():
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'email', 'message']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                'success': False,
                'message': f'{field.capitalize()} is required'
            }), 400

    submission = ContactSubmission(
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        subject=data.get('subject'),
        message=data.get('message')
    )

    db.session.add(submission)
    db.session.commit()

    # Send emails asynchronously (non-blocking)
    if app.config.get('SEND_EMAILS'):
        import threading
        
        def send_emails_async():
            with app.app_context():  # Add Flask app context
                try:
                    company = CompanyInfo.query.first()

                    # Send confirmation to user
                    email_service.send_contact_confirmation(
                        recipient_name=data.get('name'),
                        recipient_email=data.get('email'),
                        subject=data.get('subject'),
                        message_content=data.get('message'),
                        company_name=company.company_name if company else
                            '360Degree Supply',
                        company_phone=company.phone if company else
                            '+27 64 902 4363',
                        company_email=company.email if company else
                            'info@360degreesupply.co.za'
                    )

                    # Send notification to admin (info@360degreesupply.co.za)
                    admin_email = app.config.get(
                        'ADMIN_EMAIL',
                        'info@360degreesupply.co.za'
                    )
                    email_service.send_contact_notification(
                        admin_email=admin_email,
                        sender_name=data.get('name'),
                        sender_email=data.get('email'),
                        sender_phone=data.get('phone'),
                        subject=data.get('subject'),
                        message_content=data.get('message'),
                        company_name=company.company_name if company else
                            '360Degree Supply'
                    )
                except Exception as e:
                    app.logger.error(f"Background email error: {str(e)}")
        
        # Start email sending in background thread
        email_thread = threading.Thread(target=send_emails_async)
        email_thread.daemon = True
        email_thread.start()

    return jsonify({
        'success': True,
        'message': 'Your message has been submitted successfully'
    })

# =====================================================
# UNIFIED LOGIN ROUTE
# =====================================================

@app.route('/login')
def login():
    """Unified login page for both admin and customer"""
    return render_template('login.html')


# =====================================================
# ADMIN AUTHENTICATION ROUTES
# =====================================================

@app.route('/admin/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check if account is locked
        is_locked, lock_message = check_account_locked(email)
        if is_locked:
            log_security_event('login_blocked_locked', username=email, 
                             details=lock_message, ip_address=get_client_ip())
            flash(lock_message, 'error')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_admin:
            # Clear failed attempts on successful login
            clear_failed_login_attempts(email)
            
            # Check if 2FA is enabled
            if user.two_factor_enabled and user.two_factor_secret:
                # Store user ID in session for 2FA verification
                session['2fa_user_id'] = user.id
                session['2fa_remember'] = request.form.get('remember', False)
                log_security_event('login_awaiting_2fa', user_id=user.id, 
                                 username=email, ip_address=get_client_ip())
                return redirect(url_for('verify_2fa'))
            else:
                # No 2FA, log in directly
                login_user(user, remember=request.form.get('remember', False))
                session['2fa_verified'] = True  # Mark as verified (no 2FA required)
                log_security_event('login_success', user_id=user.id, 
                                 username=email, ip_address=get_client_ip())
                flash('Login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
        else:
            # Record failed login attempt
            is_now_locked = record_failed_login(email)
            
            if is_now_locked:
                log_security_event('account_locked', username=email, 
                                 details='Account locked due to multiple failed attempts',
                                 ip_address=get_client_ip())
                flash('Too many failed login attempts. Account locked for 30 minutes.', 'error')
            else:
                log_security_event('login_failed', username=email, 
                                 details='Invalid credentials', ip_address=get_client_ip())
                flash('Invalid email or password', 'error')
            
            return redirect(url_for('login'))
    
    return redirect(url_for('login'))

@app.route('/admin/logout')
@login_required
def admin_logout():
    if current_user.is_authenticated:
        log_security_event('logout', user_id=current_user.id, 
                         username=current_user.email, ip_address=get_client_ip())
    logout_user()
    session.pop('2fa_verified', None)
    session.pop('2fa_user_id', None)
    return redirect(url_for('index'))


# ============================================================================
# 2FA Routes
# ============================================================================

@app.route('/verify-2fa', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def verify_2fa():
    """Verify 2FA token after password login"""
    user_id = session.get('2fa_user_id')
    if not user_id:
        flash('Session expired. Please login again.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        token = request.form.get('token', '').strip()
        
        if verify_2fa_token(user.two_factor_secret, token):
            # 2FA successful
            remember = session.get('2fa_remember', False)
            login_user(user, remember=remember)
            session['2fa_verified'] = True
            session.pop('2fa_user_id', None)
            session.pop('2fa_remember', None)
            
            log_security_event('2fa_success', user_id=user.id, 
                             username=user.email, ip_address=get_client_ip())
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            log_security_event('2fa_failed', user_id=user.id, 
                             username=user.email, ip_address=get_client_ip())
            flash('Invalid 2FA code. Please try again.', 'error')
    
    return render_template('admin/verify_2fa.html', user=user)


@app.route('/admin/2fa/setup', methods=['GET', 'POST'])
@login_required
def setup_2fa():
    """Setup 2FA for admin account"""
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'enable':
            token = request.form.get('token', '').strip()
            secret = session.get('temp_2fa_secret')
            
            if not secret:
                flash('Session expired. Please try again.', 'error')
                return redirect(url_for('setup_2fa'))
            
            if verify_2fa_token(secret, token):
                # Save 2FA secret to user
                current_user.two_factor_secret = secret
                current_user.two_factor_enabled = True
                db.session.commit()
                session.pop('temp_2fa_secret', None)
                
                log_security_event('2fa_enabled', user_id=current_user.id, 
                                 username=current_user.email, ip_address=get_client_ip())
                flash('2FA enabled successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid code. Please scan the QR code again and try.', 'error')
        
        elif action == 'disable':
            password = request.form.get('password')
            if current_user.check_password(password):
                current_user.two_factor_secret = None
                current_user.two_factor_enabled = False
                db.session.commit()
                
                log_security_event('2fa_disabled', user_id=current_user.id, 
                                 username=current_user.email, ip_address=get_client_ip())
                flash('2FA disabled', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid password', 'error')
    
    # Generate new secret for setup
    if not current_user.two_factor_enabled:
        secret = generate_2fa_secret()
        session['temp_2fa_secret'] = secret
        qr_code = get_2fa_qr_code(current_user.email, secret)
    else:
        secret = None
        qr_code = None
    
    return render_template('admin/setup_2fa.html', 
                         qr_code=qr_code, 
                         secret=secret,
                         two_factor_enabled=current_user.two_factor_enabled)


@app.route('/admin')
@login_required
def admin_dashboard():
    total_services = Service.query.count()
    total_products = Product.query.count()
    total_transactions = Transaction.query.count()
    pending_contacts = ContactSubmission.query.filter_by(status='new').count()
    
    # Get recent transactions with customer info via order relationship
    recent_transactions = db.session.query(
        Transaction,
        Order,
        Customer
    ).join(
        Order, Transaction.order_id == Order.id
    ).join(
        Customer, Order.customer_id == Customer.id
    ).order_by(Transaction.created_at.desc()).limit(5).all()
    
    recent_contacts = ContactSubmission.query.order_by(ContactSubmission.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_services=total_services,
                         total_products=total_products,
                         total_transactions=total_transactions,
                         pending_contacts=pending_contacts,
                         recent_transactions=recent_transactions,
                         recent_contacts=recent_contacts)

@app.route('/admin/company', methods=['GET', 'POST'])
@login_required
def admin_company():
    company_info = CompanyInfo.query.first()
    
    if not company_info:
        company_info = CompanyInfo()
        db.session.add(company_info)
    
    if request.method == 'POST':
        company_info.company_name = request.form.get('company_name')
        company_info.address = request.form.get('address')
        company_info.phone = request.form.get('phone')
        company_info.email = request.form.get('email')
        company_info.description = request.form.get('description')
        company_info.mission = request.form.get('mission')
        company_info.established_year = request.form.get('established_year')
        
        if 'logo' in request.files:
            logo_url = save_upload_file(request.files['logo'])
            if logo_url:
                company_info.logo_url = logo_url
        
        db.session.commit()
        cache.clear()
        flash('Company information updated successfully', 'success')
        
        return redirect(url_for('admin_company'))
    
    return render_template('admin/company.html', company=company_info)


@app.route('/admin/homepage', methods=['GET', 'POST'])
@login_required
def admin_homepage():
    settings = HomePageSettings.query.first()
    if not settings:
        settings = HomePageSettings()
        db.session.add(settings)
        db.session.commit()
    if request.method == 'POST':
        settings.hero_title = request.form.get('hero_title')
        settings.hero_description = request.form.get('hero_description')
        settings.hero_button_text = request.form.get('hero_button_text')
        settings.hero_button_link = request.form.get('hero_button_link')
        settings.show_stats_card = request.form.get('show_stats_card') == 'on'
        settings.stats_percentage = request.form.get('stats_percentage')
        settings.stats_label = request.form.get('stats_label')
        if 'hero_image' in request.files:
            hero_image_url = save_upload_file(request.files['hero_image'])
            if hero_image_url:
                settings.hero_image = hero_image_url
        db.session.commit()
        cache.clear()
        flash('Homepage settings updated successfully!', 'success')
        return redirect(url_for('admin_homepage'))
    return render_template('admin/homepage.html', settings=settings)

@app.route('/admin/services')
@login_required
def admin_services():
    services = Service.query.order_by(Service.order_position).all()
    return render_template('admin/services.html', services=services)

@app.route('/admin/services/add', methods=['GET', 'POST'])
@login_required
def admin_service_add():
    if request.method == 'POST':
        service = Service(
            title=request.form.get('title'),
            description=request.form.get('description'),
            icon=request.form.get('icon'),
            order_position=request.form.get('order_position', 0),
            is_active=request.form.get('is_active') == 'on'
        )
        
        if 'image' in request.files:
            image_url = save_upload_file(request.files['image'])
            if image_url:
                service.image_url = image_url
        
        db.session.add(service)
        db.session.commit()
        cache.clear()
        flash('Service added successfully', 'success')
        
        return redirect(url_for('admin_services'))
    
    return render_template('admin/service_form.html', service=None)

@app.route('/admin/services/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_service_edit(id):
    service = Service.query.get_or_404(id)
    
    if request.method == 'POST':
        service.title = request.form.get('title')
        service.description = request.form.get('description')
        service.icon = request.form.get('icon')
        service.order_position = request.form.get('order_position', 0)
        service.is_active = request.form.get('is_active') == 'on'
        
        if 'image' in request.files:
            image_url = save_upload_file(request.files['image'])
            if image_url:
                service.image_url = image_url
        
        db.session.commit()
        cache.clear()
        flash('Service updated successfully', 'success')
        
        return redirect(url_for('admin_services'))
    
    return render_template('admin/service_form.html', service=service)

@app.route('/admin/services/<int:id>/delete', methods=['POST'])
@login_required
def admin_service_delete(id):
    service = Service.query.get_or_404(id)
    db.session.delete(service)
    db.session.commit()
    cache.clear()
    flash('Service deleted successfully', 'success')
    
    return redirect(url_for('admin_services'))

@app.route('/admin/products')
@login_required
def admin_products():
    products = Product.query.order_by(Product.order_position).all()
    return render_template('admin/products.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def admin_product_add():
    if request.method == 'POST':
        price_zar = request.form.get('price_zar')
        price_usd = request.form.get('price_usd')
        
        # Validate pricing
        is_valid, error_msg = pricing_service.validate_pricing_data(
            price_zar, price_usd
        )
        if not is_valid:
            flash(f'Pricing Error: {error_msg}', 'danger')
            return render_template('admin/product_form.html', product=None)
        
        product = Product(
            name=request.form.get('name'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            specifications=request.form.get('specifications'),
            price_zar=price_zar or None,
            price_usd=price_usd or None,
            unit=request.form.get('unit'),
            order_position=request.form.get('order_position', 0),
            is_active=request.form.get('is_active') == 'on'
        )
        
        if 'image' in request.files:
            image_url = save_upload_file(request.files['image'])
            if image_url:
                product.image_url = image_url
        
        db.session.add(product)
        db.session.commit()
        cache.clear()
        flash('Product added successfully', 'success')
        
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html', product=None)

@app.route('/admin/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_product_edit(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        price_zar = request.form.get('price_zar')
        price_usd = request.form.get('price_usd')
        
        # Validate pricing
        is_valid, error_msg = pricing_service.validate_pricing_data(
            price_zar, price_usd
        )
        if not is_valid:
            flash(f'Pricing Error: {error_msg}', 'danger')
            return render_template('admin/product_form.html',
                                 product=product)
        
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.category = request.form.get('category')
        product.specifications = request.form.get('specifications')
        product.price_zar = price_zar or None
        product.price_usd = price_usd or None
        product.unit = request.form.get('unit')
        product.order_position = request.form.get('order_position', 0)
        product.is_active = request.form.get('is_active') == 'on'
        
        if 'image' in request.files:
            image_url = save_upload_file(request.files['image'])
            if image_url:
                product.image_url = image_url
        
        db.session.commit()
        cache.clear()
        flash('Product updated successfully', 'success')
        
        return redirect(url_for('admin_products'))
    
    return render_template('admin/product_form.html', product=product)

@app.route('/admin/products/<int:id>/delete', methods=['POST'])
@login_required
def admin_product_delete(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    cache.clear()
    flash('Product deleted successfully', 'success')
    
    return redirect(url_for('admin_products'))

@app.route('/admin/hero-sections')
@login_required
def admin_hero_sections():
    hero_sections = HeroSection.query.order_by(HeroSection.order_position).all()
    return render_template('admin/hero_sections.html', hero_sections=hero_sections)

@app.route('/admin/hero-sections/add', methods=['GET', 'POST'])
@login_required
def admin_hero_section_add():
    if request.method == 'POST':
        hero = HeroSection(
            title=request.form.get('title'),
            subtitle=request.form.get('subtitle'),
            description=request.form.get('description'),
            cta_text=request.form.get('cta_text'),
            cta_link=request.form.get('cta_link'),
            order_position=request.form.get('order_position', 0),
            is_active=request.form.get('is_active') == 'on'
        )
        
        if 'background_image' in request.files:
            file = request.files['background_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                hero.background_image = f'/static/uploads/{filename}'
        
        db.session.add(hero)
        db.session.commit()
        cache.clear()
        flash('Hero section added successfully', 'success')
        
        return redirect(url_for('admin_hero_sections'))
    
    return render_template('admin/hero_form.html', hero=None)

@app.route('/admin/hero-sections/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def admin_hero_section_edit(id):
    hero = HeroSection.query.get_or_404(id)
    
    if request.method == 'POST':
        hero.title = request.form.get('title')
        hero.subtitle = request.form.get('subtitle')
        hero.description = request.form.get('description')
        hero.cta_text = request.form.get('cta_text')
        hero.cta_link = request.form.get('cta_link')
        hero.order_position = request.form.get('order_position', 0)
        hero.is_active = request.form.get('is_active') == 'on'
        
        if 'background_image' in request.files:
            file = request.files['background_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                hero.background_image = f'/static/uploads/{filename}'
        
        db.session.commit()
        cache.clear()
        flash('Hero section updated successfully', 'success')
        
        return redirect(url_for('admin_hero_sections'))
    
    return render_template('admin/hero_form.html', hero=hero)

@app.route('/admin/hero-sections/<int:id>/delete', methods=['POST'])
@login_required
def admin_hero_section_delete(id):
    hero = HeroSection.query.get_or_404(id)
    db.session.delete(hero)
    db.session.commit()
    cache.clear()
    flash('Hero section deleted successfully', 'success')
    
    return redirect(url_for('admin_hero_sections'))

@app.route('/admin/payment-methods')
@login_required
def admin_payment_methods():
    payment_methods = PaymentMethod.query.order_by(PaymentMethod.order_position).all()
    return render_template('admin/payment_methods.html', payment_methods=payment_methods)

@app.route('/admin/payment-terms')
@login_required
def admin_payment_terms():
    payment_terms = PaymentTerm.query.order_by(PaymentTerm.order_position).all()
    return render_template('admin/payment_terms.html', payment_terms=payment_terms)

@app.route('/admin/contacts')
@login_required
def admin_contacts():
    contacts = ContactSubmission.query.order_by(ContactSubmission.created_at.desc()).all()
    return render_template('admin/contacts.html', contacts=contacts)

@app.route('/admin/transactions')
@login_required
def admin_transactions():
    page = request.args.get('page', 1, type=int)
    
    # Query transactions with customer and order info
    transactions_query = db.session.query(
        Transaction,
        Order,
        Customer
    ).join(
        Order, Transaction.order_id == Order.id
    ).join(
        Customer, Order.customer_id == Customer.id
    ).order_by(Transaction.created_at.desc())
    
    # Paginate the results
    transactions = transactions_query.paginate(page=page, per_page=10, error_out=False)
    
    # Transform results to include customer info using a wrapper class
    class TransactionWithCustomer:
        def __init__(self, tx, order, customer, invoice):
            self.id = tx.id
            self.payment_reference = tx.payment_reference
            self.amount = tx.amount
            self.currency = tx.currency
            self.payment_method = tx.payment_method
            self.status = tx.status
            self.created_at = tx.created_at
            self.customer_name = f"{customer.first_name} {customer.last_name}"
            self.customer_email = customer.email
            self.customer_phone = customer.phone
            self.order_number = order.order_number
            self.invoice_number = invoice.invoice_number if invoice else 'N/A'
            self.material_type = 'N/A'  # Can be derived from order items if needed
    
    enriched_items = []
    for tx, order, customer in transactions.items:
        # Check if there's an invoice for this order
        invoice = Invoice.query.filter_by(order_id=order.id).first()
        enriched_items.append(TransactionWithCustomer(tx, order, customer, invoice))
    
    # Replace the items with enriched transactions
    transactions.items = enriched_items
    
    return render_template('admin/transactions.html', transactions=transactions)

@app.route('/admin/transactions/<int:transaction_id>')
@login_required
def admin_transaction_detail(transaction_id):
    # Query transaction with customer and order info
    result = db.session.query(
        Transaction,
        Order,
        Customer
    ).join(
        Order, Transaction.order_id == Order.id
    ).join(
        Customer, Order.customer_id == Customer.id
    ).filter(Transaction.id == transaction_id).first()
    
    if not result:
        flash('Transaction not found', 'error')
        return redirect(url_for('admin_transactions'))
    
    transaction, order, customer = result
    
    # Check if there's an invoice for this order
    invoice = Invoice.query.filter_by(order_id=order.id).first()
    
    return render_template('admin/transaction_detail.html',
                         transaction=transaction,
                         order=order,
                         customer=customer,
                         invoice=invoice)

@app.route('/admin/menu')
@login_required
def admin_menu():
    menu_items = MenuItem.query.filter_by(parent_id=None).order_by(MenuItem.order_position).all()
    return render_template('admin/menu.html', menu_items=menu_items)

@app.route('/admin/testimonials')
@login_required
def admin_testimonials():
    testimonials = Testimonial.query.order_by(
        Testimonial.order_position
    ).all()
    return render_template('admin/testimonials.html',
                          testimonials=testimonials)


@app.route('/admin/testimonials/add', methods=['GET', 'POST'])
@login_required
def admin_testimonial_add():
    if request.method == 'POST':
        file = request.files.get('avatar')
        avatar_url = None

        if file and allowed_file(file.filename):
            avatar_url = save_upload_file(file)

        testimonial = Testimonial(
            client_name=request.form.get('client_name'),
            company=request.form.get('company'),
            position=request.form.get('position'),
            content=request.form.get('content'),
            rating=int(request.form.get('rating', 5)),
            avatar_url=avatar_url,
            is_active=request.form.get('is_active') == 'on',
            order_position=int(
                request.form.get('order_position', 0)
            )
        )

        db.session.add(testimonial)
        db.session.commit()

        return redirect(url_for('admin_testimonials'))

    return render_template('admin/testimonial_form.html', testimonial=None)


@app.route('/admin/testimonials/<int:id>/edit',
           methods=['GET', 'POST'])
@login_required
def admin_testimonial_edit(id):
    testimonial = Testimonial.query.get_or_404(id)

    if request.method == 'POST':
        file = request.files.get('avatar')
        if file and allowed_file(file.filename):
            testimonial.avatar_url = save_upload_file(file)

        testimonial.client_name = (
            request.form.get('client_name')
        )
        testimonial.company = request.form.get('company')
        testimonial.position = request.form.get('position')
        testimonial.content = request.form.get('content')
        testimonial.rating = int(
            request.form.get('rating', 5)
        )
        testimonial.is_active = (
            request.form.get('is_active') == 'on'
        )
        testimonial.order_position = int(
            request.form.get('order_position', 0)
        )

        db.session.commit()

        return redirect(url_for('admin_testimonials'))

    return render_template('admin/testimonial_form.html',
                          testimonial=testimonial)


@app.route('/admin/testimonials/<int:id>/delete', methods=['POST'])
@login_required
def admin_testimonial_delete(id):
    testimonial = Testimonial.query.get_or_404(id)
    db.session.delete(testimonial)
    db.session.commit()

    return redirect(url_for('admin_testimonials'))


# =====================================================
# CUSTOMER AUTHENTICATION ROUTES
# =====================================================

@app.route('/customer/register', methods=['GET', 'POST'])
@limiter.limit("5 per hour")
def customer_register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        # Validation
        if not email or not password:
            flash('Email and password are required', 'danger')
            return redirect(url_for('customer_register'))

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('customer_register'))

        # Validate email exists (DNS MX record check)
        from email_validator import validate_email_for_registration
        is_valid, error_msg = validate_email_for_registration(email)
        if not is_valid:
            flash(f'Invalid email: {error_msg}', 'danger')
            return redirect(url_for('customer_register'))

        # Validate password strength
        is_strong, password_error = validate_password_strength(password)
        if not is_strong:
            flash(password_error, 'danger')
            return redirect(url_for('customer_register'))

        # Check if customer exists
        existing = Customer.query.filter_by(email=email).first()
        if existing:
            flash('Email already registered', 'danger')
            return redirect(url_for('customer_register'))

        # Create new customer
        customer = Customer(
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        customer.set_password(password)

        db.session.add(customer)
        db.session.commit()

        flash(
            'Account created! Please login to continue.',
            'success'
        )
        return redirect(url_for('customer_login'))

    menu_items = MenuItem.query.filter_by(
        is_active=True, parent_id=None
    ).order_by(MenuItem.order_position).all()
    company_info = CompanyInfo.query.first()

    return render_template('customer/register.html',
                         menu_items=menu_items,
                         company_info=company_info)


@app.route('/customer/login', methods=['GET', 'POST'])
@limiter.limit("10 per minute")
def customer_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        customer = Customer.query.filter_by(email=email).first()

        if customer and customer.check_password(password):
            if not customer.is_active:
                flash('Your account has been deactivated', 'danger')
                return redirect(url_for('login'))

            login_user(customer)
            
            # Migrate session cart to database cart
            if 'cart' in session and session['cart']:
                cart = Cart.query.filter_by(
                    customer_id=customer.id, is_active=True
                ).first()
                
                if not cart:
                    cart = Cart(customer_id=customer.id)
                    db.session.add(cart)
                    db.session.flush()
                
                # Add session cart items to database cart
                for item in session['cart']:
                    product = db.session.get(Product, item['product_id'])
                    if product:
                        # Check if product already in cart
                        cart_item = CartItem.query.filter_by(
                            cart_id=cart.id, product_id=item['product_id']
                        ).first()
                        
                        if cart_item:
                            cart_item.quantity += item['quantity']
                        else:
                            cart_item = CartItem(
                                cart_id=cart.id,
                                product_id=item['product_id'],
                                quantity=item['quantity'],
                                price_at_add=product.price
                            )
                            db.session.add(cart_item)
                
                db.session.commit()
                # Store count before clearing
                cart_count = len(session.get('cart', []))
                # Clear session cart
                session.pop('cart', None)
                if cart_count > 0:
                    flash(f'Welcome back! Your cart has been updated with {cart_count} items.', 'success')
            
            next_page = request.args.get('next')
            
            # Check if user came from trying to add to cart
            if next_page:
                # Validate next_page to prevent open redirect
                if next_page.startswith('/') and not next_page.startswith('//'):
                    flash('You can now add products to your cart!', 'success')
                    return redirect(next_page)
            
            # Default redirect - if they were trying to access cart, send to products
            # Otherwise send to dashboard
            if next_page and 'cart' in next_page.lower():
                flash('Welcome back! Browse products and add items to your cart.', 'success')
                return redirect(url_for('customer_products'))
            
            return redirect(url_for('customer_dashboard'))

        flash('Invalid email or password', 'danger')
        return redirect(url_for('login'))

    return redirect(url_for('login'))


@app.route('/customer/logout')
@login_required
def customer_logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


@app.route('/customer/dashboard')
@login_required
def customer_dashboard():
    if not isinstance(current_user, Customer):
        flash('Access denied', 'danger')
        return redirect(url_for('index'))

    # Get real statistics from database
    orders = Order.query.filter_by(customer_id=current_user.id).all()
    total_orders = len(orders)
    completed_orders = len([o for o in orders if o.status == 'delivered'])
    pending_orders = len([o for o in orders if o.status in ['pending', 'processing']])
    total_spent = sum(o.total_amount for o in orders)
    
    # Get recent orders
    recent_orders = Order.query.filter_by(
        customer_id=current_user.id
    ).order_by(Order.created_at.desc()).limit(5).all()

    menu_items = MenuItem.query.filter_by(
        is_active=True, parent_id=None
    ).order_by(MenuItem.order_position).all()
    company_info = CompanyInfo.query.first()

    return render_template('customer/dashboard.html',
                         total_orders=total_orders,
                         completed_orders=completed_orders,
                         pending_orders=pending_orders,
                         total_spent=total_spent,
                         recent_orders=recent_orders,
                         menu_items=menu_items,
                         company_info=company_info)


@app.route('/customer/profile', methods=['GET', 'POST'])
@login_required
def customer_profile():
    if not isinstance(current_user, Customer):
        flash('Access denied', 'danger')
        return redirect(url_for('index'))

    if request.method == 'POST':
        current_user.first_name = (
            request.form.get('first_name')
        )
        current_user.last_name = (
            request.form.get('last_name')
        )
        current_user.company = request.form.get('company')
        current_user.phone = request.form.get('phone')
        current_user.address = request.form.get('address')
        current_user.city = request.form.get('city')
        current_user.postal_code = (
            request.form.get('postal_code')
        )
        current_user.country = request.form.get('country')

        db.session.commit()

        flash('Profile updated successfully', 'success')
        return redirect(url_for('customer_profile'))

    menu_items = MenuItem.query.filter_by(
        is_active=True, parent_id=None
    ).order_by(MenuItem.order_position).all()
    company_info = CompanyInfo.query.first()

    return render_template('customer/profile.html',
                         menu_items=menu_items,
                         company_info=company_info)


@app.route('/customer/products')
@login_required
def customer_products():
    """Customer-facing products page with sidebar navigation"""
    if not isinstance(current_user, Customer):
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    products = Product.query.filter_by(is_active=True).order_by(
        Product.order_position
    ).all()
    
    # Get unique categories
    categories = db.session.query(Product.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    
    # Get pricing context for current customer
    pricing_ctx = pricing_service.get_product_list_context(products)
    
    return render_template('customer/products.html',
                         products=products,
                         categories=categories,
                         pricing_context=pricing_ctx)


@app.route('/customer/services')
@login_required
def customer_services():
    """Customer-facing services page with sidebar navigation"""
    if not isinstance(current_user, Customer):
        flash('Access denied', 'danger')
        return redirect(url_for('index'))
    
    services = Service.query.filter_by(is_active=True).order_by(
        Service.order_position
    ).all()
    
    return render_template('customer/services.html', services=services)


# ========== SHOPPING CART ROUTES ==========

@app.route('/cart', methods=['GET'])
@customer_required
def view_cart():
    """Display shopping cart - requires customer login"""
    menu_items = MenuItem.query.filter_by(
        is_active=True
    ).order_by(MenuItem.order_position).all()
    company_info = CompanyInfo.query.first()

    cart = None
    session_cart_items = []
    pricing_ctx = pricing_service.get_customer_pricing_context()
    
    if current_user.is_authenticated and isinstance(current_user, Customer):
        # Get database cart for logged-in customer
        cart = Cart.query.filter_by(
            customer_id=current_user.id, is_active=True
        ).first()
    else:
        # Get session cart for guest users
        if 'cart' in session:
            cart_data = session['cart']
            for item in cart_data:
                product = db.session.get(Product, item['product_id'])
                if product:
                    session_cart_items.append({
                        'product': product,
                        'quantity': item['quantity'],
                        'price': item['price']
                    })

    return render_template('cart.html',
                           cart=cart,
                           session_cart=session_cart_items,
                           pricing_context=pricing_ctx,
                           menu_items=menu_items,
                           company_info=company_info)


@app.route('/api/cart/add', methods=['POST'])
@limiter.limit("30 per minute")
@customer_required
def add_to_cart():
    """Add product to cart via AJAX - requires customer login"""
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = int(data.get('quantity', 1))

    if quantity <= 0:
        return jsonify({
            'success': False, 'message': 'Quantity must be greater than 0'
        }), 400

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({
            'success': False, 'message': 'Product not found'
        }), 404

    # Database cart for logged-in customers
    cart = Cart.query.filter_by(
        customer_id=current_user.id, is_active=True
    ).first()

    if not cart:
        cart = Cart(customer_id=current_user.id)
        db.session.add(cart)
        db.session.commit()

    # Check if product already in cart
    cart_item = CartItem.query.filter_by(
        cart_id=cart.id, product_id=product_id
    ).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
            price_at_add=product.price
        )
        db.session.add(cart_item)

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Product added to cart',
        'cart_count': cart.get_item_count(),
        'subtotal': float(cart.get_subtotal())
    })


@app.route('/api/cart/remove/<int:item_id>',
           methods=['DELETE'])
@login_required
def remove_from_cart(item_id):
    """Remove item from cart"""
    if not isinstance(current_user, Customer):
        return jsonify({
            'success': False, 'message': 'Must be logged in as customer'
        }), 401

    cart_item = db.session.get(CartItem, item_id)
    if not cart_item:
        return jsonify({
            'success': False, 'message': 'Item not found'
        }), 404

    # Verify item belongs to current user's cart
    if cart_item.cart.customer_id != current_user.id:
        return jsonify({
            'success': False, 'message': 'Unauthorized'
        }), 403

    cart_id = cart_item.cart_id
    db.session.delete(cart_item)
    db.session.commit()

    cart = db.session.get(Cart, cart_id)

    return jsonify({
        'success': True,
        'message': 'Item removed from cart',
        'cart_count': cart.get_item_count(),
        'subtotal': float(cart.get_subtotal())
    })


@app.route('/api/cart/update/<int:item_id>',
           methods=['PUT'])
@login_required
def update_cart_quantity(item_id):
    """Update quantity of item in cart"""
    if not isinstance(current_user, Customer):
        return jsonify({
            'success': False, 'message': 'Must be logged in as customer'
        }), 401

    data = request.get_json()
    quantity = int(data.get('quantity', 1))

    cart_item = db.session.get(CartItem, item_id)
    if not cart_item:
        return jsonify({
            'success': False, 'message': 'Item not found'
        }), 404

    # Verify item belongs to current user's cart
    if cart_item.cart.customer_id != current_user.id:
        return jsonify({
            'success': False, 'message': 'Unauthorized'
        }), 403

    if quantity <= 0:
        db.session.delete(cart_item)
        db.session.commit()
        message = 'Item removed from cart'
    else:
        cart_item.quantity = quantity
        db.session.commit()
        message = 'Cart updated'

    cart = cart_item.cart

    return jsonify({
        'success': True,
        'message': message,
        'cart_count': cart.get_item_count(),
        'subtotal': float(cart.get_subtotal())
    })


@app.route('/api/cart/clear', methods=['POST'])
@login_required
def clear_cart():
    """Clear all items from cart"""
    if not isinstance(current_user, Customer):
        return jsonify({
            'success': False, 'message': 'Must be logged in as customer'
        }), 401

    cart = Cart.query.filter_by(
        customer_id=current_user.id, is_active=True
    ).first()

    if cart:
        cart.clear_cart()

    return jsonify({
        'success': True,
        'message': 'Cart cleared',
        'cart_count': 0,
        'subtotal': 0
    })


@app.route('/api/cart/count', methods=['GET'])
@customer_required
def get_cart_count():
    """Get number of items in cart (for navbar) - requires customer login"""
    cart_count = 0

    cart = Cart.query.filter_by(
        customer_id=current_user.id, is_active=True
    ).first()
    if cart:
        cart_count = cart.get_item_count()

    return jsonify({'cart_count': cart_count})


# ============ ORDER MANAGEMENT ROUTES ============

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """Convert cart to order and process checkout"""
    if not isinstance(current_user, Customer):
        flash('Customers only', 'error')
        return redirect(url_for('index'))

    try:
        # Get active cart
        cart = Cart.query.filter_by(
            customer_id=current_user.id, is_active=True
        ).first()
        
        if not cart or cart.get_item_count() == 0:
            flash('Cart is empty', 'warning')
            return redirect(url_for('view_cart'))

        if request.method == 'POST':
            # Create order from cart
            import uuid
            order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
            
            shipping_address = request.form.get('shipping_address', '')
            billing_address = request.form.get('billing_address', '')
            
            subtotal = cart.get_subtotal()
            tax = subtotal * 0.15  # 15% tax
            shipping = 100.0 if subtotal > 0 else 0
            total = subtotal + tax + shipping
            
            # Create order (unpaid)
            order = Order(
                customer_id=current_user.id,
                order_number=order_number,
                status='pending',
                subtotal=subtotal,
                tax_amount=tax,
                shipping_cost=shipping,
                total_amount=total,
                payment_status='unpaid',  # Order starts unpaid
                shipping_address=shipping_address,
                billing_address=billing_address
            )
            db.session.add(order)
            db.session.flush()  # Get order ID
            
            # Convert cart items to order items
            for cart_item in cart.items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product_id,
                    quantity=cart_item.quantity,
                    price_at_purchase=cart_item.price_at_add
                )
                db.session.add(order_item)
            
            # Create invoice for the order
            invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
            due_date = datetime.utcnow() + timedelta(days=30)  # 30 days payment terms
            
            invoice = Invoice(
                customer_id=current_user.id,
                order_id=order.id,
                invoice_number=invoice_number,
                subtotal=subtotal,
                tax_amount=tax,
                total_amount=total,
                status='pending',  # Invoice pending payment
                due_date=due_date
            )
            db.session.add(invoice)
            db.session.flush()  # Get invoice ID
            
            # Add invoice items
            for cart_item in cart.items:
                invoice_item = InvoiceItem(
                    invoice_id=invoice.id,
                    order_id=order.id,
                    description=cart_item.product.name,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.price_at_add,
                    total=cart_item.price_at_add * cart_item.quantity
                )
                db.session.add(invoice_item)
            
            # Mark cart as inactive
            cart.is_active = False
            
            db.session.commit()
            
            # Send order confirmation email
            try:
                email_service = EmailService()
                email_service.send_order_confirmation(
                    current_user.email,
                    order_number,
                    total
                )
            except Exception as e:
                print(f'Email error: {e}')
            
            flash(f'Order {order_number} created! Invoice {invoice_number} generated.', 'success')
            # Redirect to invoice page to proceed with payment
            return redirect(url_for('customer_invoice_detail', invoice_id=invoice.id))
        
        # GET - show checkout form
        cart = Cart.query.filter_by(
            customer_id=current_user.id, is_active=True
        ).first()
        
        if cart:
            menu_items = MenuItem.query.filter_by(
                is_active=True, parent_id=None
            ).order_by(MenuItem.order_position).all()
            company_info = CompanyInfo.query.first()
            
            return render_template(
                'customer/checkout.html',
                cart=cart,
                customer=current_user,
                menu_items=menu_items,
                company_info=company_info
            )
        
        return redirect(url_for('view_cart'))
    
    except Exception as e:
        print(f'Checkout error: {e}')
        flash('Checkout failed', 'error')
        return redirect(url_for('view_cart'))


@app.route('/customer/orders', methods=['GET'])
@login_required
def customer_orders():
    """View customer order history"""
    if not isinstance(current_user, Customer):
        flash('Customers only', 'error')
        return redirect(url_for('index'))
    
    try:
        orders = Order.query.filter_by(
            customer_id=current_user.id
        ).order_by(Order.created_at.desc()).all()
        
        menu_items = MenuItem.query.filter_by(
            is_active=True, parent_id=None
        ).order_by(MenuItem.order_position).all()
        company_info = CompanyInfo.query.first()
        
        return render_template(
            'customer/orders.html',
            orders=orders,
            menu_items=menu_items,
            company_info=company_info
        )
    except Exception as e:
        print(f'Error: {e}')
        flash('Could not load orders', 'error')
        return redirect(url_for('customer_dashboard'))


@app.route('/customer/orders/<int:order_id>', methods=['GET'])
@login_required
def customer_order_detail(order_id):
    """View specific order details"""
    if not isinstance(current_user, Customer):
        flash('Customers only', 'error')
        return redirect(url_for('index'))
    
    try:
        order = Order.query.filter_by(
            id=order_id, customer_id=current_user.id
        ).first()
        
        if not order:
            flash('Order not found', 'error')
            return redirect(url_for('customer_orders'))
        
        menu_items = MenuItem.query.filter_by(
            is_active=True, parent_id=None
        ).order_by(MenuItem.order_position).all()
        company_info = CompanyInfo.query.first()
        
        return render_template(
            'customer/order_detail.html',
            order=order,
            menu_items=menu_items,
            company_info=company_info
        )
    except Exception as e:
        print(f'Error: {e}')
        flash('Could not load order', 'error')
        return redirect(url_for('customer_orders'))


@app.route('/customer/transactions', methods=['GET'])
@login_required
def customer_transactions():
    """View customer transaction history"""
    if not isinstance(current_user, Customer):
        flash('Customers only', 'error')
        return redirect(url_for('index'))
    
    try:
        page = request.args.get('page', 1, type=int)
        
        # Get all transactions for customer's orders
        transactions_query = db.session.query(
            Transaction,
            Order
        ).join(
            Order, Transaction.order_id == Order.id
        ).filter(
            Order.customer_id == current_user.id
        ).order_by(Transaction.created_at.desc())
        
        # Paginate results
        transactions = transactions_query.paginate(page=page, per_page=10, error_out=False)
        
        # Enrich transactions with invoice info
        enriched_items = []
        for transaction, order in transactions.items:
            invoice = Invoice.query.filter_by(order_id=order.id).first()
            
            # Create wrapper object
            class TransactionWithOrder:
                def __init__(self, tx, ord, inv):
                    self.id = tx.id
                    self.payment_reference = tx.payment_reference
                    self.amount = tx.amount
                    self.currency = tx.currency
                    self.payment_method = tx.payment_method
                    self.status = tx.status
                    self.created_at = tx.created_at
                    self.order_number = ord.order_number
                    self.order_id = ord.id
                    self.invoice_number = inv.invoice_number if inv else 'N/A'
                    self.invoice_id = inv.id if inv else None
            
            enriched_items.append(TransactionWithOrder(transaction, order, invoice))
        
        transactions.items = enriched_items
        
        menu_items = MenuItem.query.filter_by(
            is_active=True, parent_id=None
        ).order_by(MenuItem.order_position).all()
        company_info = CompanyInfo.query.first()
        
        return render_template(
            'customer/transactions.html',
            transactions=transactions,
            menu_items=menu_items,
            company_info=company_info
        )
    except Exception as e:
        print(f'Error: {e}')
        flash('Could not load transactions', 'error')
        return redirect(url_for('customer_dashboard'))


@app.route('/customer/transactions/<int:transaction_id>', methods=['GET'])
@login_required
def customer_transaction_detail(transaction_id):
    """View specific transaction details"""
    if not isinstance(current_user, Customer):
        flash('Customers only', 'error')
        return redirect(url_for('index'))
    
    try:
        # Get transaction with order
        result = db.session.query(
            Transaction,
            Order
        ).join(
            Order, Transaction.order_id == Order.id
        ).filter(
            Transaction.id == transaction_id,
            Order.customer_id == current_user.id
        ).first()
        
        if not result:
            flash('Transaction not found', 'error')
            return redirect(url_for('customer_transactions'))
        
        transaction, order = result
        
        # Get invoice if exists
        invoice = Invoice.query.filter_by(order_id=order.id).first()
        
        menu_items = MenuItem.query.filter_by(
            is_active=True, parent_id=None
        ).order_by(MenuItem.order_position).all()
        company_info = CompanyInfo.query.first()
        
        return render_template(
            'customer/transaction_detail.html',
            transaction=transaction,
            order=order,
            invoice=invoice,
            menu_items=menu_items,
            company_info=company_info
        )
    except Exception as e:
        print(f'Error: {e}')
        flash('Could not load transaction', 'error')
        return redirect(url_for('customer_transactions'))


@app.route('/admin/orders', methods=['GET'])
@login_required
def admin_orders():
    """Admin view all orders"""
    if not isinstance(current_user, User):
        flash('Admin access required', 'error')
        return redirect(url_for('index'))
    
    try:
        page = request.args.get('page', 1, type=int)
        status_filter = request.args.get('status', 'all')
        
        query = Order.query
        
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)
        
        orders = query.order_by(
            Order.created_at.desc()
        ).paginate(page=page, per_page=20)
        
        statuses = [
            'pending', 'processing', 'shipped',
            'delivered', 'cancelled'
        ]
        
        return render_template(
            'admin/orders.html',
            orders=orders,
            current_status=status_filter,
            statuses=statuses
        )
    except Exception as e:
        print(f'Error: {e}')
        flash('Could not load orders', 'error')
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/orders/<int:order_id>', methods=['GET', 'POST'])
@login_required
def admin_order_detail(order_id):
    """Admin view and update order"""
    if not isinstance(current_user, User):
        flash('Admin access required', 'error')
        return redirect(url_for('index'))
    
    try:
        order = db.session.get(Order, order_id)
        
        if not order:
            flash('Order not found', 'error')
            return redirect(url_for('admin_orders'))
        
        if request.method == 'POST':
            new_status = request.form.get('status')
            notes = request.form.get('notes', '')
            
            if new_status:
                order.update_status(new_status)
            
            if notes:
                order.notes = notes
                db.session.commit()
            
            flash('Order updated successfully', 'success')
        
        statuses = [
            'pending', 'processing', 'shipped',
            'delivered', 'cancelled'
        ]
        
        return render_template(
            'admin/order_detail.html',
            order=order,
            statuses=statuses
        )
    except Exception as e:
        print(f'Error: {e}')
        flash('Could not load order', 'error')
        return redirect(url_for('admin_orders'))


@app.route('/api/orders/<int:order_id>/status', methods=['PUT'])
@login_required
def api_update_order_status(order_id):
    """API to update order status"""
    if not isinstance(current_user, User):
        return jsonify({'error': 'Admin required'}), 403
    
    try:
        order = db.session.get(Order, order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        data = request.get_json()
        new_status = data.get('status')
        
        if order.update_status(new_status):
            return jsonify({
                'success': True,
                'status': order.status
            })
        else:
            return jsonify({'error': 'Invalid status'}), 400
    
    except Exception as e:
        print(f'Error: {e}')
        return jsonify({'error': 'Update failed'}), 500


@app.route('/api/customers/<int:customer_id>/orders', methods=['GET'])
@login_required
def api_get_customer_orders(customer_id):
    """API to get customer orders for invoice creation"""
    if not isinstance(current_user, User):
        return jsonify({'error': 'Admin required'}), 403
    
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        # Get all orders for this customer
        orders = Order.query.filter_by(customer_id=customer_id).order_by(Order.created_at.desc()).all()
        
        orders_data = []
        total_order_value = 0
        
        for order in orders:
            # Check if order already has an invoice
            has_invoice = len(order.invoices) > 0
            
            orders_data.append({
                'id': order.id,
                'order_number': order.order_number,
                'status': order.status,
                'total_amount': float(order.total_amount),
                'subtotal': float(order.subtotal),
                'tax_amount': float(order.tax_amount),
                'item_count': len(order.items),
                'created_at': order.created_at.strftime('%Y-%m-%d'),
                'has_invoice': has_invoice,
                'payment_status': order.payment_status
            })
            
            total_order_value += float(order.total_amount)
        
        return jsonify({
            'customer': {
                'id': customer.id,
                'name': customer.get_full_name(),
                'email': customer.email,
                'company': customer.company or '',
            },
            'orders': orders_data,
            'total_orders': len(orders),
            'total_order_value': total_order_value
        })
    
    except Exception as e:
        app.logger.error(f"Error fetching customer orders: {str(e)}")
        return jsonify({'error': 'Failed to fetch orders'}), 500


def stripe_payment():
    data = request.get_json()
    
    stripe_payment = StripePayment()
    result = stripe_payment.create_checkout_session(
        amount=float(data.get('amount')),
        currency=data.get('currency', 'ZAR'),
        customer_email=data.get('email'),
        invoice_number=data.get('invoice_number'),
        material_type=data.get('material_type')
    )
    
    return jsonify(result)

@app.route('/api/payment/payfast', methods=['POST'])
def payfast_payment():
    data = request.get_json()
    
    payfast_payment = PayFastPayment()
    result = payfast_payment.create_payment(
        amount=float(data.get('amount')),
        customer_name=data.get('name'),
        customer_email=data.get('email'),
        customer_phone=data.get('phone'),
        invoice_number=data.get('invoice_number'),
        material_type=data.get('material_type')
    )
    
    return jsonify(result)


def send_payment_confirmation_email(transaction):
    """Send payment confirmation emails to customer and admin."""
    if not app.config.get('SEND_EMAILS') or not transaction:
        return

    try:
        company = CompanyInfo.query.first()
        company_name = (
            company.company_name if company
            else '360Degree Supply'
        )
        company_email = (
            company.email if company
            else 'info@360degreesupply.co.za'
        )
        company_phone = (
            company.phone if company
            else '+27 64 902 4363'
        )

        # Send confirmation to customer
        if transaction.customer_email:
            email_service.send_payment_confirmation(
                recipient_email=transaction.customer_email,
                recipient_name=(
                    transaction.customer_name or 'Valued Customer'
                ),
                transaction_id=transaction.transaction_id,
                amount=str(transaction.amount),
                currency=transaction.currency or 'ZAR',
                payment_method=(
                    transaction.payment_method or 'Unknown'
                ),
                company_name=company_name,
                company_email=company_email,
                company_phone=company_phone
            )

        # Send notification to admin
        admin_email = app.config.get(
            'ADMIN_EMAIL',
            'admin@360degreesupply.co.za'
        )
        email_service.send_payment_notification(
            admin_email=admin_email,
            customer_name=(
                transaction.customer_name or 'Unknown'
            ),
            customer_email=(
                transaction.customer_email or 'N/A'
            ),
            transaction_id=transaction.transaction_id,
            amount=str(transaction.amount),
            currency=transaction.currency or 'ZAR',
            payment_method=(
                transaction.payment_method or 'Unknown'
            ),
            company_name=company_name
        )

    except Exception as e:
        app.logger.error(
            f"Error sending payment confirmation email: {str(e)}"
        )


@app.route('/webhook/stripe', methods=['POST'])
@csrf.exempt
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    stripe_payment = StripePayment()
    result = stripe_payment.verify_webhook(payload, sig_header)

    # Send payment confirmation if successful
    if result.get('success'):
        try:
            # Parse the payload to get transaction info
            event_data = json.loads(payload)
            if (event_data.get('type') ==
                    'checkout.session.completed'):
                sess = event_data.get('data', {}).get('object', {})
                transaction = Transaction.query.filter_by(
                    gateway_response=sess.get('id')
                ).first()
                if transaction:
                    send_payment_confirmation_email(transaction)
        except Exception as e:
            app.logger.error(
                f"Error sending Stripe confirmation: {str(e)}"
            )

    return jsonify(result)


@app.route('/webhook/payfast', methods=['POST'])
@csrf.exempt
def payfast_webhook():
    post_data = request.form.to_dict()
    
    payfast_payment = PayFastPayment()
    result = payfast_payment.verify_webhook(post_data)
    
    return jsonify(result)


# ==================== INVOICE ROUTES ====================

# Customer Invoice Routes
@app.route('/customer/invoices', methods=['GET'])
@login_required
def customer_invoices():
    """View all customer invoices"""
    if not isinstance(current_user, Customer):
        flash('Customers only', 'error')
        return redirect(url_for('index'))
    
    try:
        invoices = Invoice.query.filter_by(
            customer_id=current_user.id
        ).order_by(Invoice.issue_date.desc()).all()
        
        menu_items = MenuItem.query.filter_by(
            is_active=True, parent_id=None
        ).order_by(MenuItem.order_position).all()
        company_info = CompanyInfo.query.first()
        
        return render_template(
            'customer/invoices.html',
            invoices=invoices,
            menu_items=menu_items,
            company_info=company_info
        )
    except Exception as e:
        app.logger.error(f"Error fetching customer invoices: {str(e)}")
        flash('Error loading invoices', 'danger')
        return redirect(url_for('customer_dashboard'))


@app.route('/customer/invoices/<int:invoice_id>', methods=['GET'])
@login_required
def customer_invoice_detail(invoice_id):
    """View invoice details"""
    if not isinstance(current_user, Customer):
        flash('Customers only', 'error')
        return redirect(url_for('index'))
    
    try:
        invoice = Invoice.query.filter_by(
            id=invoice_id, customer_id=current_user.id
        ).first()
        
        if not invoice:
            flash('Invoice not found', 'error')
            return redirect(url_for('customer_invoices'))
        
        menu_items = MenuItem.query.filter_by(
            is_active=True, parent_id=None
        ).order_by(MenuItem.order_position).all()
        company_info = CompanyInfo.query.first()
        
        return render_template(
            'customer/invoice_detail.html',
            invoice=invoice,
            menu_items=menu_items,
            company_info=company_info
        )
    except Exception as e:
        app.logger.error(f"Error fetching invoice: {str(e)}")
        flash('Error loading invoice', 'danger')
        return redirect(url_for('customer_invoices'))


@app.route('/customer/invoices/<int:invoice_id>/pay', methods=['GET', 'POST'])
@login_required
def customer_pay_invoice(invoice_id):
    """Pay an invoice"""
    if not isinstance(current_user, Customer):
        flash('Customers only', 'error')
        return redirect(url_for('index'))
    
    try:
        invoice = Invoice.query.filter_by(
            id=invoice_id, customer_id=current_user.id
        ).first()
        
        if not invoice:
            flash('Invoice not found', 'error')
            return redirect(url_for('customer_invoices'))
        
        # Check if invoice is already paid
        if invoice.remaining_balance() <= 0:
            flash('This invoice has already been paid', 'info')
            return redirect(url_for('customer_invoice_detail', invoice_id=invoice_id))
        
        if request.method == 'POST':
            payment_method = request.form.get('payment_method', 'card')
            
            try:
                # Handle EFT/Bank Transfer with Proof of Payment
                if payment_method == 'eft' or payment_method == 'bank_transfer':
                    return handle_eft_payment(invoice, request)
                
                # Handle other payment methods (card, etc.)
                # Calculate payment amount BEFORE updating invoice
                payment_amount = invoice.remaining_balance()
                
                # Create invoice payment record
                payment = InvoicePayment(
                    invoice_id=invoice.id,
                    amount=payment_amount,
                    payment_method=payment_method,
                    payment_date=datetime.utcnow()
                )
                
                # Update invoice
                invoice.paid_amount = float(invoice.paid_amount or 0) + float(payment_amount)
                if invoice.paid_amount >= float(invoice.total_amount):
                    invoice.status = 'paid'
                else:
                    invoice.status = 'partial'
                
                # Update linked order if exists
                if invoice.order_id:
                    order = Order.query.get(invoice.order_id)
                    if order:
                        # Update order payment status
                        if invoice.status == 'paid':
                            order.payment_status = 'paid'
                        else:
                            order.payment_status = 'partial'
                        
                        # Create transaction record for the order
                        transaction = Transaction(
                            order_id=order.id,
                            amount=payment_amount,
                            currency='ZAR',
                            payment_method=payment_method,
                            payment_reference=f"{invoice.invoice_number}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                            status='completed',
                            refund_amount=0.00
                        )
                        db.session.add(transaction)
                
                db.session.add(payment)
                db.session.commit()
                
                flash(f'Payment of R{payment_amount:.2f} received successfully!', 'success')
                return redirect(url_for('customer_invoice_detail', invoice_id=invoice_id))
                
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error processing payment: {str(e)}")
                flash('Error processing payment. Please try again.', 'danger')
        
        # GET request - show payment form
        menu_items = MenuItem.query.filter_by(
            is_active=True, parent_id=None
        ).order_by(MenuItem.order_position).all()
        company_info = CompanyInfo.query.first()
        
        return render_template(
            'customer/pay_invoice.html',
            invoice=invoice,
            menu_items=menu_items,
            company_info=company_info
        )
        
    except Exception as e:
        app.logger.error(f"Error in pay invoice: {str(e)}")
        flash('Error loading payment page', 'danger')
        return redirect(url_for('customer_invoices'))


def handle_eft_payment(invoice, request):
    """Handle EFT/Bank Transfer payment with Proof of Payment upload"""
    try:
        # Check if file was uploaded
        if 'proof_of_payment' not in request.files:
            flash('Please upload proof of payment for EFT/Bank Transfer', 'warning')
            return redirect(url_for('customer_pay_invoice', invoice_id=invoice.id))
        
        file = request.files['proof_of_payment']
        
        if file.filename == '':
            flash('No file selected', 'warning')
            return redirect(url_for('customer_pay_invoice', invoice_id=invoice.id))
        
        # Validate file with secure_file_upload
        allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png'}
        max_size_mb = 10  # 10MB limit
        
        is_valid, error_msg, secure_filename = secure_file_upload(
            file, 
            allowed_extensions=allowed_extensions,
            max_size_mb=max_size_mb
        )
        
        if not is_valid:
            flash(f'Upload validation failed: {error_msg}', 'danger')
            return redirect(url_for('customer_pay_invoice', invoice_id=invoice.id))
        
        # Reset file pointer after validation
        file.seek(0)
        
        # Upload to S3 cloud storage using the helper function
        from s3_storage import upload_proof_of_payment
        file_url, error = upload_proof_of_payment(file)
        
        if error:
            flash(f'Upload failed: {error}', 'danger')
            return redirect(url_for('customer_pay_invoice', invoice_id=invoice.id))
        
        # Extract filename from S3 URL for storage
        import uuid
        file_ext = secure_filename.rsplit('.', 1)[1].lower()
        filename = f"pop_{invoice.invoice_number}_{uuid.uuid4().hex[:8]}.{file_ext}"
        
        # Get file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        # Log security event
        log_security_event(
            event_type='proof_of_payment_uploaded',
            user_id=None,
            username=invoice.customer.email if invoice.customer else 'guest',
            details=f'Invoice: {invoice.invoice_number}, File: {filename}, Size: {file_size} bytes',
            ip_address=get_client_ip()
        )
        
        # Create pending payment record
        payment = InvoicePayment(
            invoice_id=invoice.id,
            amount=invoice.remaining_balance(),
            payment_method='eft',
            payment_date=datetime.utcnow(),
            notes='Pending verification - Proof of Payment uploaded'
        )
        db.session.add(payment)
        db.session.flush()  # Get payment ID
        
        # Create ProofOfPayment record with S3 URL
        pop = ProofOfPayment(
            invoice_payment_id=payment.id,
            invoice_id=invoice.id,
            customer_id=current_user.id,
            file_path=file_url,  # Store S3 URL instead of local path
            file_name=filename,
            file_type=file_ext,
            file_size=file_size,
            verification_status='pending'
        )
        db.session.add(pop)
        db.session.flush()  # Get POP ID
        
        # Process document with OCR
        try:
            ocr_service = OCRService()
            result = ocr_service.process_document(file_path, file_ext)
            
            if result.get('success'):
                # Store extracted data
                pop.extracted_amount = result.get('amount')
                pop.extracted_reference = result.get('reference')
                pop.extracted_date = result.get('date')
                pop.extracted_payer_name = result.get('payer_name')
                pop.extracted_payer_account = result.get('payer_account')
                pop.extracted_bank_name = result.get('bank_name')
                pop.ocr_confidence = result.get('confidence', 0.0)
                pop.ocr_raw_text = result.get('raw_text', '')
                pop.processed_at = datetime.utcnow()
                
                # Validate amount
                if pop.extracted_amount:
                    validation = ocr_service.validate_payment(
                        pop.extracted_amount,
                        float(invoice.total_amount)
                    )
                    
                    pop.amount_matched = validation['matched']
                    pop.verification_status = validation['status']
                    pop.verification_notes = validation['reason']
                    
                    # Auto-verify if amount matches and confidence is high
                    if validation['matched'] and pop.ocr_confidence >= 0.75:
                        pop.verification_status = 'verified'
                        pop.verified_at = datetime.utcnow()
                        
                        # Update invoice
                        invoice.paid_amount = float(invoice.paid_amount or 0) + float(payment.amount)
                        if invoice.paid_amount >= float(invoice.total_amount):
                            invoice.status = 'paid'
                        else:
                            invoice.status = 'partial'
                        
                        # Update order if linked
                        if invoice.order_id:
                            order = Order.query.get(invoice.order_id)
                            if order:
                                order.payment_status = 'paid' if invoice.status == 'paid' else 'partial'
                        
                        flash(f'Payment verified! Amount: R{pop.extracted_amount:.2f}', 'success')
                    else:
                        pop.verification_status = 'manual_review'
                        invoice.status = 'pending_verification'
                        flash('Proof of payment uploaded successfully. Payment is pending verification.', 'info')
                else:
                    pop.verification_status = 'manual_review'
                    pop.verification_notes = 'Could not extract payment amount'
                    invoice.status = 'pending_verification'
                    flash('Proof of payment uploaded. Manual verification required.', 'warning')
            else:
                pop.verification_status = 'manual_review'
                pop.verification_notes = f'OCR Error: {result.get("error", "Unknown error")}'
                invoice.status = 'pending_verification'
                flash('Proof of payment uploaded. Manual verification required.', 'warning')
        
        except Exception as ocr_error:
            app.logger.error(f"OCR processing error: {str(ocr_error)}")
            pop.verification_status = 'manual_review'
            pop.verification_notes = f'OCR processing failed: {str(ocr_error)}'
            invoice.status = 'pending_verification'
            flash('Proof of payment uploaded. Manual verification required.', 'warning')
        
        db.session.commit()
        
        return redirect(url_for('customer_invoice_detail', invoice_id=invoice.id))
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error handling EFT payment: {str(e)}")
        flash(f'Error processing proof of payment: {str(e)}', 'danger')
        return redirect(url_for('customer_pay_invoice', invoice_id=invoice.id))


# Admin Invoice Routes
@app.route('/admin/invoices/create', methods=['GET', 'POST'])
@login_required
def admin_create_invoice():
    """Create new invoice with customer order selection"""
    if not isinstance(current_user, User):
        flash('Admin only', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            customer_id = request.form.get('customer_id')
            selected_order_ids = request.form.getlist('order_ids[]')
            due_days = int(request.form.get('due_days', 30))
            notes = request.form.get('notes', '')
            terms = request.form.get('terms', '')
            
            if not customer_id:
                flash('Please select a customer', 'error')
                return redirect(url_for('admin_create_invoice'))
            
            # Generate invoice number
            import uuid
            invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"
            
            # Calculate dates
            issue_date = datetime.datetime.utcnow()
            from datetime import timedelta
            due_date = issue_date + timedelta(days=due_days)
            
            # Initialize totals
            subtotal = 0
            tax_amount = 0
            
            # Create invoice
            invoice = Invoice(
                invoice_number=invoice_number,
                customer_id=customer_id,
                issue_date=issue_date,
                due_date=due_date,
                subtotal=0,
                tax_amount=0,
                total_amount=0,
                status='draft',
                notes=notes,
                terms=terms
            )
            db.session.add(invoice)
            db.session.flush()  # Get invoice ID
            
            # Add selected orders as invoice items
            if selected_order_ids:
                for order_id in selected_order_ids:
                    order = Order.query.get(order_id)
                    if order and order.customer_id == int(customer_id):
                        # Create invoice item for each order
                        invoice_item = InvoiceItem(
                            invoice_id=invoice.id,
                            order_id=order.id,
                            description=f"Order {order.order_number} ({len(order.items)} items)",
                            quantity=1,
                            unit_price=order.total_amount,
                            total=order.total_amount
                        )
                        db.session.add(invoice_item)
                        
                        subtotal += float(order.subtotal)
                        tax_amount += float(order.tax_amount)
            
            # Calculate totals
            total_amount = subtotal + tax_amount
            
            # Update invoice with totals
            invoice.subtotal = subtotal
            invoice.tax_amount = tax_amount
            invoice.total_amount = total_amount
            
            db.session.commit()
            
            flash(f'Invoice {invoice_number} created successfully!', 'success')
            return redirect(url_for('admin_invoice_detail', invoice_id=invoice.id))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating invoice: {str(e)}")
            flash(f'Error creating invoice: {str(e)}', 'error')
            return redirect(url_for('admin_create_invoice'))
    
    # GET - show form
    try:
        # Get all customers with orders
        customers = Customer.query.order_by(Customer.first_name, Customer.last_name).all()
        
        return render_template(
            'admin/invoice_create.html',
            customers=customers
        )
    except Exception as e:
        app.logger.error(f"Error loading invoice creation form: {str(e)}")
        flash('Error loading form', 'danger')
        return redirect(url_for('admin_invoices'))


@app.route('/admin/invoices', methods=['GET'])
@login_required
def admin_invoices():
    """View all invoices (admin)"""
    if not isinstance(current_user, User):
        flash('Admin only', 'error')
        return redirect(url_for('login'))
    
    try:
        invoices = Invoice.query.order_by(Invoice.issue_date.desc()).all()
        
        # Calculate summary stats
        total_invoices = len(invoices)
        total_amount = sum(float(inv.total_amount) for inv in invoices)
        total_paid = sum(float(inv.paid_amount) for inv in invoices)
        outstanding = total_amount - total_paid
        
        return render_template(
            'admin/invoices.html',
            invoices=invoices,
            total_invoices=total_invoices,
            total_amount=total_amount,
            total_paid=total_paid,
            outstanding=outstanding
        )
    except Exception as e:
        app.logger.error(f"Error fetching invoices: {str(e)}")
        flash('Error loading invoices', 'danger')
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/invoices/<int:invoice_id>', methods=['GET'])
@login_required
def admin_invoice_detail(invoice_id):
    """View invoice details (admin)"""
    if not isinstance(current_user, User):
        flash('Admin only', 'error')
        return redirect(url_for('login'))
    
    try:
        invoice = Invoice.query.get(invoice_id)
        
        if not invoice:
            flash('Invoice not found', 'error')
            return redirect(url_for('admin_invoices'))
        
        return render_template(
            'admin/invoice_detail.html',
            invoice=invoice
        )
    except Exception as e:
        app.logger.error(f"Error fetching invoice: {str(e)}")
        flash('Error loading invoice', 'danger')
        return redirect(url_for('admin_invoices'))


@app.route('/admin/invoices/<int:invoice_id>/edit', methods=['GET', 'POST'])
@login_required
def admin_invoice_edit(invoice_id):
    """Edit invoice (admin)"""
    if not isinstance(current_user, User):
        flash('Admin only', 'error')
        return redirect(url_for('login'))
    
    try:
        invoice = Invoice.query.get(invoice_id)
        
        if not invoice:
            flash('Invoice not found', 'error')
            return redirect(url_for('admin_invoices'))
        
        if request.method == 'POST':
            invoice.due_date = datetime.datetime.strptime(
                request.form.get('due_date'), '%Y-%m-%d'
            )
            invoice.status = request.form.get('status')
            invoice.notes = request.form.get('notes')
            invoice.terms = request.form.get('terms')
            
            db.session.commit()
            flash('Invoice updated successfully', 'success')
            return redirect(url_for('admin_invoice_detail', invoice_id=invoice.id))
        
        return render_template(
            'admin/invoice_edit.html',
            invoice=invoice
        )
    except Exception as e:
        app.logger.error(f"Error updating invoice: {str(e)}")
        flash('Error updating invoice', 'danger')
        return redirect(url_for('admin_invoices'))


@app.route('/admin/invoices/new', methods=['GET', 'POST'])
@login_required
def admin_invoice_create():
    """Redirect to new invoice creation system"""
    return redirect(url_for('admin_create_invoice'))


@app.route('/payment/success')
def payment_success():
    company_info = CompanyInfo.query.first()
    menu_items = MenuItem.query.filter_by(is_active=True, parent_id=None).order_by(MenuItem.order_position).all()
    
    return render_template('payment_success.html', 
                         company_info=company_info,
                         menu_items=menu_items)

@app.route('/payment/cancel')
def payment_cancel():
    company_info = CompanyInfo.query.first()
    menu_items = MenuItem.query.filter_by(is_active=True, parent_id=None).order_by(MenuItem.order_position).all()
    
    return render_template('payment_cancel.html', 
                         company_info=company_info,
                         menu_items=menu_items)

@app.cli.command()
def init_db():
    """Initialize the database with default data"""
    db.create_all()
    
    admin = User.query.filter_by(email='admin@360degreesupply.co.za').first()
    if not admin:
        admin = User(email='admin@360degreesupply.co.za', is_admin=True)
        admin.set_password('admin123')
        db.session.add(admin)
    
    company_info = CompanyInfo.query.first()
    if not company_info:
        company_info = CompanyInfo(
            company_name='360Degree Supply (Pty) Ltd',
            address='Ei Ridge Office Park, 100 Elizabeth Road, Impala Park, Boksburg, 1459, Gauteng, South Africa',
            phone='+27 64 902 4363 / +27 71 181 4799',
            email='info@360degreesupply.co.za',
            description='360Degree Supply (Pty) Ltd is a South African–based bulk fuel and mineral supply company established in 2020 to provide reliable, end-to-end supply solutions to the mining, transport, agriculture, and industrial sectors.',
            mission='To be a trusted supply partner, providing certainty, transparency, and efficiency in every transaction.',
            established_year='2020'
        )
        db.session.add(company_info)
    
    db.session.commit()
    print('Database initialized successfully!')

# Register monitoring blueprint
from monitoring import monitoring_bp
app.register_blueprint(monitoring_bp)
app.logger.info("✅ Monitoring endpoints registered: /health, /metrics, /status")

# Periodic cleanup of security data
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(func=cleanup_old_data, trigger="interval", hours=1)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

app.logger.info("✅ Security cleanup scheduler started")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)



