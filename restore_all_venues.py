#!/usr/bin/env python3
"""
Restore ALL venues including the original ones
"""

from venue_db import VenueDatabase, Venue

def restore_all_venues():
    db = VenueDatabase()
    
    # Check current status
    current_venues = db.get_all_venues()
    print(f"Currently have {len(current_venues)} venues")
    
    # ALL venues - original + new
    all_venues = [
        # Original venues from your database
        ("House of Yes", "Bushwick", "houseofyes", "nightclub", "2 Wyckoff Ave", "Creative nightclub with circus performances", "Thu,Fri,Sat", "$$"),
        ("Nowadays", "Queens", "nowadaysnyc", "nightclub", "56-06 Cooper Ave", "Outdoor dance venue", "Fri,Sat,Sun", "$$"),
        ("The Keep", "Queens", "thekeepny", "bar", None, "Gaming bar with vintage arcade", "Thu,Fri,Sat", "$$"),
        ("Jupiter Disco", "Bushwick", "jupiterdisco", "nightclub", None, "Underground dance club", "Fri,Sat", "$$"),
        ("Good Room", "Brooklyn", "goodroombk", "nightclub", None, "Dance club with great sound system", "Fri,Sat", "$$$"),
        ("Paragon", "Brooklyn", "paragonbk", "nightclub", None, "Techno and house music venue", "Fri,Sat", "$$"),
        ("Bossa Nova Civic Club", "Bushwick", "bossanovacivicclub", "nightclub", "1271 Myrtle Ave", "Underground dance spot", "Fri,Sat", "$$"),
        ("Market Hotel", "Bushwick", "markethotel", "live_music_venue", None, "DIY music venue", "Thu,Fri,Sat", "$$"),
        ("Trans-Pecos", "Queens", "transpecos", "live_music_venue", None, "Experimental music venue", "Thu,Fri,Sat", "$"),
        ("Mood Ring", "Bushwick", "moodringbar", "bar", "1260 Myrtle Ave", "Astrology-themed bar", "Wed,Thu,Fri,Sat", "$$"),
        ("The Johnsons", "Bushwick", "thejohnsonsnyc", "dive_bar", None, "No-frills dive bar", "Daily", "$"),
        ("Alphaville", "Bushwick", "alphavillenyc", "bar", None, "Video bar and venue", "Wed,Thu,Fri,Sat", "$"),
        ("Lovers Rock", "Brooklyn", "loversrocknyc", "bar", None, "Reggae and rum bar", "Thu,Fri,Sat", "$$"),
        ("Friends and Lovers", "Crown Heights", "friendsandlovers", "nightclub", "641 Classon Ave", "Hip-hop and dance venue", "Fri,Sat", "$$"),
        ("C'mon Everybody", "Brooklyn", "cmoneverybody", "live_music_venue", None, "Music venue and bar", "Wed,Thu,Fri,Sat", "$$"),
        ("The Sultan Room", "Bushwick", "thesultanroom", "live_music_venue", None, "Music venue with rooftop", "Thu,Fri,Sat", "$$"),
        ("Elsewhere", "Bushwick", "elsewherespace", "nightclub", "599 Johnson Ave", "Multi-room music venue", "Thu,Fri,Sat", "$$$"),
        ("Avant Gardner", "Brooklyn", "avantgardner", "nightclub", "140 Stewart Ave", "Large electronic music complex", "Fri,Sat", "$$$"),
        ("Brooklyn Mirage", "Brooklyn", "brooklynmirage", "nightclub", "140 Stewart Ave", "Outdoor electronic music venue", "Fri,Sat,Sun", "$$$"),
        ("Public Records", "Brooklyn", "publicrecords", "nightclub", None, "Hi-fi listening bar and venue", "Thu,Fri,Sat", "$$"),
        ("Baby's All Right", "Williamsburg", "babysallright", "live_music_venue", "146 Broadway", "Music venue and restaurant", "Wed,Thu,Fri,Sat", "$$"),
        ("Music Hall of Williamsburg", "Williamsburg", "musichallofwilliamsburg", "live_music_venue", None, "Popular concert venue", "Varies", "$$"),
        ("Brooklyn Bowl", "Williamsburg", "brooklynbowl", "live_music_venue", "61 Wythe Ave", "Bowling, music, and food", "Thu,Fri,Sat", "$$"),
        ("Union Pool", "Williamsburg", "unionpool", "bar", "484 Union Ave", "Bar with taco truck", "Thu,Fri,Sat", "$$"),
        ("The Ides", "Williamsburg", "theidesbar", "rooftop_bar", "80 Wythe Ave", "Wythe Hotel rooftop bar", "Thu,Fri,Sat,Sun", "$$$"),
        ("Westlight", "Williamsburg", "westlightnyc", "rooftop_bar", "111 N 12th St", "22nd floor rooftop bar", "Wed,Thu,Fri,Sat", "$$$"),
        ("Output", "Williamsburg", "outputclub", "nightclub", "74 Wythe Ave", "Underground dance club", "Fri,Sat", "$$$"),
        ("Schimanski", "Williamsburg", "schimanski", "nightclub", None, "Electronic music venue", "Fri,Sat", "$$$"),
        ("Black Flamingo", "Williamsburg", "blackflamingobk", "nightclub", None, "Plant-based club", "Fri,Sat", "$$"),
        ("Night of Joy", "Williamsburg", "nightofjoybk", "bar", None, "Dive bar with DJs", "Thu,Fri,Sat", "$"),
        ("Donna", "Williamsburg", "donnabk", "bar", None, "Cocktail bar", "Wed,Thu,Fri,Sat", "$$"),
        ("The Diamond", "Brooklyn", "thediamondbrooklyn", "bar", None, "Neighborhood bar", "Daily", "$"),
        ("Pine Box Rock Shop", "Bushwick", "pineboxrockshop", "bar", None, "Rock bar in former casket factory", "Daily", "$"),
        ("The Well", "Bushwick", "thewellbrooklyn", "bar", None, "Beer bar with backyard", "Daily", "$$"),
        ("Syndicated", "Bushwick", "syndicatedbk", "bar", None, "Bar theater with food", "Wed,Thu,Fri,Sat,Sun", "$$"),
        ("House of Wax", "Brooklyn", "houseofwaxbar", "bar", None, "Cocktail and record bar", "Thu,Fri,Sat", "$$"),
        ("Do or Dive", "Brooklyn", "doordivebk", "dive_bar", None, "Classic dive bar", "Daily", "$"),
        ("Skinny Dennis", "Williamsburg", "skinnydennis", "bar", None, "Honky tonk bar", "Daily", "$"),
        ("Rocka Rolla", "Brooklyn", "rockarollanyc", "bar", None, "Rock and metal bar", "Daily", "$"),
        ("Saint Vitus", "Brooklyn", "saintvitusbar", "live_music_venue", None, "Metal venue", "Varies", "$$"),
        ("Knitting Factory", "Brooklyn", "knittingfactory", "live_music_venue", None, "Multi-genre music venue", "Varies", "$$"),
        ("Brooklyn Steel", "Brooklyn", "brooklynsteel", "live_music_venue", None, "Large concert venue", "Varies", "$$$"),
        ("Warsaw", "Brooklyn", "warsawconcerts", "live_music_venue", None, "Polish venue for concerts", "Varies", "$$"),
        ("Kings Theatre", "Brooklyn", "kingstheatre", "live_music_venue", None, "Historic theater venue", "Varies", "$$$"),
        ("Rough Trade", "Williamsburg", "roughtradenyc", "live_music_venue", None, "Record store and venue", "Varies", "$$"),
        ("Pete's Candy Store", "Williamsburg", "petescandystore", "bar", None, "Bar with live music", "Daily", "$"),
        ("The Gutter", "Williamsburg", "thegutterbowling", "bar", None, "Bowling alley bar", "Daily", "$$"),
        ("Brooklyn Bazaar", "Brooklyn", "brooklynbazaar", "live_music_venue", None, "Music, food, and games", "Thu,Fri,Sat", "$$"),
        
        # Manhattan venues to add
        ("Death & Co", "East Village", "deathandcompany", "cocktail_bar", "433 E 6th St", "Award-winning cocktail bar", "Thu,Fri,Sat", "$$$"),
        ("Please Don't Tell", "East Village", "pdtnyc", "cocktail_bar", "113 St Marks Pl", "Speakeasy through phone booth", "Fri,Sat", "$$$"),
        ("The Box", "Lower East Side", "theboxnyc", "nightclub", "189 Chrystie St", "Burlesque and variety shows", "Thu,Fri,Sat", "$$$$"),
        ("Mr. Purple", "Lower East Side", "mrpurplenyc", "rooftop_bar", "180 Orchard St", "Rooftop bar with city views", "Fri,Sat,Sun", "$$$"),
        ("Beauty & Essex", "Lower East Side", "beautyandessex", "cocktail_bar", "146 Essex St", "Hidden behind pawn shop", "Thu,Fri,Sat", "$$$"),
        ("Employees Only", "West Village", "employeesonlynyc", "cocktail_bar", "510 Hudson St", "Prohibition-style cocktail bar", "Thu,Fri,Sat", "$$$"),
        ("The Django", "West Village", "thedjangonyc", "live_music_venue", "2 6th Ave", "Jazz club and cocktail bar", "Wed,Thu,Fri,Sat", "$$$"),
        ("Blue Note", "West Village", "bluenotenyc", "culture", "131 W 3rd St", "Legendary jazz club", "Daily", "$$$"),
        ("Comedy Cellar", "West Village", "comedycellar", "culture", "117 MacDougal St", "Famous comedy club", "Daily", "$$"),
        ("Le Bain", "Meatpacking", "lebainnewyork", "rooftop_bar", "848 Washington St", "Rooftop disco with pool", "Thu,Fri,Sat", "$$$$"),
        ("Gallow Green", "Chelsea", "gallowgreen", "rooftop_bar", "542 W 27th St", "Rooftop garden bar", "Wed,Thu,Fri,Sat", "$$$"),
        ("Sleep No More", "Chelsea", "sleepnomorenyc", "culture", "530 W 27th St", "Immersive theater experience", "Wed,Thu,Fri,Sat,Sun", "$$$$"),
        ("Rainbow Room", "Midtown", "rainbowroomnyc", "lounge", "30 Rockefeller Plaza", "Iconic supper club", "Fri,Sat", "$$$$"),
        ("Birdland", "Midtown", "birdlandjazz", "live_music_venue", "315 W 44th St", "Historic jazz club", "Daily", "$$$"),
        ("Bemelmans Bar", "Upper East Side", "bemelmansbar", "cocktail_bar", "35 E 76th St", "Classic piano bar", "Tue-Sat", "$$$$"),
        ("Little Branch", "West Village", "littlebranchnyc", "cocktail_bar", "20 7th Ave S", "Jazz and cocktails", "Daily", "$$"),
        ("Attaboy", "Lower East Side", "attaboy_ny", "cocktail_bar", "134 Eldridge St", "No-menu craft cocktails", "Wed-Sat", "$$$"),
        
        # Additional Brooklyn venues
        ("Union Hall", "Park Slope", "unionhallny", "bar", "702 Union St", "Bar with bocce courts", "Thu,Fri,Sat", "$$"),
        ("Barbès", "Park Slope", "barbesbrooklyn", "live_music_venue", "376 9th St", "World music venue", "Daily", "$"),
        ("Butter & Scotch", "Crown Heights", "butterandscotch", "bar", "818 Franklin Ave", "Dessert bar with cocktails", "Thu,Fri,Sat", "$$"),
        
        # Queens venues
        ("Dutch Kills", "Long Island City", "dutchkillsbar", "cocktail_bar", "27-24 Jackson Ave", "Craft cocktail bar", "Wed-Sat", "$$"),
        ("LIC Bar", "Long Island City", "licbar", "dive_bar", "45-58 Vernon Blvd", "Dive bar with outdoor space", "Thu,Fri,Sat", "$"),
        
        # Special events/organizations
        ("Bushwig", "Brooklyn", "bushwig", "events", "Various Locations", "Annual drag festival", "September", "$$"),
        ("House of X", "Manhattan", "houseofx", "events", "Various Locations", "Queer party collective", "Monthly", "$$"),
    ]
    
    # Add all venues
    added = 0
    skipped = 0
    
    for venue_data in all_venues:
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
                skipped += 1
        except Exception as e:
            print(f"❌ Error adding {venue_data[0]}: {e}")
            skipped += 1
    
    # Final report
    final_venues = db.get_all_venues()
    print(f"\n📊 Summary:")
    print(f"   Started with: {len(current_venues)} venues")
    print(f"   Added: {added} new venues")
    print(f"   Skipped: {skipped} (already exist)")
    print(f"   Total now: {len(final_venues)} venues")
    
    # Show neighborhood distribution
    neighborhoods = {}
    for v in final_venues:
        neighborhoods[v.neighborhood] = neighborhoods.get(v.neighborhood, 0) + 1
    
    print(f"\n📍 Venues by neighborhood:")
    for n, count in sorted(neighborhoods.items(), key=lambda x: x[1], reverse=True):
        print(f"   {n}: {count}")

if __name__ == "__main__":
    restore_all_venues()