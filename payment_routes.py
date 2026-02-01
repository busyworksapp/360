#!/usr/bin/env python
"""
Payment Processing Routes

This module provides Flask routes for payment processing:
- Payment method selection
- Stripe payment processing
- PayFast payment processing
- Webhook callbacks from both gateways
- Payment status checking
- Error handling and validation

Production-ready payment processing with dual gateway support.
Author: Barron CMS Payment Integration
"""

import logging
from datetime import datetime, timezone
from functools import wraps

from flask import (
    Blueprint, request, jsonify, render_template, redirect, url_for,
    session
)
from flask_login import login_required, current_user

from models import Order, Transaction, db
from stripe_service import StripePayment, StripePaymentError
from payfast_service import PayFastPayment, PayFastPaymentError
from email_service import EmailService
from config import Config

# Get config values
SMTP_SERVER = Config.MAIL_SERVER
SMTP_PORT = Config.MAIL_PORT
SENDER_EMAIL = Config.MAIL_USERNAME
SENDER_PASSWORD = Config.MAIL_PASSWORD
COMPANY_NAME = Config.MAIL_FROM_NAME
COMPANY_EMAIL = Config.CONTACT_EMAIL
COMPANY_PHONE = '+27 64 902 4363'

# Create blueprint
payment_bp = Blueprint(
    'payment',
    __name__,
    url_prefix='/payment'
)

# Configure logging
logger = logging.getLogger(__name__)

# Rate limiting storage (in production, use Redis)
rate_limit_store = {}

# Initialize email service
try:
    email_service = EmailService(
        smtp_server=SMTP_SERVER,
        smtp_port=SMTP_PORT,
        sender_email=SENDER_EMAIL,
        sender_password=SENDER_PASSWORD
    )
except Exception as e:
    logger.warning(f"Email service initialization failed: {str(e)}")
    email_service = None


