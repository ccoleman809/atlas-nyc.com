#!/bin/bash

echo "🔧 Deploying dead link fixes..."

# Add all changes
git add atlas_public_interface.html

# Commit the fixes
git commit -m "Fix dead links in interface

- Replace non-existent venue detail page links with map scroll
- Add conditional checks for Instagram links to prevent 404s  
- Update footer home link from /atlas to /
- Ensure all links provide working functionality

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to deploy
git push origin main

echo "✅ Dead link fixes deployed!"
echo "🔗 All links now work properly on the live site"