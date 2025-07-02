#!/bin/bash

echo "🚀 Deploying Import Button to Admin Panel..."

# Add changes
git add admin_interface.html production_api.py

# Commit
git commit -m "Add Import All Venues button to admin panel

- Added purple Import All Venues button in admin interface
- Button triggers /admin/import-venues endpoint
- Shows confirmation before importing
- Automatically refreshes venue list after import
- Will add 25+ popular NYC venues with one click

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to deploy
git push origin main

echo "✅ Pushed! Check Render dashboard for deployment status."