#!/bin/bash

echo "🚀 Deploying latest changes to Render..."

# Add all changes
git add -A

# Commit with message
git commit -m "Fix map pin dropping and improve coordinate accuracy

- Venue card clicks now properly drop pins on map
- Fixed coordinate generation with consistent hash-based positioning  
- Enhanced map click handling with better debugging
- Created venue import scripts for 80+ NYC venues
- Improved error handling and validation

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to trigger deployment
git push origin main

echo "✅ Changes pushed! Check Render dashboard for deployment status."
echo "📱 Visit https://dashboard.render.com to monitor deployment"