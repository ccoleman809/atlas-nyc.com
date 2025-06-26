#!/usr/bin/env python3
"""
Atlas-NYC Production Startup Script
Initializes and starts the Atlas-NYC API server with proper configuration
"""

import sys
import os
import uvicorn
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config import settings, validate_production_settings
from logging_config import setup_logging, setup_error_reporting, log_startup_info
from error_handlers import register_error_handlers

def pre_startup_checks():
    """Perform pre-startup validation and setup"""
    
    print("🚀 Atlas-NYC Starting Up...")
    print("=" * 50)
    
    # Validate configuration
    print("🔍 Validating configuration...")
    if not validate_production_settings():
        print("❌ Configuration validation failed!")
        sys.exit(1)
    
    # Setup logging
    print("📝 Setting up logging...")
    setup_logging()
    
    # Setup error reporting
    print("🚨 Setting up error reporting...")
    setup_error_reporting()
    
    # Check database
    print("🗄️  Checking database...")
    if not Path("nightlife.db").exists():
        print("❌ Database not found! Run 'python init_database.py' first.")
        sys.exit(1)
    
    # Create necessary directories
    print("📁 Creating directories...")
    Path("logs").mkdir(exist_ok=True)
    Path("uploads").mkdir(exist_ok=True)
    Path("static").mkdir(exist_ok=True)
    
    print("✅ Pre-startup checks completed!")
    print("=" * 50)

def create_app():
    """Create and configure the FastAPI application"""
    
    # Import here to ensure logging is setup first
    from secure_api_server import app
    
    # Register error handlers
    register_error_handlers(app)
    
    # Log startup info
    log_startup_info()
    
    return app

def main():
    """Main startup function"""
    
    # Perform pre-startup checks
    pre_startup_checks()
    
    # Create application
    app = create_app()
    
    # Configure uvicorn based on environment
    if settings.ENVIRONMENT == "production":
        # Production configuration
        uvicorn_config = {
            "host": "0.0.0.0",
            "port": int(os.getenv("PORT", 8001)),
            "workers": settings.WORKERS,
            "loop": "uvloop",
            "http": "httptools",
            "access_log": True,
            "log_level": settings.LOG_LEVEL.lower(),
        }
        
        # Add SSL configuration if certificates are provided
        if settings.SSL_CERT_PATH and settings.SSL_KEY_PATH:
            uvicorn_config.update({
                "ssl_certfile": settings.SSL_CERT_PATH,
                "ssl_keyfile": settings.SSL_KEY_PATH,
            })
            print(f"🔒 SSL enabled with certificates")
        
    else:
        # Development configuration
        uvicorn_config = {
            "host": "127.0.0.1",
            "port": 8001,
            "reload": True,
            "reload_dirs": [str(project_root)],
            "access_log": True,
            "log_level": settings.LOG_LEVEL.lower(),
        }
    
    print(f"🌐 Starting server on {uvicorn_config['host']}:{uvicorn_config['port']}")
    print(f"🎯 Environment: {settings.ENVIRONMENT}")
    print("=" * 50)
    
    # Start the server
    uvicorn.run(app, **uvicorn_config)

if __name__ == "__main__":
    main()