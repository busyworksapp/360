"""
EMAIL CONFIGURATION GUIDE for 360Degree Supply Website
========================================================

This guide explains how to set up email notifications for your website.

EMAIL FEATURES:
- Contact form confirmation emails to customers
- Contact form notifications to admin
- Payment confirmation emails
- Automatic HTML email templates with branding

SUPPORTED EMAIL PROVIDERS:

1. GMAIL SMTP (Recommended for Testing)
   - Server: smtp.gmail.com
   - Port: 587 (TLS) or 465 (SSL)
   - Username: your-email@gmail.com
   - Password: Your Gmail password OR App Password
   
   Note: For Gmail, you need to use an "App Password":
   1. Enable 2-Factor Authentication on your Gmail account
   2. Go to: https://myaccount.google.com/apppasswords
   3. Select "Mail" and "Windows Computer"
   4. Copy the 16-character password
   5. Use this as SMTP_PASSWORD

2. OUTLOOK/HOTMAIL SMTP
   - Server: smtp-mail.outlook.com
   - Port: 587
   - Username: your-email@outlook.com
   - Password: Your Outlook password

3. ZOHO MAIL (Professional Email)
   - Server: smtp.zoho.co.za (for South Africa)
   - Port: 587
   - Username: your-email@zoho.com
   - Password: Your Zoho password

4. SENDGRID (Transactional Email Service)
   - Server: smtp.sendgrid.net
   - Port: 587
   - Username: apikey
   - Password: Your SendGrid API key

5. MAILGUN (Transactional Email Service)
   - Server: smtp.mailgun.org
   - Port: 587
   - Username: postmaster@yourdomain.com
   - Password: Your Mailgun API key

ENVIRONMENT VARIABLES (.env file):

Copy these to your .env file and update with your values:

# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=True
ADMIN_EMAIL=admin@360degreesupply.co.za
SEND_EMAILS=True

CONFIGURATION OPTIONS:

SMTP_SERVER (string)
   - SMTP server address
   - Examples: smtp.gmail.com, smtp.zoho.co.za

SMTP_PORT (integer)
   - Port number for SMTP connection
   - Common: 587 (TLS), 465 (SSL), 25 (unencrypted)
   - Default: 587

SMTP_USERNAME (string)
   - Email address or username for authentication
   - Usually your email address

SMTP_PASSWORD (string)
   - Password or API key
   - Keep this secure!

SMTP_USE_TLS (boolean)
   - Use TLS encryption (True) or SSL (False)
   - True = Port 587, False = Port 465
   - Default: True

ADMIN_EMAIL (string)
   - Email address for admin notifications
   - Contact form submissions will be sent here

SEND_EMAILS (boolean)
   - Enable/disable email sending
   - True: Emails will be sent
   - False: Emails disabled (good for testing)
   - Default: False

EMAIL TEMPLATES:

1. Contact Form Confirmation (to customer)
   - Sent when customer submits contact form
   - Confirms receipt of message
   - Shows company contact info
   - Template: HTML with company branding

2. Contact Form Notification (to admin)
   - Sent when customer submits contact form
   - Contains full message details
   - Includes link to admin panel
   - Template: HTML table format

3. Payment Confirmation (to customer)
   - Sent when payment is received
   - Shows transaction details
   - Amount and payment method
   - Transaction ID for reference
   - Template: HTML with green success styling

TESTING EMAIL:

Method 1: Use a Test Email Service
1. Create free account at: https://mailtrap.io
2. Copy SMTP settings from Mailtrap
3. Configure in .env file
4. Send a test email
5. Check Mailtrap inbox (doesn't send real emails)

Method 2: Use Gmail
1. Enable 2FA on Gmail account
2. Generate App Password
3. Add to .env with SMTP_USERNAME and SMTP_PASSWORD
4. Submit contact form to test
5. Check your email inbox

Method 3: Disable Email for Development
1. Set SEND_EMAILS=False in .env
2. Emails won't be sent but no errors
3. Good for development/testing

TROUBLESHOOTING:

Issue: "Authentication failed"
Solution: Check username and password are correct
         Verify app password for Gmail
         Check SMTP_USE_TLS setting matches port

Issue: "Connection timeout"
Solution: Verify SMTP_SERVER address is correct
         Check firewall isn't blocking SMTP port
         Try different port (587 vs 465)

Issue: "Emails not being sent"
Solution: Check SEND_EMAILS=True in .env
         Check ADMIN_EMAIL is set
         Verify SMTP credentials work
         Check app.config is loading .env file

Issue: "TLS required" error
Solution: Set SMTP_USE_TLS=True
         Use port 587 instead of 25

PRODUCTION RECOMMENDATIONS:

1. Use a dedicated email service:
   - SendGrid (easiest, free tier available)
   - Mailgun (good documentation)
   - AWS SES (scalable)

2. Update from addresses:
   - Use noreply@yourdomain.com
   - Configure DKIM/SPF for domain

3. Monitor email delivery:
   - Check bounce rates
   - Monitor spam complaints
   - Use service dashboard

4. Security:
   - Never commit .env file to git
   - Use environment variables
   - Rotate API keys periodically
   - Use API keys instead of passwords

QUICK START (Gmail):

1. Edit .env file:
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-16-char-app-password
   SMTP_USE_TLS=True
   ADMIN_EMAIL=your-email@gmail.com
   SEND_EMAILS=True

2. Test by submitting contact form

3. Check email inbox

4. If working, deploy to production!

For more help, visit:
- Gmail App Passwords: https://support.google.com/accounts/answer/185833
- SendGrid: https://sendgrid.com/
- Mailgun: https://www.mailgun.com/
"""

print(__doc__)
