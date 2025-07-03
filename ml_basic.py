"""
Basic ML endpoints without heavy dependencies
This ensures the API can start successfully on Render
"""

from fastapi import APIRouter
from datetime import datetime
from typing import Dict, Optional

router = APIRouter(prefix="/api/ml", tags=["ml"])

@router.get("/status")
async def ml_status():
    """Simple ML status endpoint"""
    return {
        "status": "operational",
        "message": "Basic ML endpoints working",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@router.get("/health")  
async def ml_health():
    """ML health check"""
    return {
        "status": "healthy",
        "ml_system_initialized": False,
        "components": {
            "enhancer": False,
            "discovery": False,
            "insights": False,
            "moderation": False
        },
        "timestamp": datetime.now().isoformat(),
        "message": "ML system in setup phase"
    }

@router.get("/analytics")
async def ml_analytics():
    """Basic ML analytics"""
    return {
        "status": "success",
        "ml_system_active": False,
        "venues_enhanced": 0,
        "venues_auto_discovered": 0,
        "venue_type_distribution": {},
        "system_health": {
            "enhancer_active": False,
            "discovery_active": False,
            "insights_active": False
        },
        "last_updated": datetime.now().isoformat(),
        "message": "ML analytics will be available once system is fully initialized"
    }

# Basic moderation endpoints
moderation_router = APIRouter(prefix="/api/moderation", tags=["moderation"])

@moderation_router.get("/pending")
async def get_pending_moderation():
    """Get pending content moderation items"""
    return {
        "status": "unavailable",
        "message": "Moderation system initializing",
        "pending_items": [],
        "count": 0
    }

@moderation_router.get("/stats")  
async def get_moderation_stats():
    """Get content moderation statistics"""
    return {
        "status": "success",
        "stats": {
            "pending_items": 0,
            "approval_rate": 0,
            "total_approved": 0,
            "total_rejected": 0,
            "training_data_points": 0,
            "recent_activity": {}
        }
    }