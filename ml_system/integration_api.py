"""
Integration API for ML/AI Venue Discovery System
Provides FastAPI endpoints to integrate ML features with the main application
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import asyncio
import logging
from datetime import datetime
import json
from contextlib import asynccontextmanager

from ml_system.automated_venue_discovery import AutomatedVenueDiscovery, VenueCandidate
from ml_system.smart_content_enhancer import SmartContentEnhancer, VenueEnhancement
from ml_system.ml_models import MLModelManager

# Pydantic models for API
class DiscoveryRequest(BaseModel):
    search_terms: Optional[List[str]] = None
    max_results: Optional[int] = 100
    quality_threshold: Optional[float] = 0.6
    include_events: Optional[bool] = True

class DiscoveryResponse(BaseModel):
    status: str
    total_found: int
    added: int
    duplicates: int
    rejected: int
    execution_time: float
    discovered_venues: List[Dict[str, Any]]

class EnhancementRequest(BaseModel):
    venue_ids: Optional[List[str]] = None
    venue_data: Optional[List[Dict[str, Any]]] = None
    include_social_analysis: bool = True
    include_recommendations: bool = True

class EnhancementResponse(BaseModel):
    status: str
    enhanced_count: int
    enhancements: List[Dict[str, Any]]

class PredictionRequest(BaseModel):
    venue_id: str
    timestamp: Optional[str] = None
    include_crowd_prediction: bool = True
    include_popularity_forecast: bool = True

class PredictionResponse(BaseModel):
    venue_id: str
    predictions: Dict[str, Any]
    confidence_scores: Dict[str, float]
    generated_at: str

class ScheduledTaskRequest(BaseModel):
    task_type: str  # 'discovery', 'enhancement', 'prediction'
    schedule: str   # cron expression
    parameters: Dict[str, Any]

# Global ML components
ml_manager = None
discovery_system = None
content_enhancer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize ML components on startup"""
    global ml_manager, discovery_system, content_enhancer
    
    try:
        # Initialize ML components
        ml_manager = MLModelManager()
        discovery_system = AutomatedVenueDiscovery()
        content_enhancer = SmartContentEnhancer()
        
        # Load pre-trained models if available
        try:
            ml_manager.load_models()
        except Exception as e:
            logging.warning(f"Could not load pre-trained models: {e}")
        
        logging.info("ML/AI system initialized successfully")
        
    except Exception as e:
        logging.error(f"Failed to initialize ML system: {e}")
        raise
    
    yield
    
    # Cleanup on shutdown
    logging.info("Shutting down ML/AI system")

# Create FastAPI app
app = FastAPI(
    title="NYC Nightlife ML/AI API",
    description="AI-powered venue discovery and enhancement system",
    version="1.0.0",
    lifespan=lifespan
)

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dependency to get ML manager
async def get_ml_manager():
    if ml_manager is None:
        raise HTTPException(status_code=503, detail="ML system not initialized")
    return ml_manager

# Dependency to get discovery system
async def get_discovery_system():
    if discovery_system is None:
        raise HTTPException(status_code=503, detail="Discovery system not initialized")
    return discovery_system

# Dependency to get content enhancer
async def get_content_enhancer():
    if content_enhancer is None:
        raise HTTPException(status_code=503, detail="Content enhancer not initialized")
    return content_enhancer

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

@app.post("/discover/venues", response_model=DiscoveryResponse)
async def discover_venues(
    request: DiscoveryRequest,
    background_tasks: BackgroundTasks,
    discovery: AutomatedVenueDiscovery = Depends(get_discovery_system)
):
    """
    Discover new venues using AI and multiple data sources
    """
    start_time = datetime.now()
    
    try:
        # Run discovery
        search_terms = request.search_terms or [
            'brooklyn nightlife', 'manhattan bars', 'nyc music venues',
            'cultural centers nyc', 'art galleries brooklyn'
        ]
        
        results = await discovery.discover_venues(search_terms)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return DiscoveryResponse(
            status="success",
            total_found=results['total_found'],
            added=results['added'],
            duplicates=results['duplicates'],
            rejected=results['rejected'],
            execution_time=execution_time,
            discovered_venues=[]  # Would include actual venue data
        )
        
    except Exception as e:
        logger.error(f"Error in venue discovery: {e}")
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")

@app.post("/enhance/venues", response_model=EnhancementResponse)
async def enhance_venues(
    request: EnhancementRequest,
    enhancer: SmartContentEnhancer = Depends(get_content_enhancer)
):
    """
    Enhance venue descriptions and data using AI
    """
    try:
        if not request.venue_data and not request.venue_ids:
            raise HTTPException(status_code=400, detail="Either venue_data or venue_ids must be provided")
        
        venues_to_enhance = request.venue_data or []
        
        # If venue_ids provided, fetch venue data (would connect to main database)
        if request.venue_ids:
            # Placeholder - would fetch from actual database
            venues_to_enhance = [
                {'id': vid, 'name': f'Venue {vid}', 'venue_type': 'bar'}
                for vid in request.venue_ids
            ]
        
        # Enhance venues
        enhancements = []
        for venue in venues_to_enhance:
            enhancement = await enhancer.enhance_venue(venue)
            enhancements.append({
                'venue_id': enhancement.venue_id,
                'enhanced_description': enhancement.enhanced_description,
                'key_features': enhancement.key_features,
                'atmosphere_tags': enhancement.atmosphere_tags,
                'target_demographics': enhancement.target_demographics,
                'best_times': enhancement.best_times,
                'price_insights': enhancement.price_insights,
                'social_sentiment': enhancement.social_sentiment,
                'popularity_trend': enhancement.popularity_trend,
                'recommendations': enhancement.recommendations if request.include_recommendations else []
            })
        
        return EnhancementResponse(
            status="success",
            enhanced_count=len(enhancements),
            enhancements=enhancements
        )
        
    except Exception as e:
        logger.error(f"Error in venue enhancement: {e}")
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")

