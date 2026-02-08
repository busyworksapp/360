"""Email service module for 360Degree Supply website."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import render_template_string
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailService:
    """Handle email notifications for the website."""

    def __init__(self, smtp_server, smtp_port, sender_email,
                 sender_password, use_tls=True):
        """
        Initialize email service.

        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP port number
            sender_email: Email address to send from
            sender_password: SMTP password/API key
            use_tls: Use TLS encryption (default: True)
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.use_tls = use_tls

    def send_email(self, recipient_email, subject, html_content,
                   plain_text=None):
        """
        Send an email message.

        Args:
            recipient_email: Recipient email address(es)
            subject: Email subject
            html_content: HTML email body
            plain_text: Plain text fallback

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Skip if no SMTP credentials configured
            if not self.sender_email or not self.sender_password:
                logger.warning("Email not sent: SMTP credentials not configured")
                return False
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = (recipient_email if isinstance(
                recipient_email, str
            ) else ", ".join(recipient_email))

            # Attach plain text version
            if plain_text:
                part1 = MIMEText(plain_text, "plain")
                message.attach(part1)

            # Attach HTML version (preferred)
            part2 = MIMEText(html_content, "html")
            message.attach(part2)

            # Send email with timeout
            logger.info(f"Attempting to send email to {recipient_email} via {self.smtp_server}:{self.smtp_port}")
            
            if self.use_tls:
                server = smtplib.SMTP(
                    self.smtp_server, self.smtp_port, timeout=30
                )
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(
                    self.smtp_server, self.smtp_port, timeout=30
                )

            server.login(self.sender_email, self.sender_password)
            server.sendmail(
                self.sender_email,
                recipient_email,
                message.as_string()
            )
            server.quit()

            logger.info(
                f"Email sent successfully to {recipient_email}"
            )
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {str(e)}")
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"SMTP Connection failed: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False

    def send_contact_confirmation(self, recipient_name,
                                  recipient_email, subject,
                                  message_content, company_name,
                                  company_phone, company_email):
        """
        Send contact form confirmation email to client.

        Args:
            recipient_name: Name of person who submitted form
            recipient_email: Email address to send to
            subject: Original message subject
            message_content: Original message content
            company_name: Company name to display
            company_phone: Company phone number
            company_email: Company email address

        Returns:
            bool: True if successful
        """
        html_template = """
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <!-- Header -->
                    <div style="background-color: #1a472a; color: white;
                                padding: 20px; text-align: center;">
                        <h2>Thank You for Contacting Us!</h2>
                    </div>

                    <!-- Content -->
                    <div style="padding: 20px; background-color: #f9f9f9;">
                        <p>Dear {{ recipient_name }},</p>

                        <p>Thank you for reaching out to us. We have received
                        your message and appreciate you taking the time to
                        contact {{ company_name }}.</p>

                        <div style="background-color: white; padding: 15px;
                                    border-left: 4px solid #f39c12;
                                    margin: 20px 0;">
                            <h4 style="color: #1a472a; margin-top: 0;">
                                Your Message Summary:
                            </h4>
                            <p><strong>Subject:</strong> {{ subject }}</p>
                            <p><strong>Submitted:</strong>
                            {{ submission_date }}</p>
                        </div>

                        <p>We will review your inquiry and get back to you
                        within 24-48 business hours.</p>

                        <h4 style="color: #1a472a;">Contact Information:</h4>
                        <p>
                            <strong>{{ company_name }}</strong><br>
                            📞 {{ company_phone }}<br>
                            📧 {{ company_email }}
                        </p>

                        <p style="color: #7f8c8d; font-size: 12px;
                                  margin-top: 30px;">
                            <em>This is an automated response. Please do not
                            reply to this email.</em>
                        </p>
                    </div>

                    <!-- Footer -->
                    <div style="background-color: #1a472a; color: white;
                                padding: 15px; text-align: center;
                                font-size: 12px;">
                        <p>© 2026 {{ company_name }}. All rights reserved.
                        </p>
                        <p>Transforming Industries with Quality &
                        Reliability</p>
                    </div>
                </div>
            </body>
        </html>
        """

        plain_text = f"""
Thank you for contacting us!

Dear {recipient_name},

