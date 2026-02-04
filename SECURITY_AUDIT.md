# 🔒 PRODUCTION SECURITY AUDIT & HARDENING GUIDE
## 360 Degree Supply - Full Security Assessment

---

## ⚠️ CRITICAL VULNERABILITIES (Fix Immediately)

### 1. **NO CSRF PROTECTION** 🚨 SEVERITY: CRITICAL
**Current State:** NO CSRF tokens on any forms
**Risk:** Attackers can forge requests from authenticated users
**Impact:** Account takeover, unauthorized transactions, data manipulation

**Fix Required:**
```bash
pip install Flask-WTF
```

```python
# In app.py
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Or set to 3600 for 1 hour
app.config['WTF_CSRF_SSL_STRICT'] = True  # Enforce HTTPS
```

**Add to all forms:**
```html
<form method="POST">
    {{ csrf_token() }}
    <!-- form fields -->
</form>
```

**AJAX requests:**
```javascript
fetch('/api/cart/add', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
    },
    body: JSON.stringify(data)
})
```

---

### 2. **WEAK SECRET KEY** 🚨 SEVERITY: CRITICAL
**Current State:** `SECRET_KEY = 'dev-secret-key'` (hardcoded fallback)
**Risk:** Session hijacking, cookie forgery, authentication bypass

**Fix Required:**
```python
# Generate strong secret key
import secrets
print(secrets.token_hex(32))
```

**In .env:**
```env
SECRET_KEY=<64-character-hex-string-generated-above>
```

**Validation in config.py:**
```python
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    if not SECRET_KEY or SECRET_KEY == 'dev-secret-key':
        raise ValueError("SECRET_KEY must be set in environment variables!")
```

---

### 3. **NO RATE LIMITING** 🚨 SEVERITY: HIGH
**Current State:** No rate limiting on any endpoint
**Risk:** Brute force attacks, DDoS, credential stuffing

**Fix Required:**
```bash
pip install Flask-Limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379"  # Use Railway Redis
)

# Apply to sensitive endpoints
@app.route('/admin/login', methods=['POST'])
@limiter.limit("5 per minute")
def admin_login():
    # ...

@app.route('/customer/login', methods=['POST'])
@limiter.limit("10 per minute")
def customer_login():
    # ...

@app.route('/api/cart/add', methods=['POST'])
@limiter.limit("30 per minute")
def add_to_cart():
    # ...
```

---

### 4. **SQL INJECTION RISKS** 🚨 SEVERITY: HIGH
**Current State:** Some raw queries, no input sanitization on search
**Risk:** Database compromise, data theft

**Issues Found:**
- Contact form accepts unsanitized HTML
- Product search may be vulnerable
- No parameterized queries consistently

**Fix Required:**
```python
# Install and use
pip install bleach

# In app.py
import bleach

@app.route('/api/contact', methods=['POST'])
def contact():
    name = bleach.clean(request.form.get('name', ''))
    email = bleach.clean(request.form.get('email', ''))
    message = bleach.clean(request.form.get('message', ''))
    
    # Always use ORM or parameterized queries
    submission = ContactSubmission(
        name=name,
        email=email,
        message=message
    )
```

---

### 5. **FILE UPLOAD VULNERABILITIES** 🚨 SEVERITY: HIGH
**Current State:** Basic file type checking only
**Risk:** Remote code execution, XSS via SVG, malicious files

**Fix Required:**
```python
import magic  # pip install python-magic-bin (Windows)
from pathlib import Path

ALLOWED_MIME_TYPES = {
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/webp',
    'application/pdf'
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def secure_file_upload(file):
    """Enhanced file upload security"""
    if not file:
        return None, "No file provided"
    
    # 1. Check file size
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset
    
    if size > MAX_FILE_SIZE:
        return None, "File too large (max 5MB)"
    
    # 2. Verify MIME type (don't trust extension)
    mime = magic.from_buffer(file.read(1024), mime=True)
    file.seek(0)
    
    if mime not in ALLOWED_MIME_TYPES:
        return None, f"Invalid file type: {mime}"
    
    # 3. Sanitize filename
    filename = secure_filename(file.filename)
    
    # 4. Generate unique name to prevent overwrite attacks
    ext = Path(filename).suffix
    unique_filename = f"{secrets.token_hex(16)}{ext}"
    
    # 5. Save outside webroot if possible
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    
    # 6. Set restrictive permissions
    file.save(filepath)
    os.chmod(filepath, 0o644)
    
    return unique_filename, None
```

---

### 6. **NO HTTPS ENFORCEMENT** 🚨 SEVERITY: CRITICAL
**Current State:** No HTTPS redirect
**Risk:** Man-in-the-middle attacks, credential theft, session hijacking

