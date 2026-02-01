from flask import (Blueprint, render_template, request, jsonify, 
                   redirect, url_for, flash, session, current_app)
from flask_login import login_required, current_user
from models import (db, User, SiteSettings, CompanyInfo, Service, Product,
                   HeroSection, ContentSection, PaymentMethod, PaymentTerm,
                   Transaction, ContactSubmission, MenuItem, Testimonial)
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ==================== AUTHENTICATION ====================

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_admin:
            from flask_login import login_user
            login_user(user)
            flash('Logged in successfully', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials or insufficient permissions',
                  'danger')
    
    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    from flask_login import logout_user
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin.login'))


# ==================== DASHBOARD ====================

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('Unauthorized', 'danger')
        return redirect(url_for('index'))
    
    stats = {
        'total_products': Product.query.count(),
        'total_transactions': Transaction.query.count(),
        'total_contacts': ContactSubmission.query.count(),
        'pending_transactions': Transaction.query.filter_by(
            status='pending').count(),
        'recent_transactions': Transaction.query.order_by(
            Transaction.created_at.desc()).limit(5).all(),
        'recent_contacts': ContactSubmission.query.order_by(
            ContactSubmission.created_at.desc()).limit(5).all()
    }
    
    return render_template('admin/dashboard.html', stats=stats)


# ==================== SITE SETTINGS ====================

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'POST':
        settings_data = request.get_json()
        
        for key, value in settings_data.items():
            setting = SiteSettings.query.filter_by(key=key).first()
            if setting:
                setting.value = value
                setting.updated_by = current_user.id
            else:
                setting = SiteSettings(key=key, value=value,
                                     updated_by=current_user.id)
                db.session.add(setting)
        
        db.session.commit()
        return jsonify({'success': True}), 200
    
    settings_list = SiteSettings.query.filter_by(
        is_visible_in_admin=True).all()
    return render_template('admin/settings.html', settings=settings_list)


# ==================== COMPANY INFO ====================

@admin_bp.route('/company', methods=['GET', 'POST'])
@login_required
def company():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    company = CompanyInfo.query.first()
    
    if request.method == 'POST':
        if not company:
            company = CompanyInfo()
            db.session.add(company)
        
        company.company_name = request.form.get('company_name')
        company.address = request.form.get('address')
        company.phone = request.form.get('phone')
        company.email = request.form.get('email')
        company.secondary_phone = request.form.get('secondary_phone')
        company.secondary_email = request.form.get('secondary_email')
        company.description = request.form.get('description')
        company.mission = request.form.get('mission')
        company.established_year = request.form.get('established_year')
        
        # Handle logo upload
        if 'logo' in request.files:
            file = request.files['logo']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"logo_{int(datetime.now()
                                         .timestamp())}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],
                                      filename))
                company.logo_url = f"/static/uploads/{filename}"
        
        db.session.commit()
        flash('Company info updated', 'success')
    
    return render_template('admin/company.html', company=company)


# ==================== SERVICES ====================

@admin_bp.route('/services', methods=['GET', 'POST'])
@login_required
def services():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'POST':
        service = Service(
            title=request.form.get('title'),
            description=request.form.get('description'),
            icon=request.form.get('icon'),
            order_position=int(request.form.get('order_position', 0)),
            is_active=request.form.get('is_active') == 'on'
        )
        
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"service_{int(datetime.now()
                                         .timestamp())}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],
                                      filename))
                service.image_url = f"/static/uploads/{filename}"
        
        db.session.add(service)
        db.session.commit()
        flash('Service created', 'success')
        return redirect(url_for('admin.services'))
    
    services_list = Service.query.order_by(Service.order_position).all()
    return render_template('admin/services.html', services=services_list)


@admin_bp.route('/services/<int:id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def edit_service(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    service = Service.query.get_or_404(id)
    
    if request.method == 'POST':
        service.title = request.form.get('title')
        service.description = request.form.get('description')
        service.icon = request.form.get('icon')
        service.order_position = int(request.form.get('order_position', 0))
        service.is_active = request.form.get('is_active') == 'on'
        
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"service_{int(datetime.now()
                                         .timestamp())}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],
                                      filename))
                service.image_url = f"/static/uploads/{filename}"
        
        db.session.commit()
        flash('Service updated', 'success')
        return redirect(url_for('admin.services'))
    
    elif request.method == 'DELETE':
        db.session.delete(service)
        db.session.commit()
        return jsonify({'success': True}), 200
    
    return render_template('admin/edit_service.html', service=service)


# ==================== PRODUCTS ====================

@admin_bp.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'POST':
        product = Product(
            name=request.form.get('name'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            specifications=request.form.get('specifications'),
            price=float(request.form.get('price', 0)),
            unit=request.form.get('unit'),
            order_position=int(request.form.get('order_position', 0)),
            is_active=request.form.get('is_active') == 'on'
        )
        
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"product_{int(datetime.now()
                                         .timestamp())}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],
                                      filename))
                product.image_url = f"/static/uploads/{filename}"
        
        db.session.add(product)
        db.session.commit()
        flash('Product created', 'success')
        return redirect(url_for('admin.products'))
    
    products_list = Product.query.order_by(Product.order_position).all()
    return render_template('admin/products.html', products=products_list)


