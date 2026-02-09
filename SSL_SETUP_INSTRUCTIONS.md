# SSL Certificate Setup for HTTPS

## Option 1: Self-Signed Certificate (Testing Only - Browser Warning)

Run this in PowerShell as Administrator:

```powershell
# Generate self-signed certificate
$cert = New-SelfSignedCertificate -DnsName "localhost" -CertStoreLocation "cert:\LocalMachine\My"
$pwd = ConvertTo-SecureString -String "password123" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath "cert.pfx" -Password $pwd

# Convert to PEM format (requires OpenSSL)
openssl pkcs12 -in cert.pfx -out cert.pem -nodes -passin pass:password123
openssl pkcs12 -in cert.pfx -nocerts -out key.pem -nodes -passin pass:password123
```

Then update app.py to use SSL:
```python
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000, 
            ssl_context=('cert.pem', 'key.pem'))
```

## Option 2: Free SSL with Let's Encrypt (Production - Requires Domain)

1. Get a domain name (e.g., from Cloudflare, Namecheap)
2. Point domain to your public IP
3. Use Certbot to get free SSL:

```bash
# Install Certbot
pip install certbot

# Get certificate
certbot certonly --standalone -d yourdomain.com
```

## Option 3: Deploy to Cloud (Recommended - Automatic HTTPS)

Your app is already configured for Railway deployment with automatic HTTPS:

1. Go to https://railway.app
2. Create new project
3. Connect your GitHub repo or deploy directly
4. Railway provides automatic HTTPS with valid certificate

## Current Status

Your app is configured for production with:
- ✅ HTTPS enforcement enabled
- ✅ Security headers configured
- ✅ Database connected (Railway MySQL)
- ✅ S3 storage configured

To access on other networks:
1. Run `setup_secure_access.bat` as Administrator
2. Share your IP address (shown in the script)
3. Others access via: http://YOUR_IP:5000

For true HTTPS security, deploy to Railway or get a domain + SSL certificate.
