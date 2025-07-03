
# Add these endpoints to your main api_server.py

from ml_system.integration_api import (
    discover_venues as ml_discover_venues,
    enhance_venues as ml_enhance_venues,
    predict_venue_metrics as ml_predict_venue
)
from ml_system.automated_venue_discovery import AutomatedVenueDiscovery
from ml_system.smart_content_enhancer import SmartContentEnhancer

# Initialize ML components (add to your app startup)
ml_discovery = AutomatedVenueDiscovery()
ml_enhancer = SmartContentEnhancer()

@app.post("/api/ml/discover-venues")
async def api_discover_venues(
    search_terms: List[str] = None,
    quality_threshold: float = 0.6
):
    """Discover new venues using ML"""
    try:
        results = await ml_discovery.discover_venues(search_terms)
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/enhance-venue/{venue_id}")
async def api_enhance_venue(venue_id: int):
    """Enhance venue with ML-generated content"""
    try:
        # Get venue from database
        venue_data = get_venue_by_id(venue_id)  # Your existing function
        
        # Enhance with ML
        enhancement = await ml_enhancer.enhance_venue(venue_data)
        
        # Update database with enhancement
        update_venue_enhancement(venue_id, enhancement)  # Implement this
        
        return {"status": "success", "enhancement": enhancement}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/venue-insights/{venue_id}")
async def api_venue_insights(venue_id: int):
    """Get ML insights for a venue"""
    try:
        from ml_system.ml_models import MLModelManager
        ml_manager = MLModelManager()
        
        insights = ml_manager.get_venue_insights(str(venue_id))
        return {"status": "success", "insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background task for periodic discovery
from fastapi import BackgroundTasks

@app.post("/api/ml/schedule-discovery")
async def schedule_discovery(background_tasks: BackgroundTasks):
    """Schedule background venue discovery"""
    background_tasks.add_task(run_scheduled_discovery)
    return {"status": "scheduled"}

async def run_scheduled_discovery():
    """Background task for scheduled discovery"""
    try:
        results = await ml_discovery.discover_venues()
        # Log results to ML analytics table
        log_discovery_results(results)
    except Exception as e:
        logger.error(f"Scheduled discovery failed: {e}")