@admin_bp.route('/products/<int:id>', methods=['GET', 'POST', 'DELETE'])
@login_required
def edit_product(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.category = request.form.get('category')
        product.specifications = request.form.get('specifications')
        product.price = float(request.form.get('price', 0))
        product.unit = request.form.get('unit')
        product.order_position = int(request.form.get('order_position', 0))
        product.is_active = request.form.get('is_active') == 'on'
        
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"product_{int(datetime.now()
                                         .timestamp())}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],
                                      filename))
                product.image_url = f"/static/uploads/{filename}"
        
        db.session.commit()
        flash('Product updated', 'success')
        return redirect(url_for('admin.products'))
    
    elif request.method == 'DELETE':
        db.session.delete(product)
        db.session.commit()
        return jsonify({'success': True}), 200
    
    return render_template('admin/edit_product.html', product=product)


# ==================== HERO SECTIONS ====================

@admin_bp.route('/hero-sections', methods=['GET', 'POST'])
@login_required
def hero_sections():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'POST':
        hero = HeroSection(
            title=request.form.get('title'),
            subtitle=request.form.get('subtitle'),
            description=request.form.get('description'),
            cta_text=request.form.get('cta_text'),
            cta_link=request.form.get('cta_link'),
            order_position=int(request.form.get('order_position', 0)),
            is_active=request.form.get('is_active') == 'on'
        )
        
        if 'background_image' in request.files:
            file = request.files['background_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"hero_{int(datetime.now()
                                         .timestamp())}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],
                                      filename))
                hero.background_image = f"/static/uploads/{filename}"
        
        db.session.add(hero)
        db.session.commit()
        flash('Hero section created', 'success')
        return redirect(url_for('admin.hero_sections'))
    
    heroes = HeroSection.query.order_by(HeroSection.order_position).all()
    return render_template('admin/hero_sections.html', heroes=heroes)


@admin_bp.route('/hero-sections/<int:id>', methods=['POST', 'DELETE'])
@login_required
def edit_hero_section(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    hero = HeroSection.query.get_or_404(id)
    
    if request.method == 'POST':
        hero.title = request.form.get('title')
        hero.subtitle = request.form.get('subtitle')
        hero.description = request.form.get('description')
        hero.cta_text = request.form.get('cta_text')
        hero.cta_link = request.form.get('cta_link')
        hero.order_position = int(request.form.get('order_position', 0))
        hero.is_active = request.form.get('is_active') == 'on'
        
        if 'background_image' in request.files:
            file = request.files['background_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"hero_{int(datetime.now()
                                         .timestamp())}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],
                                      filename))
                hero.background_image = f"/static/uploads/{filename}"
        
        db.session.commit()
        flash('Hero section updated', 'success')
        return redirect(url_for('admin.hero_sections'))
    
    elif request.method == 'DELETE':
        db.session.delete(hero)
        db.session.commit()
        return jsonify({'success': True}), 200


# ==================== TESTIMONIALS ====================

@admin_bp.route('/testimonials', methods=['GET', 'POST'])
@login_required
def testimonials():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'POST':
        testimonial = Testimonial(
            client_name=request.form.get('client_name'),
            company=request.form.get('company'),
            position=request.form.get('position'),
            content=request.form.get('content'),
            rating=int(request.form.get('rating', 5)),
            order_position=int(request.form.get('order_position', 0)),
            is_active=request.form.get('is_active') == 'on'
        )
        
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"testimonial_{int(datetime.now()
                                         .timestamp())}_{file.filename}")
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'],
                                      filename))
                testimonial.avatar_url = f"/static/uploads/{filename}"
        
        db.session.add(testimonial)
        db.session.commit()
        flash('Testimonial added', 'success')
        return redirect(url_for('admin.testimonials'))
    
    testimonials_list = Testimonial.query.order_by(
        Testimonial.order_position).all()
    return render_template('admin/testimonials.html',
                          testimonials=testimonials_list)


# ==================== PAYMENT MANAGEMENT ====================

@admin_bp.route('/transactions')
@login_required
def transactions():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.order_by(
        Transaction.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/transactions.html',
                          transactions=transactions)


@admin_bp.route('/transactions/<int:id>')
@login_required
def view_transaction(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    transaction = Transaction.query.get_or_404(id)
    return render_template('admin/view_transaction.html',
                          transaction=transaction)


@admin_bp.route('/payment-methods', methods=['GET', 'POST'])
@login_required
def payment_methods():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if request.method == 'POST':
        method = PaymentMethod(
            name=request.form.get('name'),
            description=request.form.get('description'),
            icon=request.form.get('icon'),
            order_position=int(request.form.get('order_position', 0)),
            is_active=request.form.get('is_active') == 'on'
        )
        db.session.add(method)
        db.session.commit()
        flash('Payment method added', 'success')
        return redirect(url_for('admin.payment_methods'))
    
    methods = PaymentMethod.query.order_by(PaymentMethod.order_position).all()
    return render_template('admin/payment_methods.html', methods=methods)


# ==================== CONTACTS ====================

@admin_bp.route('/contacts')
@login_required
def contacts():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    page = request.args.get('page', 1, type=int)
    contacts_list = ContactSubmission.query.order_by(
        ContactSubmission.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('admin/contacts.html', contacts=contacts_list)


@admin_bp.route('/contacts/<int:id>', methods=['GET', 'POST'])
@login_required
def view_contact(id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    contact = ContactSubmission.query.get_or_404(id)
    
    if request.method == 'POST':
        contact.status = request.form.get('status')
        db.session.commit()
        flash('Contact status updated', 'success')
        return redirect(url_for('admin.contacts'))
    
    return render_template('admin/view_contact.html', contact=contact)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in \
           current_app.config['ALLOWED_EXTENSIONS']
