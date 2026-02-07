"""
Production Logging Configuration
Structured logging with JSON format for better monitoring and analysis
"""
import logging
import sys
import json
from datetime import datetime
from flask import has_request_context, request
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    Makes logs easy to parse and analyze in monitoring tools.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Add request context if available
        if has_request_context():
            log_data['request'] = {
                'method': request.method,
                'path': request.path,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', 'Unknown'),
            }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info)
            }
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'action'):
            log_data['action'] = record.action
        if hasattr(record, 'duration'):
            log_data['duration_ms'] = record.duration
        
        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """
    Colored console formatter for better readability in development.
    """
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(app):
    """
    Configure application logging based on environment.
    
    Args:
        app: Flask application instance
    """
    # Get log level from environment
    log_level_name = app.config.get('LOG_LEVEL', 'INFO').upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    
    # Determine if we're in production
    is_production = app.config.get('ENV') == 'production'
    
    # Remove default handlers
    app.logger.handlers.clear()
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Use JSON formatter in production, colored formatter in development
    if is_production:
        formatter = JSONFormatter()
        app.logger.info("📊 JSON logging enabled for production")
    else:
        formatter = ColoredFormatter(
            fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        app.logger.info("🎨 Colored logging enabled for development")
    
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(log_level)
    
    # Configure werkzeug logger
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.handlers.clear()
    werkzeug_logger.addHandler(console_handler)
    werkzeug_logger.setLevel(logging.WARNING)  # Reduce werkzeug verbosity
    
    # Configure sqlalchemy logger
    sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
    sqlalchemy_logger.handlers.clear()
    sqlalchemy_logger.addHandler(console_handler)
    # Only show SQL in debug mode
    if app.config.get('DEBUG'):
        sqlalchemy_logger.setLevel(logging.INFO)
    else:
        sqlalchemy_logger.setLevel(logging.WARNING)
    
    app.logger.info("✅ Logging configuration completed")
    app.logger.info(f"📝 Log level: {log_level_name}")
    app.logger.info(f"🌍 Environment: {app.config.get('ENV', 'development')}")


def log_request(app):
    """
    Add request logging middleware.
    Logs all HTTP requests with timing information.
    """
    @app.before_request
    def before_request():
        request._start_time = datetime.utcnow()
    
    @app.after_request
    def after_request(response):
        if hasattr(request, '_start_time'):
            duration = (datetime.utcnow() - request._start_time).total_seconds() * 1000
            
            # Log with extra context
            extra = {
                'duration': round(duration, 2),
                'status_code': response.status_code,
            }
            
            if duration > 1000:  # Slow request warning (>1 second)
                app.logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {duration:.0f}ms",
                    extra=extra
                )
            elif response.status_code >= 400:  # Error response
                app.logger.warning(
                    f"Error response: {request.method} {request.path} "
                    f"returned {response.status_code}",
                    extra=extra
                )
            elif app.config.get('DEBUG'):  # Debug logging
                app.logger.debug(
                    f"{request.method} {request.path} "
                    f"{response.status_code} ({duration:.0f}ms)",
                    extra=extra
                )
        
        return response


def log_performance(func):
    """
    Decorator to log function performance.
    
    Usage:
        @log_performance
        def slow_function():
            ...
    """
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        from flask import current_app
        start_time = datetime.utcnow()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            current_app.logger.debug(
                f"Function {func.__name__} took {duration:.2f}ms",
                extra={'duration': duration, 'function': func.__name__}
            )
    
    return wrapper
