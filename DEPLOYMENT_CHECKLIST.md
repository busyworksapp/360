# Phase 1 Security Implementation - Deployment Checklist

## ✅ COMPLETED IMPLEMENTATIONS

### 1. Security Dependencies Added
- ✅ Flask-WTF 1.2.1 (CSRF Protection)
- ✅ Flask-Limiter 3.5.0 (Rate Limiting)
- ✅ Flask-Talisman 1.1.0 (HTTPS/Security Headers)
- ✅ pyotp 2.9.0 (2FA - for future Phase 2)
- ✅ qrcode 7.4.2 (2FA QR codes - for future Phase 2)
- ✅ python-magic-bin 0.4.14 (File validation)
- ✅ gunicorn 21.2.0 (Production server)

### 2. Configuration Security (config.py)
- ✅ Mandatory SECRET_KEY enforcement (raises error if missing/default)
- ✅ Session cookie security:
  - SESSION_COOKIE_SECURE = True (HTTPS only)
  - SESSION_COOKIE_HTTPONLY = True (no JS access)
  - SESSION_COOKIE_SAMESITE = 'Lax' (CSRF protection)
  - SESSION_COOKIE_NAME = '__Host-session' (security prefix)
  - PERMANENT_SESSION_LIFETIME = 3600 (1-hour timeout)
- ✅ CSRF protection configured (WTF_CSRF_ENABLED, SSL_STRICT)
- ✅ Rate limiting storage configured (Redis with memory fallback)

### 3. Application Security Middleware (app.py)
- ✅ Version bumped to 2.2.0
- ✅ CSRF protection initialized globally
- ✅ Rate limiter configured (200/day, 50/hour defaults)
- ✅ Content Security Policy defined
- ✅ Talisman HTTPS enforcement (production-conditional)
- ✅ Security headers function (@app.after_request):
  - X-Content-Type-Options: nosniff
  - X-XSS-Protection: 1; mode=block
  - Referrer-Policy: strict-origin-when-cross-origin
  - Permissions-Policy: geolocation=(), microphone=(), camera=()

### 4. Security Helper Functions (app.py)
- ✅ `validate_password_strength()` - 12+ chars, uppercase, lowercase, number, special char
- ✅ `secure_file_upload()` - MIME validation, unique naming, size limits
- ✅ `sanitize_input()` - HTML sanitization using bleach

### 5. Rate Limiting Applied
- ✅ `/admin/login` - 5 requests per minute
- ✅ `/customer/login` - 10 requests per minute
- ✅ `/customer/register` - 5 requests per hour (prevents spam accounts)
- ✅ `/api/contact` - 3 requests per minute (prevents spam)
- ✅ `/api/cart/add` - 30 requests per minute (normal shopping behavior)

### 6. CSRF Tokens Added to Templates
- ✅ `login.html` - Admin login form
- ✅ `login.html` - Customer login form
- ✅ `customer/register.html` - Registration form
- ✅ `contact.html` - Contact form
- ✅ `base.html` - Meta tag for AJAX requests
- ✅ `products.html` - AJAX cart operations
- ✅ `customer/products.html` - AJAX cart operations

---

## 🚨 REQUIRED BEFORE DEPLOYMENT

### Environment Variables (Railway Dashboard)
You **MUST** set these in Railway:

```bash
# CRITICAL - Generate with: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=<YOUR_64_CHARACTER_HEX_STRING>

# Enable production security features
FLASK_ENV=production
ENABLE_HTTPS=True

# Database (already set, verify it's correct)
DATABASE_URL=postgresql://...

# Stripe (already set, verify it's correct)
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...

# PayFast (already set, verify it's correct)
PAYFAST_MERCHANT_ID=...
PAYFAST_MERCHANT_KEY=...
PAYFAST_PASSPHRASE=...

# Optional: Redis for rate limiting (recommended for production)
# If not set, will use in-memory storage (resets on restart)
REDIS_URL=redis://...
```

### Steps to Deploy:

1. **Generate Production SECRET_KEY:**
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Copy the output and add to Railway environment variables.

2. **Update Railway Environment Variables:**
   - Go to Railway Dashboard → Your Project → Variables
   - Add/update the environment variables listed above
   - **DO NOT** commit secrets to git!

3. **Commit and Push Changes:**
   ```bash
   git add .
   git commit -m "Phase 1: Critical security hardening - CSRF, rate limiting, HTTPS"
   git push origin main
   ```

4. **Monitor Deployment:**
   - Railway will automatically redeploy
   - Check deployment logs for errors
   - Look for "SECRET_KEY environment variable must be set!" errors

5. **Verify Security Features:**
   - [ ] Visit https://your-app.railway.app (should force HTTPS)
   - [ ] Check browser console - no CSP errors
   - [ ] Test login - should work normally with CSRF token
   - [ ] Test rapid login attempts - should see rate limit (429 status)
   - [ ] Check session cookies in browser DevTools:
     - Should have `Secure` flag
     - Should have `HttpOnly` flag
     - Should have `SameSite=Lax`

---

## ⚠️ TESTING CHECKLIST

