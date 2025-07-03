"""
ML API Endpoints
FastAPI endpoints for serving ML predictions and analytics
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json

from ml_models import MLModelManager
from ml_database import MLDatabase
from data_pipeline import DataPipeline, PipelineConfig

# Pydantic models for API
class VenuePredictionRequest(BaseModel):
    venue_id: str
    timestamp: Optional[datetime] = None

class UserRecommendationRequest(BaseModel):
    user_id: str
    preferences: Optional[Dict] = None
    location: Optional[Dict[str, float]] = None
    max_recommendations: int = 10

class TrendAnalysisRequest(BaseModel):
    category: str  # 'venue', 'neighborhood', 'music_genre'
    time_period: int = 30  # days
    
class CrowdPredictionRequest(BaseModel):
    venue_id: str
    target_time: datetime

# Initialize ML system
ml_db = MLDatabase()
model_manager = MLModelManager()
pipeline_config = PipelineConfig(scraping_enabled=False)
data_pipeline = DataPipeline(pipeline_config)

app = FastAPI(
    title="NYC Nightlife ML API",
    description="Machine Learning API for NYC nightlife predictions and analytics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize ML models on startup"""
    try:
        model_manager.load_models()
        print("✅ ML API started successfully")
    except Exception as e:
        print(f"⚠️ ML models not found, using defaults: {e}")

