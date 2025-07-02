#!/usr/bin/env python3
"""
Restore the ORIGINAL 31 venues including Schmuck, Mister Paradise, etc.
"""

from venue_db import VenueDatabase, Venue

def restore_original_venues():
    db = VenueDatabase()
    
    # The ORIGINAL 31 venues that should be in the database
    original_venues = [
        # Your original venues that are missing
        ("Schmuck", "Lower East Side", "schmucknyc", "bar", "54 Chrystie St", "Intimate cocktail bar with DJs", "Thu,Fri,Sat", "$$"),
        ("Mister Paradise", "East Village", "misterparadise", "bar", "105 1st Ave", "Tropical-themed cocktail bar", "Wed,Thu,Fri,Sat", "$$"),
        ("Ray's Bar", "Lower East Side", "raysbarnyc", "bar", "8 E 1st St", "Dive bar with great cocktails", "Daily", "$"),
        ("Beverly's", "Lower East Side", "beverlysnyc", "bar", "150 Rivington St", "Cocktail bar with DJs", "Thu,Fri,Sat", "$$"),
        ("The Flower Shop", "Lower East Side", "theflowershopnyc", "bar", "107 Eldridge St", "Bar and restaurant", "Wed,Thu,Fri,Sat", "$$$"),
        ("Kind Regards", "Lower East Side", "kindregardsnyc", "cocktail_bar", "113 Ludlow St", "Japanese-inspired cocktail bar", "Wed,Thu,Fri,Sat", "$$$"),
        ("Clandestino", "Lower East Side", "clandestinobar", "bar", "35 Canal St", "Underground dance bar", "Fri,Sat", "$$"),
        ("Mehanata", "Lower East Side", "mehanatanyc", "nightclub", "113 Ludlow St", "Bulgarian bar and nightclub", "Thu,Fri,Sat", "$$"),
        ("Home Sweet Home", "Lower East Side", "homesweethomebar", "bar", "131 Chrystie St", "Dive bar with taxidermy", "Daily", "$"),
        ("The Back Room", "Lower East Side", "thebackroomnyc", "bar", "102 Norfolk St", "Prohibition-era speakeasy", "Daily", "$$"),
        ("Hotel Chantelle", "Lower East Side", "hotelchantelle", "rooftop_bar", "92 Ludlow St", "Rooftop bar and lounge", "Thu,Fri,Sat", "$$$"),
        ("Sour Mouse", "Lower East Side", "sourmousenyc", "bar", "110 Delancey St", "Greek cocktail bar", "Wed,Thu,Fri,Sat", "$$"),
        ("Bar Goto", "Lower East Side", "bargotonyc", "cocktail_bar", "245 Eldridge St", "Japanese cocktail bar", "Wed,Thu,Fri,Sat", "$$$"),
        ("Joyface", "East Village", "joyfacenyc", "bar", "513 E 5th St", "Neighborhood cocktail bar", "Daily", "$$"),
        ("Amor y Amargo", "East Village", "amoryamargo", "cocktail_bar", "443 E 6th St", "Bitters-focused cocktail bar", "Daily", "$$"),
        ("The Wayland", "East Village", "thewaylandnyc", "bar", "700 E 9th St", "Craft cocktails and live music", "Wed,Thu,Fri,Sat", "$$"),
        ("Berlin", "East Village", "berlinnyc", "bar", "25 Ave A", "Underground bar beneath 2A", "Wed,Thu,Fri,Sat", "$"),
        ("Niagara", "East Village", "niagarabar", "bar", "112 Avenue A", "Rock and roll dive bar", "Daily", "$"),
        ("Von", "East Village", "vonbar", "bar", "3 Bleecker St", "Minimalist cocktail bar", "Wed,Thu,Fri,Sat", "$$$"),
        ("THIEF", "Brooklyn", "thiefnyc", "bar", "53 Scott Ave", "Cocktail bar with DJs", "Thu,Fri,Sat", "$$"),
        ("Birdy's", "Brooklyn", "birdysbar", "bar", "474 4th Ave", "Neighborhood bar", "Daily", "$"),
        ("Jupiter Disco", "Bushwick", "jupiterdisco", "nightclub", "1237 Flushing Ave", "Underground dance club", "Fri,Sat", "$$"),
        ("Mood Ring", "Bushwick", "moodringbar", "bar", "1260 Myrtle Ave", "Astrology-themed bar", "Wed,Thu,Fri,Sat", "$$"),
        ("The Keep", "Bushwick", "thekeepny", "bar", "205 Cypress Ave", "Board game bar", "Thu,Fri,Sat", "$$"),
        ("Bossa Nova Civic Club", "Bushwick", "bossanovacivicclub", "nightclub", "1271 Myrtle Ave", "Underground dance club", "Fri,Sat", "$$"),
        ("Good Room", "Brooklyn", "goodroombk", "nightclub", "98 Meserole Ave", "Dance club with great sound system", "Fri,Sat", "$$$"),
        ("Nowadays", "Queens", "nowadaysnyc", "nightclub", "56-06 Cooper Ave", "Outdoor dance venue", "Fri,Sat,Sun", "$$"),
        ("Paragon", "Brooklyn", "paragonbk", "nightclub", "80 Furman St", "Techno and house music venue", "Fri,Sat", "$$"),
        ("TBA Brooklyn", "Williamsburg", "tbabrooklyn", "bar", "395 Wythe Ave", "Bar and music venue", "Thu,Fri,Sat", "$$"),
        ("Sundown", "Brooklyn", "sundownbar", "bar", "355 Flatbush Ave", "Cocktail bar with DJs", "Wed,Thu,Fri,Sat", "$$"),
        ("Lovers Rock", "Brooklyn", "loversrocknyc", "bar", "419 Tompkins Ave", "Reggae and rum bar", "Thu,Fri,Sat", "$$"),
    ]
    
    # Add all original venues
    added = 0
    skipped = 0
    
    for venue_data in original_venues:
        try:
            venue = Venue(
                name=venue_data[0],
                neighborhood=venue_data[1],
                instagram_handle=venue_data[2],
                venue_type=venue_data[3],
                address=venue_data[4],
                description=venue_data[5],
                busy_nights=venue_data[6],
                price_range=venue_data[7]
            )
            result = db.add_venue(venue)
            if result > 0:
                print(f"✅ Added: {venue_data[0]} ({venue_data[1]})")
                added += 1
            else:
                print(f"⏭️  Exists: {venue_data[0]}")
                skipped += 1
        except Exception as e:
            print(f"❌ Error adding {venue_data[0]}: {e}")
            skipped += 1
    
    # Final report
    final_venues = db.get_all_venues()
    print(f"\n📊 Summary:")
    print(f"   Added: {added} original venues")
    print(f"   Skipped: {skipped}")
    print(f"   Total venues now: {len(final_venues)}")

if __name__ == "__main__":
    restore_original_venues()