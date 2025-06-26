import pytest
from fastapi.testclient import TestClient
from api_server import app
from venue_db import VenueDatabase
import os
import tempfile
import shutil

# Create test client
client = TestClient(app)

# Test database setup
@pytest.fixture
def test_db():
    """Create a temporary test database"""
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "test_nightlife.db")
    
    # Create test database
    db = VenueDatabase(test_db_path)
    
    yield db
    
    # Cleanup
    shutil.rmtree(temp_dir)

class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert data["database"] == "connected"
        assert data["google_maps"] == "enabled"
    
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "NYC Nightlife API is running!"
        assert data["version"] == "1.0.0"

class TestVenueEndpoints:
    """Test venue-related endpoints"""
    
    def test_get_venues_empty(self):
        response = client.get("/venues")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_venue(self):
        venue_data = {
            "name": "Test Bar",
            "neighborhood": "Brooklyn",
            "instagram_handle": "testbar",
            "venue_type": "dive_bar",
            "address": "123 Test St",
            "description": "A test bar",
            "busy_nights": "Fri,Sat",
            "price_range": "$$"
        }
        
        response = client.post("/venues", data=venue_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "Test Bar" in data["message"]
        assert data["id"] > 0
    
    def test_create_venue_missing_fields(self):
        incomplete_data = {
            "name": "Test Bar",
            "neighborhood": "Brooklyn"
            # Missing required fields
        }
        
        response = client.post("/venues", data=incomplete_data)
        assert response.status_code == 400

class TestMapsEndpoints:
    """Test Google Maps integration endpoints"""
    
    def test_geocode_address(self):
        response = client.get("/maps/geocode?address=Times Square, New York")
        assert response.status_code == 200
        data = response.json()
        assert "latitude" in data
        assert "longitude" in data
        assert "place_id" in data
        assert abs(data["latitude"] - 40.758) < 0.01  # Approximate Times Square lat
    
    def test_reverse_geocode(self):
        response = client.get("/maps/reverse-geocode?lat=40.7580&lng=-73.9855")
        assert response.status_code == 200
        data = response.json()
        assert "address" in data
        assert "Times Square" in data["address"]
    
    def test_nearby_places(self):
        response = client.get("/maps/nearby-places?lat=40.7580&lng=-73.9855&radius=500&place_type=bar")
        assert response.status_code == 200
        data = response.json()
        assert "places" in data
        assert isinstance(data["places"], list)
        if len(data["places"]) > 0:
            place = data["places"][0]
            assert "name" in place
            assert "latitude" in place
            assert "longitude" in place
    
    def test_geocode_invalid_address(self):
        response = client.get("/maps/geocode?address=InvalidAddressXYZ123456789")
        assert response.status_code == 404

class TestContentEndpoints:
    """Test content-related endpoints"""
    
    def test_get_content_empty(self):
        response = client.get("/content")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_stories_empty(self):
        response = client.get("/content/stories")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_create_content_invalid_venue(self):
        content_data = {
            "venue_id": 99999,  # Non-existent venue
            "content_type": "instagram_story",
            "caption": "Test content"
        }
        
        response = client.post("/content", data=content_data)
        assert response.status_code == 404

class TestStaticPages:
    """Test static HTML pages"""
    
    def test_mobile_portal(self):
        response = client.get("/mobile")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"
    
    def test_public_interface(self):
        response = client.get("/public")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/html; charset=utf-8"

class TestErrorHandling:
    """Test error handling"""
    
    def test_404_endpoint(self):
        response = client.get("/nonexistent")
        assert response.status_code == 404
    
    def test_invalid_query_params(self):
        response = client.get("/maps/reverse-geocode?lat=invalid&lng=invalid")
        assert response.status_code == 422

class TestSecurity:
    """Test security features"""
    
    def test_cors_headers(self):
        response = client.options("/venues")
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
    
    def test_file_upload_size_limit(self):
        # Create a large file (over 10MB limit)
        large_file = b"x" * (11 * 1024 * 1024)  # 11MB
        files = {"file": ("large.jpg", large_file, "image/jpeg")}
        
        response = client.post("/content", 
                             data={"venue_id": 1, "content_type": "photo", "caption": "test"},
                             files=files)
        # Should fail due to size limit
        assert response.status_code in [413, 422, 500]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])