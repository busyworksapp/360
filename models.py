from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from sqlalchemy.orm import validates
from decimal import Decimal

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class SiteSettings(db.Model):
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    value_type = db.Column(db.String(50), default='text')
    category = db.Column(db.String(50), default='general')
    display_label = db.Column(db.String(255))
    help_text = db.Column(db.Text)
    is_visible_in_admin = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                          onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))


class CompanyInfo(db.Model):
    __tablename__ = 'company_info'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255))
    address = db.Column(db.Text)
    phone = db.Column(db.String(100))
    email = db.Column(db.String(120))
    description = db.Column(db.Text)
    mission = db.Column(db.Text)
    established_year = db.Column(db.String(4))
    logo_url = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    image_url = db.Column(db.String(255))
    order_position = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    specifications = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    price = db.Column(db.Numeric(10, 2))
    unit = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    order_position = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class HeroSection(db.Model):
    __tablename__ = 'hero_sections'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    subtitle = db.Column(db.String(255))
    description = db.Column(db.Text)
    background_image = db.Column(db.String(255))
    cta_text = db.Column(db.String(100))
    cta_link = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    order_position = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentSection(db.Model):
    __tablename__ = 'content_sections'
    
    id = db.Column(db.Integer, primary_key=True)
    section_key = db.Column(db.String(100), unique=True, nullable=False)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    order_position = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PaymentMethod(db.Model):
    __tablename__ = 'payment_methods'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    order_position = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PaymentTerm(db.Model):
    __tablename__ = 'payment_terms'
    
    id = db.Column(db.Integer, primary_key=True)
    term_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order_position = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContactSubmission(db.Model):
    __tablename__ = 'contact_submissions'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50))
    subject = db.Column(db.String(255))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='new')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'))
    order_position = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    children = db.relationship('MenuItem', backref=db.backref('parent', remote_side=[id]))

class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(255), nullable=False)
    company = db.Column(db.String(255))
    position = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, default=5)
    avatar_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    order_position = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Customer(UserMixin, db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    company = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.Integer, db.ForeignKey('customers.id'),
        nullable=False
    )
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationship to customer
    customer = db.relationship(
        'Customer', backref=db.backref('carts', lazy=True)
    )
    # Relationship to cart items
    items = db.relationship(
        'CartItem', backref=db.backref('cart', lazy=True),
        cascade='all, delete-orphan'
    )

    def get_subtotal(self):
        """Calculate total price of all items in cart"""
        return sum(item.get_total() for item in self.items
                   if item.product)

    def get_item_count(self):
        """Get total number of items in cart"""
        return sum(item.quantity for item in self.items)

    def clear_cart(self):
        """Remove all items from cart"""
        for item in self.items:
            db.session.delete(item)
        db.session.commit()


class CartItem(db.Model):
    __tablename__ = 'cart_items'

    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(
        db.Integer, db.ForeignKey('carts.id'),
        nullable=False
    )
    product_id = db.Column(
        db.Integer, db.ForeignKey('products.id'),
        nullable=False
    )
    quantity = db.Column(db.Integer, default=1)
    price_at_add = db.Column(
        db.Numeric(10, 2)
    )  # Store price at time of adding to cart
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationship to product
    product = db.relationship(
        'Product', backref=db.backref('cart_items', lazy=True)
    )

    def get_total(self):
        """Calculate total price for this line item"""
        price = self.price_at_add or (
            self.product.price if self.product else 0
        )
        return float(price) * self.quantity

    def update_quantity(self, quantity):
        """Update quantity of item in cart"""
        if quantity <= 0:
            db.session.delete(self)
        else:
            self.quantity = quantity
        db.session.commit()


