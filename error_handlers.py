from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import traceback
from typing import Union
from config import settings
from logging_config import get_logger, log_security_event

# Get loggers
error_logger = get_logger("errors")
security_logger = get_logger("security")

class AtlasNYCException(Exception):
    """Base exception for Atlas-NYC specific errors"""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class VenueNotFoundException(AtlasNYCException):
    """Raised when a venue is not found"""
    def __init__(self, venue_id: Union[int, str]):
        super().__init__(
            message=f"Venue not found: {venue_id}",
            status_code=404,
            details={"venue_id": venue_id}
        )

class ContentNotFoundException(AtlasNYCException):
    """Raised when content is not found"""
    def __init__(self, content_id: int):
        super().__init__(
            message=f"Content not found: {content_id}",
            status_code=404,
            details={"content_id": content_id}
        )

class AuthenticationFailedException(AtlasNYCException):
    """Raised when authentication fails"""
    def __init__(self, details: str = "Invalid credentials"):
        super().__init__(
            message="Authentication failed",
            status_code=401,
            details={"reason": details}
        )

class AuthorizationFailedException(AtlasNYCException):
    """Raised when authorization fails"""
    def __init__(self, required_permission: str = None):
        super().__init__(
            message="Access denied",
            status_code=403,
            details={"required_permission": required_permission}
        )

class RateLimitExceededException(AtlasNYCException):
    """Raised when rate limit is exceeded"""
    def __init__(self, limit: int, window: int):
        super().__init__(
            message=f"Rate limit exceeded: {limit} requests per {window} seconds",
            status_code=429,
            details={"limit": limit, "window": window}
        )

class FileUploadException(AtlasNYCException):
    """Raised when file upload fails"""
    def __init__(self, reason: str):
        super().__init__(
            message=f"File upload failed: {reason}",
            status_code=400,
            details={"reason": reason}
        )

class DatabaseException(AtlasNYCException):
    """Raised when database operations fail"""
    def __init__(self, operation: str, details: str = None):
        super().__init__(
            message=f"Database operation failed: {operation}",
            status_code=500,
            details={"operation": operation, "details": details}
        )

class ValidationException(AtlasNYCException):
    """Raised when data validation fails"""
    def __init__(self, field: str, value: str, reason: str):
        super().__init__(
            message=f"Validation failed for {field}: {reason}",
            status_code=400,
            details={"field": field, "value": value, "reason": reason}
        )

# Error response helpers
def create_error_response(
    request: Request,
    status_code: int,
    message: str,
    details: dict = None,
    error_id: str = None
) -> Union[JSONResponse, HTMLResponse]:
    """Create appropriate error response based on request type"""
    
    # Log the error
    error_logger.error(
        f"Error {status_code}: {message}",
        extra={
            "status_code": status_code,
            "message": message,
            "details": details,
            "error_id": error_id,
            "path": str(request.url.path),
            "method": request.method,
            "user_agent": request.headers.get("user-agent"),
            "ip": request.client.host if request.client else "unknown"
        }
    )
    
    # Check if request expects JSON
    accept_header = request.headers.get("accept", "")
    content_type = request.headers.get("content-type", "")
    
    if ("application/json" in accept_header or 
        "application/json" in content_type or 
        str(request.url.path).startswith("/api/")):
        
        # Return JSON response for API requests
        return JSONResponse(
            status_code=status_code,
            content={
                "error": True,
                "status_code": status_code,
                "message": message,
                "details": details or {},
                "error_id": error_id,
                "timestamp": str(request.state.__dict__.get("start_time", "unknown"))
            }
        )
    
    else:
        # Return HTML response for web requests
        html_content = create_error_html(status_code, message, details)
        return HTMLResponse(content=html_content, status_code=status_code)

def create_error_html(status_code: int, message: str, details: dict = None) -> str:
    """Create HTML error page"""
    
    if status_code == 404:
        title = "Page Not Found"
        description = "The page you're looking for doesn't exist."
    elif status_code == 403:
        title = "Access Denied"
        description = "You don't have permission to access this resource."
    elif status_code == 429:
        title = "Too Many Requests"
        description = "Please slow down and try again later."
    elif status_code >= 500:
        title = "Server Error"
        description = "Something went wrong on our end. We're working to fix it."
    else:
        title = f"Error {status_code}"
        description = message
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Atlas-NYC</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 0;
            background: #000;
            color: #fff;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }}
        .error-container {{
            text-align: center;
            max-width: 600px;
            padding: 2rem;
        }}
        .error-code {{
            font-size: 6rem;
            font-weight: 700;
            color: #ffd700;
            margin-bottom: 1rem;
        }}
        .error-title {{
            font-size: 2rem;
            margin-bottom: 1rem;
        }}
        .error-description {{
            font-size: 1.2rem;
            opacity: 0.8;
            margin-bottom: 2rem;
        }}
        .back-link {{
            display: inline-block;
            padding: 1rem 2rem;
            background: #ffd700;
            color: #000;
            text-decoration: none;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        .back-link:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(255, 215, 0, 0.3);
        }}
        .logo {{
            font-family: 'Playfair Display', serif;
            font-size: 2rem;
            color: #ffd700;
            margin-bottom: 2rem;
        }}
    </style>
</head>
<body>
    <div class="error-container">
        <div class="logo">Atlas-NYC</div>
        <div class="error-code">{status_code}</div>
        <h1 class="error-title">{title}</h1>
        <p class="error-description">{description}</p>
        <a href="/" class="back-link">Back to Home</a>
    </div>
</body>
</html>"""

# Exception handlers
async def atlas_nyc_exception_handler(request: Request, exc: AtlasNYCException):
    """Handle Atlas-NYC specific exceptions"""
    return create_error_response(
        request=request,
        status_code=exc.status_code,
        message=exc.message,
        details=exc.details
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions"""
    
    # Log security events for certain status codes
    if exc.status_code in [401, 403, 429]:
        log_security_event(
            event_type=f"http_{exc.status_code}",
            details={"detail": exc.detail},
            request_info={
                "ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", ""),
                "path": str(request.url.path)
            }
        )
    
    return create_error_response(
        request=request,
        status_code=exc.status_code,
        message=exc.detail,
        details={"status_code": exc.status_code}
    )

async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle Starlette HTTP exceptions"""
    return create_error_response(
        request=request,
        status_code=exc.status_code,
        message=exc.detail if hasattr(exc, 'detail') else str(exc),
        details={"status_code": exc.status_code}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return create_error_response(
        request=request,
        status_code=422,
        message="Validation failed",
        details={"validation_errors": errors}
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    
    # Generate error ID for tracking
    import uuid
    error_id = str(uuid.uuid4())[:8]
    
    # Log full traceback for debugging
    error_logger.error(
        f"Unhandled exception [{error_id}]: {str(exc)}",
        extra={
            "error_id": error_id,
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc(),
            "path": str(request.url.path),
            "method": request.method,
            "user_agent": request.headers.get("user-agent"),
            "ip": request.client.host if request.client else "unknown"
        }
    )
    
    # Don't expose internal errors in production
    if settings.ENVIRONMENT == "production":
        message = "An unexpected error occurred"
        details = {"error_id": error_id}
    else:
        message = str(exc)
        details = {
            "error_id": error_id,
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc().split("\n")
        }
    
    return create_error_response(
        request=request,
        status_code=500,
        message=message,
        details=details,
        error_id=error_id
    )

# Register all error handlers
def register_error_handlers(app):
    """Register all error handlers with the FastAPI app"""
    
    app.add_exception_handler(AtlasNYCException, atlas_nyc_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    error_logger.info("Error handlers registered successfully")