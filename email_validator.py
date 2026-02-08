"""
Real Email Validation - DNS MX Record Verification
Ensures only real, existing email addresses are accepted
"""
import re
import dns.resolver
from functools import lru_cache

# Pre-compiled regex for email format
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

# Disposable email domains (block these)
DISPOSABLE_DOMAINS = frozenset([
    'tempmail.com', 'guerrillamail.com', '10minutemail.com', 'mailinator.com',
    'throwaway.email', 'temp-mail.org', 'fakeinbox.com', 'trashmail.com'
])

@lru_cache(maxsize=1000)
def verify_email_exists(email):
    """
    Verify email address exists by checking DNS MX records
    Returns: (is_valid, error_message)
    """
    # Basic format validation
    if not email or not isinstance(email, str):
        return False, "Email is required"
    
    email = email.strip().lower()
    
    # Check format
    if not EMAIL_REGEX.match(email):
        return False, "Invalid email format"
    
    # Extract domain
    try:
        domain = email.split('@')[1]
    except IndexError:
        return False, "Invalid email format"
    
    # Block disposable email domains
    if domain in DISPOSABLE_DOMAINS:
        return False, "Disposable email addresses are not allowed"
    
    # Check DNS MX records (verify domain can receive emails)
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        if not mx_records:
            return False, f"Email domain '{domain}' cannot receive emails"
        return True, None
    except dns.resolver.NXDOMAIN:
        return False, f"Email domain '{domain}' does not exist"
    except dns.resolver.NoAnswer:
        return False, f"Email domain '{domain}' has no mail server"
    except dns.resolver.Timeout:
        return False, "Email verification timeout - please try again"
    except Exception as e:
        # In production, log this error but allow the email
        # (don't block users due to DNS issues)
        return True, None

def validate_email_for_registration(email):
    """
    Validate email for user registration
    Stricter validation - must be real, existing email
    """
    is_valid, error = verify_email_exists(email)
    
    if not is_valid:
        return False, error
    
    return True, None

def validate_email_for_login(email):
    """
    Validate email for login (less strict - just format check)
    """
    if not email or not isinstance(email, str):
        return False, "Email is required"
    
    email = email.strip().lower()
    
    if not EMAIL_REGEX.match(email):
        return False, "Invalid email format"
    
    return True, None
