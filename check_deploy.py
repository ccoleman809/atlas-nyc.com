#!/usr/bin/env python3
"""
Pre-deployment check script for Railway
"""
import sys

def check_imports():
    """Check if all required imports work"""
    print("🔍 Checking imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import sqlite3
        print("✅ SQLite3 imported")
    except ImportError as e:
        print(f"❌ SQLite3 import failed: {e}")
        return False
    
    try:
        import sklearn
        print("✅ Scikit-learn imported")
    except ImportError as e:
        print(f"⚠️ Scikit-learn import failed (ML will be disabled): {e}")
    
    try:
        import pandas
        print("✅ Pandas imported")
    except ImportError as e:
        print(f"⚠️ Pandas import failed (ML will be limited): {e}")
    
    return True

def check_database():
    """Check if database is accessible"""
    print("\n🔍 Checking database...")
    
    try:
        import sqlite3
        conn = sqlite3.connect('nightlife.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM venues")
        count = cursor.fetchone()[0]
        print(f"✅ Database connected: {count} venues found")
        conn.close()
        return True
    except Exception as e:
        print(f"⚠️ Database check failed: {e}")
        return False

def check_ml_system():
    """Check if ML system can initialize"""
    print("\n🔍 Checking ML system...")
    
    try:
        from ml_basic import router
        print("✅ Basic ML endpoints available")
        return True
    except Exception as e:
        print(f"⚠️ ML system check failed: {e}")
        return False

if __name__ == "__main__":
    print("🚂 Railway Deployment Pre-Check")
    print("=" * 40)
    
    all_good = True
    
    if not check_imports():
        all_good = False
    
    if not check_database():
        all_good = False
        
    if not check_ml_system():
        print("⚠️ ML system unavailable but API can still run")
    
    print("\n" + "=" * 40)
    if all_good:
        print("✅ All checks passed! Ready for deployment")
        sys.exit(0)
    else:
        print("⚠️ Some checks failed but deployment may still work")
        sys.exit(1)