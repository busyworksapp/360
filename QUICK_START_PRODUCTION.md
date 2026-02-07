# 🚀 Quick Start - Production Deployment

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally with Gunicorn
gunicorn --config gunicorn_config.py app:app

# Or just deploy to Railway - it will use the Procfile automatically
```

## Health Check URLs

| Endpoint | Purpose |
|----------|---------|
| `/health` | Basic health check (for load balancers) |
| `/health/detailed` | Detailed diagnostics |
| `/metrics` | System & application metrics |
| `/status` | Application version & status |

## Key Environment Variables

```bash
# Minimum required
SECRET_KEY=your-secret-key
FLASK_ENV=production
DATABASE_URL=mysql://...

# Recommended
REDIS_URL=redis://...
LOG_LEVEL=INFO
GUNICORN_WORKERS=4
```

## Test Deployment

```bash
# 1. Check health
curl https://your-app.railway.app/health

# 2. View metrics
curl https://your-app.railway.app/metrics

# 3. Check logs
railway logs --tail
```

## Monitoring Checklist

- [ ] Health endpoint returns 200 OK
- [ ] Database connectivity is healthy
- [ ] Redis cache is connected (if configured)
- [ ] S3 storage is configured
- [ ] CPU usage is reasonable (<80%)
- [ ] Memory usage is stable
- [ ] No slow requests in logs (>1s)
- [ ] Worker processes are running

## Common Commands

```bash
# View live logs
railway logs --tail

# Check environment
railway env

# Restart application
railway up --detach

# Open in browser
railway open
```

## Performance Tuning

**For 1 CPU / 512MB RAM:**
```bash
GUNICORN_WORKERS=2
GUNICORN_THREADS=2
DB_POOL_SIZE=5
```

**For 2 CPU / 1GB RAM:**
```bash
GUNICORN_WORKERS=4
GUNICORN_THREADS=2
DB_POOL_SIZE=10
```

**For 4 CPU / 2GB RAM:**
```bash
GUNICORN_WORKERS=9
GUNICORN_THREADS=2
DB_POOL_SIZE=20
```

## Quick Troubleshooting

### App won't start
1. Check logs: `railway logs`
2. Verify SECRET_KEY is set
3. Check DATABASE_URL format

### High memory usage
1. Check metrics: `/metrics`
2. Reduce workers: `GUNICORN_WORKERS=2`
3. Check for memory leaks in logs

### Slow performance
1. Enable Redis caching
2. Check slow request logs
3. Increase worker threads
4. Review database connection pool

### Database errors
1. Check `/health/detailed`
2. Verify DATABASE_URL
3. Check connection pool stats in `/metrics`

## What Changed

✅ **Production Server:** Flask dev server → Gunicorn  
✅ **Logging:** Simple prints → Structured JSON logs  
✅ **Monitoring:** None → Health checks + metrics  
✅ **Performance:** Basic → Optimized with pooling  

## Next Steps

1. Deploy to Railway
2. Test health endpoints
3. Monitor logs for first hour
4. Set up alerting on health checks
5. Review metrics daily for first week

**Everything is ready! Just deploy and monitor.** 🎉
