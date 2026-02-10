from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from flask_login import login_required, current_user
from utils.master_admin_utils import require_master_admin, log_audit, log_user_activity
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'models'))
from master_admin import SecurityEvent, UserActivity, SystemLog
from security_models import BlockedIP, SystemControl, UserPermission, DetailedLog
from models import db, User, Product, Order, AuditLog, Customer, Invoice, Transaction, Service, Testimonial
from sqlalchemy import inspect, text, func, desc
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import json

master_admin_bp = Blueprint('master_admin', __name__, url_prefix='/master-admin')

@master_admin_bp.route('/dashboard')
@login_required
@require_master_admin
def dashboard():
    total_users = User.query.count()
    total_orders = Order.query.count()
    total_products = Product.query.count()
    recent_security = SecurityEvent.query.filter_by(resolved=False).order_by(SecurityEvent.timestamp.desc()).limit(10).all()
    recent_audits = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(20).all()
    recent_errors = SystemLog.query.filter(SystemLog.level.in_(['ERROR', 'CRITICAL'])).order_by(SystemLog.timestamp.desc()).limit(10).all()
    
    log_user_activity(current_user.id, 'accessed_master_admin_dashboard')
    
    return render_template('master_admin/dashboard.html',
                         total_users=total_users,
                         total_orders=total_orders,
                         total_products=total_products,
                         recent_security=recent_security,
                         recent_audits=recent_audits,
                         recent_errors=recent_errors)

@master_admin_bp.route('/users')
@login_required
@require_master_admin
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=50)
    return render_template('master_admin/users.html', users=users)

@master_admin_bp.route('/users/<int:user_id>')
@login_required
@require_master_admin
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    activities = UserActivity.query.filter_by(user_id=user_id).order_by(UserActivity.timestamp.desc()).limit(50).all()
    audits = AuditLog.query.filter_by(user_id=user_id).order_by(AuditLog.timestamp.desc()).limit(50).all()
    security_events = SecurityEvent.query.filter_by(user_id=user_id).order_by(SecurityEvent.timestamp.desc()).limit(20).all()
    
    return render_template('master_admin/user_detail.html', user=user, activities=activities, audits=audits, security_events=security_events)

@master_admin_bp.route('/database')
@login_required
@require_master_admin
def database():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    log_audit(current_user.id, 'viewed_database_tables', severity='warning')
    return render_template('master_admin/database.html', tables=tables)

@master_admin_bp.route('/database/<table_name>')
@login_required
@require_master_admin
def database_table(table_name):
    try:
        result = db.session.execute(text(f"SELECT * FROM {table_name} LIMIT 100"))
        columns = result.keys()
        rows = result.fetchall()
        log_audit(current_user.id, 'viewed_table_data', table_name=table_name, severity='warning')
        return render_template('master_admin/database_table.html', table_name=table_name, columns=columns, rows=rows)
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('master_admin.database'))

@master_admin_bp.route('/audit-logs')
@login_required
@require_master_admin
def audit_logs():
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=100)
    return render_template('master_admin/audit_logs.html', logs=logs)

@master_admin_bp.route('/security-events')
@login_required
@require_master_admin
def security_events():
    page = request.args.get('page', 1, type=int)
    events = SecurityEvent.query.filter_by(resolved=False).order_by(SecurityEvent.timestamp.desc()).paginate(page=page, per_page=50)
    return render_template('master_admin/security_events.html', events=events)

@master_admin_bp.route('/security-events/<int:event_id>/resolve', methods=['POST'])
@login_required
@require_master_admin
def resolve_security_event(event_id):
    event = SecurityEvent.query.get_or_404(event_id)
    event.resolved = True
    event.resolved_by = current_user.id
    event.resolved_at = datetime.utcnow()
    db.session.commit()
    log_audit(current_user.id, 'resolved_security_event', 'security_events', event_id)
    flash('Security event resolved', 'success')
    return redirect(url_for('master_admin.security_events'))