def rate_limit(max_calls=10, time_window=60):
    """
    Simple rate limiter decorator
    
    Args:
        max_calls: Maximum calls allowed
        time_window: Time window in seconds
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client identifier
            client_id = request.remote_addr
            key = f"{client_id}:{f.__name__}"
            
            # Check rate limit
            now = datetime.now(timezone.utc)
            if key in rate_limit_store:
                calls, timestamp = rate_limit_store[key]
                if (now - timestamp).total_seconds() < time_window:
                    if calls >= max_calls:
                        logger.warning(
                            f"Rate limit exceeded for {client_id}"
                        )
                        return jsonify(
                            {'error': 'Too many requests'}
                        ), 429
                    calls += 1
                else:
                    calls = 1
                    timestamp = now
            else:
                calls = 1
                timestamp = now
            
            rate_limit_store[key] = (calls, timestamp)
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


# ============================================================================
# Payment Method Selection Routes
# ============================================================================

@payment_bp.route('/select', methods=['GET', 'POST'])
@login_required
@rate_limit(max_calls=20)
def select_payment_method():
    """
    Display payment method selection
    
    GET: Show payment method selection page
    POST: Process payment method selection
    """
    if request.method == 'GET':
        return render_template('payment/select_method.html')
    
    # POST request - process payment method selection
    try:
        order_id = request.form.get('order_id', type=int)
        payment_method = request.form.get('payment_method', '').lower()
        
        if not order_id or not payment_method:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if payment_method not in ['stripe', 'payfast']:
            return jsonify({'error': 'Invalid payment method'}), 400
        
        # Get order
        order = Order.query.get_or_404(order_id)
        
        # Verify ownership
        if order.customer_id != current_user.id:
            return jsonify({'error': 'Not authorized'}), 403
        
        # Verify order status
        if order.payment_status != 'pending':
            return jsonify(
                {'error': 'Order payment already processed'}
            ), 400
        
        # Store in session for later use
        session['payment_order_id'] = order_id
        session['payment_method'] = payment_method
        
        logger.info(
            f"Customer {current_user.id} selected {payment_method} "
            f"for order {order_id}"
        )
        
        # Redirect to appropriate payment processor
        if payment_method == 'stripe':
            return redirect(url_for('payment.process_stripe'))
        else:
            return redirect(url_for('payment.process_payfast'))
    
    except Exception as e:
        logger.error(f"Error in select_payment_method: {str(e)}")
        return jsonify({'error': 'Payment method selection failed'}), 500


# ============================================================================
# Stripe Payment Routes
# ============================================================================

@payment_bp.route('/process-stripe', methods=['GET', 'POST'])
@login_required
@rate_limit(max_calls=10)
def process_stripe():
    """
    Process Stripe payment
    
    GET: Display Stripe checkout page
    POST: Create Stripe payment intent
    """
    try:
        # Get order ID from session or request
        order_id = session.get('payment_order_id') or \
            request.form.get('order_id', type=int)
        
        if not order_id:
            return jsonify({'error': 'No order specified'}), 400
        
        # Get order
        order = Order.query.get_or_404(order_id)
        
        # Verify ownership
        if order.customer_id != current_user.id:
            return jsonify({'error': 'Not authorized'}), 403
        
        if request.method == 'GET':
            return render_template('payment/stripe_checkout.html', order=order)
        
        # POST request - create payment intent
        try:
            stripe = StripePayment()
            intent = stripe.create_payment_intent(
                order_id=order.id,
                amount=float(order.total_amount),
                currency='usd',
                description=f'Order #{order.order_number}',
                customer_email=current_user.email,
                metadata={
                    'customer_id': str(current_user.id),
                    'customer_name': current_user.name
                }
            )
            
            logger.info(
                f"Created Stripe payment intent for order {order.id}: "
                f"${order.total_amount}"
            )
            
            return jsonify({
                'success': True,
                'client_secret': intent['client_secret'],
                'amount': intent['amount'],
                'currency': intent['currency']
            })
        
        except StripePaymentError as e:
            logger.error(f"Stripe payment error: {str(e)}")
            return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        logger.error(f"Error in process_stripe: {str(e)}")
        return jsonify({'error': 'Payment processing failed'}), 500


# ============================================================================
# PayFast Payment Routes
# ============================================================================

@payment_bp.route('/process-payfast', methods=['GET', 'POST'])
@login_required
@rate_limit(max_calls=10)
def process_payfast():
    """
    Process PayFast payment
    
    GET: Display PayFast redirect page
    POST: Create PayFast payment request and redirect
    """
    try:
        # Get order ID from session or request
        order_id = session.get('payment_order_id') or \
            request.form.get('order_id', type=int)
        
        if not order_id:
            return jsonify({'error': 'No order specified'}), 400
        
        # Get order
        order = Order.query.get_or_404(order_id)
        
        # Verify ownership
        if order.customer_id != current_user.id:
            return jsonify({'error': 'Not authorized'}), 403
        
        if request.method == 'GET':
            return render_template('payment/payfast_checkout.html', order=order)
        
        # POST request - create payment request and redirect
        try:
            payfast = PayFastPayment()
            result = payfast.create_payment_request(
                order_id=order.id,
                amount=float(order.total_amount),
                customer_name=current_user.name,
                customer_email=current_user.email,
                description=f'Order #{order.order_number}'
            )
            
            logger.info(
                f"Created PayFast payment request for order {order.id}: "
                f"R{order.total_amount}"
            )
            
            # Return payment URL for redirect
            return jsonify({
                'success': True,
                'payment_url': result['payment_url']
            })
        
        except PayFastPaymentError as e:
            logger.error(f"PayFast payment error: {str(e)}")
            return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        logger.error(f"Error in process_payfast: {str(e)}")
        return jsonify({'error': 'Payment processing failed'}), 500


# ============================================================================
# Payment Status Route
# ============================================================================

@payment_bp.route('/status', methods=['GET'])
@login_required
@rate_limit(max_calls=20)
def payment_status():
    """
    Display payment status after return from payment gateway
    
    Query params:
    - order_id: Order ID
    - status: Payment status (COMPLETE, FAILED, etc.)
    """
    try:
        order_id = request.args.get('order_id', type=int) or \
            session.get('payment_order_id')
        status = request.args.get('status', '').upper()
        
        if not order_id:
            return jsonify({'error': 'No order specified'}), 400
        
        # Get order
        order = Order.query.get_or_404(order_id)
        
        # Verify ownership
        if order.customer_id != current_user.id:
            return jsonify({'error': 'Not authorized'}), 403
        
        # Get latest transaction
        transaction = Transaction.query.filter_by(
            order_id=order.id
        ).order_by(Transaction.created_at.desc()).first()
        
        # Determine status display
        if order.payment_status == 'confirmed':
            page_status = 'success'
            message = 'Payment completed successfully!'
        elif order.payment_status == 'failed':
            page_status = 'failed'
            message = 'Payment failed. Please try again.'
        elif order.payment_status == 'pending':
            page_status = 'pending'
            message = 'Payment is being processed. Please wait.'
        else:
            page_status = 'unknown'
            message = 'Payment status is unknown.'
        
        logger.info(
            f"Payment status page viewed for order {order.id}: "
            f"{page_status}"
        )
        
        try:
            return render_template(
                'payment/status.html',
                order=order,
                transaction=transaction,
                status=page_status,
                message=message
            )
        except Exception:
            # If template rendering fails, return JSON response
            return jsonify({
                'success': True,
                'status': page_status,
                'message': message,
                'order_id': order.id,
                'payment_status': order.payment_status
            })
    
    except Exception as e:
        logger.error(f"Error in payment_status: {str(e)}")
        return jsonify({'error': 'Payment status check failed'}), 500


# ============================================================================
# Webhook Routes
# ============================================================================

@payment_bp.route('/webhooks/stripe', methods=['POST'])
@rate_limit(max_calls=100)
def stripe_webhook():
    """
    Handle Stripe webhook events
    
    Events:
    - payment_intent.succeeded
    - payment_intent.payment_failed
    - charge.refunded
    """
    try:
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('X-Stripe-Signature')
        
        if not sig_header:
            logger.warning("Stripe webhook received without signature")
            return jsonify({'error': 'Missing signature'}), 400
        
        try:
            stripe = StripePayment()
            result = stripe.handle_webhook(payload, sig_header)
            
            logger.info(
                f"Stripe webhook processed: {result['event_type']} "
                f"for order {result.get('order_id')}"
            )
            
            # Send notification emails based on event type
            event_type = result.get('event_type')
            order_id = result.get('order_id')
            
            if order_id and email_service:
                order = db.session.get(Order, order_id)
                if order:
                    # Get customer email
                    if hasattr(order, 'customer') and order.customer:
                        customer_email = order.customer.email
                        customer_name = order.customer.name
                    else:
                        customer_email = order.customer_email if \
                            hasattr(order, 'customer_email') else None
                        customer_name = order.customer_name if \
                            hasattr(order, 'customer_name') else "Customer"
                    
                    if customer_email:
                        # Handle payment success
                        if event_type == 'payment_intent.succeeded':
                            transaction = db.session.get(
                                Transaction,
                                result.get('transaction_id')
                            )
                            if transaction:
                                email_service.\
                                    send_payment_confirmation(
                                        recipient_email=customer_email,
                                        recipient_name=customer_name,
                                        transaction_id=transaction.id,
                                        amount=transaction.amount,
                                        currency='ZAR',
                                        payment_method='Stripe',
                                        company_name=COMPANY_NAME,
                                        company_email=COMPANY_EMAIL,
                                        company_phone=COMPANY_PHONE
                                    )
                        
                        # Handle payment failure
                        elif event_type == 'payment_intent.payment_failed':
                            error_msg = result.get(
                                'error_message',
                                'Payment processing failed'
                            )
                            retry_url = (
                                f"{request.host_url.rstrip('/')}"
                                f"/payment/select?order={order_id}"
                            )
                            email_service.\
                                send_payment_failed_email(
                                    recipient_email=customer_email,
                                    recipient_name=customer_name,
                                    order_number=order.order_number,
                                    error_message=error_msg,
                                    company_name=COMPANY_NAME,
                                    company_email=COMPANY_EMAIL,
                                    company_phone=COMPANY_PHONE,
                                    retry_url=retry_url
                                )
                        
                        # Handle refund
                        elif event_type == 'charge.refunded':
                            transaction = db.session.get(
                                Transaction,
                                result.get('transaction_id')
                            )
                            if transaction:
                                refund_amount = (
                                    transaction.refund_amount
                                )
                                refund_reason = (
                                    transaction.refund_reason or
                                    'Refund processed'
                                )
                                email_service.send_refund_email(
                                    recipient_email=customer_email,
                                    recipient_name=customer_name,
                                    order_number=order.order_number,
                                    transaction_id=transaction.id,
                                    refund_amount=refund_amount,
                                    currency='ZAR',
                                    refund_reason=refund_reason,
                                    company_name=COMPANY_NAME,
                                    company_email=COMPANY_EMAIL,
                                    company_phone=COMPANY_PHONE
                                )
            
            return jsonify({
                'success': True,
                'event_id': result['event_id'],
                'event_type': result['event_type']
            }), 200
        
        except StripePaymentError as e:
            logger.error(f"Stripe webhook error: {str(e)}")
            return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        logger.error(f"Error in stripe_webhook: {str(e)}")
        return jsonify({'error': 'Webhook processing failed'}), 500


@payment_bp.route('/webhooks/payfast', methods=['POST'])
@rate_limit(max_calls=100)
def payfast_webhook():
    """
    Handle PayFast payment callback
    
    Receives POST data from PayFast with payment status
    """
    try:
        try:
            payfast = PayFastPayment()
            result = payfast.handle_callback(request.form)
            
            logger.info(
                f"PayFast callback processed: {result['status']} "
                f"for order {result['order_id']}"
            )
            
            # Send notification emails based on payment status
            status = result.get('status')
            order_id = result.get('order_id')
            
            if order_id and email_service:
                order = db.session.get(Order, order_id)
                if order:
                    # Get customer email
                    if hasattr(order, 'customer') and order.customer:
                        customer_email = order.customer.email
                        customer_name = order.customer.name
                    else:
                        customer_email = order.customer_email if \
                            hasattr(order, 'customer_email') else None
                        customer_name = order.customer_name if \
                            hasattr(order, 'customer_name') else "Customer"
                    
                    if customer_email:
                        # Handle payment success
                        if status == 'completed':
                            transaction = db.session.get(
                                Transaction,
                                result.get('transaction_id')
                            )
                            if transaction:
                                email_service.\
                                    send_payment_confirmation(
                                        recipient_email=customer_email,
                                        recipient_name=customer_name,
                                        transaction_id=transaction.id,
                                        amount=transaction.amount,
                                        currency='ZAR',
                                        payment_method='PayFast',
                                        company_name=COMPANY_NAME,
                                        company_email=COMPANY_EMAIL,
                                        company_phone=COMPANY_PHONE
                                    )
                        
                        # Handle payment failure
                        elif status in ['failed', 'cancelled']:
                            error_msg = 'Payment was not completed'
                            if status == 'cancelled':
                                error_msg = 'Payment was cancelled'
                            
                            retry_url = (
                                f"{request.host_url.rstrip('/')}"
                                f"/payment/select?order={order_id}"
                            )
                            email_service.\
                                send_payment_failed_email(
                                    recipient_email=customer_email,
                                    recipient_name=customer_name,
                                    order_number=order.order_number,
                                    error_message=error_msg,
                                    company_name=COMPANY_NAME,
                                    company_email=COMPANY_EMAIL,
                                    company_phone=COMPANY_PHONE,
                                    retry_url=retry_url
                                )
            
            # PayFast expects 'success' in response
            return 'success', 200
        
        except PayFastPaymentError as e:
            logger.error(f"PayFast callback error: {str(e)}")
            return 'error', 400
    
    except Exception as e:
        logger.error(f"Error in payfast_webhook: {str(e)}")
        return 'error', 500


# ============================================================================
# Admin Routes
# ============================================================================

@payment_bp.route('/admin/transactions', methods=['GET'])
@login_required
@rate_limit(max_calls=30)
def admin_transactions_list():
    """
    Display list of all transactions (admin only)
    
    Query params:
    - gateway: Filter by payment gateway (stripe, payfast)
    - status: Filter by transaction status (completed, failed, pending)
    - order_by: Sort order (date, amount, status)
    - search: Search by order number, customer name, or transaction ID
    - date_from: Filter from date (YYYY-MM-DD)
    - date_to: Filter to date (YYYY-MM-DD)
    - page: Page number for pagination
    """
    try:
        # Check admin permission
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        # Get filter parameters
        gateway = request.args.get('gateway', '').lower()
        status = request.args.get('status', '').lower()
        order_by = request.args.get('order_by', 'date').lower()
        search = request.args.get('search', '').strip()
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        page = request.args.get('page', 1, type=int)
        
        # Build query
        query = Transaction.query
        
        # Apply filters
        if gateway and gateway in ['stripe', 'payfast']:
            query = query.filter_by(payment_method=gateway)
        
        if status and status in ['completed', 'failed', 'pending', 'refunded']:
            query = query.filter_by(status=status)
        
        # Search filter (order number, customer, transaction ID)
        if search:
            from models import Order
            # Search in transactions by ID or reference
            search_filter = (
                Transaction.id.ilike(f'%{search}%') |
                Transaction.payment_reference.ilike(f'%{search}%')
            )
            # Also search in related orders
            query = query.filter(
                (search_filter) |
                (Transaction.order_id.in_(
                    Order.query.filter(
                        (Order.order_number.ilike(f'%{search}%')) |
                        (Order.customer_email.ilike(f'%{search}%'))
                    ).with_entities(Order.id)
                ))
            )
        
        # Date range filter
        if date_from:
            try:
                from_date = datetime.strptime(
                    date_from,
                    '%Y-%m-%d'
                )
                query = query.filter(
                    Transaction.created_at >= from_date
                )
            except ValueError:
                logger.warning(f"Invalid date_from: {date_from}")
        
        if date_to:
            try:
                to_date = datetime.strptime(
                    date_to,
                    '%Y-%m-%d'
                )
                # Add 1 day to include end of day
                to_date = to_date.replace(
                    hour=23,
                    minute=59,
                    second=59
                )
                query = query.filter(
                    Transaction.created_at <= to_date
                )
            except ValueError:
                logger.warning(f"Invalid date_to: {date_to}")
        
        # Order by
        if order_by == 'amount':
            query = query.order_by(Transaction.amount.desc())
        elif order_by == 'status':
            query = query.order_by(Transaction.status.asc())
        else:  # date
            query = query.order_by(Transaction.created_at.desc())
        
        # Paginate
        transactions = query.paginate(page=page, per_page=20)
        
        logger.info(
            f"Admin viewed transactions list: {len(transactions.items)} "
            f"transactions (page {page})"
        )
        
        try:
            return render_template(
                'payment/admin_transactions.html',
                transactions=transactions,
                current_gateway=gateway,
                current_status=status,
                current_sort=order_by,
                search_query=search,
                date_from=date_from,
                date_to=date_to
            )
        except Exception:
            # If template rendering fails, return JSON response
            return jsonify({
                'success': True,
                'transactions': [
                    {
                        'id': tx.id,
                        'order_id': tx.order_id,
                        'amount': str(tx.amount),
                        'payment_method': tx.payment_method,
                        'status': tx.status,
                        'created_at': tx.created_at.isoformat() if tx.created_at else None
                    }
                    for tx in transactions.items
                ],
                'page': page,
                'total_pages': transactions.pages,
                'total_items': transactions.total
            })
    
    except Exception as e:
        logger.error(
            f"Error in admin_transactions_list: {str(e)}"
        )
        return jsonify(
            {'error': 'Error retrieving transactions'}
        ), 500


@payment_bp.route('/admin/transactions/<int:tx_id>', methods=['GET'])
@login_required
@rate_limit(max_calls=30)
def admin_transaction_detail(tx_id):
    """Display transaction details (admin only)"""
    try:
        # Check admin permission
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        transaction = Transaction.query.get_or_404(tx_id)
        order = transaction.order
        
        logger.info(f"Admin viewed transaction {tx_id} details")
        
        return render_template(
            'payment/admin_transaction_detail.html',
            transaction=transaction,
            order=order
        )
    
    except Exception as e:
        logger.error(f"Error in admin_transaction_detail: {str(e)}")
        return jsonify({'error': 'Error retrieving transaction'}), 500


@payment_bp.route('/admin/transactions/<int:tx_id>/refund',
                   methods=['POST'])
@login_required
@rate_limit(max_calls=10)
def admin_refund_transaction(tx_id):
    """
    Process refund for a transaction (admin only)
    
    POST params:
    - amount: Refund amount (optional, full refund if not specified)
    - reason: Refund reason
    """
    try:
        # Check admin permission
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        transaction = Transaction.query.get_or_404(tx_id)
        
        if transaction.payment_method not in ['stripe', 'payfast']:
            return jsonify({'error': 'Unknown payment gateway'}), 400
        
        amount = request.form.get('amount', type=float)
        reason = request.form.get(
            'reason',
            'requested_by_admin'
        )
        
        try:
            if transaction.payment_method == 'stripe':
                stripe = StripePayment()
                result = stripe.refund_payment(
                    transaction.payment_reference,
                    amount=int(amount * 100) if amount else None,
                    reason=reason
                )
            else:  # payfast
                # PayFast doesn't support direct refunds through API
                # Must be done manually in PayFast dashboard
                logger.warning(
                    f"PayFast refund requested for {tx_id}. "
                    f"Must be processed manually."
                )
                return jsonify({
                    'error': 'PayFast refunds must be processed manually '
                             'in the PayFast dashboard'
                }), 400
            
            logger.info(
                f"Refund processed for transaction {tx_id}: "
                f"{result.get('amount', amount)}"
            )
            
            # Send refund notification email
            refund_amount = result.get('amount', amount)
            order = db.session.get(Order, transaction.order_id)
            
            if order and email_service:
                # Get customer email
                if hasattr(order, 'customer') and order.customer:
                    customer_email = order.customer.email
                    customer_name = order.customer.name
                else:
                    customer_email = order.customer_email if \
                        hasattr(order, 'customer_email') else None
                    customer_name = order.customer_name if \
                        hasattr(order, 'customer_name') else "Customer"
                
                if customer_email:
                    email_service.send_refund_email(
                        recipient_email=customer_email,
                        recipient_name=customer_name,
                        order_number=order.order_number,
                        transaction_id=transaction.id,
                        refund_amount=refund_amount,
                        currency='ZAR',
                        refund_reason=reason,
                        company_name=COMPANY_NAME,
                        company_email=COMPANY_EMAIL,
                        company_phone=COMPANY_PHONE
                    )
            
            return jsonify({
                'success': True,
                'refund_id': result.get('refund_id'),
                'amount': result.get('amount', amount)
            })
        
        except (StripePaymentError, PayFastPaymentError) as e:
            logger.error(f"Refund error: {str(e)}")
            return jsonify({'error': str(e)}), 400
    
    except Exception as e:
        logger.error(f"Error in admin_refund_transaction: {str(e)}")
        return jsonify({'error': 'Refund processing failed'}), 500


@payment_bp.route('/admin/transactions/bulk-action', methods=['POST'])
@login_required
@rate_limit(max_calls=20)
def admin_bulk_action():
    """
    Handle bulk actions on multiple transactions
    
    POST data:
    - action: Action to perform (export, mark_complete, etc.)
    - transaction_ids: Comma-separated transaction IDs
    """
    try:
        # Check admin permission
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        action = request.form.get('action', '').lower()
        tx_ids = request.form.get('transaction_ids', '')
        
        if not tx_ids:
            return jsonify({'error': 'No transactions selected'}), 400
        
        # Parse transaction IDs
        try:
            transaction_ids = [
                int(id.strip()) for id in tx_ids.split(',')
                if id.strip().isdigit()
            ]
        except (ValueError, AttributeError):
            return jsonify(
                {'error': 'Invalid transaction IDs'}
            ), 400
        
        if not transaction_ids:
            return jsonify({'error': 'No valid transactions'}), 400
        
        # Limit bulk actions to 100 transactions at a time
        if len(transaction_ids) > 100:
            return jsonify({
                'error': 'Too many transactions (max 100)'
            }), 400
        
        # Process based on action
        if action == 'export':
            # Return CSV data of selected transactions
            import csv
            from io import StringIO
            
            transactions = Transaction.query.filter(
                Transaction.id.in_(transaction_ids)
            ).all()
            
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow([
                'ID', 'Order ID', 'Amount', 'Currency',
                'Method', 'Status', 'Date', 'Customer Email'
            ])
            
            for tx in transactions:
                order = db.session.get(Order, tx.order_id)
                customer_email = (
                    order.customer.email
                    if hasattr(order, 'customer') and order.customer
                    else order.customer_email
                    if hasattr(order, 'customer_email')
                    else 'N/A'
                )
                writer.writerow([
                    tx.id,
                    tx.order_id,
                    float(tx.amount),
                    'ZAR',
                    tx.payment_method,
                    tx.status,
                    tx.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    customer_email
                ])
            
            logger.info(
                f"Admin exported {len(transactions)} transactions"
            )
            
            return {
                'success': True,
                'data': output.getvalue(),
                'filename': 'transactions.csv'
            }
        
        elif action == 'status-check':
            # Check current status of multiple transactions
            transactions = Transaction.query.filter(
                Transaction.id.in_(transaction_ids)
            ).all()
            
            status_summary = {
                'completed': 0,
                'pending': 0,
                'failed': 0,
                'refunded': 0
            }
            
            for tx in transactions:
                if tx.status in status_summary:
                    status_summary[tx.status] += 1
            
            logger.info(
                f"Admin checked status of "
                f"{len(transactions)} transactions"
            )
            
            return jsonify({
                'success': True,
                'total': len(transactions),
                'statuses': status_summary
            })
        
        else:
            return jsonify({
                'error': f'Unknown action: {action}'
            }), 400
    
    except Exception as e:
        logger.error(f"Error in admin_bulk_action: {str(e)}")
        return jsonify({'error': 'Bulk action failed'}), 500


# ============================================================================
# Error Handlers
# ============================================================================

@payment_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@payment_bp.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


# ============================================================================
# Registration Helper
# ============================================================================

def register_payment_routes(app):
    """
    Register payment routes with Flask app
    
    Usage:
    from payment_routes import register_payment_routes
    register_payment_routes(app)
    """
    app.register_blueprint(payment_bp)
    logger.info("Payment routes registered successfully")
