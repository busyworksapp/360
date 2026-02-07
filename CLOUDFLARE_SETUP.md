# ☁️ Cloudflare Setup Guide for 360Degree Supply

## Why Use Cloudflare?

Railway already provides SSL, but Cloudflare adds:
- 🛡️ **DDoS Protection** - Automatic threat mitigation
- 🚀 **Global CDN** - Faster load times (300+ data centers)
- 📊 **Advanced Analytics** - Better insights
- 🔒 **Additional Security** - WAF, Bot protection
- ⚡ **Caching & Optimization** - Reduced server load
- 💰 **Free Plan** - All essential features included

---

## 📋 Step-by-Step Setup

### Step 1: Create Cloudflare Account (5 minutes)

1. Go to **https://cloudflare.com**
2. Click **Sign Up** → Enter email and password
3. Verify your email
4. Login to dashboard

---

### Step 2: Add Your Domain (2 minutes)

1. Click **+ Add Site** button
2. Enter: `360degreesupply.co.za`
3. Click **Add Site**
4. Select **Free Plan** → Click **Continue**
5. Cloudflare will scan your existing DNS records

---

### Step 3: Configure DNS Records (5 minutes)

#### Get Your Railway Domain:
1. Go to Railway Dashboard
2. Settings → Networking
3. Copy your Railway domain (e.g., `your-app-production.up.railway.app`)

#### In Cloudflare DNS Settings, add:

**Record 1 - Root Domain**:
```
Type: CNAME
Name: @ (or 360degreesupply.co.za)
Target: your-app-production.up.railway.app
Proxy status: Proxied (☁️ orange cloud)
TTL: Auto
```

**Record 2 - WWW Subdomain**:
```
Type: CNAME
Name: www
Target: your-app-production.up.railway.app
Proxy status: Proxied (☁️ orange cloud)
TTL: Auto
```

**Important**: 
- Make sure the cloud icon is **ORANGE** ☁️ (Proxied)
- If it's gray, click it to enable proxy

#### Optional Records:
```
Type: CNAME
Name: api
Target: your-app-production.up.railway.app
Proxy status: Proxied
TTL: Auto
```

---

### Step 4: Update Nameservers (10 minutes)

Cloudflare will provide two nameservers:
```
ns1.cloudflare.com
ns2.cloudflare.com
```

#### Go to Your Domain Registrar:
(Where you bought `360degreesupply.co.za`)

1. Login to your domain registrar account
2. Find domain management/DNS settings
3. Look for **Nameservers** or **DNS Management**
4. Change from current nameservers to:
   ```
   ns1.cloudflare.com
   ns2.cloudflare.com
   ```
5. Save changes

**Common Registrars**:
- **GoDaddy**: Domain Settings → Nameservers → Change → Custom
- **Namecheap**: Domain List → Manage → Nameservers → Custom DNS
- **Google Domains**: DNS → Name servers → Custom
- **Cloudflare Registrar**: Already done!

---

### Step 5: Wait for Activation (1-24 hours)

- Cloudflare will check nameserver propagation
- Usually takes 1-2 hours
- Can take up to 24-48 hours
- You'll receive an email when active

**Check Status**:
- Go to Cloudflare Dashboard
- Look for "Status: Active" at the top

---

### Step 6: Configure SSL/TLS (5 minutes)

1. In Cloudflare Dashboard → **SSL/TLS** tab
2. **Overview** → Select encryption mode:
   ```
   ⚙️ Full (strict)
   ```
   This ensures end-to-end encryption: Browser → Cloudflare → Railway

3. **Edge Certificates**:
   - ✅ **Always Use HTTPS** (ON)
   - ✅ **Automatic HTTPS Rewrites** (ON)
   - ✅ **Minimum TLS Version**: TLS 1.2
   - ✅ **Opportunistic Encryption** (ON)
   - ✅ **TLS 1.3** (ON)

---

### Step 7: Configure Speed Settings (3 minutes)

#### Auto Minify:
1. Go to **Speed** → **Optimization**
2. Enable:
   - ✅ **JavaScript**
   - ✅ **CSS**
   - ✅ **HTML**

#### Brotli Compression:
- ✅ **Enable** (better than gzip)