@master_admin_bp.route('/system-logs')
@login_required
@require_master_admin
def system_logs():
    page = request.args.get('page', 1, type=int)
    logs = SystemLog.query.order_by(SystemLog.timestamp.desc()).paginate(page=page, per_page=100)
    return render_template('master_admin/system_logs.html', logs=logs)

# ===== USER MANAGEMENT =====

@master_admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@require_master_admin
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        old_data = {'email': user.email, 'is_admin': user.is_admin}
        user.email = request.form.get('email')
        user.is_admin = request.form.get('is_admin') == 'on'
        db.session.commit()
        log_audit(current_user.id, 'updated_user', 'users', user_id, old_data, {'email': user.email, 'is_admin': user.is_admin})
        flash('User updated successfully', 'success')
        return redirect(url_for('master_admin.user_detail', user_id=user_id))
    return render_template('master_admin/edit_user.html', user=user)

@master_admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@require_master_admin
def delete_user(user_id):
    if user_id == current_user.id:
        flash('Cannot delete your own account', 'danger')
        return redirect(url_for('master_admin.users'))
    user = User.query.get_or_404(user_id)
    email = user.email
    db.session.delete(user)
    db.session.commit()
    log_audit(current_user.id, 'deleted_user', 'users', user_id, {'email': email}, severity='warning')
    flash(f'User {email} deleted successfully', 'success')
    return redirect(url_for('master_admin.users'))

@master_admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@require_master_admin
def reset_user_password(user_id):
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password')
    if not new_password or len(new_password) < 8:
        flash('Password must be at least 8 characters', 'danger')
        return redirect(url_for('master_admin.user_detail', user_id=user_id))
    user.password_hash = generate_password_hash(new_password)
    db.session.commit()
    log_audit(current_user.id, 'reset_user_password', 'users', user_id, severity='warning')
    flash('Password reset successfully', 'success')
    return redirect(url_for('master_admin.user_detail', user_id=user_id))

@master_admin_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@require_master_admin
def add_user():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin') == 'on'
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return render_template('master_admin/add_user.html')
        
        user = User(email=email, is_admin=is_admin)
        user.password_hash = generate_password_hash(password)
        db.session.add(user)
        db.session.commit()
        log_audit(current_user.id, 'created_user', 'users', user.id, new_value={'email': email, 'is_admin': is_admin})
        flash('User created successfully', 'success')
        return redirect(url_for('master_admin.users'))
    return render_template('master_admin/add_user.html')

# ===== CUSTOMER MANAGEMENT =====

@master_admin_bp.route('/customers')
@login_required
@require_master_admin
def customers():
    page = request.args.get('page', 1, type=int)
    customers = Customer.query.order_by(Customer.created_at.desc()).paginate(page=page, per_page=50)
    return render_template('master_admin/customers.html', customers=customers)

@master_admin_bp.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
@require_master_admin
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if request.method == 'POST':
        customer.email = request.form.get('email')
        customer.first_name = request.form.get('first_name')
        customer.last_name = request.form.get('last_name')
        customer.company = request.form.get('company')
        customer.phone = request.form.get('phone')
        customer.is_active = request.form.get('is_active') == 'on'
        db.session.commit()
        log_audit(current_user.id, 'updated_customer', 'customers', customer_id)
        flash('Customer updated successfully', 'success')
        return redirect(url_for('master_admin.customers'))
    return render_template('master_admin/edit_customer.html', customer=customer)

@master_admin_bp.route('/customers/<int:customer_id>/delete', methods=['POST'])
@login_required
@require_master_admin
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    email = customer.email
    db.session.delete(customer)
    db.session.commit()
    log_audit(current_user.id, 'deleted_customer', 'customers', customer_id, severity='warning')
    flash(f'Customer {email} deleted successfully', 'success')
    return redirect(url_for('master_admin.customers'))

# ===== PRODUCT MANAGEMENT =====

