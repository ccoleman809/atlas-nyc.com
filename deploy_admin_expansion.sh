#!/bin/bash

echo "📊 Deploying admin interface expansion..."

# Add all changes
git add admin_interface.html

# Commit the admin improvements
git commit -m "Expand admin interface to view whole database

- Fix pagination to load up to 1000 venues instead of default 20
- Add database statistics dashboard showing:
  - Total venues in database
  - Currently displayed venues (updates with search/filter)
  - Number of unique neighborhoods
  - Number of unique venue types
- Improve admin overview capabilities for better database management

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to deploy
git push origin main

echo "✅ Admin interface expansion deployed!"
echo "🗄️ Admin page now shows complete database with statistics dashboard"