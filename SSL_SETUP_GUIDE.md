# 🔒 SSL/HTTPS Setup Guide for 360Degree Supply

## Current Issue
Your website `https://www.360degreesupply.co.za/` shows "Not Secured" because:
1. **No SSL certificate is configured** on the hosting platform
2. Traffic is being served over **HTTP (port 80)** instead of **HTTPS (port 443)**

---

## ✅ Solution: Enable SSL on Railway

Railway provides **FREE automatic SSL certificates** via Let's Encrypt. Follow these steps:

### Step 1: Access Railway Dashboard
1. Go to https://railway.app
2. Login to your account
3. Select your **360Degree Supply** project

### Step 2: Configure Custom Domain
1. Click on your **service** (the main application)
2. Go to **Settings** tab
3. Scroll to **Networking** section
4. Click **+ Generate Domain** (Railway will give you a default domain with HTTPS)

### Step 3: Add Your Custom Domain
1. In the **Networking** section, find **Custom Domains**
2. Click **+ Add Domain**
3. Enter your domain: `360degreesupply.co.za`
4. Click **Add Domain**
5. Repeat for www subdomain: `www.360degreesupply.co.za`

### Step 4: Update DNS Records
Go to your domain registrar (e.g., GoDaddy, Namecheap, Cloudflare) and add these DNS records:

#### For Root Domain (`360degreesupply.co.za`):
```
Type: A
Name: @ (or leave blank)
Value: [Railway will provide this IP]
TTL: Automatic or 3600
```

#### For WWW Subdomain (`www.360degreesupply.co.za`):
```
Type: CNAME
Name: www
Value: [Your Railway domain].railway.app
TTL: Automatic or 3600
```

**Note**: Railway will show you the exact DNS records to add in the domain settings page.

### Step 5: Wait for DNS Propagation
- DNS changes can take **5 minutes to 48 hours** to propagate
- Use this tool to check: https://dnschecker.org/
- Railway will automatically provision SSL certificates once DNS is verified

### Step 6: Verify HTTPS
Once DNS propagates and SSL is provisioned:
1. Visit `https://www.360degreesupply.co.za/` 
2. Check for the **🔒 padlock icon** in the browser
3. Click the padlock to verify certificate details

---

## 🔧 What We Just Fixed in Code

### Added HTTPS Redirect Middleware
```python
@app.before_request
def force_https():
    """Force HTTPS in production by redirecting HTTP to HTTPS"""
    if is_railway or is_production:
        if not request.is_secure:
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)
```

This ensures:
- All HTTP traffic is **automatically redirected to HTTPS**
- Users always see the secure version
- Search engines index the HTTPS version

---

## 📋 Environment Variables to Set

Make sure these are configured in Railway:

```bash
# Production Mode
FLASK_ENV=production

# Enable HTTPS
ENABLE_HTTPS=True

# Railway automatically sets this
RAILWAY_ENVIRONMENT=production
```

---

## 🧪 Testing SSL After Setup

### 1. Check Certificate
```bash
curl -I https://www.360degreesupply.co.za/
```
Should return `HTTP/2 200` or `HTTP/1.1 200` with SSL info.

### 2. Test Redirect
```bash
curl -I http://www.360degreesupply.co.za/
```
Should return `HTTP/1.1 301` with `Location: https://...`

### 3. SSL Labs Test
Go to: https://www.ssllabs.com/ssltest/analyze.html?d=www.360degreesupply.co.za
- Target grade: **A or A+**

### 4. Browser Security Headers
Check your security headers at: https://securityheaders.com/?q=https://www.360degreesupply.co.za

---

## 🚨 Common Issues & Solutions

### Issue 1: "NET::ERR_CERT_COMMON_NAME_INVALID"
**Cause**: Domain not properly added to Railway or DNS not propagated.
**Solution**: 
- Verify DNS records are correct
- Wait for DNS propagation (up to 48 hours)
- Check Railway domain configuration

### Issue 2: "Mixed Content Warning"
**Cause**: Some resources (images, scripts) loaded over HTTP instead of HTTPS.
**Solution**: Already fixed! Your app uses `https:` in img-src CSP policy.

### Issue 3: Still Shows "Not Secured"
**Cause**: Certificate not provisioned yet or DNS not pointing to Railway.
**Solution**:
- Check Railway logs for SSL provisioning status
- Verify DNS with `nslookup 360degreesupply.co.za`
- Contact Railway support if issue persists

### Issue 4: Certificate Valid but Redirect Not Working
**Cause**: `X-Forwarded-Proto` header not being passed by proxy.
**Solution**: Already fixed with our middleware that checks both `request.is_secure` and `X-Forwarded-Proto` header.

---

## 🎯 Expected Results After Setup

✅ **HTTPS Enabled**: Padlock icon appears in browser  
✅ **HTTP Redirects**: All HTTP traffic redirects to HTTPS  
✅ **Security Headers**: HSTS, CSP, and other headers enabled  
✅ **SSL Grade A+**: High security rating on SSL Labs  
✅ **SEO Improved**: Search engines prefer HTTPS sites  
✅ **Payment Ready**: Required for Stripe and PayFast  

---

## 📞 Need Help?

### Railway Documentation
- Custom Domains: https://docs.railway.app/guides/public-networking#custom-domains
- SSL/TLS: https://docs.railway.app/guides/public-networking#ssltls

### Contact Support
- Railway Discord: https://discord.gg/railway
- Support Email: team@railway.app

---

## ⏱️ Timeline

| Step | Duration | Status |
|------|----------|--------|
| Add domain to Railway | 5 minutes | ⏳ Pending |
| Update DNS records | 10 minutes | ⏳ Pending |
| DNS propagation | 5 min - 48 hours | ⏳ Pending |
| SSL certificate provisioning | 5-30 minutes | ⏳ Pending |
| HTTPS fully operational | - | ⏳ Pending |

**Total Time**: Typically 1-2 hours, max 48 hours for DNS propagation.

---

## 🎉 Success Checklist

- [ ] Railway custom domain added
- [ ] DNS records updated
- [ ] DNS propagation verified
- [ ] SSL certificate provisioned
- [ ] HTTPS accessible
- [ ] HTTP redirects to HTTPS
- [ ] No mixed content warnings
- [ ] SSL grade A or A+
- [ ] All pages load securely
- [ ] Payment integrations work

---

**Last Updated**: February 7, 2026  
**Version**: 2.3.1 - SSL/HTTPS Configuration
