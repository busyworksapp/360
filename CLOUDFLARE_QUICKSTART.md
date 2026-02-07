# 🚀 Cloudflare Quick Start for 360Degree Supply

## ✅ Your Account Information

**Zone ID**: `a8331c11ff49edc7911695d728489522`  
**Account ID**: `7cadcf83e035af60cc06004b11227831`  
**Domain**: `360degreesupply.co.za`

---

## 📋 Step 1: Configure DNS (5 minutes)

### Get Your Railway Domain:
1. Go to **Railway Dashboard**: https://railway.app
2. Select **360Degree Supply** project
3. **Settings** → **Networking**
4. Copy your domain (looks like: `your-app-production.up.railway.app`)

### Add DNS Records in Cloudflare:

1. Go to **Cloudflare Dashboard**: https://dash.cloudflare.com
2. Select **360degreesupply.co.za**
3. Click **DNS** tab
4. Add these records:

#### Record 1 - Root Domain (@):
```
Type: CNAME
Name: @ (or 360degreesupply.co.za)
Target: [paste-your-railway-domain].railway.app
Proxy status: Proxied (☁️ ORANGE)
TTL: Auto
```

#### Record 2 - WWW Subdomain:
```
Type: CNAME  
Name: www
Target: [paste-your-railway-domain].railway.app
Proxy status: Proxied (☁️ ORANGE)
TTL: Auto
```

**Important**: Make sure the cloud is **ORANGE** (Proxied), not gray!

---

## 🔒 Step 2: Configure SSL (3 minutes)

1. Go to **SSL/TLS** tab
2. **Overview** → Select: **Full (strict)**
3. **Edge Certificates**:
   - ✅ Turn ON **Always Use HTTPS**
   - ✅ Turn ON **Automatic HTTPS Rewrites**
   - Set **Minimum TLS Version**: **TLS 1.2**

---

## ⚡ Step 3: Enable Speed Optimizations (2 minutes)

### Auto Minify:
1. Go to **Speed** → **Optimization**
2. Enable:
   - ✅ JavaScript
   - ✅ CSS
   - ✅ HTML

### Compression:
- ✅ **Brotli** (should be ON by default)

---

## 💾 Step 4: Configure Caching (5 minutes)

### Browser Cache:
1. **Caching** → **Configuration**
2. **Browser Cache TTL**: Set to **4 hours**

### Page Rules (3 available on Free plan):

#### Rule 1 - Cache Static Assets:
```
URL Pattern: *360degreesupply.co.za/static/*
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
  - Browser Cache TTL: 7 days
```

#### Rule 2 - Bypass Admin Cache:
```
URL Pattern: *360degreesupply.co.za/admin*
Settings:
  - Cache Level: Bypass
  - Security Level: High
```

#### Rule 3 - Cache Images:
```
URL Pattern: *360degreesupply.co.za/*.{jpg,jpeg,png,gif,webp,svg,ico}
Settings:
  - Cache Level: Cache Everything
  - Edge Cache TTL: 1 month
```

---

## 🛡️ Step 5: Security Settings (3 minutes)

1. **Security** → **Settings**
2. **Security Level**: **Medium**
3. ✅ Enable **Bot Fight Mode**
4. **Challenge Passage**: **30 minutes**

---

## 🌐 Step 6: Update Nameservers

Cloudflare gave you nameservers like:
```
ns1.cloudflare.com
ns2.cloudflare.com
```

### Update at Your Domain Registrar:
1. Login to where you registered `360degreesupply.co.za`
2. Find **DNS/Nameserver Settings**
3. Replace with Cloudflare nameservers
4. **Save changes**

**Wait Time**: 5 minutes to 48 hours (usually 1-2 hours)

---

## 🔑 Step 7: Create API Token (Optional - for cache management)

1. Go to: https://dash.cloudflare.com/profile/api-tokens
2. Click **Create Token**
3. Use **Edit zone DNS** template
4. **Permissions**:
   - Zone → Cache Purge → Purge
   - Zone → Zone Settings → Read
5. **Zone Resources**:
   - Include → Specific zone → `360degreesupply.co.za`
