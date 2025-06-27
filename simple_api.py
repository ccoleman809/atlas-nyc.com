#!/usr/bin/env python3
"""
Simplified Atlas-NYC API for debugging deployment issues
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime

# Create simple FastAPI app
app = FastAPI(title="Atlas-NYC API (Simple)", version="1.0.0")

# Simple CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Atlas-NYC API is running!",
        "version": "1.0.0",
        "status": "simplified_mode"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "simplified"
    }

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
        "total_env_vars": len(os.environ),
        "python_version": os.sys.version
    }

@app.get("/venues")
async def sample_venues():
    """Sample venues data"""
    return {
        "venues": [
            {
                "id": 1,
                "name": "House of Yes",
                "neighborhood": "Bushwick",
                "instagram_handle": "houseofyes",
                "venue_type": "nightclub",
                "description": "Creative nightclub with themed parties"
            },
            {
                "id": 2,
                "name": "Brooklyn Bowl",
                "neighborhood": "Williamsburg",
                "instagram_handle": "brooklynbowl", 
                "venue_type": "live_music_venue",
                "description": "Bowling alley, music venue, and restaurant"
            }
        ],
        "total": 2,
        "source": "sample_data"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting simplified Atlas-NYC API on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)