"""
Gunicorn Production Configuration
Optimized for Railway deployment with monitoring and logging
"""
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
backlog = 2048

# Worker processes
workers = int(os.environ.get('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
max_requests = 1000  # Restart workers after this many requests (prevents memory leaks)
max_requests_jitter = 50
timeout = 120  # Increased for long-running requests (OCR processing)
keepalive = 5

# Threading
threads = int(os.environ.get('GUNICORN_THREADS', 2))

# Process naming
proc_name = '360degree-supply'

# Logging
accesslog = '-'  # Log to stdout
errorlog = '-'   # Log errors to stdout
loglevel = os.environ.get('LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Preload app for better performance
preload_app = True

# Server hooks for monitoring
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("🚀 Starting 360Degree Supply Application")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("🔄 Reloading workers")

def when_ready(server):
    """Called just after the server is started."""
    server.log.info(f"✅ Server is ready. Workers: {workers}, Threads: {threads}")

def worker_int(worker):
    """Called when a worker receives the INT or QUIT signal."""
    worker.log.info(f"👷 Worker {worker.pid} received INT or QUIT signal")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.warning(f"⚠️  Worker {worker.pid} aborted")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    pass

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"👷 Worker spawned (pid: {worker.pid})")

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info(f"✅ Worker {worker.pid} initialized")

def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info(f"👋 Worker {worker.pid} exited")

def child_exit(server, worker):
    """Called just after a worker has been exited, in the worker process."""
    pass

def nworkers_changed(server, new_value, old_value):
    """Called just after num_workers has been changed."""
    server.log.info(f"📊 Workers changed from {old_value} to {new_value}")

# SSL (if needed in future)
# keyfile = None
# certfile = None
