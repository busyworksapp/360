import stripe
import hashlib
import requests
from flask import current_app, url_for
from models import Transaction, Order, db
from datetime import datetime, timezone
import uuid

class StripePayment:
    def __init__(self):
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    
    def create_payment_intent(self, order_id, amount, currency='usd', description=''):
        """Create a Stripe payment intent for an order"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Stripe uses cents
                currency=currency,
                metadata={'order_id': order_id},
                description=description,
            )
            
            transaction = Transaction(
                order_id=order_id,
                amount=amount,
                payment_method='stripe',
                payment_reference=intent.id,
                status='pending',
                gateway_response={'intent_id': intent.id, 'client_secret': intent.client_secret}
            )
            db.session.add(transaction)
            db.session.commit()
            
            return {'success': True, 'intent_id': intent.id, 'client_secret': intent.client_secret}
        except Exception as e:
            current_app.logger.error(f"Stripe error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def confirm_payment(self, payment_intent_id):
        """Confirm a Stripe payment"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            transaction = Transaction.query.filter_by(payment_reference=payment_intent_id).first()
            if transaction:
                if intent.status == 'succeeded':
                    transaction.status = 'completed'
                    transaction.mark_completed()
                    # Update order status
                    order = db.session.get(Order, transaction.order_id)
                    if order:
                        order.payment_method = 'stripe'
                        order.payment_reference = payment_intent_id
                        order.payment_confirmed_at = datetime.now(timezone.utc)
                        db.session.commit()
                else:
                    transaction.status = 'failed'
                    transaction.mark_failed()
            
            return {'success': True, 'status': intent.status}
        except Exception as e:
            current_app.logger.error(f"Stripe confirmation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def handle_webhook(self, event):
        """Handle Stripe webhook events"""
        try:
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                transaction = Transaction.query.filter_by(payment_reference=payment_intent['id']).first()
                if transaction:
                    transaction.status = 'completed'
                    transaction.mark_completed()
                    order = db.session.get(Order, transaction.order_id)
                    if order:
                        order.payment_confirmed_at = datetime.now(timezone.utc)
                        db.session.commit()
            
            elif event['type'] == 'payment_intent.payment_failed':
                payment_intent = event['data']['object']
                transaction = Transaction.query.filter_by(payment_reference=payment_intent['id']).first()
                if transaction:
                    transaction.status = 'failed'
                    transaction.mark_failed()
            
            return {'success': True}
        except Exception as e:
            current_app.logger.error(f"Webhook error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def refund_payment(self, payment_intent_id, amount=None, reason=''):
        """Refund a Stripe payment"""
        try:
            transaction = Transaction.query.filter_by(payment_reference=payment_intent_id).first()
            if not transaction:
                return {'success': False, 'error': 'Transaction not found'}
            
            refund_amount = amount or transaction.amount
            
            refund = stripe.Refund.create(
                payment_intent=payment_intent_id,
                amount=int(refund_amount * 100) if amount else None,
            )
            
            transaction.refund(refund_amount, reason or 'Refund requested')
            
            return {'success': True, 'refund_id': refund.id}
        except Exception as e:
            current_app.logger.error(f"Refund error: {str(e)}")
            return {'success': False, 'error': str(e)}

class PayFastPayment:
    def __init__(self):
        self.merchant_id = current_app.config.get('PAYFAST_MERCHANT_ID')
        self.merchant_key = current_app.config.get('PAYFAST_MERCHANT_KEY')
        self.passphrase = current_app.config.get('PAYFAST_PASSPHRASE')
        self.mode = current_app.config.get('PAYFAST_MODE', 'sandbox')
        
        if self.mode == 'live':
            self.process_url = 'https://www.payfast.co.za/eng/process'
        else:
            self.process_url = 'https://sandbox.payfast.co.za/eng/process'
    
    def generate_signature(self, data_dict):
        """Generate PayFast signature"""
        data_string = ''
        for key in sorted(data_dict.keys()):
            data_string += f"{key}={requests.utils.quote_plus(str(data_dict[key]))}&"
        
        data_string = data_string[:-1]
        
        if self.passphrase:
            data_string += f"&passphrase={requests.utils.quote_plus(self.passphrase)}"
        
        return hashlib.md5(data_string.encode()).hexdigest()
    
    def create_payment_request(self, order_id, amount, customer_email='', description=''):
        """Create a PayFast payment request"""
        try:
            payment_reference = f'PF-{uuid.uuid4().hex[:12].upper()}'
            
            data = {
                'merchant_id': self.merchant_id,
                'merchant_key': self.merchant_key,
                'return_url': url_for('payment_success', _external=True),
                'cancel_url': url_for('payment_cancel', _external=True),
                'notify_url': url_for('payfast_webhook', _external=True),
                'email_address': customer_email,
                'm_payment_id': payment_reference,
                'amount': f'{amount:.2f}',
                'item_name': description or f'Payment for Order {order_id}',
                'custom_str1': str(order_id),
            }
            
            signature = self.generate_signature(data)
            data['signature'] = signature
            
            transaction = Transaction(
                order_id=order_id,
                amount=amount,
                payment_method='payfast',
                payment_reference=payment_reference,
                status='pending',
                gateway_response={'form_data': data}
            )
            db.session.add(transaction)
            db.session.commit()
            
            return {'success': True, 'data': data, 'url': self.process_url, 'payment_reference': payment_reference}
        except Exception as e:
            current_app.logger.error(f"PayFast error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def verify_signature(self, post_data):
        """Verify PayFast callback signature"""
        try:
            signature = post_data.get('signature')
            
            data_dict = {k: v for k, v in post_data.items() if k != 'signature'}
            
            calculated_signature = self.generate_signature(data_dict)
            
            if signature != calculated_signature:
                return False
            
            return True
        except Exception as e:
            current_app.logger.error(f"Signature verification error: {str(e)}")
            return False
    
    def handle_callback(self, post_data):
        """Handle PayFast callback"""
        try:
            if not self.verify_signature(post_data):
                return {'success': False, 'error': 'Invalid signature'}
            
            payment_reference = post_data.get('m_payment_id')
            payment_status = post_data.get('payment_status')
            
            transaction = Transaction.query.filter_by(payment_reference=payment_reference).first()
            if transaction:
                if payment_status == 'COMPLETE':
                    transaction.status = 'completed'
                    transaction.mark_completed()
                    order = db.session.get(Order, transaction.order_id)
                    if order:
                        order.payment_method = 'payfast'
                        order.payment_reference = payment_reference
                        order.payment_confirmed_at = datetime.now(timezone.utc)
                        db.session.commit()
                else:
                    transaction.status = 'failed'
                    transaction.mark_failed()
                
                transaction.gateway_response = dict(post_data)
            
            return {'success': True}
        except Exception as e:
            current_app.logger.error(f"PayFast callback error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def check_status(self, payment_reference):
        """Check payment status"""
        try:
            transaction = Transaction.query.filter_by(payment_reference=payment_reference).first()
            if not transaction:
                return {'success': False, 'error': 'Payment not found'}
            
            return {
                'success': True,
                'status': transaction.status,
                'amount': float(transaction.amount),
                'created_at': transaction.created_at.isoformat()
            }
        except Exception as e:
            current_app.logger.error(f"Status check error: {str(e)}")
            return {'success': False, 'error': str(e)}

