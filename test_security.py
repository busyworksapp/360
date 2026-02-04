"""
Security Feature Testing Script
Tests all Phase 1 security implementations
"""
import requests
import time
from urllib.parse import urljoin

# CONFIGURE THIS: Your Railway app URL
BASE_URL = "https://your-app.railway.app"  # Replace with your actual Railway URL

def test_https_redirect():
    """Test that HTTP redirects to HTTPS"""
    print("\n🔒 Testing HTTPS Enforcement...")
    try:
        # Try HTTP (should redirect to HTTPS)
        response = requests.get(BASE_URL.replace('https://', 'http://'), 
                              allow_redirects=True, timeout=10)
        if response.url.startswith('https://'):
            print("✅ HTTPS redirect working - HTTP → HTTPS")
        else:
            print("❌ HTTPS redirect NOT working")
        return response
    except Exception as e:
        print(f"⚠️ Could not test HTTPS: {e}")
        return None

def test_security_headers(response):
    """Test security headers are present"""
    print("\n🛡️ Testing Security Headers...")
    
    headers_to_check = {
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
        'X-Frame-Options': 'SAMEORIGIN',
    }
    
    for header, expected in headers_to_check.items():
        value = response.headers.get(header)
        if value:
            print(f"✅ {header}: {value}")
        else:
            print(f"❌ Missing: {header}")

def test_csrf_protection():
    """Test that CSRF tokens are present in forms"""
    print("\n🔐 Testing CSRF Protection...")
    try:
        response = requests.get(urljoin(BASE_URL, '/login'), timeout=10)
        if 'csrf_token' in response.text or 'csrf-token' in response.text:
            print("✅ CSRF tokens present in login form")
        else:
            print("❌ CSRF tokens NOT found")
    except Exception as e:
        print(f"⚠️ Could not test CSRF: {e}")

def test_rate_limiting():
    """Test rate limiting on login endpoint"""
    print("\n⏱️ Testing Rate Limiting...")
    print("Attempting 6 rapid login requests (limit is 5/minute)...")
    
    login_url = urljoin(BASE_URL, '/admin/login')
    
    for i in range(6):
        try:
            response = requests.post(login_url, 
                                    data={'email': 'test@test.com', 'password': 'test'},
                                    timeout=10,
                                    allow_redirects=False)
            
            if response.status_code == 429:
                print(f"✅ Request {i+1}: Rate limited (429 Too Many Requests)")
                return
            else:
                print(f"   Request {i+1}: {response.status_code}")
            
            time.sleep(0.5)  # Small delay between requests
        except Exception as e:
            print(f"⚠️ Request {i+1} failed: {e}")
    
    print("⚠️ No rate limiting detected (may need more requests or CSRF token)")

def test_session_cookies():
    """Test that session cookies have secure flags"""
    print("\n🍪 Testing Session Cookie Security...")
    try:
        session = requests.Session()
        response = session.get(BASE_URL, timeout=10)
        
        # Check if we got any cookies
        for cookie in session.cookies:
            print(f"   Cookie: {cookie.name}")
            if cookie.secure:
                print(f"   ✅ Secure flag: True")
            else:
                print(f"   ⚠️ Secure flag: False (may be OK in development)")
            
            if hasattr(cookie, 'has_nonstandard_attr'):
                if cookie.has_nonstandard_attr('HttpOnly'):
                    print(f"   ✅ HttpOnly flag: True")
    except Exception as e:
        print(f"⚠️ Could not test cookies: {e}")

def test_csp_header(response):
    """Test Content Security Policy"""
    print("\n📋 Testing Content Security Policy...")
    csp = response.headers.get('Content-Security-Policy')
    if csp:
        print(f"✅ CSP Header present")
        print(f"   Policy: {csp[:100]}...")
    else:
        print("⚠️ CSP Header not found (may be normal if not in production mode)")

def main():
    print("=" * 60)
    print("🔐 PHASE 1 SECURITY TESTING")
    print("=" * 60)
    print(f"Testing URL: {BASE_URL}")
    print("\nNote: Update BASE_URL in this script with your Railway URL")
    print("=" * 60)
    
    # Test HTTPS redirect first
    response = test_https_redirect()
    
    if response:
        # Test security headers
        test_security_headers(response)
        
        # Test CSP
        test_csp_header(response)
        
        # Test session cookies
        test_session_cookies()
    
    # Test CSRF protection
    test_csrf_protection()
    
    # Test rate limiting
    test_rate_limiting()
    
    print("\n" + "=" * 60)
    print("✅ Security testing complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Check Railway logs for any errors")
    print("2. Verify SECRET_KEY is set in Railway environment variables")
    print("3. Test login functionality manually")
    print("4. Monitor for any security alerts")
    print("\nFor detailed deployment checklist, see DEPLOYMENT_CHECKLIST.md")

if __name__ == "__main__":
    main()
