#!/bin/bash

echo "🔧 Fixing 502 Error - Removing problematic cache calls..."

# Add the fix
git add production_api.py

# Commit the fix
git commit -m "Fix 502 error by removing undefined cache function calls

- Commented out _get_cached_venues.cache_clear() calls
- This function doesn't exist in production_api.py
- Should resolve 502 server error

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push the fix
git push origin main

echo "✅ Fix pushed! Site should be back online in 5-10 minutes."
echo "📱 Check Render dashboard to monitor deployment."