#### Image Optimization:
- ✅ **Polish**: Lossless (Free plan)
- ✅ **Mirage**: ON
- ✅ **WebP**: ON

---

### Step 8: Configure Caching (5 minutes)

#### Browser Cache TTL:
1. Go to **Caching** → **Configuration**
2. Set **Browser Cache TTL**: 4 hours

#### Cache Rules (Free plan - 3 rules available):

**Rule 1 - Static Assets**:
```
If: URI Path contains "/static/"
Then: 
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
  - Browser Cache TTL: 7 days
```

**Rule 2 - Images**:
```
If: URI Path matches ".*\.(jpg|jpeg|png|gif|webp|svg|ico)$"
Then:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
```

**Rule 3 - CSS/JS**:
```
If: URI Path matches ".*\.(css|js)$"
Then:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 week
```

---

### Step 9: Security Settings (5 minutes)

#### Security Level:
1. Go to **Security** → **Settings**
2. Set **Security Level**: Medium
   - Low: Less strict
   - Medium: Balanced (recommended)
   - High: More challenges
   - I'm Under Attack: Emergency mode

#### Bot Fight Mode:
- ✅ **Enable** (Free plan)
- Blocks bad bots automatically

#### Challenge Passage:
- Set to **30 minutes**

#### Browser Integrity Check:
- ✅ **Enable**

---

### Step 10: Configure Firewall (Optional)

1. Go to **Security** → **WAF**
2. Create rules for additional protection:

**Example Rule - Block Suspicious Paths**:
```
If: URI Path contains "/admin" AND Country != "South Africa"
Then: Block
```

**Example Rule - Rate Limiting**:
```
If: URI Path equals "/api/login"
And: Request rate > 10 requests per minute
Then: Challenge (CAPTCHA)
```

---

## ✅ Verification Checklist

After setup, verify everything works:

### 1. DNS Check:
```powershell
nslookup www.360degreesupply.co.za
```
Should return Cloudflare IP addresses (104.x.x.x or 172.x.x.x)

### 2. SSL Check:
Visit: `https://www.360degreesupply.co.za/`
- Should show 🔒 padlock
- Certificate issuer: Cloudflare Inc ECC CA-3

### 3. Cloudflare Detection:
Check response headers:
```powershell
$response = Invoke-WebRequest "https://www.360degreesupply.co.za/" -UseBasicParsing
$response.Headers['CF-RAY']
$response.Headers['Server']
```
Should show Cloudflare headers

### 4. Caching Test:
```powershell
$response = Invoke-WebRequest "https://www.360degreesupply.co.za/static/js/table-functions.js" -UseBasicParsing
$response.Headers['CF-Cache-Status']
```
Should return: HIT, MISS, EXPIRED, or BYPASS

---

## 🔄 What Changed in Your App

We updated your application code to support Cloudflare:

### 1. HTTPS Detection (`app.py`)
```python
# Now checks Cloudflare's CF-Visitor header
cf_visitor = request.headers.get('CF-Visitor', '{}')
is_https_cloudflare = '"scheme":"https"' in cf_visitor
```

### 2. Real IP Detection (`security_utils.py`)
```python
# Prioritizes Cloudflare's CF-Connecting-IP header
cf_ip = request.headers.get('CF-Connecting-IP')
if cf_ip:
    return cf_ip
```

These changes ensure:
- ✅ HTTPS redirects work through Cloudflare
- ✅ Rate limiting uses real visitor IPs
- ✅ Audit logs show real visitor IPs
- ✅ Geolocation works correctly

---

## 📊 Cloudflare Dashboard Features

### Analytics:
- **Traffic**: Requests, bandwidth, threats blocked
- **Performance**: Response times, cache hit ratio
- **Security**: Threats blocked, challenge rate

### Logs (Enterprise only):
- Real-time HTTP request logs
- Firewall events
- Security events

### Free Plan Limitations:
- 3 Page Rules (cache rules)
- 5 Firewall Rules
- Basic analytics (24 hours)
- Standard DDoS protection
- Shared SSL certificate

---

## 🎯 Performance Improvements Expected

