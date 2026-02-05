# ⚡ ADD THESE 9 ENVIRONMENT VARIABLES TO RAILWAY NOW

## 🎯 Action Required: Go to Railway Dashboard → Your Project → Variables Tab

Railway URL: https://railway.app/

### Copy-Paste These Variables (One by One):

```bash
# 1. SECRET_KEY (Required for Flask security)
SECRET_KEY=00c284d8f3c9df87c6de9fd12cd9a839d4302ddb560b1cbc05cfde92c3bb6a67

# 2. FLASK_ENV (Production mode)
FLASK_ENV=production

# 3. ENABLE_HTTPS (Force HTTPS redirect)
ENABLE_HTTPS=True

# 4. S3_ENDPOINT_URL (Railway Object Storage endpoint)
S3_ENDPOINT_URL=https://t3.storageapi.dev

# 5. S3_REGION (Auto-detect region)
S3_REGION=auto

# 6. S3_BUCKET_NAME (Your storage bucket)
S3_BUCKET_NAME=collapsible-larder-kyexia

# 7. S3_ACCESS_KEY_ID (Storage credentials)
S3_ACCESS_KEY_ID=tid_LXFhRXKmgkcfkfZ_SUyMKRlRMXQnoRt_ZfxEtQoUiOeNVmRfFA

# 8. S3_SECRET_ACCESS_KEY (Storage secret key)
S3_SECRET_ACCESS_KEY=tsec_bf3CqpB48On0gAzhTLW0uvGFPPF+Xt7TD2SCDg5dtt+xWW9nqXuJCfkOeRmflQigkB1SI_

# 9. S3_USE_VIRTUAL_HOST_STYLE (URL format)
S3_USE_VIRTUAL_HOST_STYLE=true
```

---

## ✅ Expected Console Output After Deployment:

Look for these messages in Railway logs:

```
✅ S3 Storage initialized: collapsible-larder-kyexia
✅ Security middleware active
* Running on http://127.0.0.1:8080
```

---

## ⚠️ If You See These Errors:

### "CRITICAL SECURITY ERROR: SECRET_KEY environment variable must be set!"
- **Fix**: Add `SECRET_KEY` variable in Railway dashboard

### "S3 storage is not enabled"
- **Fix**: Add all 6 S3 variables (S3_ENDPOINT_URL through S3_USE_VIRTUAL_HOST_STYLE)

### "ModuleNotFoundError: No module named 's3_storage'"
- **Fix**: Railway should auto-deploy after git push. Wait 2-3 minutes and check logs.

---

## 🧪 Test After Adding Variables:

1. **Login to admin panel** at: `https://your-railway-url.up.railway.app/admin/login`
2. **Navigate to Company Settings** 
3. **Upload a logo image**
4. **Verify**: Image should load immediately (not 404)
5. **Check the URL**: Should be `https://t3.storageapi.dev/collapsible-larder-kyexia/uploads/...`

---

## 🔐 Security Check:

After deployment, verify security headers using browser DevTools:

1. Open **DevTools (F12)** → **Network Tab**
2. Refresh the page
3. Click on the main page request
4. Check **Response Headers**:
   - ✅ `Strict-Transport-Security: max-age=31536000; includeSubDomains`
   - ✅ `X-Content-Type-Options: nosniff`
   - ✅ `X-XSS-Protection: 1; mode=block`
   - ✅ `Content-Security-Policy: default-src 'self'; ...`

---

## 📊 Monitor Deployment:

1. Go to Railway Dashboard → **Deployments**
2. Click on the latest deployment (commit: `a62a89f`)
3. Watch build logs for:
   ```
   Successfully built requirements
   Installing dependencies...
   Starting application...
   ```

---

## 🚨 Critical: File Upload Fix

**Before S3 Integration:**
- ❌ Files saved to local `/static/uploads/` (ephemeral)
- ❌ Files lost on every deployment
- ❌ 404 errors for all uploaded images

**After S3 Integration (NOW):**
- ✅ Files saved to Railway Object Storage (persistent)
- ✅ Files survive deployments forever
- ✅ Direct S3 URLs: `https://t3.storageapi.dev/bucket/...`

---

## 📝 Next Steps After Variables Added:

1. Wait 2-3 minutes for Railway to redeploy
2. Check deployment logs for success messages
3. Test file upload functionality
4. Verify uploaded files are accessible
5. Run security header checks

---

## 🆘 Troubleshooting:

### Railway app won't start:
```bash
# Check Railway logs for the exact error
# Common issues:
# 1. Missing SECRET_KEY → Add variable
# 2. Invalid S3 credentials → Double-check key/secret
# 3. Module not found → Wait for build to complete
```

### Files still showing 404:
```bash
# Old files (uploaded before S3) will show 404
# Solution: Re-upload them through the admin panel
# New uploads will work immediately
```

### Upload fails with error message:
```bash
# Check Railway logs for S3 errors
# Possible causes:
# 1. Wrong S3_ENDPOINT_URL
# 2. Invalid credentials
# 3. Bucket name mismatch
```

---

## ✨ What Changed in Latest Deployment:

**Commit: a62a89f** - "Integrate S3 cloud storage for persistent file uploads"

**Files Modified:**
- `app.py` (3 changes):
  1. Added `from s3_storage import storage_service` at top
  2. Replaced `save_upload_file()` function to use S3 (lines 249-267)
  3. Updated proof of payment upload to use S3 (lines 2250-2295)

**Impact:**
- ✅ Company logo uploads → S3
- ✅ Product images → S3
- ✅ Service images → S3
- ✅ Hero section backgrounds → S3
- ✅ Proof of payment documents → S3

**Database Changes:**
- File URLs now store full S3 URLs instead of local paths
- Example: `https://t3.storageapi.dev/collapsible-larder-kyexia/uploads/product_20260204_203045_a3f8b2c1.jpg`

---

## 🎉 Success Criteria:

You'll know it's working when:

1. ✅ Railway deployment shows "Running"
2. ✅ Logs show "S3 Storage initialized: collapsible-larder-kyexia"
3. ✅ File upload returns S3 URL (not `/static/uploads/...`)
4. ✅ Uploaded images load immediately (no 404)
5. ✅ Images survive redeployments

---

**⏰ Estimated Time to Add Variables: 5 minutes**

**🚀 Ready? Go add those variables now!**