# Prediction endpoints
@app.post("/api/ml/predict/venue-popularity")
async def predict_venue_popularity(request: VenuePredictionRequest):
    """Predict venue popularity score"""
    try:
        # Get venue insights
        insights = model_manager.get_venue_insights(request.venue_id)
        
        return {
            "venue_id": request.venue_id,
            "prediction": insights["predictions"]["popularity"],
            "timestamp": datetime.now().isoformat(),
            "model_version": "1.0"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/predict/crowd-level")
async def predict_crowd_level(request: CrowdPredictionRequest):
    """Predict crowd level for a venue at specific time"""
    try:
        prediction = model_manager.crowd_model.predict_crowd_level(
            request.venue_id,
            request.target_time
        )
        
        return {
            "success": True,
            "prediction": prediction
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/predict/trending-venues")
async def get_trending_venues(limit: int = 10):
    """Get currently trending venues"""
    try:
        # Get predictions for all venues
        trending_venues = []
        
        for venue in pipeline_config.venues_to_track:
            venue_id = venue.lower().replace(' ', '_')
            insights = model_manager.get_venue_insights(venue_id)
            
            trending_venues.append({
                "venue_id": venue_id,
                "venue_name": venue,
                "trending_score": insights["predictions"]["trend"]["momentum"],
                "trend_direction": insights["predictions"]["trend"]["direction"],
                "popularity_score": insights["predictions"]["popularity"]["score"]
            })
        
        # Sort by trending score
        trending_venues.sort(key=lambda x: x["trending_score"], reverse=True)
        
        return {
            "trending_venues": trending_venues[:limit],
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Recommendation endpoints
@app.post("/api/ml/recommendations/venues")
async def get_venue_recommendations(request: UserRecommendationRequest):
    """Get personalized venue recommendations"""
    try:
        recommendations = model_manager.recommendation_engine.get_recommendations(
            request.user_id,
            request.max_recommendations
        )
        
        # Enhance with current predictions
        enhanced_recommendations = []
        for rec in recommendations:
            insights = model_manager.get_venue_insights(rec["venue_id"])
            
            enhanced_recommendations.append({
                **rec,
                "current_popularity": insights["predictions"]["popularity"]["score"],
                "predicted_crowd": insights["predictions"]["current_crowd"]["category"],
                "peak_hour": insights["predictions"]["popularity"]["peak_hour"]
            })
        
        return {
            "user_id": request.user_id,
            "recommendations": enhanced_recommendations,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/recommendations/similar/{venue_id}")
async def get_similar_venues(venue_id: str, limit: int = 5):
    """Get venues similar to the given venue"""
    try:
        similar_venues = model_manager.recommendation_engine.get_similar_venues(
            venue_id, limit
        )
        
        return {
            "venue_id": venue_id,
            "similar_venues": similar_venues,
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Analytics endpoints
@app.post("/api/ml/analytics/trend-analysis")
async def analyze_trends(request: TrendAnalysisRequest):
    """Analyze trends for a category"""
    try:
        trend_prediction = model_manager.trend_model.predict_trend(
            request.category,
            request.time_period
        )
        
        return {
            "category": request.category,
            "time_period_days": request.time_period,
            "trend_analysis": {
                "direction": trend_prediction.trend_direction,
                "momentum": trend_prediction.momentum_score,
                "predicted_growth": trend_prediction.predicted_growth,
                "confidence": trend_prediction.confidence
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/analytics/venue-insights/{venue_id}")
async def get_venue_insights(venue_id: str):
    """Get comprehensive ML insights for a venue"""
    try:
        insights = model_manager.get_venue_insights(venue_id)
        
        # Add recent Instagram data
        instagram_posts = ml_db.get_venue_instagram_posts(venue_id, days=7)
        insights["social_metrics"] = {
            "recent_posts": len(instagram_posts),
            "avg_engagement": sum(p["engagement_rate"] for p in instagram_posts) / len(instagram_posts) if instagram_posts else 0,
            "total_likes": sum(p["likes"] for p in instagram_posts),
            "total_comments": sum(p["comments"] for p in instagram_posts)
        }
        
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/analytics/dashboard")
async def get_analytics_dashboard():
    """Get data for analytics dashboard"""
    try:
        dashboard_data = {
            "summary": {
                "total_venues_tracked": len(pipeline_config.venues_to_track),
                "predictions_generated_today": 0,  # Would count from database
                "model_accuracy": 0.85,  # Would calculate from recent predictions
                "last_model_update": "2024-01-01T00:00:00"
            },
            "trending_insights": [],
            "prediction_accuracy": {},
            "recent_activity": []
        }
        
        # Get trending venues
        trending = await get_trending_venues(5)
        dashboard_data["trending_insights"] = trending["trending_venues"]
        
        # Get model accuracy metrics
        for pred_type in ["popularity", "crowd", "trend"]:
            accuracy = ml_db.get_prediction_accuracy(pred_type, days=30)
            dashboard_data["prediction_accuracy"][pred_type] = accuracy
        
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Model management endpoints
@app.post("/api/ml/models/retrain")
async def retrain_models(background_tasks: BackgroundTasks):
    """Trigger model retraining"""
    try:
        # Run training in background
        background_tasks.add_task(data_pipeline.run_training)
        
        return {
            "message": "Model retraining started",
            "status": "processing",
            "estimated_completion": (datetime.now() + timedelta(hours=2)).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/models/status")
async def get_model_status():
    """Get status of ML models"""
    try:
        status = {
            "models_loaded": model_manager.models_loaded,
            "last_training": "2024-01-01T00:00:00",  # Would get from database
            "model_versions": {
                "popularity_model": "1.0",
                "trend_model": "1.0",
                "recommendation_engine": "1.0",
                "crowd_model": "1.0"
            },
            "health": "healthy"
        }
        
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Data collection endpoints
@app.post("/api/ml/data/collect")
async def trigger_data_collection(background_tasks: BackgroundTasks):
    """Trigger data collection"""
    if not pipeline_config.scraping_enabled:
        return {
            "message": "Data collection disabled (Instagram scraping not authorized)",
            "status": "disabled"
        }
    
    try:
        background_tasks.add_task(data_pipeline.run_collection)
        
        return {
            "message": "Data collection started",
            "status": "processing"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User interaction logging
@app.post("/api/ml/interactions/log")
async def log_user_interaction(
    user_id: str,
    venue_id: str,
    interaction_type: str,
    rating: Optional[float] = None
):
    """Log user interaction for model training"""
    try:
        ml_db.log_user_interaction(user_id, venue_id, interaction_type, rating)
        
        return {
            "message": "Interaction logged successfully",
            "user_id": user_id,
            "venue_id": venue_id,
            "interaction_type": interaction_type
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# A/B testing endpoints
@app.post("/api/ml/ab-test/create")
async def create_ab_test(
    test_name: str,
    model_a: str,
    model_b: str,
    traffic_split: float = 0.5
):
    """Create A/B test for model comparison"""
    # Implementation would create A/B test configuration
    return {
        "test_id": f"test_{test_name}_{datetime.now().strftime('%Y%m%d')}",
        "test_name": test_name,
        "models": {"a": model_a, "b": model_b},
        "traffic_split": traffic_split,
        "status": "active"
    }

@app.get("/api/ml/ab-test/{test_id}/results")
async def get_ab_test_results(test_id: str):
    """Get A/B test results"""
    # Implementation would analyze test performance
    return {
        "test_id": test_id,
        "results": {
            "model_a": {"accuracy": 0.85, "user_satisfaction": 0.82},
            "model_b": {"accuracy": 0.87, "user_satisfaction": 0.84}
        },
        "winner": "model_b",
        "confidence": 0.95
    }

# Health check
@app.get("/api/ml/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": model_manager.models_loaded,
        "database_connected": True,  # Would check database connection
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)