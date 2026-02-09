from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from utils.master_admin_utils import require_master_admin, log_audit, log_user_activity
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'models'))
from master_admin import SecurityEvent, UserActivity, SystemLog
from models import db, User, Product, Order, AuditLog
from sqlalchemy import inspect, text
from datetime import datetime

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
