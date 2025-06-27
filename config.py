from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database
    DATABASE_URL: str = "sqlite:///nightlife.db"
    
    # Domain Configuration
    BASE_URL: str = "http://localhost:8002"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost:8002", "https://atlas-nyc.onrender.com"]
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mov"]
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/atlas-nyc.log"
    
    # Performance
    WORKERS: int = 1
    MAX_REQUESTS: int = 1000
    MAX_REQUESTS_JITTER: int = 100
    
    # Analytics
    ANALYTICS_ENABLED: bool = True
    ANALYTICS_RETENTION_DAYS: int = 365
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Social Media
    TWITTER_HANDLE: str = "@atlasnyc"
    INSTAGRAM_HANDLE: str = "atlasnyc"
    FACEBOOK_PAGE: str = "atlasnyc"
    
    # Email (optional)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    FROM_EMAIL: str = "noreply@atlas-nyc.com"
    
    # Redis (optional)
    REDIS_URL: Optional[str] = None
    
    # SSL (production)
    SSL_CERT_PATH: Optional[str] = None
    SSL_KEY_PATH: Optional[str] = None
    
    # Backup
    BACKUP_ENABLED: bool = False
    BACKUP_SCHEDULE: str = "0 2 * * *"  # Daily at 2 AM
    BACKUP_RETENTION_DAYS: int = 30
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    # Google Maps API
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Parse ALLOWED_ORIGINS if it's a string
        if isinstance(self.ALLOWED_ORIGINS, str):
            self.ALLOWED_ORIGINS = [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        
        # Parse ALLOWED_FILE_TYPES if it's a string
        if isinstance(self.ALLOWED_FILE_TYPES, str):
            self.ALLOWED_FILE_TYPES = [ext.strip() for ext in self.ALLOWED_FILE_TYPES.split(",")]

# Create settings instance
settings = Settings()

# Production validation
def validate_production_settings():
    """Validate production settings and warn about insecure configurations"""
    warnings = []
    errors = []
    
    if settings.ENVIRONMENT == "production":
        # Security checks
        if settings.SECRET_KEY == "your-secret-key-here-change-in-production":
            errors.append("SECRET_KEY must be changed in production!")
        
        if settings.DEBUG:
            warnings.append("DEBUG should be False in production")
        
        if "localhost" in settings.BASE_URL or settings.BASE_URL == "http://localhost:8002":
            warnings.append("BASE_URL should be set to your production domain")
        
        if any("localhost" in origin for origin in settings.ALLOWED_ORIGINS):
            warnings.append("ALLOWED_ORIGINS contains localhost entries")
        
        # SSL checks
        if not settings.BASE_URL.startswith("https://"):
            warnings.append("BASE_URL should use HTTPS in production")
        
        # Database checks
        if settings.DATABASE_URL == "nightlife.db":
            warnings.append("Consider using PostgreSQL for production")
    
    # Print warnings and errors
    if warnings:
        print("⚠️  Production Warnings:")
        for warning in warnings:
            print(f"   - {warning}")
    
    if errors:
        print("❌ Production Errors:")
        for error in errors:
            print(f"   - {error}")
        if settings.ENVIRONMENT == "production":
            print("\nFix these errors before deploying to production!")
            return False
    
    return True