**Fix Required:**
```python
from flask_talisman import Talisman

Talisman(app, 
    force_https=True,
    strict_transport_security=True,
    strict_transport_security_max_age=31536000,  # 1 year
    content_security_policy={
        'default-src': "'self'",
        'script-src': [
            "'self'",
            "'unsafe-inline'",  # Consider removing and using nonces
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
        'img-src': ["'self'", 'data:', 'https:'],
        'font-src': ["'self'", 'cdnjs.cloudflare.com']
    }
)
```

---

### 7. **WEAK PASSWORD POLICY** 🚨 SEVERITY: MEDIUM
**Current State:** No password strength requirements
**Risk:** Weak passwords, easy brute force

**Fix Required:**
```python
import re

def validate_password_strength(password):
    """Enforce strong password policy"""
    if len(password) < 12:
        return False, "Password must be at least 12 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain a number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain special character"
    
    # Check against common passwords
    common_passwords = ['password123', 'admin123', '12345678']
    if password.lower() in common_passwords:
        return False, "Password too common"
    
    return True, "Password is strong"

# Add to user registration/password change
@app.route('/customer/register', methods=['POST'])
def customer_register():
    password = request.form.get('password')
    is_valid, message = validate_password_strength(password)
    
    if not is_valid:
        flash(message, 'error')
        return redirect(url_for('customer_register'))
```

---

### 8. **NO SESSION SECURITY** 🚨 SEVERITY: HIGH
**Current State:** Default session settings
**Risk:** Session fixation, session hijacking

**Fix Required:**
```python
# In config.py
class Config:
    # Session Security
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour timeout
    SESSION_COOKIE_NAME = '__Host-session'  # More secure naming
    
    # Remember Me Cookie Security
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 7  # Days
    REMEMBER_COOKIE_NAME = '__Host-remember'
```

---

### 9. **NO INPUT VALIDATION** 🚨 SEVERITY: MEDIUM
**Current State:** Minimal validation on forms
**Risk:** XSS, injection attacks, data corruption

**Fix Required:**
```python
from wtforms import Form, StringField, DecimalField, validators
from wtforms.validators import DataRequired, Email, Length, NumberRange

class ProductForm(Form):
    name = StringField('Name', [
        DataRequired(),
        Length(min=3, max=255)
    ])
    price = DecimalField('Price', [
        DataRequired(),
        NumberRange(min=0.01, max=999999.99)
    ])
    category = StringField('Category', [
        DataRequired(),
        Length(max=100)
    ])

# Use in routes
@app.route('/admin/products/add', methods=['POST'])
@login_required
def add_product():
    form = ProductForm(request.form)
    
    if not form.validate():
        for field, errors in form.errors.items():
            flash(f"{field}: {', '.join(errors)}", 'error')
        return redirect(url_for('add_product'))
    
    # Process validated data
```

---

### 10. **MISSING SECURITY HEADERS** 🚨 SEVERITY: MEDIUM
**Current State:** No security headers
**Risk:** XSS, clickjacking, MIME sniffing attacks

**Fix Required:**
```python
@app.after_request
def set_security_headers(response):
    # Prevent clickjacking
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # Prevent MIME sniffing
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Enable XSS filter
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Referrer policy
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Permissions policy
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    
    return response
```

---

## 🔐 AUTHENTICATION & AUTHORIZATION ISSUES

### 11. **NO TWO-FACTOR AUTHENTICATION** 🚨 SEVERITY: HIGH (for Admin)
**Fix Required:**
```bash
pip install pyotp qrcode
```

```python
import pyotp
import qrcode
from io import BytesIO
import base64

class User(UserMixin, db.Model):
    # ... existing fields ...
    totp_secret = db.Column(db.String(32), nullable=True)
    totp_enabled = db.Column(db.Boolean, default=False)
    
    def generate_totp_secret(self):
        """Generate TOTP secret for 2FA"""
        self.totp_secret = pyotp.random_base32()
        return self.totp_secret
    
    def get_totp_uri(self):
        """Get TOTP URI for QR code"""
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.email,
            issuer_name='360 Degree Supply'
        )
    
    def verify_totp(self, token):
        """Verify TOTP token"""
        if not self.totp_enabled:
            return True  # Skip if not enabled
        
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token, valid_window=1)

# Login route with 2FA
@app.route('/admin/login', methods=['POST'])
@limiter.limit("5 per minute")
def admin_login():
    email = request.form.get('email')
    password = request.form.get('password')
    totp_token = request.form.get('totp_token')
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        if user.totp_enabled:
            if not totp_token or not user.verify_totp(totp_token):
                flash('Invalid 2FA code', 'error')
                return redirect(url_for('admin_login'))
        
        login_user(user)
        return redirect(url_for('admin_dashboard'))
    
    flash('Invalid credentials', 'error')
    return redirect(url_for('admin_login'))
```

---

