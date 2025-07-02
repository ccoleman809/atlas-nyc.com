#!/usr/bin/env python3
"""
Add sample entries for new categories: DJs, Cultural Organizations, Recurring Events, and Influencers
"""

from venue_db import VenueDatabase, Venue

def add_new_category_entries():
    db = VenueDatabase()
    
    # Sample entries for new categories
    new_entries = [
        # DJs
        ("DJ Moma", "Manhattan", "djmoma", "dj", None, "MoMA PS1 Warm Up resident DJ", "Saturdays", "$$$"),
        ("Quest Love", "Manhattan", "questlove", "dj", None, "Legendary DJ and musician", "Varies", "$$$$"),
        ("DJ Spinna", "Brooklyn", "djspinna", "dj", None, "Brooklyn's finest soul/hip-hop DJ", "Weekends", "$$$"),
        ("Honey Dijon", "Manhattan", "honeydijon", "dj", None, "International house music icon", "Special Events", "$$$$"),
        
        # Cultural Organizations
        ("MoMA PS1", "Queens", "momaps1", "cultural_organization", "22-25 Jackson Ave", "Contemporary art institution", "Thu-Mon", "$$"),
        ("Brooklyn Arts Council", "Brooklyn", "brooklynartscouncil", "cultural_organization", "55 Washington St", "Supporting Brooklyn artists", "Mon-Fri", "$"),
        ("The Shed", "Manhattan", "theshedny", "cultural_organization", "545 W 30th St", "Cultural center for art innovation", "Wed-Sun", "$$$"),
        ("National Black Theatre", "Harlem", "nationalblacktheatre", "cultural_organization", "2031 5th Ave", "African American cultural institution", "Varies", "$$"),
        
        # Recurring Events
        ("Warm Up at MoMA PS1", "Queens", "warmupps1", "recurring_event", "22-25 Jackson Ave", "Summer Saturday dance parties", "Saturdays (Summer)", "$$$"),
        ("Afropunk Festival", "Brooklyn", "afropunk", "recurring_event", "Commodore Barry Park", "Annual celebration of Black culture", "August", "$$"),
        ("Pride March", "Manhattan", "nycpride", "recurring_event", "Various Locations", "Annual LGBTQ+ celebration", "June", "Free"),
        ("SummerStage", "Manhattan", "summerstage", "recurring_event", "Central Park", "Free outdoor concerts", "Summer", "Free"),
        ("Brooklyn Hip-Hop Festival", "Brooklyn", "bkhiphopfest", "recurring_event", "Various Locations", "Annual hip-hop celebration", "July", "$$"),
        
        # Influencers
        ("NYC Basic", "Manhattan", "nycbasic", "influencer", None, "NYC lifestyle and nightlife blogger", "Active", "N/A"),
        ("The Infatuation", "Manhattan", "theinfatuation", "influencer", None, "Restaurant and bar recommendations", "Active", "N/A"),
        ("Guest of a Guest", "Manhattan", "guestofaguest", "influencer", None, "NYC social scene coverage", "Active", "N/A"),
        ("Brownstoner", "Brooklyn", "brownstoner", "influencer", None, "Brooklyn culture and events", "Active", "N/A"),
        ("Time Out New York", "Manhattan", "timeoutnewyork", "influencer", None, "NYC entertainment guide", "Active", "N/A"),
    ]
    
    # Add entries
    added = 0
    for entry in new_entries:
        try:
            venue = Venue(
                name=entry[0],
                neighborhood=entry[1],
                instagram_handle=entry[2],
                venue_type=entry[3],
                address=entry[4],
                description=entry[5],
                busy_nights=entry[6],
                price_range=entry[7]
            )
            result = db.add_venue(venue)
            if result > 0:
                print(f"✅ Added: {entry[0]} ({entry[3]})")
                added += 1
            else:
                print(f"⏭️  Skipped: {entry[0]} (already exists)")
        except Exception as e:
            print(f"❌ Error adding {entry[0]}: {e}")
    
    print(f"\n📊 Summary: Added {added} new entries for DJs, Cultural Orgs, Events, and Influencers")

if __name__ == "__main__":
    add_new_category_entries()