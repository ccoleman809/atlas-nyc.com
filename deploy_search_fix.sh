#!/bin/bash

echo "🔍 Deploying search functionality fix..."

# Add all changes
git add atlas_public_interface.html

# Commit the search fix
git commit -m "Fix search functionality - ensure venues load on page load

- Add loadVenuesForSearch function to pre-load venues independently of map
- Call loadVenuesForSearch on DOMContentLoaded to ensure search works immediately
- Add comprehensive console logging for debugging search issues
- Improve error handling when map isn't loaded yet
- Add fallback venue loading if search is performed before venues are available

This resolves the issue where search didn't work because allVenues array
was only populated when the map loaded, not when the page loaded.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to deploy
git push origin main

echo "✅ Search functionality fix deployed!"
echo "🔍 Search should now work immediately on page load"