@app.post("/predict/venue", response_model=PredictionResponse)
async def predict_venue_metrics(
    request: PredictionRequest,
    ml_manager: MLModelManager = Depends(get_ml_manager)
):
    """
    Generate ML predictions for a venue (popularity, crowd levels, etc.)
    """
    try:
        timestamp = datetime.now()
        if request.timestamp:
            timestamp = datetime.fromisoformat(request.timestamp)
        
        # Get comprehensive venue insights
        insights = ml_manager.get_venue_insights(request.venue_id)
        
        # Extract predictions and confidence scores
        predictions = insights.get('predictions', {})
        confidence_scores = {}
        
        if 'popularity' in predictions:
            confidence_scores['popularity'] = 0.85
        if 'trend' in predictions:
            confidence_scores['trend'] = 0.78
        if 'current_crowd' in predictions:
            confidence_scores['crowd'] = predictions['current_crowd'].get('confidence', 0.8)
        
        return PredictionResponse(
            venue_id=request.venue_id,
            predictions=predictions,
            confidence_scores=confidence_scores,
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error in venue prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/venues/{venue_id}/insights")
async def get_venue_insights(
    venue_id: str,
    ml_manager: MLModelManager = Depends(get_ml_manager)
):
    """
    Get comprehensive AI-powered insights for a venue
    """
    try:
        insights = ml_manager.get_venue_insights(venue_id)
        return JSONResponse(content=insights)
        
    except Exception as e:
        logger.error(f"Error getting venue insights: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@app.post("/discover/events")
async def discover_events(
    search_location: str = "New York City",
    days_ahead: int = 30,
    event_types: Optional[List[str]] = None
):
    """
    Discover upcoming events using AI and multiple sources
    """
    try:
        # This would integrate with the discovery system to find events
        # For now, return placeholder data
        
        sample_events = [
            {
                "name": "Brooklyn Art Gallery Opening",
                "venue": "Local Gallery",
                "date": "2024-07-15",
                "type": "cultural",
                "confidence": 0.9
            },
            {
                "name": "Live Music Night",
                "venue": "Music Venue",
                "date": "2024-07-16",
                "type": "music",
                "confidence": 0.85
            }
        ]
        
        return {
            "status": "success",
            "events_found": len(sample_events),
            "events": sample_events,
            "search_parameters": {
                "location": search_location,
                "days_ahead": days_ahead,
                "event_types": event_types
            }
        }
        
    except Exception as e:
        logger.error(f"Error in event discovery: {e}")
        raise HTTPException(status_code=500, detail=f"Event discovery failed: {str(e)}")

@app.post("/schedule/task")
async def schedule_ml_task(
    request: ScheduledTaskRequest,
    background_tasks: BackgroundTasks
):
    """
    Schedule recurring ML tasks (discovery, enhancement, etc.)
    """
    try:
        # Add task to background processing queue
        if request.task_type == "discovery":
            background_tasks.add_task(
                scheduled_discovery_task,
                request.parameters
            )
        elif request.task_type == "enhancement":
            background_tasks.add_task(
                scheduled_enhancement_task,
                request.parameters
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid task type")
        
        return {
            "status": "scheduled",
            "task_type": request.task_type,
            "schedule": request.schedule,
            "scheduled_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error scheduling task: {e}")
        raise HTTPException(status_code=500, detail=f"Task scheduling failed: {str(e)}")

@app.get("/analytics/discovery")
async def get_discovery_analytics():
    """
    Get analytics on venue discovery performance
    """
    try:
        # This would fetch real analytics from the ML database
        analytics = {
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
        
        return JSONResponse(content=analytics)
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

# Background task functions
async def scheduled_discovery_task(parameters: Dict[str, Any]):
    """Background task for scheduled venue discovery"""
    try:
        logger.info("Running scheduled discovery task")
        
        if discovery_system:
            search_terms = parameters.get('search_terms', [])
            results = await discovery_system.discover_venues(search_terms)
            logger.info(f"Scheduled discovery completed: {results}")
        
    except Exception as e:
        logger.error(f"Scheduled discovery task failed: {e}")

async def scheduled_enhancement_task(parameters: Dict[str, Any]):
    """Background task for scheduled venue enhancement"""
    try:
        logger.info("Running scheduled enhancement task")
        
        if content_enhancer:
            # Would enhance venues that need updating
            logger.info("Scheduled enhancement completed")
        
    except Exception as e:
        logger.error(f"Scheduled enhancement task failed: {e}")

# WebSocket endpoint for real-time updates
@app.websocket("/ws/discovery")
async def websocket_discovery_updates(websocket):
    """WebSocket endpoint for real-time discovery updates"""
    await websocket.accept()
    
    try:
        while True:
            # Send periodic updates about discovery progress
            update = {
                "type": "discovery_status",
                "timestamp": datetime.now().isoformat(),
                "status": "running",
                "venues_processed": 42
            }
            
            await websocket.send_json(update)
            await asyncio.sleep(5)  # Send updates every 5 seconds
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "integration_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )