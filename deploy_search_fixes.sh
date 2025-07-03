#!/bin/bash

echo "🔍 Deploying search functionality fixes..."

# Add all changes
git add atlas_public_interface.html

# Commit the search and navigation fixes
git commit -m "Fix search functionality and Show All neighborhood link

Search fixes:
- Use allVenues array instead of fetching fresh data each search
- Add fallback to load venues if array is empty
- Improve error handling with empty search term alerts
- Fix event listener timing with DOMContentLoaded wrapper

Show All neighborhood fix:
- Replace dead link with proper showAllVenuesWithResults function
- Display all venues on map and as browsable cards
- Update visual styling to highlight active selection
- Scroll to map for better user experience

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to deploy
git push origin main

echo "✅ Search and navigation fixes deployed!"
echo "🔍 Search bar now works properly and Show All displays all venues"