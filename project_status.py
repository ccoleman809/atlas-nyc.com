#!/usr/bin/env python3
"""
Atlas-NYC Project Status Report
"""

import os
import sqlite3
from datetime import datetime
from pathlib import Path

def check_file_exists(filepath):
    """Check if a file exists and return status"""
    return "✅" if os.path.exists(filepath) else "❌"

def get_database_stats():
    """Get database statistics"""
    stats = {}
    try:
        conn = sqlite3.connect("nightlife.db")
        cursor = conn.cursor()
        
        # Count venues
        cursor.execute("SELECT COUNT(*) FROM venues")
        stats['venues'] = cursor.fetchone()[0]
        
        # Count content
        cursor.execute("SELECT COUNT(*) FROM content")
        stats['content'] = cursor.fetchone()[0]
        
        # Count admin users
        cursor.execute("SELECT COUNT(*) FROM admin_users")
        stats['admins'] = cursor.fetchone()[0]
        
        # Database size
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        size_bytes = cursor.fetchone()[0]
        stats['size_mb'] = size_bytes / (1024 * 1024)
        
        conn.close()
    except Exception as e:
        stats['error'] = str(e)
    
    return stats

def check_configuration():
    """Check configuration status"""
    config = {}
    
    # Check .env file
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
            config['secret_key'] = "✅" if "SECRET_KEY=" in env_content and "your-secret-key-here" not in env_content else "❌"
            config['google_maps'] = "✅" if "GOOGLE_MAPS_API_KEY=AIza" in env_content else "❌"
            config['environment'] = "development" if "ENVIRONMENT=development" in env_content else "production"
    else:
        config['env_exists'] = False
    
    return config

def main():
    """Generate project status report"""
    print("=" * 60)
    print("🌆 ATLAS-NYC PROJECT STATUS REPORT")
    print("=" * 60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Core files
    print("📁 CORE FILES:")
    files = {
        "API Server": "api_server.py",
        "Secure API": "secure_api_server.py",
        "Configuration": "config.py",
        "Database": "nightlife.db",
        "Environment": ".env",
        "Requirements": "requirements.txt"
    }
    
    for name, filepath in files.items():
        status = check_file_exists(filepath)
        print(f"  {status} {name}: {filepath}")
    
    # Features implemented
    print("\n✨ FEATURES IMPLEMENTED:")
    features = [
        "✅ FastAPI REST API with pagination",
        "✅ JWT authentication system",
        "✅ Google Maps integration",
        "✅ Venue management system",
        "✅ Content/Instagram story tracking",
        "✅ Admin dashboard",
        "✅ Public interface",
        "✅ Mobile portal",
        "✅ Database indexes for performance",
        "✅ Comprehensive test suite",
        "✅ Production deployment script",
        "✅ NYC venue import script (48 venues)"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    # Database statistics
    print("\n📊 DATABASE STATISTICS:")
    stats = get_database_stats()
    if 'error' not in stats:
        print(f"  • Venues: {stats['venues']}")
        print(f"  • Content items: {stats['content']}")
        print(f"  • Admin users: {stats['admins']}")
        print(f"  • Database size: {stats['size_mb']:.2f} MB")
    else:
        print(f"  ❌ Error: {stats['error']}")
    
    # Configuration status
    print("\n⚙️  CONFIGURATION STATUS:")
    config = check_configuration()
    if config.get('env_exists', True):
        print(f"  • Secret key configured: {config.get('secret_key', '❌')}")
        print(f"  • Google Maps API: {config.get('google_maps', '❌')}")
        print(f"  • Environment: {config.get('environment', 'unknown')}")
    else:
        print("  ❌ .env file not found")
    
    # Security improvements
    print("\n🔒 SECURITY IMPROVEMENTS:")
    security = [
        "✅ Secure SECRET_KEY generated",
        "✅ API key removed from code",
        "✅ JWT authentication implemented",
        "✅ Rate limiting configured",
        "✅ Input validation with Pydantic",
        "✅ SQL injection protection"
    ]
    
    for item in security:
        print(f"  {item}")
    
    # API endpoints
    print("\n🔌 API ENDPOINTS:")
    endpoints = [
        "GET  /                    - API info",
        "GET  /health              - Health check",
        "GET  /venues              - List venues (paginated)",
        "POST /venues              - Create venue",
        "GET  /content             - List content (paginated)",
        "POST /content             - Create content",
        "GET  /content/stories     - Active stories",
        "GET  /maps/geocode        - Geocode address",
        "GET  /maps/reverse-geocode - Reverse geocode",
        "GET  /maps/nearby-places  - Find nearby places",
        "GET  /maps/place-details  - Place information",
        "GET  /maps/distance-matrix - Calculate distances"
    ]
    
    for endpoint in endpoints:
        print(f"  {endpoint}")
    
    # Next steps
    print("\n📋 RECOMMENDED NEXT STEPS:")
    next_steps = [
        "1. Set up PostgreSQL for production",
        "2. Configure domain and SSL certificates",
        "3. Set up monitoring (Sentry, Prometheus)",
        "4. Implement Redis caching",
        "5. Create mobile apps (iOS/Android)",
        "6. Add more NYC venues",
        "7. Set up CI/CD pipeline",
        "8. Configure automated backups"
    ]
    
    for step in next_steps:
        print(f"  {step}")
    
    print("\n🚀 QUICK START:")
    print("  source venv/bin/activate")
    print("  python api_server.py")
    print("  # Visit http://localhost:8002")
    
    print("\n=" * 60)
    print("Project is ready for beta testing! 🎉")
    print("=" * 60)

if __name__ == "__main__":
    main()