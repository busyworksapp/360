"""
PERFORMANCE OPTIMIZATION MODULE
Ultra-fast database queries and caching
"""
from functools import wraps, lru_cache
from flask import g
import time
import hashlib

# QUERY CACHE (IN-MEMORY)
_query_cache = {}
_cache_ttl = {}

def cached_query(ttl=300):
    """Cache database query results"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Generate cache key
            key = hashlib.md5(f"{f.__name__}{args}{kwargs}".encode()).hexdigest()
            now = time.time()
            
            # Check cache
            if key in _query_cache and key in _cache_ttl:
                if now < _cache_ttl[key]:
                    return _query_cache[key]
            
            # Execute query
            result = f(*args, **kwargs)
            
            # Store in cache
            _query_cache[key] = result
            _cache_ttl[key] = now + ttl
            
            return result
        return decorated
    return decorator


def clear_query_cache():
    """Clear all cached queries"""
    _query_cache.clear()
    _cache_ttl.clear()


def batch_query(model, ids, chunk_size=100):
    """Batch query for multiple IDs - prevents N+1 queries"""
    results = []
    for i in range(0, len(ids), chunk_size):
        chunk = ids[i:i + chunk_size]
        results.extend(model.query.filter(model.id.in_(chunk)).all())
    return results


def optimize_query(query):
    """Add common optimizations to query"""
    return query.options(
        # Eager load relationships
        # joinedload('*'),
        # Defer large columns
        # defer('large_column')
    )


class QueryTimer:
    """Context manager for timing queries"""
    def __enter__(self):
        self.start = time.time()
        return self
    
    def __exit__(self, *args):
        self.duration = time.time() - self.start
        if self.duration > 0.1:  # Log slow queries
            print(f"SLOW QUERY: {self.duration:.3f}s")


def index_hint(model, index_name):
    """Add index hint to query (MySQL)"""
    return model.query.with_hint(model, f'USE INDEX ({index_name})')


# RESPONSE COMPRESSION
def compress_response(data):
    """Compress response data"""
    import gzip
    return gzip.compress(data.encode() if isinstance(data, str) else data)


# PAGINATION OPTIMIZATION
def fast_paginate(query, page, per_page=20):
    """Fast pagination without counting total"""
    items = query.limit(per_page + 1).offset((page - 1) * per_page).all()
    has_next = len(items) > per_page
    return items[:per_page], has_next


# DATABASE CONNECTION POOLING
def optimize_db_connection(app):
    """Optimize database connection settings"""
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 20,
        'max_overflow': 40,
        'pool_timeout': 10,
        'pool_recycle': 1800,
        'pool_pre_ping': True,
        'echo': False,
        'connect_args': {
            'connect_timeout': 5,
            'charset': 'utf8mb4'
        }
    }


# STATIC FILE OPTIMIZATION
def optimize_static_files(app):
    """Configure static file caching"""
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year


# JSON OPTIMIZATION
def fast_json_response(data):
    """Fast JSON serialization"""
    import json
    return json.dumps(data, separators=(',', ':'), ensure_ascii=False)


# TEMPLATE OPTIMIZATION
def optimize_templates(app):
    """Optimize Jinja2 templates"""
    app.jinja_env.auto_reload = False
    app.jinja_env.cache_size = 400
    app.config['TEMPLATES_AUTO_RELOAD'] = False


# CLEANUP OLD CACHE
def cleanup_cache():
    """Remove expired cache entries"""
    now = time.time()
    expired = [k for k, v in _cache_ttl.items() if v < now]
    for key in expired:
        _query_cache.pop(key, None)
        _cache_ttl.pop(key, None)