### 12. **NO ACCOUNT LOCKOUT** 🚨 SEVERITY: HIGH
**Risk:** Unlimited brute force attempts

**Fix Required:**
```python
from datetime import datetime, timedelta

class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)
    attempt_time = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=False)

def check_account_lockout(email, ip_address):
    """Check if account or IP is locked out"""
    # Check last 15 minutes
    cutoff_time = datetime.utcnow() - timedelta(minutes=15)
    
    failed_attempts = LoginAttempt.query.filter(
        LoginAttempt.email == email,
        LoginAttempt.attempt_time > cutoff_time,
        LoginAttempt.success == False
    ).count()
    
    if failed_attempts >= 5:
        return True, "Account locked due to too many failed attempts. Try again in 15 minutes."
    
    return False, None

def log_login_attempt(email, ip_address, success):
    """Log login attempt"""
    attempt = LoginAttempt(
        email=email,
        ip_address=ip_address,
        success=success
    )
    db.session.add(attempt)
    db.session.commit()

@app.route('/admin/login', methods=['POST'])
def admin_login():
    email = request.form.get('email')
    ip_address = request.remote_addr
    
    # Check lockout
    is_locked, message = check_account_lockout(email, ip_address)
    if is_locked:
        flash(message, 'error')
        return redirect(url_for('admin_login'))
    
    user = User.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        log_login_attempt(email, ip_address, True)
        login_user(user)
        return redirect(url_for('admin_dashboard'))
    else:
        log_login_attempt(email, ip_address, False)
        flash('Invalid credentials', 'error')
        return redirect(url_for('admin_login'))
```

---

### 13. **NO AUDIT LOGGING** 🚨 SEVERITY: MEDIUM
**Risk:** Cannot track security incidents or unauthorized access

**Fix Required:**
```python
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_email = db.Column(db.String(120))
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    details = db.Column(db.Text)  # JSON
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

def log_audit(action, resource_type=None, resource_id=None, details=None):
    """Log security-relevant action"""
    log = AuditLog(
        user_id=current_user.id if current_user.is_authenticated else None,
        user_email=current_user.email if current_user.is_authenticated else None,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        details=json.dumps(details) if details else None
    )
    db.session.add(log)
    db.session.commit()

# Use in sensitive operations
@app.route('/admin/products/<int:id>/delete', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    
    log_audit('DELETE_PRODUCT', 'Product', id, {
        'name': product.name,
        'category': product.category
    })
    
    db.session.delete(product)
    db.session.commit()
    
    return redirect(url_for('admin_products'))
```

---

## 💰 PAYMENT SECURITY ISSUES

### 14. **PAYMENT PROCESSING VULNERABILITIES** 🚨 SEVERITY: CRITICAL
**Current Issues:**
- No webhook signature verification
- No amount validation on server
- No idempotency keys

**Fix Required:**
```python
# Stripe webhook security
@app.route('/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, app.config['STRIPE_WEBHOOK_SECRET']
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Process event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        
        # CRITICAL: Validate amount matches order
        order = Order.query.filter_by(
            stripe_payment_intent_id=payment_intent['id']
        ).first()
        
        if not order:
            log_audit('WEBHOOK_ERROR', 'Payment', None, {
                'error': 'Order not found',
                'payment_intent': payment_intent['id']
            })
            return jsonify({'error': 'Order not found'}), 404
        
        expected_amount = int(order.total_amount * 100)  # Convert to cents
        if payment_intent['amount'] != expected_amount:
            log_audit('PAYMENT_FRAUD_ATTEMPT', 'Order', order.id, {
                'expected': expected_amount,
                'received': payment_intent['amount']
            })
            return jsonify({'error': 'Amount mismatch'}), 400
        
        # Update order status
        order.payment_status = 'paid'
        db.session.commit()
    
    return jsonify({'success': True})

# Idempotency for payment creation
@app.route('/api/create-payment-intent', methods=['POST'])
@customer_required
def create_payment_intent():
    order_id = request.json.get('order_id')
    order = Order.query.get_or_404(order_id)
    
    # Check if payment intent already exists
    if order.stripe_payment_intent_id:
        # Retrieve existing intent
        intent = stripe.PaymentIntent.retrieve(
            order.stripe_payment_intent_id
        )
        return jsonify({'clientSecret': intent.client_secret})
    
    # Create new intent with idempotency key
    idempotency_key = f"order_{order.id}_{int(time.time())}"
    
    intent = stripe.PaymentIntent.create(
        amount=int(order.total_amount * 100),
        currency='zar',
        metadata={'order_id': order.id},
        idempotency_key=idempotency_key
    )
    
    order.stripe_payment_intent_id = intent.id
    db.session.commit()
    
    return jsonify({'clientSecret': intent.client_secret})
```

---

## 🗄️ DATABASE SECURITY

