#!/usr/bin/env python3
"""
Test deployed Atlas-NYC API
"""

import requests
import json
import sys
from datetime import datetime

def test_api(base_url):
    """Test the deployed API"""
    print(f"🧪 Testing Atlas-NYC API at: {base_url}")
    print("=" * 60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data.get('status', 'unknown')}")
            print(f"   Database: {data.get('database', 'unknown')}")
            print(f"   Google Maps: {data.get('google_maps', 'unknown')}")
            tests_passed += 1
        else:
            print(f"❌ Health Check Failed: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Health Check Error: {e}")
        tests_failed += 1
    
    # Test 2: Venues Endpoint
    try:
        response = requests.get(f"{base_url}/venues?page=1&per_page=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            venue_count = len(data.get('venues', []))
            total = data.get('pagination', {}).get('total', 0)
            print(f"✅ Venues Endpoint: {venue_count} venues (total: {total})")
            tests_passed += 1
        else:
            print(f"❌ Venues Endpoint Failed: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Venues Endpoint Error: {e}")
        tests_failed += 1
    
    # Test 3: Google Maps Integration
    try:
        response = requests.get(f"{base_url}/maps/geocode?address=Times Square, New York", timeout=10)
        if response.status_code == 200:
            data = response.json()
            lat = data.get('latitude', 0)
            lng = data.get('longitude', 0)
            print(f"✅ Google Maps: Times Square at ({lat:.4f}, {lng:.4f})")
            tests_passed += 1
        else:
            print(f"❌ Google Maps Failed: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Google Maps Error: {e}")
        tests_failed += 1
    
    # Test 4: Nearby Places
    try:
        response = requests.get(f"{base_url}/maps/nearby-places?lat=40.7580&lng=-73.9855&radius=500&place_type=bar", timeout=10)
        if response.status_code == 200:
            data = response.json()
            place_count = len(data.get('places', []))
            print(f"✅ Nearby Places: Found {place_count} bars near Times Square")
            tests_passed += 1
        else:
            print(f"❌ Nearby Places Failed: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Nearby Places Error: {e}")
        tests_failed += 1
    
    # Test 5: Static Pages
    try:
        response = requests.get(f"{base_url}/mobile", timeout=10)
        if response.status_code == 200:
            print("✅ Mobile Portal: Accessible")
            tests_passed += 1
        else:
            print(f"❌ Mobile Portal Failed: {response.status_code}")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Mobile Portal Error: {e}")
        tests_failed += 1
    
    # Results
    print("\n" + "=" * 60)
    print(f"📊 Test Results:")
    print(f"   ✅ Passed: {tests_passed}")
    print(f"   ❌ Failed: {tests_failed}")
    print(f"   📈 Success Rate: {tests_passed/(tests_passed+tests_failed)*100:.1f}%")
    
    if tests_failed == 0:
        print("\n🎉 All tests passed! Your deployment is working correctly.")
        return True
    else:
        print(f"\n⚠️  {tests_failed} tests failed. Check the logs for issues.")
        return False

def main():
    """Main test function"""
    if len(sys.argv) != 2:
        print("Usage: python test_deployment.py <BASE_URL>")
        print("Example: python test_deployment.py https://atlas-nyc.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print(f"🌆 Atlas-NYC Deployment Test")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {base_url}")
    print()
    
    success = test_api(base_url)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()