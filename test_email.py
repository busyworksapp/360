"""Test email configuration."""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, email_service
from models import CompanyInfo


def test_email_connection():
    """Test SMTP connection and send a test email."""
    print("\n" + "=" * 60)
    print("🧪 EMAIL CONFIGURATION TEST")
    print("=" * 60 + "\n")

    with app.app_context():
        # Check configuration
        print("📋 Configuration Check:")
        print(f"   SMTP Server: {app.config.get('SMTP_SERVER')}")
        print(f"   SMTP Port: {app.config.get('SMTP_PORT')}")
        print(f"   Username: {app.config.get('SMTP_USERNAME')}")
        print(f"   Use TLS: {app.config.get('SMTP_USE_TLS')}")
        print(f"   Admin Email: {app.config.get('ADMIN_EMAIL')}")
        print(f"   Send Emails: {app.config.get('SEND_EMAILS')}")
        print()

        # Test basic connection
        if not app.config.get('SEND_EMAILS'):
            print("⚠️  WARNING: SEND_EMAILS is disabled")
            print("   Set SEND_EMAILS=True in .env to enable emails\n")
            return False

        if not app.config.get('SMTP_PASSWORD'):
            print("❌ ERROR: SMTP_PASSWORD not configured")
            print("   Add SMTP_PASSWORD to .env file\n")
            return False

        # Get company info for test email
        company = CompanyInfo.query.first()
        if not company:
            print("❌ ERROR: No company info in database")
            print("   Run: python reseed_db.py\n")
            return False

        # Test contact confirmation email
        print("📧 Testing Contact Confirmation Email...")
        result = email_service.send_contact_confirmation(
            recipient_name="Test User",
            recipient_email=app.config.get('ADMIN_EMAIL'),
            subject="Test Subject",
            message_content="This is a test message.",
            company_name=company.company_name,
            company_phone=company.phone,
            company_email=company.email
        )

        if result:
            print("   ✅ SUCCESS: Contact confirmation email sent!")
            print(f"   Email sent to: {app.config.get('ADMIN_EMAIL')}")
        else:
            print("   ❌ FAILED: Could not send contact email")
            print("   Check SMTP configuration in .env")
            return False

        # Test payment confirmation email
        print("\n📧 Testing Payment Confirmation Email...")
        result = email_service.send_payment_confirmation(
            recipient_email=app.config.get('ADMIN_EMAIL'),
            recipient_name="Test Customer",
            transaction_id="TEST-123456",
            amount=1234.50,
            currency="ZAR",
            payment_method="Stripe Card",
            company_name=company.company_name,
            company_email=company.email,
            company_phone=company.phone
        )

        if result:
            print("   ✅ SUCCESS: Payment confirmation email sent!")
            print(f"   Email sent to: {app.config.get('ADMIN_EMAIL')}")
        else:
            print("   ❌ FAILED: Could not send payment email")
            return False

        print("\n" + "=" * 60)
        print("✅ EMAIL CONFIGURATION TEST COMPLETE")
        print("=" * 60)
        print("\n📌 Next Steps:")
        print("   1. Check your email inbox for test messages")
        print("   2. Try submitting the contact form on the website")
        print("   3. Make a test payment to verify payment emails")
        print("\nFor help, see: EMAIL_SETUP.py\n")

        return True


if __name__ == '__main__':
    success = test_email_connection()
    sys.exit(0 if success else 1)
