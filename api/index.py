# Vercel entry point for Atlas-NYC
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from api_server import app

# Vercel serverless function handler
def handler(request, response):
    return app