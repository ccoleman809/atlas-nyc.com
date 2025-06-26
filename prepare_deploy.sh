#!/bin/bash
# Prepare Atlas-NYC for Render.com deployment

echo "🚀 Preparing Atlas-NYC for Render.com deployment..."

# Check if we're in the right directory
if [ ! -f "api_server.py" ]; then
    echo "❌ Error: Please run this script from the nightlife_project directory"
    exit 1
fi

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial Atlas-NYC deployment preparation"
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Check for required files
echo "📋 Checking required files..."

required_files=(
    "api_server.py"
    "config.py"
    "render.yaml"
    "requirements.txt"
    "init_render_db.py"
    "import_nyc_venues.py"
    "RENDER_DEPLOYMENT.md"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "❌ Missing required files. Please ensure all files are present."
    exit 1
fi

# Test local dependencies
echo "🧪 Testing local setup..."
if command -v python &> /dev/null; then
    if python -c "import fastapi, uvicorn, googlemaps" 2>/dev/null; then
        echo "✅ Required Python packages installed"
    else
        echo "⚠️  Some Python packages missing. Run: pip install -r requirements.txt"
    fi
else
    echo "⚠️  Python not found in PATH"
fi

# Check environment configuration
echo "⚙️  Checking configuration..."
if [ -f ".env" ]; then
    if grep -q "SECRET_KEY=NKcFBYjR1a0Xns-WsixfChYxgxyJt1iJsamWVuHeO-uCCuLICZfyv_HrvXt0Fw_EnAdTwAbnAC1uNK8-dmrPCw" .env; then
        echo "✅ Secure SECRET_KEY configured"
    else
        echo "⚠️  SECRET_KEY may need updating"
    fi
    
    if grep -q "GOOGLE_MAPS_API_KEY=AIza" .env; then
        echo "✅ Google Maps API key configured"
    else
        echo "⚠️  Google Maps API key not found"
    fi
else
    echo "⚠️  .env file not found"
fi

# Display next steps
echo ""
echo "🎯 Next Steps for Render.com Deployment:"
echo "1. Push code to GitHub:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/atlas-nyc.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "2. Deploy to Render.com:"
echo "   - Go to render.com/dashboard"
echo "   - Click 'New' → 'Blueprint'"
echo "   - Connect your GitHub repository"
echo "   - Render will auto-detect render.yaml"
echo ""
echo "3. Configure environment variables in Render dashboard:"
echo "   GOOGLE_MAPS_API_KEY=AIzaSyCIJcXpuBHBiDhlz2KcfKjkdQn7gYo6iD0"
echo ""
echo "4. After deployment, initialize database:"
echo "   python init_render_db.py"
echo "   python import_nyc_venues.py"
echo ""
echo "📖 Full deployment guide: RENDER_DEPLOYMENT.md"
echo ""
echo "✨ Atlas-NYC is ready for deployment!"