@master_admin_bp.route('/products')
@login_required
@require_master_admin
def products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.order_by(Product.created_at.desc()).paginate(page=page, per_page=50)
    return render_template('master_admin/products.html', products=products)

@master_admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
@require_master_admin
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    name = product.name
    db.session.delete(product)
    db.session.commit()
    log_audit(current_user.id, 'deleted_product', 'products', product_id, severity='warning')
    flash(f'Product {name} deleted successfully', 'success')
    return redirect(url_for('master_admin.products'))

# ===== ORDER MANAGEMENT =====

@master_admin_bp.route('/orders')
@login_required
@require_master_admin
def orders():
    page = request.args.get('page', 1, type=int)
    orders = Order.query.order_by(Order.created_at.desc()).paginate(page=page, per_page=50)
    return render_template('master_admin/orders.html', orders=orders)

@master_admin_bp.route('/orders/<int:order_id>/update-status', methods=['POST'])
@login_required
@require_master_admin
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    old_status = order.status
    new_status = request.form.get('status')
    order.status = new_status
    db.session.commit()
    log_audit(current_user.id, 'updated_order_status', 'orders', order_id, {'status': old_status}, {'status': new_status})
    flash('Order status updated', 'success')
    return redirect(url_for('master_admin.orders'))

@master_admin_bp.route('/orders/<int:order_id>/delete', methods=['POST'])
@login_required
@require_master_admin
def delete_order(order_id):
    order = Order.query.get_or_404(order_id)
    order_number = order.order_number
    db.session.delete(order)
    db.session.commit()
    log_audit(current_user.id, 'deleted_order', 'orders', order_id, severity='critical')
    flash(f'Order {order_number} deleted successfully', 'success')
    return redirect(url_for('master_admin.orders'))

# ===== INVOICE MANAGEMENT =====

@master_admin_bp.route('/invoices')
@login_required
@require_master_admin
def invoices():
    page = request.args.get('page', 1, type=int)
    invoices = Invoice.query.order_by(Invoice.created_at.desc()).paginate(page=page, per_page=50)
    return render_template('master_admin/invoices.html', invoices=invoices)

@master_admin_bp.route('/invoices/<int:invoice_id>/delete', methods=['POST'])
@login_required
@require_master_admin
def delete_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    invoice_number = invoice.invoice_number
    db.session.delete(invoice)
    db.session.commit()
    log_audit(current_user.id, 'deleted_invoice', 'invoices', invoice_id, severity='critical')
    flash(f'Invoice {invoice_number} deleted successfully', 'success')
    return redirect(url_for('master_admin.invoices'))

# ===== TRANSACTION MANAGEMENT =====

@master_admin_bp.route('/transactions')
@login_required
@require_master_admin
def transactions():
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).paginate(page=page, per_page=50)
    return render_template('master_admin/transactions.html', transactions=transactions)

@master_admin_bp.route('/transactions/<int:transaction_id>/delete', methods=['POST'])
@login_required
@require_master_admin
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    ref = transaction.payment_reference
    db.session.delete(transaction)
    db.session.commit()
    log_audit(current_user.id, 'deleted_transaction', 'transactions', transaction_id, severity='critical')
    flash(f'Transaction {ref} deleted successfully', 'success')
    return redirect(url_for('master_admin.transactions'))

# ===== DATA MANAGEMENT =====

@master_admin_bp.route('/data/services')
@login_required
@require_master_admin
def manage_services():
    services = Service.query.order_by(Service.order_position).all()
    return render_template('master_admin/services.html', services=services)

@master_admin_bp.route('/data/services/<int:service_id>/delete', methods=['POST'])
@login_required
@require_master_admin
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    title = service.title
    db.session.delete(service)
    db.session.commit()
    log_audit(current_user.id, 'deleted_service', 'services', service_id)
    flash(f'Service {title} deleted successfully', 'success')
    return redirect(url_for('master_admin.manage_services'))

