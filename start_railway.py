#!/usr/bin/env python3
"""
Minimal start script for Railway deployment
Falls back to basic API if ML system fails
"""
import os
import sys

# Set environment variable to skip ML if needed
if "--skip-ml" in sys.argv:
    os.environ["SKIP_ML_INIT"] = "true"
    print("⚠️ Starting with ML system disabled")

try:
    # Try to import and run the full API
    from api_server import app
    import uvicorn
    
    port = int(os.environ.get("PORT", 8000))
    print(f"✅ Starting full API server on port {port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
    
except Exception as e:
    print(f"❌ Failed to start full API: {e}")
    print("🔄 Attempting to start minimal API...")
    
    # Fall back to minimal API
    from fastapi import FastAPI
    import uvicorn
    
    app = FastAPI(title="Atlas-NYC API (Minimal)")
    
    @app.get("/")
    async def root():
        return {"status": "minimal", "message": "API running in fallback mode"}
    
    @app.get("/health")
    async def health():
        return {"status": "healthy", "mode": "minimal"}
    
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)