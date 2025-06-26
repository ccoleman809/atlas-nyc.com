import logging
import logging.handlers
import sys
import os
from pathlib import Path
from datetime import datetime
from config import settings

def setup_logging():
    """Configure logging for Atlas-NYC"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Set log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove default handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler (errors only)
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/atlas-nyc-errors.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Configure specific loggers
    configure_specific_loggers()
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Atlas-NYC logging initialized - Level: {settings.LOG_LEVEL}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Log file: {settings.LOG_FILE}")

def configure_specific_loggers():
    """Configure specific loggers for different components"""
    
    # FastAPI/Uvicorn loggers
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Database logger
    db_logger = logging.getLogger("database")
    db_logger.setLevel(logging.INFO)
    
    # Analytics logger
    analytics_logger = logging.getLogger("analytics")
    analytics_logger.setLevel(logging.INFO)
    
    # Security logger
    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.WARNING)
    
    # Performance logger
    performance_logger = logging.getLogger("performance")
    performance_logger.setLevel(logging.INFO)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)

# Performance logging decorator
def log_performance(func_name: str = None):
    """Decorator to log function performance"""
    def decorator(func):
        import functools
        import time
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger("performance")
            name = func_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"{name} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{name} failed after {duration:.3f}s: {str(e)}")
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger("performance")
            name = func_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"{name} completed in {duration:.3f}s")
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"{name} failed after {duration:.3f}s: {str(e)}")
                raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Security logging functions
def log_security_event(event_type: str, details: dict, request_info: dict = None):
    """Log security-related events"""
    logger = get_logger("security")
    
    message = f"Security Event: {event_type}"
    if request_info:
        message += f" | IP: {request_info.get('ip', 'unknown')}"
        message += f" | User-Agent: {request_info.get('user_agent', 'unknown')[:100]}"
    
    logger.warning(message, extra={
        'event_type': event_type,
        'details': details,
        'request_info': request_info
    })

def log_authentication_attempt(username: str, success: bool, ip_address: str, details: dict = None):
    """Log authentication attempts"""
    logger = get_logger("security")
    
    status = "SUCCESS" if success else "FAILED"
    message = f"Authentication {status}: {username} from {ip_address}"
    
    if success:
        logger.info(message, extra={'username': username, 'ip': ip_address, 'details': details})
    else:
        logger.warning(message, extra={'username': username, 'ip': ip_address, 'details': details})

def log_rate_limit_exceeded(ip_address: str, endpoint: str, details: dict = None):
    """Log rate limit violations"""
    logger = get_logger("security")
    
    message = f"Rate limit exceeded: {ip_address} on {endpoint}"
    logger.warning(message, extra={
        'ip_address': ip_address,
        'endpoint': endpoint,
        'details': details
    })

# Database logging functions
def log_database_operation(operation: str, table: str, record_id: int = None, details: dict = None):
    """Log database operations"""
    logger = get_logger("database")
    
    message = f"DB {operation.upper()}: {table}"
    if record_id:
        message += f" (ID: {record_id})"
    
    logger.info(message, extra={
        'operation': operation,
        'table': table,
        'record_id': record_id,
        'details': details
    })

# Analytics logging functions
def log_analytics_event(event_type: str, venue_id: int = None, user_session: str = None, details: dict = None):
    """Log analytics events"""
    logger = get_logger("analytics")
    
    message = f"Analytics: {event_type}"
    if venue_id:
        message += f" (Venue: {venue_id})"
    if user_session:
        message += f" (Session: {user_session[:8]}...)"
    
    logger.info(message, extra={
        'event_type': event_type,
        'venue_id': venue_id,
        'user_session': user_session,
        'details': details
    })

# Error reporting
def setup_error_reporting():
    """Setup error reporting (Sentry, etc.)"""
    if settings.SENTRY_DSN and settings.ENVIRONMENT == "production":
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.logging import LoggingIntegration
            
            sentry_logging = LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )
            
            sentry_sdk.init(
                dsn=settings.SENTRY_DSN,
                integrations=[
                    FastApiIntegration(auto_enable=True),
                    sentry_logging,
                ],
                traces_sample_rate=0.1,
                environment=settings.ENVIRONMENT,
                release=f"atlas-nyc@{datetime.now().strftime('%Y%m%d')}"
            )
            
            logger = get_logger(__name__)
            logger.info("Sentry error reporting initialized")
            
        except ImportError:
            logger = get_logger(__name__)
            logger.warning("Sentry SDK not installed, error reporting disabled")

# Health check logging
def log_health_check(status: str, details: dict = None):
    """Log health check results"""
    logger = get_logger("health")
    
    message = f"Health check: {status}"
    if status == "healthy":
        logger.info(message, extra=details)
    else:
        logger.error(message, extra=details)

# Startup logging
def log_startup_info():
    """Log startup information"""
    logger = get_logger("startup")
    
    logger.info("=" * 50)
    logger.info("Atlas-NYC Starting Up")
    logger.info("=" * 50)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Base URL: {settings.BASE_URL}")
    logger.info(f"Database: {settings.DATABASE_URL}")
    logger.info(f"Analytics: {'Enabled' if settings.ANALYTICS_ENABLED else 'Disabled'}")
    logger.info(f"Workers: {settings.WORKERS}")
    logger.info("=" * 50)