@master_admin_bp.route('/data/testimonials')
@login_required
@require_master_admin
def manage_testimonials():
    testimonials = Testimonial.query.order_by(Testimonial.created_at.desc()).all()
    return render_template('master_admin/testimonials.html', testimonials=testimonials)

@master_admin_bp.route('/data/testimonials/<int:testimonial_id>/delete', methods=['POST'])
@login_required
@require_master_admin
def delete_testimonial(testimonial_id):
    testimonial = Testimonial.query.get_or_404(testimonial_id)
    name = testimonial.client_name
    db.session.delete(testimonial)
    db.session.commit()
    log_audit(current_user.id, 'deleted_testimonial', 'testimonials', testimonial_id)
    flash(f'Testimonial from {name} deleted successfully', 'success')
    return redirect(url_for('master_admin.manage_testimonials'))

# ===== IP BLOCKING & SECURITY =====

@master_admin_bp.route('/security/blocked-ips')
@login_required
@require_master_admin
def blocked_ips():
    try:
        page = request.args.get('page', 1, type=int)
        blocked = BlockedIP.query.order_by(BlockedIP.blocked_at.desc()).paginate(page=page, per_page=50)
        return render_template('master_admin/blocked_ips.html', blocked_ips=blocked)
    except Exception as e:
        flash(f'Feature not available: {str(e)}. Please run database migration.', 'warning')
        return redirect(url_for('master_admin.dashboard'))

@master_admin_bp.route('/security/block-ip', methods=['POST'])
@login_required
@require_master_admin
def block_ip():
    ip_address = request.form.get('ip_address')
    reason = request.form.get('reason')
    is_permanent = request.form.get('is_permanent') == 'on'
    duration_hours = int(request.form.get('duration_hours', 24))
    
    if not ip_address or not reason:
        flash('IP address and reason are required', 'danger')
        return redirect(url_for('master_admin.blocked_ips'))
    
    # Check if already blocked
    existing = BlockedIP.query.filter_by(ip_address=ip_address).first()
    if existing:
        flash(f'IP {ip_address} is already blocked', 'warning')
        return redirect(url_for('master_admin.blocked_ips'))
    
    blocked = BlockedIP(
        ip_address=ip_address,
        reason=reason,
        blocked_by=current_user.id,
        is_permanent=is_permanent,
        expires_at=None if is_permanent else datetime.utcnow() + timedelta(hours=duration_hours)
    )
    db.session.add(blocked)
    db.session.commit()
    
    log_audit(current_user.id, 'blocked_ip', 'blocked_ips', blocked.id, new_value={'ip': ip_address, 'reason': reason}, severity='critical')
    flash(f'IP {ip_address} blocked successfully', 'success')
    return redirect(url_for('master_admin.blocked_ips'))

@master_admin_bp.route('/security/unblock-ip/<int:block_id>', methods=['POST'])
@login_required
@require_master_admin
def unblock_ip(block_id):
    blocked = BlockedIP.query.get_or_404(block_id)
    ip_address = blocked.ip_address
    db.session.delete(blocked)
    db.session.commit()
    
    log_audit(current_user.id, 'unblocked_ip', 'blocked_ips', block_id, old_value={'ip': ip_address}, severity='warning')
    flash(f'IP {ip_address} unblocked successfully', 'success')
    return redirect(url_for('master_admin.blocked_ips'))

# ===== SYSTEM CONTROL =====

@master_admin_bp.route('/system/control')
@login_required
@require_master_admin
def system_control():
    try:
        control = SystemControl.query.first()
        if not control:
            control = SystemControl()
            db.session.add(control)
            db.session.commit()
        return render_template('master_admin/system_control.html', control=control)
    except Exception as e:
        flash(f'Feature not available: {str(e)}. Please run database migration.', 'warning')
        return redirect(url_for('master_admin.dashboard'))

