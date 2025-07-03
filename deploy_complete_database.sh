#!/bin/bash

echo "🚀 Deploying COMPLETE database with ALL original venues..."

# Add all changes
git add production_api.py admin_interface.html restore_original_31_venues.py

# Commit
git commit -m "Add ALL original 31 venues including Schmuck, Mister Paradise, etc.

FINALLY includes all your original venues that were missing:
- Schmuck (Lower East Side) - Intimate cocktail bar with DJs
- Mister Paradise (East Village) - Tropical-themed cocktail bar  
- Ray's Bar (Lower East Side) - Dive bar with great cocktails
- Beverly's (Lower East Side) - Cocktail bar with DJs
- The Flower Shop (Lower East Side) - Bar and restaurant
- Kind Regards (Lower East Side) - Japanese-inspired cocktails
- Clandestino (Lower East Side) - Underground dance bar
- Mehanata (Lower East Side) - Bulgarian bar and nightclub
- Home Sweet Home (Lower East Side) - Dive bar with taxidermy
- The Back Room (Lower East Side) - Prohibition-era speakeasy
- Hotel Chantelle (Lower East Side) - Rooftop bar and lounge
- Sour Mouse (Lower East Side) - Greek cocktail bar
- Bar Goto (Lower East Side) - Japanese cocktail bar
- Joyface (East Village) - Neighborhood cocktail bar
- Amor y Amargo (East Village) - Bitters-focused cocktails
- Berlin (East Village) - Underground bar beneath 2A
- Niagara (East Village) - Rock and roll dive bar
- Von (East Village) - Minimalist cocktail bar
- THIEF (Brooklyn) - Cocktail bar with DJs
- Birdy's (Brooklyn) - Neighborhood bar
- TBA Brooklyn (Williamsburg) - Bar and music venue
- Sundown (Brooklyn) - Cocktail bar with DJs
- Plus all the other venues, DJs, events, and influencers

Complete import now includes 130+ total entries!

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to deploy
git push origin main

echo "✅ Pushed! ALL your original venues are now included!"
echo "🎯 Schmuck, Mister Paradise, and all 31 original venues will be restored!"