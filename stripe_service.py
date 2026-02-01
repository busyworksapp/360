#!/usr/bin/env python
"""
Stripe Payment Gateway Integration

This module provides Stripe payment processing functionality:
- Create payment intents for checkout
- Confirm payments after client completion
- Handle webhook events from Stripe
- Process refunds

Production-ready Stripe integration with comprehensive error handling.
Author: Barron CMS Payment Integration
"""

import os
import json
import logging
from datetime import datetime, timezone
from decimal import Decimal

import stripe
from flask import current_app

from models import db, Transaction, Order

# Configure logging
logger = logging.getLogger(__name__)


class StripePaymentError(Exception):
    """Custom exception for Stripe payment errors"""
    pass


class StripePayment:
    """Stripe payment processing service"""

    def __init__(self):
        """Initialize Stripe with API key from config"""
        self.api_key = current_app.config.get('STRIPE_SECRET_KEY')
        self.webhook_secret = current_app.config.get(
            'STRIPE_WEBHOOK_SECRET'
        )
        
        if not self.api_key:
            raise StripePaymentError(
                "STRIPE_SECRET_KEY not configured in environment"
            )
        
        stripe.api_key = self.api_key
        self.gateway_name = 'stripe'

    def create_payment_intent(
        self,
        order_id,
        amount,
        currency='usd',
        description='',
        customer_email=None,
        metadata=None
    ):
        """
        Create a Stripe payment intent for checkout
        
        Args:
            order_id (int): Order ID to link with payment
            amount (Decimal/float): Amount in cents (e.g., 1000 for $10.00)
            currency (str): ISO 4217 currency code (default: 'usd')
            description (str): Payment description
            customer_email (str): Customer email for Stripe customer
            metadata (dict): Additional metadata to attach
            
        Returns:
            dict: Payment intent details {
                'id': client_secret,
                'client_secret': secret,
                'amount': amount,
                'currency': currency,
                'status': 'requires_payment_method'
            }
            
        Raises:
            StripePaymentError: If payment intent creation fails
        """
        try:
            # Validate amount
            if isinstance(amount, Decimal):
                amount_value = float(amount)
            else:
                amount_value = float(amount)
            
            if amount_value <= 0:
                error_msg = f"Invalid amount: {amount_value}. Amount must be greater than 0."
                logger.error(error_msg)
                raise StripePaymentError(error_msg)
            
            # Ensure amount is an integer (cents)
            if isinstance(amount, Decimal):
                amount_cents = int(amount * 100)
            else:
                amount_cents = int(float(amount) * 100)
            
            # Prepare metadata
            intent_metadata = {
                'order_id': str(order_id),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            if metadata:
                intent_metadata.update(metadata)
            
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                description=description,
                metadata=intent_metadata,
                receipt_email=customer_email,
                statement_descriptor='BARRON CMS'
            )
            
            logger.info(
                f"Created Stripe payment intent {intent.id} for order "
                f"{order_id}: ${amount_cents/100:.2f} {currency}"
            )
            
            return {
                'id': intent.id,
                'client_secret': intent.client_secret,
                'amount': amount_cents,
                'currency': currency,
                'status': intent.status
            }
            
        except Exception as e:
            # Handle Stripe API errors
            error_msg = f"Stripe error: {str(e)}"
            logger.error(error_msg)
            raise StripePaymentError(error_msg)

    def confirm_payment(self, payment_intent_id):
        """
        Confirm a Stripe payment after client-side processing
        
        Args:
            payment_intent_id (str): Stripe PaymentIntent ID
            
        Returns:
            dict: Payment confirmation {
                'success': bool,
                'intent_id': id,
                'status': status,
                'amount': amount,
                'receipt_url': url
            }
            
        Raises:
            StripePaymentError: If confirmation fails
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if intent.status not in ['succeeded', 'processing']:
                raise StripePaymentError(
                    f"Payment not completed. Status: {intent.status}"
                )
            
            order_id = intent.metadata.get('order_id')
            
            logger.info(
                f"Confirmed Stripe payment {payment_intent_id} for order "
                f"{order_id}. Status: {intent.status}"
            )
            
            return {
                'success': True,
                'intent_id': intent.id,
                'status': intent.status,
                'amount': intent.amount / 100,
                'receipt_url': intent.charges.data[0].receipt_url
                if intent.charges.data else None
            }
            
        except stripe.error.StripeError as e:
            error_msg = f"Payment confirmation error: {str(e)}"
            logger.error(error_msg)
            raise StripePaymentError(error_msg)

    def handle_webhook(self, event_json, signature):
        """
        Handle Stripe webhook events (payment_intent.succeeded, etc.)
        
        Args:
            event_json (str): Raw webhook JSON payload
            signature (str): X-Stripe-Signature header value
            
        Returns:
            dict: Webhook processing result {
                'success': bool,
                'event_id': id,
                'event_type': type,
                'order_id': id,
                'transaction_id': id
            }
            
        Raises:
            StripePaymentError: If webhook handling fails
        """
        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(
                event_json,
                signature,
                self.webhook_secret
            )
            
            event_type = event['type']
            logger.info(f"Received Stripe webhook: {event_type}")
            
            # Handle payment_intent.succeeded event
            if event_type == 'payment_intent.succeeded':
                return self._handle_payment_succeeded(event)
            
            # Handle payment_intent.payment_failed event
            elif event_type == 'payment_intent.payment_failed':
                return self._handle_payment_failed(event)
            
            # Handle charge.refunded event
            elif event_type == 'charge.refunded':
                return self._handle_charge_refunded(event)
            
            else:
                logger.warning(
                    f"Unhandled Stripe webhook event: {event_type}"
                )
                return {
                    'success': True,
                    'event_id': event['id'],
                    'event_type': event_type,
                    'handled': False
                }
            
        except ValueError as e:
            error_msg = f"Invalid webhook payload: {str(e)}"
            logger.error(error_msg)
            raise StripePaymentError(error_msg)
        
        except stripe.error.SignatureVerificationError as e:
            error_msg = f"Invalid webhook signature: {str(e)}"
            logger.error(error_msg)
            raise StripePaymentError(error_msg)

    def _handle_payment_succeeded(self, event):
        """Process payment_intent.succeeded webhook event"""
        try:
            intent = event['data']['object']
            payment_intent_id = intent['id']
            order_id = int(intent['metadata'].get('order_id', 0))
            
            # Find or create transaction
            transaction = Transaction.query.filter_by(
                payment_reference=payment_intent_id
            ).first()
            
            if not transaction:
                # Create new transaction record
                transaction = Transaction(
                    order_id=order_id,
                    amount=Decimal(str(intent['amount'] / 100)),
                    payment_method=self.gateway_name,
                    payment_reference=payment_intent_id,
                    status='completed',
                    gateway_response=json.dumps({
                        'intent_id': payment_intent_id,
                        'status': intent['status'],
                        'charges': len(intent.get('charges', {}).get('data', []))
                    })
                )
                db.session.add(transaction)
            else:
                # Update existing transaction
                transaction.status = 'completed'
                transaction.gateway_response = json.dumps({
                    'intent_id': payment_intent_id,
                    'status': intent['status']
                })
            
            # Update order with payment confirmation
            order = db.session.get(Order, order_id)
            if order:
                order.payment_method = self.gateway_name
                order.payment_reference = payment_intent_id
                order.payment_confirmed_at = datetime.now(timezone.utc)
                order.payment_status = 'confirmed'
            
            db.session.commit()
            
            logger.info(
                f"Payment succeeded for order {order_id}. "
                f"Transaction: {transaction.id}"
            )
            
            return {
                'success': True,
                'event_id': event['id'],
                'event_type': 'payment_intent.succeeded',
                'order_id': order_id,
                'transaction_id': transaction.id
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error handling payment succeeded: {str(e)}")
            raise StripePaymentError(str(e))

    def _handle_payment_failed(self, event):
        """Process payment_intent.payment_failed webhook event"""
        try:
            intent = event['data']['object']
            payment_intent_id = intent['id']
            order_id = int(intent['metadata'].get('order_id', 0))
            
            # Find or create transaction
            transaction = Transaction.query.filter_by(
                payment_reference=payment_intent_id
            ).first()
            
            if not transaction:
                transaction = Transaction(
                    order_id=order_id,
                    amount=Decimal(str(intent['amount'] / 100)),
                    payment_method=self.gateway_name,
                    payment_reference=payment_intent_id,
                    status='failed',
                    gateway_response=json.dumps({
                        'intent_id': payment_intent_id,
                        'status': intent['status'],
                        'last_payment_error': intent.get('last_payment_error')
                    })
                )
                db.session.add(transaction)
            else:
                transaction.status = 'failed'
                transaction.gateway_response = json.dumps({
                    'intent_id': payment_intent_id,
                    'status': intent['status'],
                    'error': intent.get('last_payment_error')
                })
            
            # Update order
            order = db.session.get(Order, order_id)
            if order:
                order.payment_status = 'failed'
            
            db.session.commit()
            
            logger.warning(
                f"Payment failed for order {order_id}. "
                f"Reason: {intent.get('last_payment_error')}"
            )
            
            return {
                'success': True,
                'event_id': event['id'],
                'event_type': 'payment_intent.payment_failed',
                'order_id': order_id,
                'transaction_id': transaction.id
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error handling payment failed: {str(e)}")
            raise StripePaymentError(str(e))

    def _handle_charge_refunded(self, event):
        """Process charge.refunded webhook event"""
        try:
            charge = event['data']['object']
            charge_id = charge['id']
            refund_amount = Decimal(str(charge['amount_refunded'] / 100))
            
            # Find transaction by charge ID or payment intent
            payment_intent_id = charge.get('payment_intent')
            transaction = Transaction.query.filter_by(
                payment_reference=payment_intent_id
            ).first()
            
            if transaction:
                transaction.status = 'refunded'
                transaction.refund_amount = refund_amount
                transaction.gateway_response = json.dumps({
                    'charge_id': charge_id,
                    'refund_amount': str(refund_amount),
                    'refund_reason': charge.get('refund_reason', 'N/A')
                })
                
                db.session.commit()
                
                logger.info(
                    f"Refund processed for transaction {transaction.id}. "
                    f"Amount: ${refund_amount}"
                )
            
            return {
                'success': True,
                'event_id': event['id'],
                'event_type': 'charge.refunded',
                'transaction_id': transaction.id if transaction else None,
                'refund_amount': str(refund_amount)
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error handling refund: {str(e)}")
            raise StripePaymentError(str(e))

    def refund_payment(
        self,
        payment_intent_id,
        amount=None,
        reason='requested_by_customer'
    ):
        """
        Refund a Stripe payment (full or partial)
        
        Args:
            payment_intent_id (str): Stripe PaymentIntent ID
            amount (int/None): Amount in cents. None for full refund.
            reason (str): Refund reason for Stripe
            
        Returns:
            dict: Refund confirmation {
                'success': bool,
                'refund_id': id,
                'amount': amount,
                'status': status,
                'reason': reason
            }
            
        Raises:
            StripePaymentError: If refund fails
        """
        try:
            # Get the payment intent
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            if not intent.charges.data:
                raise StripePaymentError(
                    f"No charges found for payment intent {payment_intent_id}"
                )
            
            # Get the charge ID
            charge_id = intent.charges.data[0].id
            
            # Create refund
            refund = stripe.Refund.create(
                charge=charge_id,
                amount=amount,
                reason=reason,
                metadata={'payment_intent': payment_intent_id}
            )
            
            # Update transaction record
            transaction = Transaction.query.filter_by(
                payment_reference=payment_intent_id
            ).first()
            
            if transaction:
                transaction.status = 'refunded'
                transaction.refund_amount = Decimal(
                    str(refund.amount / 100)
                )
                transaction.refund_reason = reason
                db.session.commit()
            
            logger.info(
                f"Refund {refund.id} processed for payment "
                f"{payment_intent_id}. Amount: ${refund.amount/100:.2f}"
            )
            
            return {
                'success': True,
                'refund_id': refund.id,
                'amount': refund.amount / 100,
                'status': refund.status,
                'reason': reason
            }
            
        except stripe.error.StripeError as e:
            error_msg = f"Refund error: {str(e)}"
            logger.error(error_msg)
            raise StripePaymentError(error_msg)
        
        except Exception as e:
            error_msg = f"Error processing refund: {str(e)}"
            logger.error(error_msg)
            raise StripePaymentError(error_msg)

    def get_payment_status(self, payment_intent_id):
        """
        Get current status of a Stripe payment
        
        Args:
            payment_intent_id (str): Stripe PaymentIntent ID
            
        Returns:
            dict: Payment status {
                'id': intent_id,
                'status': status,
                'amount': amount,
                'amount_received': amount_received,
                'currency': currency
            }
        """
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'id': intent.id,
                'status': intent.status,
                'amount': intent.amount / 100,
                'amount_received': intent.amount_received / 100,
                'currency': intent.currency,
                'charges': len(intent.charges.data) if intent.charges else 0
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Error getting payment status: {str(e)}")
            raise StripePaymentError(str(e))


def get_stripe_service():
    """Factory function to get StripePayment service"""
    return StripePayment()
