# Vercel entry point for Atlas-NYC
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import and configure the FastAPI app for serverless
try:
    from api_server import app
except ImportError as e:
    print(f"Import error: {e}")
    # Create a minimal app as fallback
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    def root():
        return {"message": "Atlas-NYC API (Vercel deployment)", "status": "running"}
    
    @app.get("/health")
    def health():
        return {"status": "healthy", "platform": "vercel"}

# Export the app for Vercel
handler = app