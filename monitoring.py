"""
Health Check and Monitoring Endpoints
Provides system status, metrics, and diagnostics for monitoring
"""
from flask import Blueprint, jsonify, current_app
from datetime import datetime
import psutil
import os
from models import db

monitoring_bp = Blueprint('monitoring', __name__)


@monitoring_bp.route('/health', methods=['GET'])
def health_check():
    """
    Basic health check endpoint for load balancers and monitoring services.
    Returns 200 if application is healthy, 503 if unhealthy.
    """
    try:
        # Check database connectivity
        db.session.execute(db.text('SELECT 1'))
        db_status = 'healthy'
    except Exception as e:
        current_app.logger.error(f"Database health check failed: {e}")
        db_status = 'unhealthy'
        return jsonify({
            'status': 'unhealthy',
            'database': db_status,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 503
    
    return jsonify({
        'status': 'healthy',
        'database': db_status,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200


@monitoring_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """
    Detailed health check with more comprehensive diagnostics.
    Includes database, cache, and system metrics.
    """
    health_data = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'checks': {}
    }
    
    overall_healthy = True
    
    # Database check
    try:
        db.session.execute(db.text('SELECT 1'))
        health_data['checks']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        current_app.logger.error(f"Database check failed: {e}")
        health_data['checks']['database'] = {
            'status': 'unhealthy',
            'message': str(e)
        }
        overall_healthy = False
    
    # Cache check (if Redis is configured)
    if current_app.config.get('CACHE_TYPE') == 'redis':
        try:
            from flask import current_app as app
            cache = app.extensions.get('cache')
            if cache:
                cache.set('health_check', 'ok', timeout=5)
                result = cache.get('health_check')
                if result == 'ok':
                    health_data['checks']['cache'] = {
                        'status': 'healthy',
                        'message': 'Cache connection successful'
                    }
                else:
                    health_data['checks']['cache'] = {
                        'status': 'degraded',
                        'message': 'Cache responding but data mismatch'
                    }
        except Exception as e:
            current_app.logger.error(f"Cache check failed: {e}")
            health_data['checks']['cache'] = {
                'status': 'unhealthy',
                'message': str(e)
            }
    
    # S3 Storage check
    try:
        from s3_storage import storage_service
        if storage_service.s3_client:
            health_data['checks']['s3_storage'] = {
                'status': 'healthy',
                'message': 'S3 storage configured'
            }
        else:
            health_data['checks']['s3_storage'] = {
                'status': 'degraded',
                'message': 'S3 storage not configured'
            }
    except Exception as e:
        health_data['checks']['s3_storage'] = {
            'status': 'degraded',
            'message': f'S3 check error: {str(e)}'
        }
    
    health_data['status'] = 'healthy' if overall_healthy else 'unhealthy'
    status_code = 200 if overall_healthy else 503
    
    return jsonify(health_data), status_code


@monitoring_bp.route('/metrics', methods=['GET'])
def metrics():
    """
    System metrics endpoint for monitoring and alerting.
    Provides CPU, memory, disk usage, and application stats.
    """
    if not current_app.config.get('METRICS_ENABLED', True):
        return jsonify({'error': 'Metrics disabled'}), 403
    
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Process metrics
        process = psutil.Process(os.getpid())
        process_memory = process.memory_info()
        
        metrics_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'system': {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total_mb': round(memory.total / 1024 / 1024, 2),
                    'available_mb': round(memory.available / 1024 / 1024, 2),
                    'used_mb': round(memory.used / 1024 / 1024, 2),
                    'percent': memory.percent
                },
                'disk': {
                    'total_gb': round(disk.total / 1024 / 1024 / 1024, 2),
                    'used_gb': round(disk.used / 1024 / 1024 / 1024, 2),
                    'free_gb': round(disk.free / 1024 / 1024 / 1024, 2),
                    'percent': disk.percent
                }
            },
            'process': {
                'pid': process.pid,
                'memory_rss_mb': round(process_memory.rss / 1024 / 1024, 2),
                'memory_vms_mb': round(process_memory.vms / 1024 / 1024, 2),
                'num_threads': process.num_threads(),
                'cpu_percent': process.cpu_percent(interval=0.1)
            },
            'application': {
                'environment': current_app.config.get('ENV', 'development'),
                'debug': current_app.debug,
            }
        }
        
        # Database connection pool stats (if available)
        try:
            engine = db.engine
            if hasattr(engine.pool, 'size'):
                metrics_data['database'] = {
                    'pool_size': engine.pool.size(),
                    'checked_in': engine.pool.checkedin(),
                    'checked_out': engine.pool.checkedout(),
                    'overflow': engine.pool.overflow()
                }
        except Exception as e:
            current_app.logger.debug(f"Could not get DB pool stats: {e}")
        
        return jsonify(metrics_data), 200
    
    except Exception as e:
        current_app.logger.error(f"Metrics endpoint error: {e}")
        return jsonify({'error': 'Failed to collect metrics'}), 500


@monitoring_bp.route('/status', methods=['GET'])
def status():
    """
    Simple status endpoint returning basic application information.
    """
    return jsonify({
        'application': '360Degree Supply',
        'version': '2.2.0',
        'status': 'running',
        'environment': current_app.config.get('ENV', 'development'),
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200