@master_admin_bp.route('/system/shutdown', methods=['POST'])
@login_required
@require_master_admin
def shutdown_system():
    reason = request.form.get('reason', 'System shutdown by administrator')
    
    control = SystemControl.query.first()
    if not control:
        control = SystemControl()
        db.session.add(control)
    
    control.is_system_active = False
    control.shutdown_reason = reason
    control.shutdown_by = current_user.id
    control.shutdown_at = datetime.utcnow()
    db.session.commit()
    
    log_audit(current_user.id, 'system_shutdown', 'system_controls', control.id, new_value={'reason': reason}, severity='critical')
    flash('System has been shut down', 'warning')
    return redirect(url_for('master_admin.system_control'))

@master_admin_bp.route('/system/activate', methods=['POST'])
@login_required
@require_master_admin
def activate_system():
    control = SystemControl.query.first()
    if control:
        control.is_system_active = True
        control.maintenance_mode = False
        control.shutdown_reason = None
        db.session.commit()
    
    log_audit(current_user.id, 'system_activated', 'system_controls', control.id if control else None, severity='warning')
    flash('System has been activated', 'success')
    return redirect(url_for('master_admin.system_control'))

@master_admin_bp.route('/system/maintenance', methods=['POST'])
@login_required
@require_master_admin
def toggle_maintenance():
    message = request.form.get('message', 'System is under maintenance')
    
    control = SystemControl.query.first()
    if not control:
        control = SystemControl()
        db.session.add(control)
    
    control.maintenance_mode = not control.maintenance_mode
    control.maintenance_message = message if control.maintenance_mode else None
    db.session.commit()
    
    status = 'enabled' if control.maintenance_mode else 'disabled'
    log_audit(current_user.id, f'maintenance_mode_{status}', 'system_controls', control.id, severity='warning')
    flash(f'Maintenance mode {status}', 'info')
    return redirect(url_for('master_admin.system_control'))

# ===== USER PERMISSIONS =====

