from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from flask_cors import CORS
from flask_caching import Cache
import os
import datetime
from config import Config
from models import (
    db, User, SiteSettings, CompanyInfo, Service, Product, HeroSection,
    ContentSection, PaymentMethod, PaymentTerm, Transaction,
    ContactSubmission, MenuItem, Testimonial, Customer, Cart, CartItem,
    Order, OrderItem, Invoice, InvoicePayment
)
from email_service import EmailService
import json
from werkzeug.utils import secure_filename
from payments import StripePayment, PayFastPayment
from email_service import EmailService

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
cache = Cache(app)
CORS(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'admin_login'

# Initialize Email Service
email_service = EmailService(
    smtp_server=app.config.get('MAIL_SERVER'),
    smtp_port=app.config.get('MAIL_PORT'),
    sender_email=app.config.get('MAIL_USERNAME'),
    sender_password=app.config.get('MAIL_PASSWORD'),
    use_tls=app.config.get('MAIL_USE_TLS')
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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in \
           app.config['ALLOWED_EXTENSIONS']


def save_upload_file(file):
    """Save uploaded file with timestamp to prevent filename collisions"""
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    filename = secure_filename(file.filename)
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{name}_{timestamp}.{ext}"
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    file.save(filepath)
    
    return f'/static/uploads/{new_filename}'


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
    ).order_by(Testimonial.order_position).all()
    company_info = CompanyInfo.query.first()
    content_sections = ContentSection.query.filter_by(
        is_active=True
    ).order_by(ContentSection.order_position).all()
    menu_items = MenuItem.query.filter_by(
        is_active=True, parent_id=None
    ).order_by(MenuItem.order_position).all()

    return render_template('index.html',
                         hero_sections=hero_sections,
                         services=services,
                         testimonials=testimonials,
                         company_info=company_info,
                         content_sections=content_sections,
                         menu_items=menu_items)

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
    products = Product.query.filter_by(is_active=True).order_by(Product.order_position).all()
    company_info = CompanyInfo.query.first()
    menu_items = MenuItem.query.filter_by(is_active=True, parent_id=None).order_by(MenuItem.order_position).all()
    
    return render_template('products.html', 
                         products=products,
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
def submit_contact():
    data = request.get_json()

    submission = ContactSubmission(
        name=data.get('name'),
        email=data.get('email'),
        phone=data.get('phone'),
        subject=data.get('subject'),
        message=data.get('message')
    )

    db.session.add(submission)
    db.session.commit()

    # Send emails if enabled
    if app.config.get('SEND_EMAILS'):
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

        # Send notification to admin
        admin_email = app.config.get(
            'ADMIN_EMAIL',
            'admin@360degreesupply.co.za'
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
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_admin:
            login_user(user)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password', 'error')
            return redirect(url_for('login'))
    
    return redirect(url_for('login'))

@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    total_services = Service.query.count()
    total_products = Product.query.count()
    total_transactions = Transaction.query.count()
    pending_contacts = ContactSubmission.query.filter_by(status='new').count()
    
    recent_transactions = Transaction.query.order_by(Transaction.created_at.desc()).limit(5).all()
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
        product = Product(
            name=request.form.get('name'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            specifications=request.form.get('specifications'),
            price=request.form.get('price'),
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
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.category = request.form.get('category')
        product.specifications = request.form.get('specifications')
        product.price = request.form.get('price')
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
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).paginate(page=page, per_page=10)
    return render_template('admin/transactions.html', transactions=transactions)

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

        if len(password) < 6:
            flash(
                'Password must be at least 6 characters',
                'danger'
            )
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
            next_page = request.args.get('next')
            if not next_page or (
                next_page.startswith('http') or
                next_page.startswith('/')
            ):
                if next_page and not (
                    next_page.startswith('http')
                ):
                    return redirect(next_page)
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

    menu_items = MenuItem.query.filter_by(
        is_active=True, parent_id=None
    ).order_by(MenuItem.order_position).all()
    company_info = CompanyInfo.query.first()

    return render_template('customer/dashboard.html',
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


# ========== SHOPPING CART ROUTES ==========

@app.route('/cart', methods=['GET'])
def view_cart():
    """Display shopping cart"""
    menu_items = MenuItem.query.filter_by(
        is_active=True
    ).order_by(MenuItem.order_position).all()
    company_info = CompanyInfo.query.first()

    cart = None
    if current_user and isinstance(current_user, Customer):
        cart = Cart.query.filter_by(
            customer_id=current_user.id, is_active=True
        ).first()

    return render_template('cart.html',
                           cart=cart,
                           menu_items=menu_items,
                           company_info=company_info)


@app.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """Add product to cart via AJAX"""
    if not isinstance(current_user, Customer):
        return jsonify({
            'success': False, 'message': 'Must be logged in as customer'
        }), 401

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

    # Get or create customer's cart
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
def get_cart_count():
    """Get number of items in cart (for navbar)"""
    cart_count = 0

    if current_user and isinstance(current_user, Customer):
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
            
            order = Order(
                customer_id=current_user.id,
                order_number=order_number,
                status='pending',
                subtotal=subtotal,
                tax_amount=tax,
                shipping_cost=shipping,
                total_amount=total,
                payment_status='pending',
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
            
            flash('Order created successfully!', 'success')
            return redirect(url_for('customer_orders'))
        
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


# Admin Invoice Routes
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
            invoice.due_date = datetime.strptime(
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
    """Create new invoice (admin)"""
    if not isinstance(current_user, User):
        flash('Admin only', 'error')
        return redirect(url_for('login'))
    
    try:
        if request.method == 'POST':
            customer_id = request.form.get('customer_id')
            invoice_number = request.form.get('invoice_number')
            total_amount = request.form.get('total_amount')
            due_date = datetime.strptime(
                request.form.get('due_date'), '%Y-%m-%d'
            )
            
            invoice = Invoice(
                invoice_number=invoice_number,
                customer_id=customer_id,
                total_amount=total_amount,
                due_date=due_date,
                status='draft'
            )
            
            db.session.add(invoice)
            db.session.commit()
            
            flash('Invoice created successfully', 'success')
            return redirect(url_for('admin_invoice_detail', invoice_id=invoice.id))
        
        customers = Customer.query.all()
        return render_template(
            'admin/invoice_create.html',
            customers=customers
        )
    except Exception as e:
        app.logger.error(f"Error creating invoice: {str(e)}")
        flash('Error creating invoice', 'danger')
        return redirect(url_for('admin_invoices'))


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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