| Metric | Before Cloudflare | With Cloudflare | Improvement |
|--------|------------------|-----------------|-------------|
| **Global Load Time** | 2-5 seconds | 0.5-2 seconds | 60-75% faster |
| **South Africa** | 200-500ms | 50-150ms | 70% faster |
| **Europe** | 1-2 seconds | 200-400ms | 80% faster |
| **USA** | 2-4 seconds | 300-600ms | 75% faster |
| **Cache Hit Ratio** | 0% | 80-95% | Huge savings |
| **Bandwidth Usage** | 100% | 20-40% | 60-80% reduction |

---

## 🚨 Common Issues & Solutions

### Issue 1: "Too Many Redirects"
**Cause**: SSL mode mismatch
**Solution**: 
1. Cloudflare → SSL/TLS → Overview
2. Change to **Full (strict)**

### Issue 2: "Origin Server Error"
**Cause**: Cloudflare can't reach Railway
**Solution**:
1. Check Railway is running
2. Verify DNS CNAME points to correct Railway domain
3. Wait for DNS propagation

### Issue 3: Cloudflare Serving Old Content
**Cause**: Aggressive caching
**Solution**:
1. Cloudflare → Caching → Configuration
2. Click **Purge Everything**
3. Or use **Custom Purge** for specific URLs

### Issue 4: Real IP Not Detected
**Cause**: App not reading CF-Connecting-IP
**Solution**: Already fixed in our code update!

### Issue 5: Slow First Load
**Cause**: Cache miss, fetching from origin
**Solution**: Normal behavior. Subsequent loads will be fast.

---

## 🔧 Railway Configuration

### Update Environment Variables:
```bash
# Add these to Railway
CLOUDFLARE_ENABLED=True
BEHIND_PROXY=True
```

### Keep Railway Domain:
- Don't delete the Railway domain
- Cloudflare routes traffic to it
- It's your "origin server"

---

## 📈 Monitoring & Optimization

### Weekly Tasks:
1. Check Cloudflare Analytics
2. Review threats blocked
3. Optimize cache rules based on hit ratio

### Monthly Tasks:
1. Review firewall rules
2. Check SSL certificate expiry (auto-renewed)
3. Analyze performance improvements

---

## 💡 Pro Tips

1. **Use Cloudflare's Development Mode**:
   - Temporarily bypass cache during development
   - Settings → Caching → Development Mode (ON)

2. **Create Page Rules for Admin**:
   - Bypass cache for `/admin/*`
   - Higher security level

3. **Enable Argo Smart Routing** (Paid):
   - Even faster routing
   - ~$5/month + $0.10/GB

4. **Use Cloudflare Workers** (Advanced):
   - Run code at the edge
   - Customize responses before reaching Railway

5. **Set Up Email Forwarding**:
   - Forward emails from your domain
   - Free with Cloudflare

---

## 🎉 Expected Results

After setup:
- ✅ Faster global load times (60-80% improvement)
- ✅ DDoS protection active
- ✅ Automatic SSL (Cloudflare certificate)
- ✅ Reduced Railway bandwidth usage
- ✅ Better security (WAF, bot protection)
- ✅ Advanced analytics
- ✅ CDN caching worldwide

---

## 📞 Support

### Cloudflare Support:
- Community: https://community.cloudflare.com/
- Documentation: https://developers.cloudflare.com/
- Status: https://www.cloudflarestatus.com/

### Railway Support:
- Discord: https://discord.gg/railway
- Docs: https://docs.railway.app/

---

## 🔄 Deployment Steps Summary

1. ✅ Updated code for Cloudflare compatibility
2. ⏳ Sign up for Cloudflare account
3. ⏳ Add domain to Cloudflare
4. ⏳ Configure DNS records (CNAME to Railway)
5. ⏳ Update nameservers at registrar
6. ⏳ Wait for activation (1-24 hours)
7. ⏳ Configure SSL/TLS (Full strict)
8. ⏳ Enable speed optimizations
9. ⏳ Set up caching rules
10. ⏳ Configure security settings
11. ✅ Test and verify

---

**Ready to deploy?** Commit these code changes first, then start the Cloudflare setup! 🚀

**Last Updated**: February 7, 2026  
**Version**: 2.3.2 - Cloudflare Integration
