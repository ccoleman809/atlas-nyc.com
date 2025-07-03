#!/bin/bash

echo "🚀 Deploying new categories: DJs, Cultural Orgs, Events & Influencers..."

# Add all changes
git add production_api.py admin_interface.html atlas_public_interface.html add_new_categories.py

# Commit
git commit -m "Add new venue categories: DJs, Cultural Orgs, Events & Influencers

- Added 4 new venue types: dj, cultural_organization, recurring_event, influencer
- Updated admin interface with new category options and emojis
- Added filter buttons on map for each new category
- Created unique map markers for each category
- Import now includes sample entries for all new categories:
  * DJs: DJ Moma, Quest Love, DJ Spinna, Honey Dijon
  * Cultural Orgs: MoMA PS1, Brooklyn Arts Council, The Shed
  * Events: Warm Up, Afropunk, Pride, SummerStage
  * Influencers: NYC Basic, The Infatuation, Time Out NY
- Total import now includes 100+ entries across all categories

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to deploy
git push origin main

echo "✅ Pushed! New categories will be available after deployment."
echo "🎯 You can now track DJs, cultural organizations, recurring events, and influencers!"