class Order(db.Model):
    """Customer orders model"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.Integer, db.ForeignKey('users.id'),
        nullable=False
    )
    order_number = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(
        db.String(20),
        default='pending',
        nullable=False
    )
    # pending, processing, shipped, delivered, cancelled
    subtotal = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    shipping_cost = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(
        db.String(20),
        default='pending',
        nullable=False
    )
    # pending, completed, failed
    shipping_address = db.Column(db.Text)
    billing_address = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # ===== PAYMENT TRACKING (Phase 6) =====
    payment_method = db.Column(
        db.String(50),
        nullable=True
    )
    # Payment method used: 'stripe', 'payfast', etc.
    
    payment_reference = db.Column(
        db.String(255),
        nullable=True,
        index=True
    )
    # Payment reference from gateway (for easy lookup)
    
    payment_confirmed_at = db.Column(
        db.DateTime,
        nullable=True
    )
    # When payment was confirmed by gateway
    
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow
    )
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    customer = db.relationship(
        'User', backref=db.backref(
            'orders', lazy=True, cascade='all, delete-orphan'
        )
    )
    items = db.relationship(
        'OrderItem', lazy=True, cascade='all, delete-orphan'
    )

    def get_subtotal(self):
        """Calculate subtotal from order items"""
        return sum(item.get_total() for item in self.items)

    def get_item_count(self):
        """Get total number of items in order"""
        return sum(item.quantity for item in self.items)

    def update_status(self, new_status):
        """Update order status"""
        valid_statuses = [
            'pending', 'processing', 'shipped',
            'delivered', 'cancelled'
        ]
        if new_status in valid_statuses:
            self.status = new_status
            self.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            return True
        return False


class OrderItem(db.Model):
    """Order line items model"""
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey('orders.id'),
        nullable=False
    )
    product_id = db.Column(
        db.Integer, db.ForeignKey('products.id'),
        nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow
    )

    # Relationships
    product = db.relationship(
        'Product', backref=db.backref('order_items', lazy=True)
    )

    def get_total(self):
        """Calculate total for this line item"""
        return self.quantity * self.price_at_purchase


class Transaction(db.Model):
    """Payment transaction tracking model"""
    __tablename__ = 'transactions'
    
    # ===== PRIMARY KEY =====
    id = db.Column(db.Integer, primary_key=True)
    
    # ===== FOREIGN KEYS =====
    order_id = db.Column(
        db.Integer, 
        db.ForeignKey('orders.id'), 
        nullable=False,
        unique=True
    )
    
    # ===== PAYMENT AMOUNT =====
    amount = db.Column(
        db.Numeric(10, 2),
        nullable=False
    )
    
    # ===== CURRENCY =====
    currency = db.Column(
        db.String(3),
        nullable=False,
        default='usd'
    )
    # Valid values: 'usd', 'zar', 'eur', etc. (ISO 4217 currency codes)
    
    # ===== PAYMENT METHOD =====
    payment_method = db.Column(
        db.String(50),
        nullable=False
    )
    # Valid values: 'stripe', 'payfast', 'bank_transfer', 'eft'
    
    # ===== PAYMENT REFERENCE =====
    payment_reference = db.Column(
        db.String(255),
        nullable=False,
        unique=True,
        index=True
    )
    # Stripe: 'pi_xxxxx' or 'ch_xxxxx'
    # PayFast: 'm_xxxxx' or payment ID
    
    # ===== STATUS TRACKING =====
    status = db.Column(
        db.String(20),
        nullable=False,
        default='pending',
        index=True
    )
    # Valid values: pending, processing, completed, failed, refunded
    
    # ===== GATEWAY RESPONSE =====
    gateway_response = db.Column(
        db.JSON,
        default=None
    )
    # Full API response from payment gateway (for debugging)
    
    # ===== REFUND TRACKING =====
    refund_amount = db.Column(
        db.Numeric(10, 2),
        nullable=False,
        default=0.00
    )
    
    refund_reason = db.Column(
        db.Text,
        default=None
    )
    
    # ===== TIMESTAMPS =====
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )
    
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # ===== RELATIONSHIPS =====
    order = db.relationship(
        'Order',
        backref=db.backref('transaction', uselist=False, cascade='all, delete-orphan')
    )
    
    # ===== VALIDATORS =====
    @validates('amount')
    def validate_amount(self, key, value):
        """Ensure amount is positive (> 0)"""
        if value is None:
            raise ValueError("Amount cannot be None")
        # Convert to Decimal for comparison
        amount_val = Decimal(str(value)) if not isinstance(value, Decimal) else value
        if amount_val <= 0:
            raise ValueError("Amount must be greater than 0")
        return value
    
    # ===== METHODS =====
    
    def is_pending(self):
        """Check if transaction is pending"""
        return self.status == 'pending'
    
    def is_completed(self):
        """Check if transaction is completed"""
        return self.status == 'completed'
    
    def is_failed(self):
        """Check if transaction failed"""
        return self.status == 'failed'
    
    def is_refunded(self):
        """Check if transaction was refunded"""
        return self.status == 'refunded'
    
    def mark_processing(self):
        """Mark transaction as processing"""
        self.status = 'processing'
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def mark_completed(self):
        """Mark transaction as completed"""
        self.status = 'completed'
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def mark_failed(self):
        """Mark transaction as failed"""
        self.status = 'failed'
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def refund(self, amount, reason):
        """Record a refund"""
        self.status = 'refunded'
        self.refund_amount = amount
        self.refund_reason = reason
        self.updated_at = datetime.now(timezone.utc)
        db.session.commit()
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'amount': float(self.amount),
            'payment_method': self.payment_method,
            'payment_reference': self.payment_reference,
            'status': self.status,
            'refund_amount': float(self.refund_amount),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Invoice(db.Model):
    __tablename__ = 'invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Invoice Details
    issue_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    tax_amount = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    paid_amount = db.Column(db.Numeric(10, 2), default=0, nullable=False)
    
    # Invoice Status: draft, sent, viewed, partial, paid, overdue, cancelled
    status = db.Column(db.String(20), default='draft', nullable=False)
    
    # Notes and details
    notes = db.Column(db.Text)
    terms = db.Column(db.Text)
    
    # File storage (PDF path)
    pdf_path = db.Column(db.String(255))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    customer = db.relationship('Customer', backref='invoices')
    order = db.relationship('Order', backref='invoices')
    payments = db.relationship('InvoicePayment', backref='invoice', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'

    def is_overdue(self):
        """Check if invoice is overdue"""
        if self.status == 'paid':
            return False
        return datetime.utcnow() > self.due_date

    def remaining_balance(self):
        """Calculate remaining balance"""
        return float(self.total_amount) - float(self.paid_amount)

    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'customer_id': self.customer_id,
            'order_id': self.order_id,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'total_amount': float(self.total_amount),
            'paid_amount': float(self.paid_amount),
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class InvoicePayment(db.Model):
    __tablename__ = 'invoice_payments'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoices.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # stripe, payfast, bank_transfer, etc
    transaction_id = db.Column(db.String(255), unique=True)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<InvoicePayment {self.id}>'