### 15. **DATABASE CREDENTIALS IN CODE** 🚨 SEVERITY: CRITICAL
**Fix Required:**
- ✅ Already using environment variables (GOOD)
- Add connection encryption
- Use least privilege database user

```python
# In Railway/Production, set DATABASE_URL with SSL:
# mysql://user:pass@host:3306/db?ssl-mode=REQUIRED

# Add to config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_size': 10,
    'max_overflow': 20,
    'connect_args': {
        'ssl': {
            'ssl_mode': 'REQUIRED'
        }
    }
}
```

---

### 16. **NO DATABASE BACKUPS** 🚨 SEVERITY: HIGH
**Fix Required:**
```bash
# Add to Railway/cron job
0 2 * * * mysqldump -u user -p database > backup_$(date +\%Y\%m\%d).sql
```

---

## 📊 DEPENDENCY VULNERABILITIES

### 17. **OUTDATED DEPENDENCIES** 🚨 SEVERITY: MEDIUM
**Fix Required:**
```bash
# Check for vulnerabilities
pip install safety
safety check

# Update requirements.txt
Flask>=3.0.3
Werkzeug>=3.0.3
cryptography>=42.0.0
Pillow>=10.3.0
```

---

## 🚀 PRODUCTION DEPLOYMENT CHECKLIST

### Environment Variables (Required)
```env
# CRITICAL - Must be set
SECRET_KEY=<strong-64-char-hex>
DATABASE_URL=mysql+pymysql://user:pass@host/db?ssl-mode=REQUIRED
REDIS_URL=redis://default:password@host:port

# Payment Providers
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
PAYFAST_MERCHANT_ID=...
PAYFAST_MERCHANT_KEY=...
PAYFAST_PASSPHRASE=...
PAYFAST_MODE=live

# Email
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=...
MAIL_PASSWORD=...
SEND_EMAILS=True

# Security
FLASK_ENV=production
FLASK_DEBUG=False
SESSION_COOKIE_SECURE=True
```

### Gunicorn Configuration
```python
# gunicorn_config.py
bind = "0.0.0.0:8080"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 10000
max_requests_jitter = 1000
timeout = 30
keepalive = 2
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

### Update Procfile
```
web: gunicorn -c gunicorn_config.py wsgi:app
```

---

## 📝 IMPLEMENTATION PRIORITY

### Phase 1: IMMEDIATE (Deploy Blocker)
1. ✅ Add CSRF protection to ALL forms
2. ✅ Set strong SECRET_KEY in environment
3. ✅ Enable HTTPS enforcement (Flask-Talisman)
4. ✅ Add rate limiting to login/API endpoints
5. ✅ Fix file upload vulnerabilities
6. ✅ Set secure session cookies

### Phase 2: HIGH PRIORITY (Week 1)
1. ✅ Implement 2FA for admin accounts
2. ✅ Add account lockout mechanism
3. ✅ Add input validation to all forms
4. ✅ Implement audit logging
5. ✅ Add security headers
6. ✅ Password strength enforcement

### Phase 3: MEDIUM PRIORITY (Week 2-3)
1. ✅ Enhanced payment validation
2. ✅ Webhook signature verification
3. ✅ SQL injection prevention audit
4. ✅ Update all dependencies
5. ✅ Database connection encryption
6. ✅ Automated backups

### Phase 4: ONGOING
1. ✅ Security monitoring and alerting
2. ✅ Regular penetration testing
3. ✅ Dependency vulnerability scanning
4. ✅ Security awareness training
5. ✅ Incident response plan

---

## 🎯 COMPLIANCE REQUIREMENTS

### PCI DSS (Payment Card Industry)
- Never store full credit card numbers
- Never store CVV/CVC codes
- Use Stripe.js for client-side tokenization
- Log all access to cardholder data

### POPIA (South African Data Protection)
- Obtain consent for data processing
- Allow users to request data deletion
- Implement data retention policies
- Notify users of breaches within 72 hours

### GDPR (If serving EU customers)
- Right to be forgotten
- Data portability
- Privacy by design
- Cookie consent

---

## 📊 ESTIMATED IMPLEMENTATION TIME

- **Phase 1 (Critical):** 2-3 days
- **Phase 2 (High):** 5-7 days
- **Phase 3 (Medium):** 7-10 days
- **Total:** ~3 weeks for full hardening

---

## 📞 INCIDENT RESPONSE PLAN

1. **Detection:** Monitor logs for suspicious activity
2. **Containment:** Disable compromised accounts immediately
3. **Investigation:** Review audit logs and access patterns
4. **Eradication:** Remove malicious code/access
5. **Recovery:** Restore from clean backups
6. **Lessons Learned:** Update security measures

---

**Last Updated:** February 4, 2026
**Next Review:** March 4, 2026 (Monthly)
