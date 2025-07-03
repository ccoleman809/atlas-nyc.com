#!/bin/bash

echo "📊 Deploying pagination fix to show all venues..."

# Add all changes
git add atlas_public_interface.html

# Commit the pagination fix
git commit -m "Fix venue pagination to show all database entries

- Increase per_page parameter from default 20 to 1000
- Ensures all venues appear on map and in search results
- Resolves issue where only first 20 venues were displayed

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to deploy
git push origin main

echo "✅ Pagination fix deployed!"
echo "🗄️ All venues from database will now be visible on the live site"