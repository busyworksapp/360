#!/usr/bin/env python
"""
PayFast Payment Gateway Integration

This module provides PayFast payment processing functionality:
- Create payment requests for checkout
- Verify payment signatures (security)
- Handle payment callbacks/notifications
- Check payment transaction status
- Support for South African payment methods

Production-ready PayFast integration for ZAR transactions.
Author: Barron CMS Payment Integration
"""

import os
import hashlib
import logging
from datetime import datetime, timezone
from decimal import Decimal
from urllib.parse import urlencode
import requests

from flask import current_app

from models import db, Transaction, Order

# Configure logging
logger = logging.getLogger(__name__)


class PayFastPaymentError(Exception):
    """Custom exception for PayFast payment errors"""
    pass


class PayFastPayment:
    """PayFast payment processing service"""

    # PayFast API endpoints
    SANDBOX_URL = 'https://sandbox.payfast.co.za/eng/process'
    LIVE_URL = 'https://www.payfast.co.za/eng/process'
    SANDBOX_API_URL = 'https://sandbox.payfast.co.za/api/query/transaction'
    LIVE_API_URL = 'https://api.payfast.co.za/query/transaction'

    def __init__(self):
        """Initialize PayFast with configuration from config"""
        self.merchant_id = current_app.config.get(
            'PAYFAST_MERCHANT_ID'
        )
        self.merchant_key = current_app.config.get(
            'PAYFAST_MERCHANT_KEY'
        )
        self.passphrase = current_app.config.get('PAYFAST_PASSPHRASE')
        self.mode = current_app.config.get('PAYFAST_MODE', 'sandbox')
        
        if not self.merchant_id or not self.merchant_key:
            raise PayFastPaymentError(
                "PayFast credentials not configured in environment"
            )
        
        self.gateway_name = 'payfast'
        self.base_url = (
            self.LIVE_URL if self.mode == 'live' else self.SANDBOX_URL
        )
        self.api_url = (
            self.LIVE_API_URL if self.mode == 'live'
            else self.SANDBOX_API_URL
        )

    def create_payment_request(
        self,
        order_id,
        amount,
        customer_name='',
        customer_email='',
        description=''
    ):
        """
        Create a PayFast payment request for redirect to PayFast
        
        Args:
            order_id (int): Order ID to link with payment
            amount (Decimal/float): Amount in ZAR
            customer_name (str): Customer name
            customer_email (str): Customer email
            description (str): Payment description
            
        Returns:
            dict: Payment request details {
                'success': True,
                'payment_url': url,
                'merchant_id': id,
                'reference': reference
            }
            
        Raises:
            PayFastPaymentError: If request creation fails
        """
        try:
            # Convert amount to cents (PayFast uses cents for ZAR)
            if isinstance(amount, Decimal):
                amount_cents = int(amount * 100)
            else:
                amount_cents = int(float(amount) * 100)
            
            # Create unique reference
            reference = f"ORD-{order_id}-{datetime.now(timezone.utc).timestamp()}"
            
            # Build payment data
            data = {
                'merchant_id': self.merchant_id,
                'merchant_key': self.merchant_key,
                'return_url': current_app.config.get(
                    'PAYFAST_RETURN_URL',
                    f'{current_app.config.get("BASE_URL", "http://localhost:5000")}/checkout/status'
                ),
                'cancel_url': current_app.config.get(
                    'PAYFAST_CANCEL_URL',
                    f'{current_app.config.get("BASE_URL", "http://localhost:5000")}/checkout'
                ),
                'notify_url': f'{current_app.config.get("BASE_URL", "http://localhost:5000")}/webhooks/payfast',
                'name_first': customer_name.split()[0] if customer_name else 'Customer',
                'name_last': ' '.join(customer_name.split()[1:]) if customer_name and len(customer_name.split()) > 1 else '',
                'email_address': customer_email,
                'amount': '{:.2f}'.format(amount_cents / 100),
                'm_payment_id': str(order_id),
                'item_name': description or f'Order #{order_id}',
                'item_description': f'Order #{order_id}',
            }
            
            # Add custom return data
            data['custom_str1'] = str(order_id)
            data['custom_str2'] = reference
            
            # Create signature
            signature = self._create_signature(data, 'request')
            data['signature'] = signature
            
            # Construct payment URL
            payment_url = f"{self.base_url}?{urlencode(data)}"
            
            logger.info(
                f"Created PayFast payment request for order {order_id}: "
                f"ZAR {amount_cents/100:.2f}, Reference: {reference}"
            )
            
            return {
                'success': True,
                'payment_url': payment_url,
                'merchant_id': self.merchant_id,
                'reference': reference,
                'amount': amount_cents / 100
            }
            
        except Exception as e:
            error_msg = f"Payment request creation error: {str(e)}"
            logger.error(error_msg)
            raise PayFastPaymentError(error_msg)

    def verify_signature(self, post_data):
        """
        Verify PayFast callback signature
        
        Args:
            post_data (dict): POST data from PayFast callback
            
        Returns:
            bool: True if signature is valid
            
        Raises:
            PayFastPaymentError: If signature verification fails
        """
        try:
            # Extract signature
            signature = post_data.get('signature')
            if not signature:
                raise PayFastPaymentError("No signature in callback data")
            
            # Verify signature
            calculated_sig = self._create_signature(post_data, 'response')
            
            if signature != calculated_sig:
                logger.warning(
                    f"Signature mismatch. Expected: {calculated_sig}, "
                    f"Got: {signature}"
                )
                raise PayFastPaymentError("Invalid PayFast signature")
            
            logger.debug("PayFast signature verified successfully")
            return True
            
        except Exception as e:
            error_msg = f"Signature verification error: {str(e)}"
            logger.error(error_msg)
            raise PayFastPaymentError(error_msg)

    def handle_callback(self, post_data):
        """
        Handle PayFast payment callback/notification
        
        Args:
            post_data (dict): POST data from PayFast
            
        Returns:
            dict: Callback processing result {
                'success': bool,
                'order_id': id,
                'transaction_id': id,
                'status': status
            }
            
        Raises:
            PayFastPaymentError: If callback handling fails
        """
        try:
            # Verify signature first
            self.verify_signature(post_data)
            
            # Extract payment details
            order_id = int(post_data.get('custom_str1', 0))
            payment_reference = post_data.get('pf_payment_id')
            amount = Decimal(str(post_data.get('amount_gross', 0)))
            status = post_data.get('payment_status', 'UNKNOWN')
            
            # Map PayFast status to our status
            if status == 'COMPLETE':
                transaction_status = 'completed'
            elif status == 'PENDING':
                transaction_status = 'pending'
            elif status == 'FAILED':
                transaction_status = 'failed'
            elif status == 'CANCELLED':
                transaction_status = 'failed'
            else:
                transaction_status = 'pending'
            
            # Find or create transaction
            transaction = Transaction.query.filter_by(
                payment_reference=payment_reference
            ).first()
            
            if not transaction:
                transaction = Transaction(
                    order_id=order_id,
                    amount=amount,
                    payment_method=self.gateway_name,
                    payment_reference=payment_reference,
                    status=transaction_status,
                    gateway_response=self._format_gateway_response(
                        post_data
                    )
                )
                db.session.add(transaction)
            else:
                transaction.status = transaction_status
                transaction.gateway_response = self._format_gateway_response(
                    post_data
                )
            
            # Update order if payment completed
            order = db.session.get(Order, order_id)
            if order:
                order.payment_method = self.gateway_name
                order.payment_reference = payment_reference
                
                if transaction_status == 'completed':
                    order.payment_confirmed_at = datetime.now(timezone.utc)
                    order.payment_status = 'confirmed'
                else:
                    order.payment_status = 'pending' if transaction_status == 'pending' else 'failed'
            
            db.session.commit()
            
            logger.info(
                f"PayFast callback processed for order {order_id}. "
                f"Status: {transaction_status}, Transaction: {transaction.id}"
            )
            
            return {
                'success': True,
                'order_id': order_id,
                'transaction_id': transaction.id,
                'status': transaction_status
            }
            
        except PayFastPaymentError:
            db.session.rollback()
            raise
        except Exception as e:
            db.session.rollback()
            error_msg = f"Callback processing error: {str(e)}"
            logger.error(error_msg)
            raise PayFastPaymentError(error_msg)

    def check_status(self, payment_reference):
        """
        Check PayFast payment transaction status via API
        
        Args:
            payment_reference (str): PayFast payment ID
            
        Returns:
            dict: Payment status {
                'id': payment_id,
                'status': status,
                'amount': amount,
                'merchant_reference': reference
            }
            
        Raises:
            PayFastPaymentError: If status check fails
        """
        try:
            # Query PayFast API
            params = {
                'merchant-id': self.merchant_id,
                'passphrase': self.passphrase,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            response = requests.get(
                f"{self.api_url}/{payment_reference}",
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                raise PayFastPaymentError(
                    f"PayFast API error: {response.status_code}"
                )
            
            data = response.json()
            
            return {
                'id': data.get('id'),
                'status': data.get('status'),
                'amount': Decimal(str(data.get('amount', 0))),
                'merchant_reference': data.get('merchant_reference')
            }
            
        except requests.RequestException as e:
            error_msg = f"API connection error: {str(e)}"
            logger.error(error_msg)
            raise PayFastPaymentError(error_msg)
        except Exception as e:
            error_msg = f"Status check error: {str(e)}"
            logger.error(error_msg)
            raise PayFastPaymentError(error_msg)

    def _create_signature(self, data, mode='request'):
        """
        Create PayFast signature for request or response
        
        Args:
            data (dict): Payment data
            mode (str): 'request' or 'response'
            
        Returns:
            str: MD5 signature
        """
        # Fields for signature (order matters)
        if mode == 'request':
            sig_fields = [
                'merchant_id', 'merchant_key', 'return_url', 'cancel_url',
                'notify_url', 'name_first', 'name_last', 'email_address',
                'cell_number', 'fax', 'item_name', 'item_description',
                'item_id', 'item_url', 'amount', 'quantity', 'subscription_type',
                'recurring_amount', 'frequency', 'cycles', 'billing_date',
                'profile_date', 'm_payment_id', 'cc_cvv', 'cc_type',
                'email_confirmation', 'confirmation_address', 'payment_method',
                'custom_int1', 'custom_int2', 'custom_int3', 'custom_int4',
                'custom_int5', 'custom_str1', 'custom_str2', 'custom_str3',
                'custom_str4', 'custom_str5'
            ]
        else:
            sig_fields = [
                'amount_gross', 'amount_fee', 'amount_net', 'custom_int1',
                'custom_int2', 'custom_int3', 'custom_int4', 'custom_int5',
                'custom_str1', 'custom_str2', 'custom_str3', 'custom_str4',
                'custom_str5', 'email_address', 'item_description',
                'item_id', 'item_name', 'merchant_id', 'm_payment_id',
                'payment_date', 'payment_status', 'pf_payment_id',
                'reference'
            ]
        
        # Build signature string
        sig_string = ''
        for field in sig_fields:
            value = data.get(field, '')
            if value != '':
                sig_string += f"{field}={value}&"
        
        # Add passphrase
        if self.passphrase:
            sig_string += f"passphrase={self.passphrase}"
        else:
            # Remove trailing & if no passphrase
            sig_string = sig_string.rstrip('&')
        
        # Create MD5 hash
        signature = hashlib.md5(sig_string.encode('utf-8')).hexdigest()
        
        return signature

    def _format_gateway_response(self, post_data):
        """Format PayFast response for storage"""
        import json
        
        return json.dumps({
            'payment_id': post_data.get('pf_payment_id'),
            'status': post_data.get('payment_status'),
            'amount_gross': float(post_data.get('amount_gross', 0)),
            'amount_fee': float(post_data.get('amount_fee', 0)),
            'amount_net': float(post_data.get('amount_net', 0)),
            'payment_date': post_data.get('payment_date'),
            'merchant_reference': post_data.get('reference'),
            'item_id': post_data.get('item_id')
        })

    def get_payment_url(self, order_id, amount, customer_name='', customer_email='', description=''):
        """
        Convenience method to get payment URL for redirect
        
        Returns just the URL string instead of full dict
        """
        result = self.create_payment_request(
            order_id,
            amount,
            customer_name,
            customer_email,
            description
        )
        return result['payment_url']


def get_payfast_service():
    """Factory function to get PayFastPayment service"""
    return PayFastPayment()
