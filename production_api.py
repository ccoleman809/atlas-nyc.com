#!/usr/bin/env python3
"""
Production-ready Atlas-NYC API with database connection
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
from datetime import datetime
from venue_db import VenueDatabase
from pathlib import Path

# Create FastAPI app
app = FastAPI(title="Atlas-NYC API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
try:
    db = VenueDatabase()
    print("✅ Database initialized successfully")
except Exception as e:
    print(f"⚠️ Database initialization failed: {e}")
    db = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Atlas-NYC API is running!",
        "version": "2.0.0",
        "status": "production",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if db else "not_connected"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected" if db else "not_connected",
        "environment": os.environ.get("ENVIRONMENT", "production")
    }

@app.get("/venues")
async def get_venues(
    page: int = 1,
    per_page: int = 20,
    neighborhood: str = None,
    venue_type: str = None
):
    """Get venues from database with pagination"""
    try:
        if not db:
            # Return sample data if database not available
            return {
                "venues": [
                    {
                        "id": 1,
                        "name": "House of Yes",
                        "neighborhood": "Bushwick",
                        "instagram_handle": "houseofyes",
                        "venue_type": "nightclub",
                        "description": "Creative nightclub with themed parties",
                        "lat": 40.7053,
                        "lng": -73.9233
                    },
                    {
                        "id": 2,
                        "name": "Brooklyn Bowl",
                        "neighborhood": "Williamsburg",
                        "instagram_handle": "brooklynbowl",
                        "venue_type": "live_music_venue",
                        "description": "Bowling alley, music venue, and restaurant",
                        "lat": 40.7220,
                        "lng": -73.9575
                    }
                ],
                "pagination": {
                    "page": 1,
                    "per_page": 20,
                    "total": 2,
                    "pages": 1
                },
                "source": "sample_data"
            }
        
        # Get all venues from database
        all_venues = db.get_all_venues()
        
        # Apply filters
        filtered_venues = all_venues
        if neighborhood:
            filtered_venues = [v for v in filtered_venues if v.neighborhood.lower() == neighborhood.lower()]
        if venue_type:
            filtered_venues = [v for v in filtered_venues if v.venue_type == venue_type]
        
        # Calculate pagination
        total = len(filtered_venues)
        start = (page - 1) * per_page
        end = start + per_page
        
        # Get page of venues
        page_venues = filtered_venues[start:end]
        
        # Format response
        venues_data = []
        for v in page_venues:
            venue_dict = {
                "id": v.venue_id,
                "name": v.name,
                "neighborhood": v.neighborhood,
                "instagram_handle": v.instagram_handle,
                "venue_type": v.venue_type,
                "description": v.description,
                "busy_nights": v.busy_nights,
                "price_range": v.price_range
            }
            
            # Add sample coordinates for map
            if v.name == "House of Yes":
                venue_dict.update({"lat": 40.7053, "lng": -73.9233})
            elif v.name == "Brooklyn Bowl":
                venue_dict.update({"lat": 40.7220, "lng": -73.9575})
            elif v.name == "Death & Co":
                venue_dict.update({"lat": 40.7259, "lng": -73.9846})
            elif v.name == "Le Bain":
                venue_dict.update({"lat": 40.7411, "lng": -74.0083})
            elif v.name == "Beauty & Essex":
                venue_dict.update({"lat": 40.7204, "lng": -73.9869})
            else:
                # Default Manhattan coordinates
                venue_dict.update({"lat": 40.7589, "lng": -73.9851})
            
            venues_data.append(venue_dict)
        
        return {
            "venues": venues_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page if per_page > 0 else 0
            },
            "source": "database"
        }
        
    except Exception as e:
        print(f"Error getting venues: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/atlas", response_class=HTMLResponse)
async def get_atlas_interface():
    """Serve the Atlas public interface"""
    try:
        with open("atlas_public_interface.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Atlas interface not found")

@app.get("/debug")
async def debug():
    """Debug environment"""
    return {
        "environment_vars": {
            "DATABASE_URL": bool(os.environ.get("DATABASE_URL")),
            "GOOGLE_MAPS_API_KEY": bool(os.environ.get("GOOGLE_MAPS_API_KEY")),
            "SECRET_KEY": bool(os.environ.get("SECRET_KEY")),
            "ENVIRONMENT": os.environ.get("ENVIRONMENT", "not_set"),
            "BASE_URL": os.environ.get("BASE_URL", "not_set"),
            "RENDER": bool(os.environ.get("RENDER")),
        },
        "database_status": "connected" if db else "not_connected",
        "total_env_vars": len(os.environ),
        "python_version": os.sys.version,
        "working_directory": os.getcwd(),
        "files_in_directory": os.listdir(".")[:10]  # First 10 files
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting Atlas-NYC Production API on port {port}...")
    print(f"📊 Database: {'Connected' if db else 'Not connected'}")
    print(f"🌍 Environment: {os.environ.get('ENVIRONMENT', 'production')}")
    uvicorn.run(app, host="0.0.0.0", port=port)