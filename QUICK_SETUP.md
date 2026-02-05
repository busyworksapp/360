# ⚡ QUICK REFERENCE - Railway S3 Setup

## 🎯 What You Need to Do NOW

### Step 1: Add Environment Variables (5 minutes)
Go to: **Railway Dashboard → Your Project → Variables Tab**

Copy-paste these **9 variables** one by one:

```
SECRET_KEY=00c284d8f3c9df87c6de9fd12cd9a839d4302ddb560b1cbc05cfde92c3bb6a67
FLASK_ENV=production
ENABLE_HTTPS=True
S3_ENDPOINT_URL=https://t3.storageapi.dev
S3_REGION=auto
S3_BUCKET_NAME=collapsible-larder-kyexia
S3_ACCESS_KEY_ID=tid_LXFhRXKmgkcfkfZ_SUyMKRlRMXQnoRt_ZfxEtQoUiOeNVmRfFA
S3_SECRET_ACCESS_KEY=tsec_bf3CqpB48On0gAzhTLW0uvGFPPF+Xt7TD2SCDg5dtt+xWW9nqXuJCfkOeRmflQigkB1SI_
S3_USE_VIRTUAL_HOST_STYLE=true
```

### Step 2: Wait for Deployment (2-3 minutes)
Railway will automatically redeploy. Watch the logs.

### Step 3: Test Upload (2 minutes)
1. Login to admin: `https://your-railway-url.up.railway.app/admin/login`
2. Company Settings → Upload Logo
3. Verify image loads (no 404)

---

## ✅ Success Checklist

Railway Logs should show:
```
✅ S3 Storage initialized: collapsible-larder-kyexia
✅ Security middleware active
* Running on http://127.0.0.1:8080
```

Upload should return:
```
✅ S3 URL: https://t3.storageapi.dev/collapsible-larder-kyexia/uploads/...
```

---

## 🆘 If Something Goes Wrong

### Error: "CRITICAL SECURITY ERROR: SECRET_KEY must be set"
**Fix**: Add `SECRET_KEY` variable to Railway

### Error: "S3 storage is not enabled"
**Fix**: Add all 6 S3 variables (S3_ENDPOINT_URL through S3_USE_VIRTUAL_HOST_STYLE)

### Error: "ModuleNotFoundError: No module named 's3_storage'"
**Fix**: Wait for build to complete (2-3 min), Railway is still deploying

### Upload succeeds but shows 404
**Check**: Is it an OLD file (uploaded before S3)?
**Fix**: Re-upload through admin panel

---

## 📚 Documentation Files

- `ADD_RAILWAY_VARIABLES.md` - Detailed variable setup guide
- `S3_INTEGRATION_COMPLETE.md` - Full integration summary
- `SECURITY_AUDIT.md` - Security roadmap (4 phases)
- `DEPLOYMENT_CHECKLIST.md` - Complete deployment guide

---

## 🎉 What Was Fixed

**Problem**: Railway's ephemeral filesystem lost all uploaded files
**Solution**: S3 cloud storage - files persist forever
**Impact**: All uploads (logos, products, proofs) now work

---

## ⏰ Total Time Needed

- Add variables: **5 minutes**
- Wait for deploy: **2-3 minutes**
- Test uploads: **2 minutes**
- **TOTAL: ~10 minutes**

---

## 🚀 Ready?

**Next Action**: Go add those 9 variables to Railway NOW!

**Then**: Test an upload and you're done! 🎉
