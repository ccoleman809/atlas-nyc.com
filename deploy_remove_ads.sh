#!/bin/bash

echo "🧹 Removing advertising code that's causing page errors..."

# Add all changes
git add atlas_public_interface.html

# Commit the cleanup
git commit -m "Remove advertising code causing JavaScript errors

- Remove Google AdSense integration and ad containers
- Remove Resy affiliate widgets and tracking
- Remove ad-related CSS styles
- Restore core functionality without advertising clutter

This should fix the blank page and broken map/search issues
by removing code that was causing JavaScript errors.

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to deploy
git push origin main

echo "✅ Advertising code removed!"
echo "🔍 Map and search should now work properly"