Thank you for reaching out to us. We have received your message and
appreciate you taking the time to contact {company_name}.

Your Message Summary:
Subject: {subject}
Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M')}

We will review your inquiry and get back to you within 24-48 business
hours.

Contact Information:
{company_name}
📞 {company_phone}
📧 {company_email}

This is an automated response. Please do not reply to this email.

© 2026 {company_name}. All rights reserved.
        """

        from flask import render_template_string

        html_content = render_template_string(
            html_template,
            recipient_name=recipient_name,
            subject=subject,
            company_name=company_name,
            company_phone=company_phone,
            company_email=company_email,
            submission_date=datetime.now().strftime('%Y-%m-%d %H:%M')
        )

        return self.send_email(
            recipient_email,
            f"Thank You - {subject}",
            html_content,
            plain_text
        )

    def send_contact_notification(self, admin_email, sender_name,
                                  sender_email, sender_phone,
                                  subject, message_content,
                                  company_name):
        """
        Send contact form notification to admin.

        Args:
            admin_email: Admin email to notify
            sender_name: Name of person who submitted form
            sender_email: Email of person who submitted form
            sender_phone: Phone of person who submitted form
            subject: Message subject
            message_content: Message content
            company_name: Company name

        Returns:
            bool: True if successful
        """
        html_template = """
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <div style="background-color: #1a472a; color: white;
                                padding: 20px;">
                        <h2>New Contact Form Submission</h2>
                    </div>

                    <div style="padding: 20px; background-color: #f9f9f9;">
                        <h4 style="color: #1a472a;">
                            Contact Details:
                        </h4>

                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px; font-weight: bold;
                                          width: 30%;">Name:</td>
                                <td style="padding: 8px;">
                                {{ sender_name }}
                                </td>
                            </tr>
                            <tr style="background-color: white;">
                                <td style="padding: 8px; font-weight: bold;">
                                Email:</td>
                                <td style="padding: 8px;">
                                <a href="mailto:{{ sender_email }}">
                                {{ sender_email }}</a>
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; font-weight: bold;">
                                Phone:</td>
                                <td style="padding: 8px;">
                                <a href="tel:{{ sender_phone }}">
                                {{ sender_phone }}</a>
                                </td>
                            </tr>
                            <tr style="background-color: white;">
                                <td style="padding: 8px; font-weight: bold;">
                                Subject:</td>
                                <td style="padding: 8px;">
                                {{ subject }}
                                </td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; font-weight: bold;
                                          vertical-align: top;">Message:</td>
                                <td style="padding: 8px;">
                                {{ message_content }}
                                </td>
                            </tr>
                            <tr style="background-color: white;">
                                <td style="padding: 8px; font-weight: bold;">
                                Submitted:</td>
                                <td style="padding: 8px;">
                                {{ submission_date }}
                                </td>
                            </tr>
                        </table>

                        <p style="margin-top: 20px;">
                            <a href="{{ admin_link }}"
                               style="background-color: #1a472a;
                                      color: white; padding: 10px 20px;
                                      text-decoration: none;
                                      border-radius: 4px;">
                                View in Admin Panel
                            </a>
                        </p>
                    </div>

                    <div style="background-color: #1a472a; color: white;
                                padding: 15px; text-align: center;
                                font-size: 12px;">
                        <p>© 2026 {{ company_name }}. All rights
                        reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """

        html_content = render_template_string(
            html_template,
            sender_name=sender_name,
            sender_email=sender_email,
            sender_phone=sender_phone,
            subject=subject,
            message_content=message_content,
            company_name=company_name,
            submission_date=datetime.now().strftime(
                '%Y-%m-%d %H:%M'
            ),
            admin_link="http://localhost:5000/admin/contacts"
        )

        return self.send_email(
            admin_email,
            f"New Contact Form: {subject}",
            html_content
        )

    def send_payment_confirmation(self, recipient_email, recipient_name,
                                  transaction_id, amount, currency,
                                  payment_method, company_name,
                                  company_email, company_phone):
        """
        Send payment confirmation email.

        Args:
            recipient_email: Email to send to
            recipient_name: Name of payer
            transaction_id: Transaction ID
            amount: Payment amount
            currency: Currency code (e.g., ZAR)
            payment_method: Method used (e.g., Stripe, PayFast)
            company_name: Company name
            company_email: Company email
            company_phone: Company phone

        Returns:
            bool: True if successful
        """
        html_template = """
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <div style="background-color: #1a472a; color: white;
                                padding: 20px; text-align: center;">
                        <h2>✓ Payment Received</h2>
                    </div>

                    <div style="padding: 20px; background-color: #f9f9f9;">
                        <p>Dear {{ recipient_name }},</p>

                        <p>We have successfully received your payment.
                        Thank you for your business!</p>

                        <div style="background-color: #e8f5e9;
                                    padding: 20px; border-radius: 4px;
                                    margin: 20px 0; border-left: 4px
                                    solid #4caf50;">
                            <h4 style="color: #1a472a; margin-top: 0;">
                                Payment Summary
                            </h4>

                            <table style="width: 100%;
                                        border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px;
                                              font-weight: bold;">
                                    Transaction ID:
                                    </td>
                                    <td style="padding: 8px;">
                                    {{ transaction_id }}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px;
                                              font-weight: bold;">
                                    Amount:
                                    </td>
                                    <td style="padding: 8px;">
                                    {{ currency }} {{ amount }}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px;
                                              font-weight: bold;">
                                    Payment Method:
                                    </td>
                                    <td style="padding: 8px;">
                                    {{ payment_method }}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px;
                                              font-weight: bold;">
                                    Date:
                                    </td>
                                    <td style="padding: 8px;">
                                    {{ payment_date }}
                                    </td>
                                </tr>
                            </table>
                        </div>

                        <p>If you have any questions about this payment,
                        please contact us:</p>

                        <p>
                            {{ company_name }}<br>
                            📧 {{ company_email }}<br>
                            📞 {{ company_phone }}
                        </p>

                        <p style="color: #7f8c8d; font-size: 12px;
                                  margin-top: 30px;">
                            <em>This is an automated receipt. Please keep
                            this email for your records.</em>
                        </p>
                    </div>

                    <div style="background-color: #1a472a; color: white;
                                padding: 15px; text-align: center;
                                font-size: 12px;">
                        <p>© 2026 {{ company_name }}. All rights
                        reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """



        html_content = render_template_string(
            html_template,
            recipient_name=recipient_name,
            transaction_id=transaction_id,
            amount=f"{float(amount):.2f}",
            currency=currency,
            payment_method=payment_method,
            company_name=company_name,
            company_email=company_email,
            company_phone=company_phone,
            payment_date=datetime.now().strftime('%Y-%m-%d %H:%M')
        )

        return self.send_email(
            recipient_email,
            f"Payment Confirmation - {transaction_id}",
            html_content
        )

    def send_order_confirmation(self, recipient_email, order_number,
                                total_amount, company_name='360Degree Supply',
                                company_email='info@360degreesupply.co.za',
                                company_phone='+27 64 902 4363'):
        """
        Send order confirmation email.

        Args:
            recipient_email: Customer email address
            order_number: Unique order identifier
            total_amount: Order total amount
            company_name: Company name (default: 360Degree Supply)
            company_email: Company email (default: info@...)
            company_phone: Company phone (default: +27 64 902...)

        Returns:
            bool: True if successful, False otherwise
        """
        html_template = '''
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;
                         color: #333;">
                <div style="background-color: #1a472a; color: white; padding:
                            20px; text-align: center;">
                    <h1>Order Confirmation</h1>
                </div>
                
                <div style="padding: 20px; max-width: 600px; margin: 0 auto;">
                    <p>Thank you for your order!</p>
                    
                    <h3>Order Details:</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr style="background-color: #f5f5f5;">
                            <td style="padding: 10px; border: 1px solid #ddd;">
                                <strong>Order Number:</strong>
                            </td>
                            <td style="padding: 10px; border: 1px solid #ddd;">
                                {{ order_number }}
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd;">
                                <strong>Order Date:</strong>
                            </td>
                            <td style="padding: 10px; border: 1px solid #ddd;">
                                {{ order_date }}
                            </td>
                        </tr>
                        <tr style="background-color: #f5f5f5;">
                            <td style="padding: 10px; border: 1px solid #ddd;">
                                <strong>Total Amount:</strong>
                            </td>
                            <td style="padding: 10px; border: 1px solid #ddd;">
                                R{{ total_amount }}
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border: 1px solid #ddd;">
                                <strong>Status:</strong>
                            </td>
                            <td style="padding: 10px; border: 1px solid #ddd;">
                                Pending Processing
                            </td>
                        </tr>
                    </table>
                    
                    <h3>Next Steps:</h3>
                    <ul>
                        <li>Your order is being processed</li>
                        <li>You will receive tracking info soon</li>
                        <li>Questions? Contact us at {{ company_email }}
                        </li>
                    </ul>
                    
                    <hr style="margin: 20px 0;">
                    
                    <div style="background-color: #f5f5f5; padding: 15px;
                                border-left: 4px solid #f39c12;">
                        <p><strong>{{ company_name }}</strong></p>
                        <p>
                            Email: <a href="mailto:{{ company_email }}">
                            {{ company_email }}</a><br>
                            Phone: {{ company_phone }}<br>
                            Website: 
                            <a href="http://360degreesupply.co.za">
                            360degreesupply.co.za</a>
                        </p>
                    </div>
                </div>
            </body>
        </html>
        '''

        html_content = render_template_string(
            html_template,
            order_number=order_number,
            total_amount=f"{float(total_amount):.2f}",
            order_date=datetime.now().strftime('%Y-%m-%d %H:%M'),
            company_name=company_name,
            company_email=company_email,
            company_phone=company_phone
        )

        return self.send_email(
            recipient_email,
            f"Order Confirmation - {order_number}",
            html_content
        )

    def send_payment_failed_email(self, recipient_email, recipient_name,
                                  order_number, error_message, company_name,
                                  company_email, company_phone,
                                  retry_url=None):
        """
        Send payment failure notification email.

        Args:
            recipient_email: Email to send to
            recipient_name: Name of customer
            order_number: Order number that failed
            error_message: Error message to display
            company_name: Company name
            company_email: Company email
            company_phone: Company phone
            retry_url: URL to retry payment (optional)

        Returns:
            bool: True if successful
        """
        html_template = """
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <div style="background-color: #1a472a; color: white;
                                padding: 20px; text-align: center;">
                        <h2>⚠ Payment Failed</h2>
                    </div>

                    <div style="padding: 20px; background-color: #f9f9f9;">
                        <p>Dear {{ recipient_name }},</p>

                        <p>Unfortunately, we were unable to process your
                        payment for order
                        <strong>{{ order_number }}</strong>.</p>

                        <div style="background-color: #ffebee;
                                    padding: 20px; border-radius: 4px;
                                    margin: 20px 0; border-left: 4px
                                    solid #f44336;">
                            <h4 style="color: #c62828; margin-top: 0;">
                                Error Details
                            </h4>
                            <p style="margin: 0;">
                                <strong>Reason:</strong>
                                {{ error_message }}
                            </p>
                        </div>

                        <h4 style="color: #1a472a;">What Happens Next?</h4>
                        <ul>
                            <li>Your order has been saved and is ready for
                            payment</li>
                            <li>Please verify your card/payment details and
                            try again</li>
                            <li>If the problem persists, please contact us
                            for assistance</li>
                        </ul>

                        {% if retry_url %}
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{{ retry_url }}"
                               style="background-color: #1a472a;
                                      color: white; padding: 12px 30px;
                                      text-decoration: none;
                                      border-radius: 4px;
                                      display: inline-block;
                                      font-weight: bold;">
                                Retry Payment
                            </a>
                        </div>
                        {% endif %}

                        <h4 style="color: #1a472a;">Need Help?</h4>
                        <p>
                            Please don't hesitate to contact us:
                        </p>
                        <p>
                            {{ company_name }}<br>
                            📧 {{ company_email }}<br>
                            📞 {{ company_phone }}
                        </p>

                        <p style="color: #7f8c8d; font-size: 12px;
                                  margin-top: 30px;">
                            <em>This is an automated notification. Please do
                            not reply to this email.</em>
                        </p>
                    </div>

                    <div style="background-color: #1a472a; color: white;
                                padding: 15px; text-align: center;
                                font-size: 12px;">
                        <p>© 2026 {{ company_name }}. All rights
                        reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """

        html_content = render_template_string(
            html_template,
            recipient_name=recipient_name,
            order_number=order_number,
            error_message=error_message,
            company_name=company_name,
            company_email=company_email,
            company_phone=company_phone,
            retry_url=retry_url
        )

        return self.send_email(
            recipient_email,
            f"Payment Failed - Order {order_number}",
            html_content
        )

    def send_refund_email(self, recipient_email, recipient_name,
                          order_number, transaction_id, refund_amount,
                          currency, refund_reason, company_name,
                          company_email, company_phone):
        """
        Send refund notification email.

        Args:
            recipient_email: Email to send to
            recipient_name: Name of customer
            order_number: Order number for refund
            transaction_id: Original transaction ID
            refund_amount: Amount being refunded
            currency: Currency code (e.g., ZAR)
            refund_reason: Reason for refund
            company_name: Company name
            company_email: Company email
            company_phone: Company phone

        Returns:
            bool: True if successful
        """
        html_template = """
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <div style="background-color: #1a472a; color: white;
                                padding: 20px; text-align: center;">
                        <h2>💰 Refund Processed</h2>
                    </div>

                    <div style="padding: 20px; background-color: #f9f9f9;">
                        <p>Dear {{ recipient_name }},</p>

                        <p>We have successfully processed a refund for your
                        order. Please see the details below.</p>

                        <div style="background-color: #e8f5e9;
                                    padding: 20px; border-radius: 4px;
                                    margin: 20px 0; border-left: 4px
                                    solid #4caf50;">
                            <h4 style="color: #2e7d32; margin-top: 0;">
                                Refund Summary
                            </h4>

                            <table style="width: 100%;
                                        border-collapse: collapse;">
                                <tr>
                                    <td style="padding: 8px;
                                              font-weight: bold;">
                                    Order Number:
                                    </td>
                                    <td style="padding: 8px;">
                                    {{ order_number }}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px;
                                              font-weight: bold;">
                                    Original Transaction:
                                    </td>
                                    <td style="padding: 8px;">
                                    {{ transaction_id }}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px;
                                              font-weight: bold;">
                                    Refund Amount:
                                    </td>
                                    <td style="padding: 8px;
                                              color: #2e7d32;
                                              font-weight: bold;">
                                    {{ currency }}
                                    {{ refund_amount }}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px;
                                              font-weight: bold;">
                                    Reason:
                                    </td>
                                    <td style="padding: 8px;">
                                    {{ refund_reason }}
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 8px;
                                              font-weight: bold;">
                                    Processed Date:
                                    </td>
                                    <td style="padding: 8px;">
                                    {{ processed_date }}
                                    </td>
                                </tr>
                            </table>
                        </div>

                        <h4 style="color: #1a472a;">Refund Timeline</h4>
                        <p>
                            The refund has been initiated. Please allow
                            <strong>3-5 business days</strong> for the funds
                            to appear back in your original payment method.
                        </p>

                        <h4 style="color: #1a472a;">Questions?</h4>
                        <p>
                            If you don't see the refund within 5 business
                            days or have any questions, please contact us:
                        </p>
                        <p>
                            {{ company_name }}<br>
                            📧 {{ company_email }}<br>
                            📞 {{ company_phone }}
                        </p>

                        <p style="color: #7f8c8d; font-size: 12px;
                                  margin-top: 30px;">
                            <em>This is an automated notification. Please
                            keep this email for your records.</em>
                        </p>
                    </div>

                    <div style="background-color: #1a472a; color: white;
                                padding: 15px; text-align: center;
                                font-size: 12px;">
                        <p>© 2026 {{ company_name }}. All rights
                        reserved.</p>
                    </div>
                </div>
            </body>
        </html>
        """

        html_content = render_template_string(
            html_template,
            recipient_name=recipient_name,
            order_number=order_number,
            transaction_id=transaction_id,
            refund_amount=f"{float(refund_amount):.2f}",
            currency=currency,
            refund_reason=refund_reason,
            company_name=company_name,
            company_email=company_email,
            company_phone=company_phone,
            processed_date=datetime.now().strftime('%Y-%m-%d %H:%M')
        )

        return self.send_email(
            recipient_email,
            f"Refund Processed - Order {order_number}",
            html_content
        )
