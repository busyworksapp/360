from datetime import datetime
from models import db
from sqlalchemy.dialects.mysql import LONGTEXT

class MasterAdmin(db.Model):
    __tablename__ = 'master_admins'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    mfa_enabled = db.Column(db.Boolean, default=False)
    mfa_secret = db.Column(db.String(32))
    last_login = db.Column(db.DateTime)
    last_ip = db.Column(db.String(45))
    granted_by = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('master_admin_profile', uselist=False))

class SecurityEvent(db.Model):
    __tablename__ = 'security_events'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    severity = db.Column(db.String(20), default='low')
    resolved = db.Column(db.Boolean, default=False)
    resolved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    resolved_at = db.Column(db.DateTime)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', foreign_keys=[user_id], backref='security_events')
    resolver = db.relationship('User', foreign_keys=[resolved_by])

class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text, nullable=False)
    module = db.Column(db.String(100))
    func_name = db.Column(db.String(100))
    line_number = db.Column(db.Integer)
    exception = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

class UserActivity(db.Model):
    __tablename__ = 'user_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', backref='activities')
