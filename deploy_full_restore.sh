#!/bin/bash

echo "🚀 Deploying comprehensive venue restore..."

# Add the updated files
git add production_api.py admin_interface.html restore_all_venues.py

# Commit with descriptive message
git commit -m "Restore ALL original venues including Brooklyn/Queens spots

- Updated import endpoint to include 80+ venues
- Includes all original venues: Nowadays, Jupiter Disco, Good Room, etc.
- Plus Manhattan venues: Death & Co, Blue Note, Le Bain, etc.
- Import button now restores complete venue database
- Fixed missing venues issue by including full original list

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to deploy
git push origin main

echo "✅ Pushed! Full venue restore will be available after deployment."
echo "📍 The import button will now restore ALL 80+ venues!"