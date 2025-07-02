#!/usr/bin/env python3
"""
Add more NYC nightlife venues to the database
"""

from venue_db import VenueDatabase, Venue

def add_venues():
    db = VenueDatabase()
    
    # Count existing venues
    existing = db.get_all_venues()
    print(f"Currently have {len(existing)} venues in database")
    
    # Define a comprehensive list of NYC nightlife venues
    new_venues = [
        # Manhattan - East Village
        Venue("Death & Co", "East Village", "deathandcompany", "cocktail_bar", 
              "433 E 6th St", "Award-winning cocktail bar", "Thu,Fri,Sat", "$$$"),
        Venue("Please Don't Tell", "East Village", "pdtnyc", "cocktail_bar",
              "113 St Marks Pl", "Speakeasy accessed through phone booth", "Fri,Sat", "$$$"),
        Venue("The Wayland", "East Village", "thewaylandnyc", "bar",
              "700 E 9th St", "Craft cocktails and live music", "Wed,Thu,Fri,Sat", "$$"),
        Venue("Angel's Share", "East Village", "angelsharenyc", "cocktail_bar",
              "8 Stuyvesant St", "Hidden Japanese cocktail bar", "Thu,Fri,Sat", "$$$"),
        
        # Manhattan - Lower East Side
        Venue("The Box", "Lower East Side", "theboxnyc", "nightclub",
              "189 Chrystie St", "Burlesque and variety shows", "Thu,Fri,Sat", "$$$$"),
        Venue("Pianos", "Lower East Side", "pianosnyc", "live_music_venue",
              "158 Ludlow St", "Live music venue and bar", "Thu,Fri,Sat", "$$"),
        Venue("Mr. Purple", "Lower East Side", "mrpurplenyc", "rooftop_bar",
              "180 Orchard St", "Rooftop bar with city views", "Fri,Sat,Sun", "$$$"),
        Venue("Attaboy", "Lower East Side", "attaboy_ny", "cocktail_bar",
              "134 Eldridge St", "No-menu craft cocktail bar", "Wed,Thu,Fri,Sat", "$$$"),
        
        # Manhattan - West Village
        Venue("Employees Only", "West Village", "employeesonlynyc", "cocktail_bar",
              "510 Hudson St", "Prohibition-style cocktail bar", "Thu,Fri,Sat", "$$$"),
        Venue("Little Branch", "West Village", "littlebranchnyc", "cocktail_bar",
              "20 7th Ave S", "Jazz and cocktails in basement bar", "Mon,Tue,Wed,Thu,Fri,Sat", "$$"),
        Venue("Henrietta Hudson", "West Village", "henriettahudson", "bar",
              "438 Hudson St", "Lesbian bar and dance club", "Thu,Fri,Sat", "$$"),
        Venue("The Django", "West Village", "thedjangonyc", "live_music_venue",
              "2 6th Ave", "Jazz club and cocktail bar", "Wed,Thu,Fri,Sat", "$$$"),
        
        # Manhattan - Chelsea
        Venue("The High Line Hotel Bar", "Chelsea", "highlinehotel", "bar",
              "180 10th Ave", "Refectory bar in former seminary", "Thu,Fri,Sat", "$$$"),
        Venue("Rebar", "Chelsea", "rebarchelsea", "bar",
              "225 W 19th St", "Gay sports bar", "Thu,Fri,Sat", "$$"),
        Venue("Gallow Green", "Chelsea", "gallowgreen", "rooftop_bar",
              "542 W 27th St", "Rooftop garden bar at McKittrick Hotel", "Wed,Thu,Fri,Sat", "$$$"),
        
        # Manhattan - Meatpacking
        Venue("Le Bain", "Meatpacking", "lebainnewyork", "rooftop_bar",
              "848 Washington St", "Rooftop disco and bar with pool", "Thu,Fri,Sat", "$$$$"),
        Venue("PhD Rooftop", "Meatpacking", "phdrooftop", "rooftop_bar",
              "355 W 16th St", "Rooftop lounge at Dream Downtown", "Thu,Fri,Sat", "$$$"),
        Venue("Brass Monkey", "Meatpacking", "brassmonkeynyc", "bar",
              "55 Little W 12th St", "Multi-level bar with roof deck", "Fri,Sat", "$$"),
        
        # Manhattan - SoHo
        Venue("Paul's Casablanca", "SoHo", "paulscasablanca", "cocktail_bar",
              "305 Spring St", "New Orleans-inspired cocktail bar", "Thu,Fri,Sat", "$$"),
        Venue("Pegu Club", "SoHo", "peguclubnyc", "cocktail_bar",
              "77 W Houston St", "Classic cocktail destination", "Wed,Thu,Fri,Sat", "$$$"),
        Venue("Temple Bar", "SoHo", "templebarmanhattan", "cocktail_bar",
              "332 Lafayette St", "Upscale cocktail lounge", "Thu,Fri,Sat", "$$$"),
        
        # Manhattan - Tribeca
        Venue("Ward III", "Tribeca", "wardiii", "cocktail_bar",
              "111 Reade St", "Neighborhood cocktail bar", "Thu,Fri,Sat", "$$"),
        Venue("Weather Up", "Tribeca", "weatheruptribeca", "cocktail_bar",
              "159 Duane St", "Intimate cocktail bar", "Wed,Thu,Fri,Sat", "$$"),
        
        # Manhattan - Midtown
        Venue("Press Lounge", "Midtown", "presslounge", "rooftop_bar",
              "653 11th Ave", "Rooftop bar with Hudson views", "Thu,Fri,Sat", "$$$"),
        Venue("The Campbell", "Midtown", "thecampbellnyc", "cocktail_bar",
              "15 Vanderbilt Ave", "Historic bar in Grand Central", "Wed,Thu,Fri", "$$$"),
        Venue("Rainbow Room", "Midtown", "rainbowroomnyc", "lounge",
              "30 Rockefeller Plaza", "Iconic supper club with views", "Fri,Sat", "$$$$"),
        Venue("Birdland", "Midtown", "birdlandjazz", "live_music_venue",
              "315 W 44th St", "Historic jazz club", "Mon,Tue,Wed,Thu,Fri,Sat,Sun", "$$$"),
        
        # Manhattan - Upper East Side
        Venue("The Penrose", "Upper East Side", "thepenrosenyc", "bar",
              "1590 2nd Ave", "Cork-lined gastropub", "Thu,Fri,Sat", "$$"),
        Venue("Bemelmans Bar", "Upper East Side", "bemelmansbar", "cocktail_bar",
              "35 E 76th St", "Classic piano bar at The Carlyle", "Tue,Wed,Thu,Fri,Sat", "$$$$"),
        Venue("Seamstress", "Upper East Side", "seamstressny", "cocktail_bar",
              "339 E 75th St", "Cocktail bar with secret back room", "Thu,Fri,Sat", "$$$"),
        
        # Brooklyn - Williamsburg
        Venue("Brooklyn Bowl", "Williamsburg", "brooklynbowl", "live_music_venue",
              "61 Wythe Ave", "Bowling, music venue, and restaurant", "Thu,Fri,Sat", "$$"),
        Venue("Output", "Williamsburg", "outputclub", "nightclub",
              "74 Wythe Ave", "Underground dance club", "Fri,Sat", "$$$"),
        Venue("Union Pool", "Williamsburg", "unionpool", "bar",
              "484 Union Ave", "Bar with taco truck and fire pit", "Thu,Fri,Sat", "$$"),
        Venue("Baby's All Right", "Williamsburg", "babysallright", "live_music_venue",
              "146 Broadway", "Music venue and restaurant", "Wed,Thu,Fri,Sat", "$$"),
        Venue("The Ides", "Williamsburg", "theidesbar", "rooftop_bar",
              "80 Wythe Ave", "Rooftop bar at Wythe Hotel", "Thu,Fri,Sat,Sun", "$$$"),
        Venue("Westlight", "Williamsburg", "westlightnyc", "rooftop_bar",
              "111 N 12th St", "22nd floor rooftop bar", "Wed,Thu,Fri,Sat", "$$$"),
        
        # Brooklyn - Bushwick
        Venue("House of Yes", "Bushwick", "houseofyes", "nightclub",
              "2 Wyckoff Ave", "Creative nightclub with themed parties", "Thu,Fri,Sat", "$$"),
        Venue("Mood Ring", "Bushwick", "moodringbar", "bar",
              "1260 Myrtle Ave", "Astrology-themed bar", "Wed,Thu,Fri,Sat", "$$"),
        Venue("The Keep", "Bushwick", "thekeepny", "bar",
              "205 Cypress Ave", "Board game bar", "Thu,Fri,Sat", "$$"),
        Venue("Bossa Nova Civic Club", "Bushwick", "bossanovacivicclub", "nightclub",
              "1271 Myrtle Ave", "Underground dance club", "Fri,Sat", "$$"),
        
        # Brooklyn - Park Slope
        Venue("Union Hall", "Park Slope", "unionhallny", "bar",
              "702 Union St", "Bar with bocce courts", "Thu,Fri,Sat", "$$"),
        Venue("Barbès", "Park Slope", "barbesbrooklyn", "live_music_venue",
              "376 9th St", "World music venue", "Tue,Wed,Thu,Fri,Sat,Sun", "$"),
        
        # Brooklyn - Crown Heights
        Venue("Butter & Scotch", "Crown Heights", "butterandscotch", "bar",
              "818 Franklin Ave", "Dessert bar with cocktails", "Thu,Fri,Sat", "$$"),
        Venue("Friends and Lovers", "Crown Heights", "friendsandlovers", "nightclub",
              "641 Classon Ave", "Dance club and music venue", "Fri,Sat", "$$"),
        
        # Queens - Long Island City
        Venue("Dutch Kills", "Long Island City", "dutchkillsbar", "cocktail_bar",
              "27-24 Jackson Ave", "Craft cocktail bar", "Wed,Thu,Fri,Sat", "$$"),
        Venue("LIC Bar", "Long Island City", "licbar", "dive_bar",
              "45-58 Vernon Blvd", "Dive bar with outdoor space", "Thu,Fri,Sat", "$"),
        
        # Special Events/Organizations
        Venue("Bushwig", "Brooklyn", "bushwig", "events",
              "Various Locations", "Annual drag festival", "September", "$$"),
        Venue("Brooklyn Mirage", "Brooklyn", "brooklynmirage", "events",
              "140 Stewart Ave", "Outdoor electronic music venue", "Fri,Sat,Sun", "$$$"),
        Venue("House of X", "Manhattan", "houseofx", "events",
              "Various Locations", "Queer party collective", "Monthly", "$$"),
        
        # Culture Venues
        Venue("Sleep No More", "Chelsea", "sleepnomorenyc", "culture",
              "530 W 27th St", "Immersive theater experience", "Wed,Thu,Fri,Sat,Sun", "$$$$"),
        Venue("Blue Note", "West Village", "bluenotenyc", "culture",
              "131 W 3rd St", "Legendary jazz club", "Mon,Tue,Wed,Thu,Fri,Sat,Sun", "$$$"),
        Venue("Comedy Cellar", "West Village", "comedycellar", "culture",
              "117 MacDougal St", "Famous comedy club", "Mon,Tue,Wed,Thu,Fri,Sat,Sun", "$$"),
    ]
    
    # Add venues to database
    added_count = 0
    skipped_count = 0
    
    for venue in new_venues:
        result = db.add_venue(venue)
        if result > 0:
            print(f"✅ Added: {venue.name} ({venue.neighborhood})")
            added_count += 1
        else:
            print(f"⏭️  Skipped: {venue.name} (already exists)")
            skipped_count += 1
    
    # Final count
    final_venues = db.get_all_venues()
    print(f"\n📊 Summary:")
    print(f"   Started with: {len(existing)} venues")
    print(f"   Added: {added_count} new venues")
    print(f"   Skipped: {skipped_count} duplicates")
    print(f"   Total now: {len(final_venues)} venues")
    
    # Show distribution
    neighborhoods = {}
    types = {}
    for v in final_venues:
        neighborhoods[v.neighborhood] = neighborhoods.get(v.neighborhood, 0) + 1
        types[v.venue_type] = types.get(v.venue_type, 0) + 1
    
    print(f"\n📍 Venues by neighborhood:")
    for n, count in sorted(neighborhoods.items()):
        print(f"   {n}: {count}")
    
    print(f"\n🎭 Venues by type:")
    for t, count in sorted(types.items()):
        print(f"   {t}: {count}")

if __name__ == "__main__":
    add_venues()