@master_admin_bp.route('/permissions/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@require_master_admin
def manage_user_permissions(user_id):
    user = User.query.get_or_404(user_id)
    perms = UserPermission.query.filter_by(user_id=user_id).first()
    
    if not perms:
        perms = UserPermission(user_id=user_id)
        db.session.add(perms)
        db.session.commit()
    
    if request.method == 'POST':
        # Access permissions
        perms.can_access_products = request.form.get('can_access_products') == 'on'
        perms.can_access_services = request.form.get('can_access_services') == 'on'
        perms.can_access_cart = request.form.get('can_access_cart') == 'on'
        perms.can_access_orders = request.form.get('can_access_orders') == 'on'
        perms.can_access_invoices = request.form.get('can_access_invoices') == 'on'
        perms.can_access_transactions = request.form.get('can_access_transactions') == 'on'
        perms.can_access_profile = request.form.get('can_access_profile') == 'on'
        
        # Sidebar visibility
        perms.show_products_tab = request.form.get('show_products_tab') == 'on'
        perms.show_services_tab = request.form.get('show_services_tab') == 'on'
        perms.show_orders_tab = request.form.get('show_orders_tab') == 'on'
        perms.show_invoices_tab = request.form.get('show_invoices_tab') == 'on'
        perms.show_transactions_tab = request.form.get('show_transactions_tab') == 'on'
        perms.show_profile_tab = request.form.get('show_profile_tab') == 'on'
        
        # Block status
        is_blocked = request.form.get('is_blocked') == 'on'
        if is_blocked and not perms.is_blocked:
            perms.is_blocked = True
            perms.block_reason = request.form.get('block_reason')
            perms.blocked_by = current_user.id
            perms.blocked_at = datetime.utcnow()
        elif not is_blocked:
            perms.is_blocked = False
            perms.block_reason = None
        
        db.session.commit()
        log_audit(current_user.id, 'updated_user_permissions', 'user_permissions', perms.id)
        flash('Permissions updated successfully', 'success')
        return redirect(url_for('master_admin.user_detail', user_id=user_id))
    
    return render_template('master_admin/user_permissions.html', user=user, perms=perms)

@master_admin_bp.route('/permissions/customer/<int:customer_id>', methods=['GET', 'POST'])
@login_required
@require_master_admin
def manage_customer_permissions(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    perms = UserPermission.query.filter_by(customer_id=customer_id).first()
    
    if not perms:
        perms = UserPermission(customer_id=customer_id)
        db.session.add(perms)
        db.session.commit()
    
    if request.method == 'POST':
        # Access permissions
        perms.can_access_products = request.form.get('can_access_products') == 'on'
        perms.can_access_services = request.form.get('can_access_services') == 'on'
        perms.can_access_cart = request.form.get('can_access_cart') == 'on'
        perms.can_access_orders = request.form.get('can_access_orders') == 'on'
        perms.can_access_invoices = request.form.get('can_access_invoices') == 'on'
        perms.can_access_transactions = request.form.get('can_access_transactions') == 'on'
        perms.can_access_profile = request.form.get('can_access_profile') == 'on'
        
        # Sidebar visibility
        perms.show_products_tab = request.form.get('show_products_tab') == 'on'
        perms.show_services_tab = request.form.get('show_services_tab') == 'on'
        perms.show_orders_tab = request.form.get('show_orders_tab') == 'on'
        perms.show_invoices_tab = request.form.get('show_invoices_tab') == 'on'
        perms.show_transactions_tab = request.form.get('show_transactions_tab') == 'on'
        perms.show_profile_tab = request.form.get('show_profile_tab') == 'on'
        
        # Block status
        is_blocked = request.form.get('is_blocked') == 'on'
        if is_blocked and not perms.is_blocked:
            perms.is_blocked = True
            perms.block_reason = request.form.get('block_reason')
            perms.blocked_by = current_user.id
            perms.blocked_at = datetime.utcnow()
        elif not is_blocked:
            perms.is_blocked = False
            perms.block_reason = None
        
        db.session.commit()
        log_audit(current_user.id, 'updated_customer_permissions', 'user_permissions', perms.id)
        flash('Permissions updated successfully', 'success')
        return redirect(url_for('master_admin.customers'))
    
    return render_template('master_admin/customer_permissions.html', customer=customer, perms=perms)

# ===== DETAILED LOGS & MONITORING =====

@master_admin_bp.route('/logs/detailed')
@login_required
@require_master_admin
def detailed_logs():
    try:
        page = request.args.get('page', 1, type=int)
        log_type = request.args.get('type', 'all')
        severity = request.args.get('severity', 'all')
        suspicious_only = request.args.get('suspicious') == 'true'
        
        query = DetailedLog.query
        
        if log_type != 'all':
            query = query.filter_by(log_type=log_type)
        if severity != 'all':
            query = query.filter_by(severity=severity)
        if suspicious_only:
            query = query.filter_by(is_suspicious=True)
        
        logs = query.order_by(DetailedLog.timestamp.desc()).paginate(page=page, per_page=100)
        
        # Get statistics
        total_logs = DetailedLog.query.count()
        suspicious_logs = DetailedLog.query.filter_by(is_suspicious=True).count()
        error_logs = DetailedLog.query.filter(DetailedLog.severity.in_(['error', 'critical'])).count()
        
        return render_template('master_admin/detailed_logs.html', 
                             logs=logs, 
                             total_logs=total_logs,
                             suspicious_logs=suspicious_logs,
                             error_logs=error_logs,
                             current_type=log_type,
                             current_severity=severity)
    except Exception as e:
        flash(f'Feature not available: {str(e)}. Please run database migration.', 'warning')
        return redirect(url_for('master_admin.dashboard'))

@master_admin_bp.route('/logs/detailed/<int:log_id>')
@login_required
@require_master_admin
def log_detail(log_id):
    log = DetailedLog.query.get_or_404(log_id)
    return render_template('master_admin/log_detail.html', log=log)

@master_admin_bp.route('/logs/detailed/<int:log_id>/review', methods=['POST'])
@login_required
@require_master_admin
def review_log(log_id):
    log = DetailedLog.query.get_or_404(log_id)
    log.is_reviewed = True
    log.reviewed_by = current_user.id
    log.reviewed_at = datetime.utcnow()
    log.review_notes = request.form.get('notes')
    db.session.commit()
    
    flash('Log reviewed successfully', 'success')
    return redirect(url_for('master_admin.log_detail', log_id=log_id))

@master_admin_bp.route('/logs/live')
@login_required
@require_master_admin
def live_logs():
    """Live log monitoring page"""
    return render_template('master_admin/live_logs.html')

@master_admin_bp.route('/api/logs/live')
@login_required
@require_master_admin
def api_live_logs():
    """API endpoint for live log updates"""
    try:
        since = request.args.get('since', type=int, default=0)
        
        if since > 0:
            since_time = datetime.fromtimestamp(since / 1000.0)
            logs = DetailedLog.query.filter(DetailedLog.timestamp > since_time).order_by(DetailedLog.timestamp.desc()).limit(50).all()
        else:
            logs = DetailedLog.query.order_by(DetailedLog.timestamp.desc()).limit(50).all()
        
        return jsonify({
            'logs': [{
                'id': log.id,
                'timestamp': log.timestamp.isoformat(),
                'severity': log.severity,
                'log_type': log.log_type,
                'username': log.username or 'Anonymous',
                'ip_address': log.ip_address,
                'request_path': log.request_path,
                'response_status': log.response_status,
                'is_suspicious': log.is_suspicious,
                'error_message': log.error_message
            } for log in logs],
            'timestamp': int(datetime.utcnow().timestamp() * 1000)
        })
    except Exception as e:
        return jsonify({'error': str(e), 'logs': [], 'timestamp': int(datetime.utcnow().timestamp() * 1000)})

# ===== ANALYTICS & INSIGHTS =====

@master_admin_bp.route('/analytics')
@login_required
@require_master_admin
def analytics():
    try:
        # Get statistics for last 24 hours
        last_24h = datetime.utcnow() - timedelta(hours=24)
        
        # Request statistics
        total_requests = DetailedLog.query.filter(DetailedLog.timestamp >= last_24h).count()
        error_requests = DetailedLog.query.filter(
            DetailedLog.timestamp >= last_24h,
            DetailedLog.severity.in_(['error', 'critical'])
        ).count()
        suspicious_requests = DetailedLog.query.filter(
            DetailedLog.timestamp >= last_24h,
            DetailedLog.is_suspicious == True
        ).count()
        
        # Top IPs
        top_ips = db.session.query(
            DetailedLog.ip_address,
            func.count(DetailedLog.id).label('count')
        ).filter(
            DetailedLog.timestamp >= last_24h
        ).group_by(DetailedLog.ip_address).order_by(desc('count')).limit(10).all()
        
        # Top users
        top_users = db.session.query(
            DetailedLog.username,
            func.count(DetailedLog.id).label('count')
        ).filter(
            DetailedLog.timestamp >= last_24h,
            DetailedLog.username.isnot(None)
        ).group_by(DetailedLog.username).order_by(desc('count')).limit(10).all()
        
        # Response time statistics
        avg_response_time = db.session.query(
            func.avg(DetailedLog.response_time)
        ).filter(
            DetailedLog.timestamp >= last_24h,
            DetailedLog.response_time.isnot(None)
        ).scalar() or 0
        
        return render_template('master_admin/analytics.html',
                             total_requests=total_requests,
                             error_requests=error_requests,
                             suspicious_requests=suspicious_requests,
                             top_ips=top_ips,
                             top_users=top_users,
                             avg_response_time=round(avg_response_time, 2))
    except Exception as e:
        flash(f'Feature not available: {str(e)}. Please run database migration.', 'warning')
        return redirect(url_for('master_admin.dashboard'))
