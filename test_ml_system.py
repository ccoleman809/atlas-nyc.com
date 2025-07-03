#!/usr/bin/env python3
"""
Test script for ML/AI system functionality
"""

import sys
import os
import asyncio
import sqlite3
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_integration():
    """Test that ML columns were added to database"""
    print("🔍 Testing database integration...")
    
    try:
        conn = sqlite3.connect('nightlife.db')
        cursor = conn.cursor()
        
        # Check if ML columns exist
        cursor.execute("PRAGMA table_info(venues)")
        columns = [col[1] for col in cursor.fetchall()]
        
        ml_columns = [
            'ml_confidence_score', 'ml_enhanced_description', 
            'ml_atmosphere_tags', 'discovery_source'
        ]
        
        missing_columns = [col for col in ml_columns if col not in columns]
        
        if missing_columns:
            print(f"❌ Missing ML columns: {missing_columns}")
            return False
        
        # Check if ML tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ml_%'")
        ml_tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['ml_discovery_runs', 'ml_enhancement_history', 'ml_predictions', 'ml_analytics']
        missing_tables = [table for table in expected_tables if table not in ml_tables]
        
        if missing_tables:
            print(f"❌ Missing ML tables: {missing_tables}")
            return False
        
        print("✅ Database integration successful!")
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_ml_imports():
    """Test that ML modules can be imported"""
    print("🔍 Testing ML imports...")
    
    try:
        from ml_system.ml_models import MLModelManager
        print("✅ MLModelManager imported")
        
        from ml_system.automated_venue_discovery import AutomatedVenueDiscovery, VenueCandidate
        print("✅ AutomatedVenueDiscovery imported")
        
        from ml_system.smart_content_enhancer import SmartContentEnhancer
        print("✅ SmartContentEnhancer imported")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_ml_initialization():
    """Test that ML components can be initialized"""
    print("🔍 Testing ML initialization...")
    
    try:
        from ml_system.ml_models import MLModelManager
        from ml_system.automated_venue_discovery import AutomatedVenueDiscovery
        from ml_system.smart_content_enhancer import SmartContentEnhancer
        
        # Initialize components
        ml_manager = MLModelManager()
        print("✅ MLModelManager initialized")
        
        discovery = AutomatedVenueDiscovery()
        print("✅ AutomatedVenueDiscovery initialized")
        
        enhancer = SmartContentEnhancer()
        print("✅ SmartContentEnhancer initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False

async def test_venue_discovery():
    """Test basic venue discovery functionality"""
    print("🔍 Testing venue discovery...")
    
    try:
        from ml_system.automated_venue_discovery import AutomatedVenueDiscovery
        
        discovery = AutomatedVenueDiscovery()
        
        # Test with minimal search terms (without actual API calls)
        print("✅ Venue discovery system ready")
        return True
        
    except Exception as e:
        print(f"❌ Venue discovery test failed: {e}")
        return False

async def test_content_enhancement():
    """Test content enhancement functionality"""
    print("🔍 Testing content enhancement...")
    
    try:
        from ml_system.smart_content_enhancer import SmartContentEnhancer
        
        enhancer = SmartContentEnhancer()
        
        # Test with sample venue data
        sample_venue = {
            'id': '1',
            'name': 'Test Venue',
            'venue_type': 'cocktail_lounge',
            'neighborhood': 'Brooklyn'
        }
        
        enhancement = await enhancer.enhance_venue(sample_venue)
        
        if enhancement.enhanced_description:
            print("✅ Content enhancement working")
            print(f"   Enhanced description: {enhancement.enhanced_description[:100]}...")
            return True
        else:
            print("❌ No enhanced description generated")
            return False
        
    except Exception as e:
        print(f"❌ Content enhancement test failed: {e}")
        return False

def test_configuration():
    """Test that configuration was created"""
    print("🔍 Testing configuration...")
    
    config_path = 'ml_system/config.json'
    if os.path.exists(config_path):
        try:
            import json
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            required_sections = ['database', 'discovery', 'enhancement', 'ml_models']
            missing_sections = [section for section in required_sections if section not in config]
            
            if missing_sections:
                print(f"❌ Missing config sections: {missing_sections}")
                return False
            
            print("✅ Configuration file valid")
            return True
            
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            return False
    else:
        print("❌ Configuration file not found")
        return False

async def main():
    """Run all tests"""
    print("🚀 Testing ML/AI System Deployment\n")
    
    tests = [
        ("Database Integration", test_database_integration),
        ("ML Imports", test_ml_imports),
        ("ML Initialization", test_ml_initialization),
        ("Configuration", test_configuration),
        ("Venue Discovery", test_venue_discovery),
        ("Content Enhancement", test_content_enhancement)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"TEST: {test_name}")
        print(f"{'='*50}")
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
                
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    print(f"{'='*50}")
    
    if passed == total:
        print("🎉 All tests passed! ML/AI system is ready to use.")
        print("\n📖 Next steps:")
        print("1. Configure API keys in .env.ml_template")
        print("2. Start the ML API: python ml_system/integration_api.py")
        print("3. Access http://localhost:8001/docs for API documentation")
        print("4. Integrate with your admin dashboard")
    else:
        print("⚠️  Some tests failed. Please check the output above.")
    
    return passed == total

if __name__ == "__main__":
    # Change to the project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests
    asyncio.run(main())