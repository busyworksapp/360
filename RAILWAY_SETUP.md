# Railway Environment Variables Setup

## ⚠️ CRITICAL: Set These Variables NOW

Go to Railway Dashboard: https://railway.app/dashboard

### Steps:

1. **Click on your project** (360)
2. **Click on your service** (web service)
3. **Click "Variables" tab**
4. **Add these three variables:**

```bash
SECRET_KEY=00c284d8f3c9df87c6de9fd12cd9a839d4302ddb560b1cbc05cfde92c3bb6a67
```
```bash
FLASK_ENV=production
```
```bash
ENABLE_HTTPS=True
```

### How to Add Variables in Railway:

1. Click "+ New Variable"
2. Enter Variable Name: `SECRET_KEY`
3. Enter Value: `00c284d8f3c9df87c6de9fd12cd9a839d4302ddb560b1cbc05cfde92c3bb6a67`
4. Click "Add"
5. Repeat for `FLASK_ENV` and `ENABLE_HTTPS`

### ✅ Verify Existing Variables:

Make sure these are already set (from previous setup):
- `DATABASE_URL` - Should be set automatically by Railway MySQL
- `PAYFAST_MERCHANT_ID` - Already configured
- `PAYFAST_MERCHANT_KEY` - Already configured  
- `PAYFAST_PASSPHRASE` - Already configured
- `PAYFAST_MODE` - Already configured

### After Adding Variables:

Railway will automatically **redeploy** your app (takes 2-3 minutes).

Watch the deployment logs for:
- ✅ "Build successful"
- ✅ "Deployment live"
- ❌ Any error messages about missing SECRET_KEY

---

## Quick Verification (After Deployment):

### 1. Check Deployment Status:
- Railway Dashboard → Deployments tab
- Should show "SUCCESS" or "LIVE"

### 2. Check Logs:
- Railway Dashboard → Deployments → Click latest → View Logs
- Look for startup messages
- No errors about SECRET_KEY

### 3. Test Your App:
```bash
# Update the URL in test_security.py and run:
python test_security.py
```

### 4. Manual Browser Test:
Visit your Railway URL:
- Should automatically redirect HTTP → HTTPS
- Login should work normally
- Try logging in 6 times quickly (should get rate limited)

---

## Troubleshooting:

### Error: "CRITICAL SECURITY ERROR: SECRET_KEY must be set!"
**Solution:** Add SECRET_KEY variable in Railway (see above)

### Error: "ModuleNotFoundError: No module named 'flask_wtf'"
**Solution:** Railway should auto-install from requirements.txt. Check build logs.

### Error: "Database connection failed"
**Solution:** Verify DATABASE_URL is set correctly in Railway variables

### HTTPS not enforcing:
**Solution:** Make sure ENABLE_HTTPS=True is set in Railway variables

---

## Security Checklist:

- [ ] SECRET_KEY added to Railway
- [ ] FLASK_ENV=production added to Railway
- [ ] ENABLE_HTTPS=True added to Railway
- [ ] Deployment shows "SUCCESS"
- [ ] No errors in deployment logs
- [ ] App loads in browser (HTTPS)
- [ ] Login works
- [ ] Rate limiting works (test with 6 rapid attempts)
- [ ] Security headers visible in browser DevTools

---

## Your Railway App URL:

Find it in Railway Dashboard → Service → Settings → Domains

Format: `https://your-app-name.railway.app`

Update this in `test_security.py` to run automated tests.

---

**Current Status:** ✅ Code deployed, waiting for environment variables
**Next Step:** Add SECRET_KEY, FLASK_ENV, ENABLE_HTTPS to Railway
