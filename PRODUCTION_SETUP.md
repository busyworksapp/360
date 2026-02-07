# 360Degree Supply - Production Deployment Guide

## 🚀 Production Optimizations Implemented

### Version 2.3.0 - Production Ready with Gunicorn and Monitoring

This update includes comprehensive production optimizations for better performance, monitoring, and reliability.

---

## ✅ What's New

### 1. **Gunicorn Production Server**
- Replaced Flask development server with Gunicorn WSGI server
- Multi-worker configuration for better concurrency
- Automatic worker recycling to prevent memory leaks
- Optimized for Railway deployment

### 2. **Advanced Logging System**
- Structured JSON logging for production
- Colored console logging for development
- Request timing and performance monitoring
- Automatic slow request detection (>1 second)
- Error and exception tracking with full context

### 3. **Health Check & Monitoring**
- `/health` - Basic health check for load balancers
- `/health/detailed` - Comprehensive diagnostics (DB, cache, S3)
- `/metrics` - System metrics (CPU, memory, disk, DB pool)
- `/status` - Application version and status

### 4. **Performance Optimizations**
- Database connection pooling configured
- Redis caching for better performance
- Connection pool monitoring
- Automatic pool recycling

---

## 📋 Configuration Files

### `gunicorn_config.py`
Production-ready Gunicorn configuration with:
- Worker process management
- Timeout settings optimized for OCR processing
- Request logging with timing information
- Automatic worker recycling
- Server lifecycle hooks for monitoring

### `logging_config.py`
Advanced logging system featuring:
- JSON formatter for structured logs
- Colored formatter for development
- Request timing middleware
- Performance decorator for function profiling

### `monitoring.py`
Health check and metrics endpoints:
- Application health status
- Database connectivity checks
- System resource monitoring
- Application metrics

---

## 🔧 Environment Variables

### Required for Production

```bash
# Application
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
DATABASE_URL=mysql://user:password@host:port/database

# Redis (Recommended for production)
REDIS_URL=redis://user:password@host:port

# Gunicorn Configuration (Optional - has sensible defaults)
GUNICORN_WORKERS=4  # Default: (CPU cores * 2) + 1
GUNICORN_THREADS=2  # Default: 2
LOG_LEVEL=INFO      # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Database Pool Settings (Optional)
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_RECYCLE=3600
DB_POOL_TIMEOUT=30

# Monitoring (Optional)
METRICS_ENABLED=True
```

---

## 🚀 Deployment

### Local Testing with Gunicorn

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn --config gunicorn_config.py app:app

# Or use Railway Procfile
railway up
```

### Railway Deployment

The `Procfile` is already configured:
```
web: gunicorn --config gunicorn_config.py app:app
```

Railway will automatically:
1. Install dependencies from `requirements.txt`
2. Run database migrations
3. Start Gunicorn with the configuration
4. Expose the application on $PORT

---

## 📊 Monitoring & Health Checks

### Health Check Endpoints

#### Basic Health Check
```bash
curl https://your-domain.com/health
```

Response (200 OK):
```json
{
  "status": "healthy",
  "database": "healthy",
  "timestamp": "2026-02-07T14:30:00Z"
}
```

#### Detailed Health Check
```bash
curl https://your-domain.com/health/detailed
```

Response includes:
- Database connectivity
- Cache status (if Redis configured)
- S3 storage status
- Overall health assessment

#### System Metrics
```bash
curl https://your-domain.com/metrics
```

Response includes:
- CPU usage
- Memory utilization
- Disk usage
- Process information
- Database connection pool stats

#### Application Status
```bash
curl https://your-domain.com/status
```

Simple status check showing:
- Application name and version
- Environment
- Current timestamp

---

## 📈 Performance Monitoring

### Logging

**Production (JSON):**
```json
{
  "timestamp": "2026-02-07T14:30:00Z",
  "level": "INFO",
  "logger": "app",
  "message": "User login successful",
  "request": {
    "method": "POST",
    "path": "/login",
    "remote_addr": "100.64.0.2"
  },
  "user_id": 123
}
```

**Development (Colored):**
```
2026-02-07 14:30:00 [INFO] app: User login successful
```

### Slow Request Detection

Automatically logs warnings for requests taking >1 second:
```json
{
  "level": "WARNING",
  "message": "Slow request: POST /api/ocr/process took 2500ms",
  "duration": 2500,
  "status_code": 200
}
```

### Performance Profiling

Use the `@log_performance` decorator:
```python
from logging_config import log_performance

@log_performance
def expensive_operation():
    # Your code here
    pass
```

---

## 🔧 Gunicorn Configuration

### Worker Tuning

**Default Formula:** `(CPU cores × 2) + 1`

For a 2-core machine: 5 workers
For a 4-core machine: 9 workers

**Override with environment variable:**
```bash
export GUNICORN_WORKERS=4
export GUNICORN_THREADS=2
```

### Timeout Settings

- **Default timeout:** 120 seconds (for OCR processing)
- **Keepalive:** 5 seconds
- **Max requests per worker:** 1000 (prevents memory leaks)

### Worker Lifecycle

Workers automatically restart after:
- 1000 requests (prevents memory leaks)
- Graceful shutdown on INT/QUIT signals
- Immediate shutdown on SIGABRT

---

## 🛠️ Troubleshooting

### High Memory Usage

1. Reduce worker count:
   ```bash
   export GUNICORN_WORKERS=2
   ```

2. Check for memory leaks in logs:
   ```bash
   curl https://your-domain.com/metrics
   ```

### Slow Requests

1. Check metrics for bottlenecks
2. Review slow request logs
3. Optimize database queries
4. Increase worker threads for I/O bound operations

### Database Connection Issues

1. Check connection pool stats:
   ```bash
   curl https://your-domain.com/metrics
   ```

2. Adjust pool settings:
   ```bash
   export DB_POOL_SIZE=20
   export DB_MAX_OVERFLOW=40
   ```

### Health Check Failures

1. Check detailed health:
   ```bash
   curl https://your-domain.com/health/detailed
   ```

2. Review application logs
3. Verify database connectivity
4. Check Redis connection (if used)

---

## 📚 Additional Resources

- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Flask Production Best Practices](https://flask.palletsprojects.com/en/latest/deploying/)
- [Railway Deployment Guide](https://docs.railway.app/)

---

## 🔐 Security Notes

- Always use HTTPS in production
- Rotate SECRET_KEY regularly
- Keep dependencies updated
- Monitor logs for security events
- Use Redis for rate limiting in production
- Enable all security headers (already configured)

---

## 📝 Version History

### 2.3.0 (Current)
- ✅ Gunicorn production server
- ✅ Advanced structured logging
- ✅ Health check endpoints
- ✅ System metrics monitoring
- ✅ Database connection pooling
- ✅ Performance optimizations

### 2.2.0
- Production security hardening
- 2FA implementation
- Enhanced CSRF protection

### 2.1.0
- S3 storage integration
- OCR proof of payment processing
- Payment gateway integrations

---

## 💡 Best Practices

1. **Always use Gunicorn in production** (not Flask's built-in server)
2. **Monitor health checks** with your hosting provider
3. **Review metrics regularly** for performance insights
4. **Set up log aggregation** for better analysis
5. **Use Redis** for caching and rate limiting
6. **Configure alerting** based on health check failures
7. **Keep worker count** appropriate for your machine size

---

## 🆘 Support

For issues or questions:
- Check logs: `railway logs`
- Review health checks
- Check system metrics
- Contact support with log evidence

---

**Built with ❤️ for 360Degree Supply (Pty) Ltd**