6. Click **Continue to summary**
7. Click **Create Token**
8. **Copy the token** (you won't see it again!)

### Add to Railway:
1. Railway Dashboard → Your project
2. **Variables** tab
3. Add these:
   ```
   CLOUDFLARE_ZONE_ID=a8331c11ff49edc7911695d728489522
   CLOUDFLARE_ACCOUNT_ID=7cadcf83e035af60cc06004b11227831
   CLOUDFLARE_API_TOKEN=[paste your token]
   CLOUDFLARE_ENABLED=True
   ```

---

## ✅ Step 8: Verify Setup

### Check DNS:
```powershell
nslookup www.360degreesupply.co.za
```
Should return Cloudflare IPs (104.x.x.x range)

### Check Website:
Visit: `https://www.360degreesupply.co.za/`
- Should show 🔒 padlock
- Certificate: Cloudflare Inc

### Check Headers:
```powershell
$response = Invoke-WebRequest "https://www.360degreesupply.co.za/" -UseBasicParsing
$response.Headers['CF-RAY']  # Should show Cloudflare ray ID
$response.Headers['Server']  # Should show "cloudflare"
```

---

## 🎯 Quick Commands

### Clear All Cache (after deployment):
```powershell
python cloudflare_cache.py all
```

### Clear Static Assets:
```powershell
python cloudflare_cache.py static
```

### Clear Specific URLs:
```powershell
python cloudflare_cache.py urls https://www.360degreesupply.co.za/ https://www.360degreesupply.co.za/store
```

---

## 📊 Monitor Performance

### Cloudflare Dashboard:
1. Select your domain
2. **Analytics** → **Traffic**
3. View:
   - Requests per day
   - Bandwidth saved
   - Threats blocked
   - Cache hit ratio

### Expected Improvements:
- **Cache Hit Ratio**: 80-95%
- **Bandwidth Reduction**: 60-80%
- **Load Time**: 60-75% faster globally

---

## 🚨 Troubleshooting

### "Too Many Redirects"
**Solution**: 
1. SSL/TLS → Overview
2. Change to **Full (strict)**

### Cloudflare Not Active
**Solution**: 
1. Wait for nameserver propagation (check email)
2. Verify nameservers: https://dnschecker.org/

### Cache Not Working
**Solution**:
1. Check Page Rules are enabled
2. Verify proxy status is ON (orange cloud)
3. Wait 5-10 minutes for rules to apply

### Old Content Showing
**Solution**:
1. Caching → Configuration → **Purge Everything**
2. Or use: `python cloudflare_cache.py all`

---

## 📝 Checklist

- [ ] DNS records added (@ and www)
- [ ] DNS records proxied (orange cloud)
- [ ] SSL set to Full (strict)
- [ ] Always Use HTTPS enabled
- [ ] Auto Minify enabled
- [ ] Browser Cache TTL set
- [ ] Page Rules created (3 rules)
- [ ] Security level set to Medium
- [ ] Bot Fight Mode enabled
- [ ] Nameservers updated at registrar
- [ ] API token created (optional)
- [ ] Environment variables added to Railway
- [ ] DNS propagation complete
- [ ] Website accessible via Cloudflare
- [ ] Cache working (check CF-Cache-Status header)

---

## 🎉 Success Indicators

You'll know it's working when:
- ✅ `nslookup` shows Cloudflare IPs
- ✅ Response headers show `CF-RAY` and `Server: cloudflare`
- ✅ Static assets return `CF-Cache-Status: HIT`
- ✅ Cloudflare dashboard shows traffic
- ✅ Load times improved significantly
- ✅ Analytics showing cache hit ratio

---

## 📞 Support

- **Cloudflare Community**: https://community.cloudflare.com/
- **Cloudflare Docs**: https://developers.cloudflare.com/
- **Railway Discord**: https://discord.gg/railway

---

## 🔄 After Setup

### When Deploying Updates:
```powershell
# 1. Deploy to Railway (git push)
git push origin main

# 2. Wait for Railway deployment (2-3 minutes)

# 3. Purge Cloudflare cache
python cloudflare_cache.py all

# 4. Test changes
# Visit: https://www.360degreesupply.co.za/
```

### Weekly Maintenance:
- Check Cloudflare analytics
- Review threats blocked
- Monitor cache hit ratio
- Optimize cache rules if needed

---

**Your account is ready!** Just follow the steps above to activate Cloudflare. 🚀

**Estimated Setup Time**: 30 minutes + DNS propagation (1-24 hours)

**Last Updated**: February 7, 2026  
**Zone ID**: a8331c11ff49edc7911695d728489522