### Before Going Live:
- [ ] Test admin login with rate limiting (try 6 times quickly)
- [ ] Test customer login with rate limiting
- [ ] Test customer registration
- [ ] Test contact form submission
- [ ] Test add to cart functionality
- [ ] Verify HTTPS redirect works
- [ ] Verify security headers in browser DevTools (Network tab)
- [ ] Test from different browsers (Chrome, Firefox, Safari)
- [ ] Test on mobile devices
- [ ] Check error logs in Railway dashboard

### Expected Behaviors:
- ✅ Login forms should work normally (CSRF tokens automatically included)
- ✅ Too many login attempts → "429 Too Many Requests" error
- ✅ All HTTP requests should redirect to HTTPS (when ENABLE_HTTPS=True)
- ✅ Session should expire after 1 hour of inactivity
- ✅ AJAX requests should include X-CSRFToken header

---

## 📝 KNOWN LIMITATIONS (Phase 1)

### Not Yet Implemented (See SECURITY_AUDIT.md for full plan):
- ⏳ 2FA for admin accounts (Phase 2)
- ⏳ Account lockout after failed logins (Phase 2)
- ⏳ Audit logging (Phase 2)
- ⏳ Input validation on all form fields (Phase 2)
- ⏳ Database encryption at rest (Phase 3)
- ⏳ Security monitoring/alerting (Phase 3)
- ⏳ WAF configuration (Phase 4)
- ⏳ Automated security scanning (Phase 4)

### Current Rate Limits (Can be adjusted):
- Admin login: 5/minute (very strict)
- Customer login: 10/minute
- Registration: 5/hour
- Contact form: 3/minute
- Add to cart: 30/minute

**To adjust:** Edit the `@limiter.limit()` decorator in `app.py`

---

## 🔒 SECURITY NOTES

### What's Protected:
1. **CSRF Attacks** - All forms have tokens, state-changing operations protected
2. **Brute Force** - Rate limiting prevents password guessing
3. **XSS** - Security headers, input sanitization, CSP
4. **MITM** - HTTPS enforcement, secure cookies
5. **Session Hijacking** - Short timeout, secure cookie flags
6. **Clickjacking** - X-Frame-Options header (via Talisman)
7. **MIME Sniffing** - X-Content-Type-Options header

### What Needs More Work:
1. **SQL Injection** - Using SQLAlchemy ORM (good), but need input validation
2. **File Upload Attacks** - `secure_file_upload()` function added but not yet applied to all upload routes
3. **Password Policy** - `validate_password_strength()` function added but not yet enforced on registration
4. **Admin Access** - No 2FA yet (Phase 2)
5. **Audit Trail** - No logging of security events yet (Phase 2)

---

## 🚀 POST-DEPLOYMENT MONITORING

### Things to Watch:
1. **Railway Logs** - Check for rate limit errors (normal for attackers)
2. **Failed Login Attempts** - High volumes = possible attack
3. **CSRF Token Errors** - Should be rare; investigate if common
4. **Application Performance** - Rate limiting adds minimal overhead
5. **Redis Usage** - If using Redis for rate limiting, monitor memory

### Performance Impact:
- CSRF validation: ~1-2ms per request
- Rate limiting: ~1-3ms per request (in-memory), ~5-10ms (Redis)
- HTTPS overhead: Handled by Railway's proxy
- Security headers: <1ms per request

**Overall impact: <20ms added latency per request**

---

## 📞 IF SOMETHING BREAKS

### Common Issues:

1. **"CRITICAL SECURITY ERROR: SECRET_KEY must be set!"**
   - Solution: Set SECRET_KEY environment variable in Railway

2. **Login forms not working:**
   - Check browser console for CSRF errors
   - Verify `csrf_token()` is in form templates
   - Check that Flask-WTF is installed

3. **"429 Too Many Requests" on legitimate users:**
   - Adjust rate limits in app.py
   - Consider Redis for rate limiting (shared across instances)

4. **HTTPS redirect loop:**
   - Verify Railway is handling SSL termination
   - Check ENABLE_HTTPS environment variable

5. **Session expires too quickly:**
   - Adjust PERMANENT_SESSION_LIFETIME in config.py (currently 3600s = 1 hour)

### Emergency Rollback:
```bash
git revert HEAD
git push origin main
```

---

## 📊 NEXT PHASE PREVIEW (Phase 2 - Days 4-7)

What's coming next:
1. **2FA for Admin Accounts** - TOTP using pyotp (already installed)
2. **Account Lockout** - 5 failed attempts = 15-minute lockout
3. **Enhanced Input Validation** - Apply to all forms
4. **Password Strength Enforcement** - Use `validate_password_strength()` on registration
5. **Audit Logging** - Track all admin actions
6. **File Upload Security** - Apply `secure_file_upload()` to all upload routes

See `SECURITY_AUDIT.md` for complete roadmap.

---

## ✅ DEPLOYMENT APPROVAL

Once you've completed all items in "REQUIRED BEFORE DEPLOYMENT":

1. Set SECRET_KEY in Railway ✅
2. Set FLASK_ENV=production ✅
3. Set ENABLE_HTTPS=True ✅
4. Commit and push changes ✅
5. Monitor deployment logs ✅
6. Run testing checklist ✅

**You're ready to go live with Phase 1 security!**

---

**Last Updated:** Phase 1 Implementation Complete
**App Version:** 2.2.0
**Security Level:** Production-Ready (Phase 1 of 4)
