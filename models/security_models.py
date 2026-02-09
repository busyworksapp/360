from datetime import datetime
from models import db

class BlockedIP(db.Model):
    """Blocked IP addresses for security"""
    __tablename__ = 'blocked_ips'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), unique=True, nullable=False, index=True)
    reason = db.Column(db.Text, nullable=False)
    blocked_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    blocked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_permanent = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime)
    block_count = db.Column(db.Integer, default=1)
    last_attempt = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    blocker = db.relationship('User', foreign_keys=[blocked_by])

class SystemControl(db.Model):
    """System-wide control settings"""
    __tablename__ = 'system_controls'
    
    id = db.Column(db.Integer, primary_key=True)
    is_system_active = db.Column(db.Boolean, default=True)
    maintenance_mode = db.Column(db.Boolean, default=False)
    maintenance_message = db.Column(db.Text)
    shutdown_reason = db.Column(db.Text)
    shutdown_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    shutdown_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    shutdown_user = db.relationship('User', foreign_keys=[shutdown_by])

class UserPermission(db.Model):
    """User-specific permissions and restrictions"""
    __tablename__ = 'user_permissions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), unique=True)
    
    # Access restrictions
    can_access_products = db.Column(db.Boolean, default=True)
    can_access_services = db.Column(db.Boolean, default=True)
    can_access_cart = db.Column(db.Boolean, default=True)
    can_access_orders = db.Column(db.Boolean, default=True)
    can_access_invoices = db.Column(db.Boolean, default=True)
    can_access_transactions = db.Column(db.Boolean, default=True)
    can_access_profile = db.Column(db.Boolean, default=True)
    
    # Sidebar visibility
    show_products_tab = db.Column(db.Boolean, default=True)
    show_services_tab = db.Column(db.Boolean, default=True)
    show_orders_tab = db.Column(db.Boolean, default=True)
    show_invoices_tab = db.Column(db.Boolean, default=True)
    show_transactions_tab = db.Column(db.Boolean, default=True)
    show_profile_tab = db.Column(db.Boolean, default=True)
    
    # Account status
    is_blocked = db.Column(db.Boolean, default=False)
    block_reason = db.Column(db.Text)
    blocked_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    blocked_at = db.Column(db.DateTime)
    
    # Restrictions
    max_order_amount = db.Column(db.Numeric(10, 2))
    requires_approval = db.Column(db.Boolean, default=False)
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='permissions')
    customer = db.relationship('Customer', foreign_keys=[customer_id], backref='permissions')
    blocker = db.relationship('User', foreign_keys=[blocked_by])

class DetailedLog(db.Model):
    """Detailed system logs with deep dive capability"""
    __tablename__ = 'detailed_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    log_type = db.Column(db.String(50), nullable=False, index=True)  # request, action, error, security
    severity = db.Column(db.String(20), default='info', index=True)  # info, warning, error, critical
    
    # User info
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    username = db.Column(db.String(120))
    
    # Request info
    ip_address = db.Column(db.String(45), index=True)
    user_agent = db.Column(db.Text)
    request_method = db.Column(db.String(10))
    request_path = db.Column(db.String(500))
    request_data = db.Column(db.Text)  # JSON
    
    # Response info
    response_status = db.Column(db.Integer)
    response_time = db.Column(db.Float)  # milliseconds
    
    # Action details
    action = db.Column(db.String(100))
    target_table = db.Column(db.String(100))
    target_id = db.Column(db.Integer)
    old_value = db.Column(db.Text)  # JSON
    new_value = db.Column(db.Text)  # JSON
    
    # Error details
    error_message = db.Column(db.Text)
    error_traceback = db.Column(db.Text)
    
    # Additional context
    session_id = db.Column(db.String(100))
    referrer = db.Column(db.String(500))
    geo_location = db.Column(db.String(100))
    device_type = db.Column(db.String(50))
    browser = db.Column(db.String(100))
    
    # Flags
    is_suspicious = db.Column(db.Boolean, default=False)
    is_reviewed = db.Column(db.Boolean, default=False)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    review_notes = db.Column(db.Text)
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    user = db.relationship('User', foreign_keys=[user_id])
    customer = db.relationship('Customer', foreign_keys=[customer_id])
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
