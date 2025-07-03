#!/bin/bash

echo "🔧 Deploying comprehensive debugging fixes..."

# Add all changes
git add atlas_public_interface.html

# Commit the debugging fixes
git commit -m "Add comprehensive debugging for search and map issues

Search function fixes:
- Simplified search to fetch directly from API instead of using allVenues
- Added detailed console logging at every step
- Better error handling and user feedback
- Direct API calls to bypass potential variable issues

Map function fixes:
- Added detailed logging for venue loading and marker creation
- Better error handling for marker creation failures
- Step-by-step coordinate validation logging
- Fixed missing closing brace in forEach loop
- Added total marker count logging

This will help identify exactly where search and map are failing
with detailed console output for debugging.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to deploy
git push origin main

echo "✅ Debugging fixes deployed!"
echo "🔍 Check browser console for detailed logs to identify issues"