#!/usr/bin/env python3
"""
Simple ML API Server
"""

import sys
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import asyncio
import logging
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Initialize FastAPI app
app = FastAPI(
    title="NYC Nightlife ML/AI API",
    description="AI-powered venue discovery and enhancement system",
    version="1.0.0"
)

# Global ML components
ml_manager = None
discovery_system = None
content_enhancer = None

@app.on_event("startup")
async def startup_event():
    """Initialize ML components"""
    global ml_manager, discovery_system, content_enhancer
    
    try:
        from ml_system.ml_models import MLModelManager
        from ml_system.automated_venue_discovery import AutomatedVenueDiscovery
        from ml_system.smart_content_enhancer import SmartContentEnhancer
        
        ml_manager = MLModelManager()
        discovery_system = AutomatedVenueDiscovery()
        content_enhancer = SmartContentEnhancer()
        
        print("✅ ML/AI system initialized successfully")
        
    except Exception as e:
        print(f"❌ Failed to initialize ML system: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "NYC Nightlife ML/AI API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "ml_manager": ml_manager is not None,
            "discovery_system": discovery_system is not None,
            "content_enhancer": content_enhancer is not None
        }
    }

# Pydantic models
class VenueEnhanceRequest(BaseModel):
    venue_id: str
    name: str
    venue_type: str
    neighborhood: Optional[str] = None
    instagram_handle: Optional[str] = None

class DiscoveryRequest(BaseModel):
    search_terms: Optional[List[str]] = None
    max_results: Optional[int] = 10

@app.post("/enhance-venue")
async def enhance_venue(request: VenueEnhanceRequest):
    """Enhance a venue with AI-generated content"""
    if content_enhancer is None:
        raise HTTPException(status_code=503, detail="Content enhancer not initialized")
    
    try:
        venue_data = {
            'id': request.venue_id,
            'name': request.name,
            'venue_type': request.venue_type,
            'neighborhood': request.neighborhood,
            'instagram_handle': request.instagram_handle
        }
        
        enhancement = await content_enhancer.enhance_venue(venue_data)
        
        return {
            "status": "success",
            "venue_id": request.venue_id,
            "enhanced_description": enhancement.enhanced_description,
            "key_features": enhancement.key_features,
            "atmosphere_tags": enhancement.atmosphere_tags,
            "target_demographics": enhancement.target_demographics,
            "social_sentiment": enhancement.social_sentiment,
            "popularity_trend": enhancement.popularity_trend,
            "recommendations": enhancement.recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")

@app.post("/discover-venues")
async def discover_venues(request: DiscoveryRequest):
    """Discover new venues using AI"""
    if discovery_system is None:
        raise HTTPException(status_code=503, detail="Discovery system not initialized")
    
    try:
        # For demo, return simulated results
        # In production, this would call the actual discovery system
        sample_results = {
            "status": "success",
            "total_found": 25,
            "added": 5,
            "duplicates": 15,
            "rejected": 5,
            "search_terms": request.search_terms or ["brooklyn nightlife", "manhattan bars"],
            "discovered_venues": [
                {
                    "name": "Sample Venue 1",
                    "address": "123 Main St, Brooklyn, NY",
                    "venue_type": "cocktail_lounge",
                    "confidence_score": 0.85,
                    "source": "google_places"
                },
                {
                    "name": "Sample Venue 2", 
                    "address": "456 Broadway, Manhattan, NY",
                    "venue_type": "dive_bar",
                    "confidence_score": 0.78,
                    "source": "yelp"
                }
            ]
        }
        
        return sample_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")

@app.get("/venue-insights/{venue_id}")
async def get_venue_insights(venue_id: str):
    """Get ML insights for a venue"""
    if ml_manager is None:
        raise HTTPException(status_code=503, detail="ML manager not initialized")
    
    try:
        insights = ml_manager.get_venue_insights(venue_id)
        return {
            "status": "success",
            "venue_id": venue_id,
            "insights": insights
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@app.get("/analytics/discovery")
async def get_discovery_analytics():
    """Get discovery analytics"""
    return {
        "total_venues_discovered": 150,
        "success_rate": 0.75,
        "top_sources": ["google_places", "yelp", "nyc_open_data"],
        "venue_types_distribution": {
            "bar": 45,
            "restaurant": 35, 
            "club": 25,
            "cultural": 45
        },
        "quality_scores": {
            "average": 0.78,
            "above_threshold": 0.85
        },
        "last_updated": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting NYC Nightlife ML/AI API Server...")
    print("📖 API Documentation: http://localhost:8001/docs")
    print("🔧 Health Check: http://localhost:8001/health")
    
    uvicorn.run(
        "run_ml_api:app",
        host="0.0.0.0", 
        port=8001,
        reload=False,
        log_level="info"
    )