#!/usr/bin/env python3
"""
Launcher script for ML/AI Integration API
"""

import sys
import os
import uvicorn

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Fix the imports in integration_api.py by using absolute imports
def fix_imports():
    """Fix relative imports in integration_api.py"""
    api_file = os.path.join('ml_system', 'integration_api.py')
    
    if os.path.exists(api_file):
        with open(api_file, 'r') as f:
            content = f.read()
        
        # Replace relative imports with absolute imports
        content = content.replace(
            'from .automated_venue_discovery import',
            'from ml_system.automated_venue_discovery import'
        )
        content = content.replace(
            'from .smart_content_enhancer import',
            'from ml_system.smart_content_enhancer import'
        )
        content = content.replace(
            'from .ml_models import',
            'from ml_system.ml_models import'
        )
        
        with open(api_file, 'w') as f:
            f.write(content)

def main():
    """Start the ML API server"""
    print("🚀 Starting ML/AI Integration API Server...")
    
    # Fix imports
    fix_imports()
    
    # Import the app after fixing imports
    from ml_system.integration_api import app
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()