#!/usr/bin/env python3
"""
Complete venue import - check existing and add comprehensive list
"""

import sqlite3

def main():
    # Connect to database
    conn = sqlite3.connect('nightlife.db')
    cursor = conn.cursor()
    
    # Check what's currently in the database
    cursor.execute("SELECT name, neighborhood FROM venues ORDER BY name")
    existing_venues = cursor.fetchall()
    
    print(f"Found {len(existing_venues)} existing venues:")
    for name, neighborhood in existing_venues:
        print(f"  {name} ({neighborhood})")
    
    print("\n" + "="*50)
    print("Adding comprehensive venue list...")
    
    # Complete list of NYC nightlife venues
    all_venues = [
        # Existing venues that should be preserved + new comprehensive list
        
        # Manhattan - East Village
        ("Death & Co", "East Village", "deathandcompany", "cocktail_bar", "433 E 6th St", "Award-winning cocktail bar", "Thu,Fri,Sat", "$$$"),
        ("Please Don't Tell", "East Village", "pdtnyc", "cocktail_bar", "113 St Marks Pl", "Speakeasy accessed through phone booth", "Fri,Sat", "$$$"),
        ("The Wayland", "East Village", "thewaylandnyc", "bar", "700 E 9th St", "Craft cocktails and live music", "Wed,Thu,Fri,Sat", "$$"),
        ("Angel's Share", "East Village", "angelsharenyc", "cocktail_bar", "8 Stuyvesant St", "Hidden Japanese cocktail bar", "Thu,Fri,Sat", "$$$"),
        ("Pyramid Club", "East Village", "pyramidclubnyc", "nightclub", "101 Avenue A", "Legendary punk rock club", "Thu,Fri,Sat", "$$"),
        ("Nowhere Bar", "East Village", "nowherebar", "dive_bar", "322 E 14th St", "Dive bar with pool table", "Daily", "$"),
        
        # Manhattan - Lower East Side
        ("The Box", "Lower East Side", "theboxnyc", "nightclub", "189 Chrystie St", "Burlesque and variety shows", "Thu,Fri,Sat", "$$$$"),
        ("Pianos", "Lower East Side", "pianosnyc", "live_music_venue", "158 Ludlow St", "Live music venue and bar", "Thu,Fri,Sat", "$$"),
        ("Mr. Purple", "Lower East Side", "mrpurplenyc", "rooftop_bar", "180 Orchard St", "Rooftop bar with city views", "Fri,Sat,Sun", "$$$"),
        ("Attaboy", "Lower East Side", "attaboy_ny", "cocktail_bar", "134 Eldridge St", "No-menu craft cocktail bar", "Wed,Thu,Fri,Sat", "$$$"),
        ("Beauty & Essex", "Lower East Side", "beautyandessex", "cocktail_bar", "146 Essex St", "Hidden behind pawn shop", "Thu,Fri,Sat", "$$$"),
        ("The DL", "Lower East Side", "thedlnyc", "rooftop_bar", "95 Delancey St", "Rooftop bar and restaurant", "Thu,Fri,Sat", "$$"),
        
        # Manhattan - West Village
        ("Employees Only", "West Village", "employeesonlynyc", "cocktail_bar", "510 Hudson St", "Prohibition-style cocktail bar", "Thu,Fri,Sat", "$$$"),
        ("Little Branch", "West Village", "littlebranchnyc", "cocktail_bar", "20 7th Ave S", "Jazz and cocktails in basement bar", "Daily", "$$"),
        ("Henrietta Hudson", "West Village", "henriettahudson", "bar", "438 Hudson St", "Lesbian bar and dance club", "Thu,Fri,Sat", "$$"),
        ("The Django", "West Village", "thedjangonyc", "live_music_venue", "2 6th Ave", "Jazz club and cocktail bar", "Wed,Thu,Fri,Sat", "$$$"),
        ("Blue Note", "West Village", "bluenotenyc", "culture", "131 W 3rd St", "Legendary jazz club", "Daily", "$$$"),
        ("Comedy Cellar", "West Village", "comedycellar", "culture", "117 MacDougal St", "Famous comedy club", "Daily", "$$"),
        ("Marie's Crisis", "West Village", "mariescrisis", "bar", "59 Grove St", "Piano bar singalong", "Daily", "$"),
        ("Stonewall Inn", "West Village", "thestonewallinnnyc", "bar", "53 Christopher St", "Historic LGBTQ+ landmark", "Daily", "$$"),
        
        # Manhattan - Chelsea
        ("Gallow Green", "Chelsea", "gallowgreen", "rooftop_bar", "542 W 27th St", "Rooftop garden bar at McKittrick Hotel", "Wed,Thu,Fri,Sat", "$$$"),
        ("The High Line Hotel Bar", "Chelsea", "highlinehotel", "bar", "180 10th Ave", "Refectory bar in former seminary", "Thu,Fri,Sat", "$$$"),
        ("Rebar", "Chelsea", "rebarchelsea", "bar", "225 W 19th St", "Gay sports bar", "Thu,Fri,Sat", "$$"),
        ("Sleep No More", "Chelsea", "sleepnomorenyc", "culture", "530 W 27th St", "Immersive theater experience", "Wed,Thu,Fri,Sat,Sun", "$$$$"),
        ("House of Yes Chelsea", "Chelsea", "houseofyeschelsea", "events", "Various Locations", "Pop-up events in Chelsea", "Weekends", "$$"),
        
        # Manhattan - Meatpacking District
        ("Le Bain", "Meatpacking", "lebainnewyork", "rooftop_bar", "848 Washington St", "Rooftop disco and bar with pool", "Thu,Fri,Sat", "$$$$"),
        ("PhD Rooftop", "Meatpacking", "phdrooftop", "rooftop_bar", "355 W 16th St", "Rooftop lounge at Dream Downtown", "Thu,Fri,Sat", "$$$"),
        ("Brass Monkey", "Meatpacking", "brassmonkeynyc", "bar", "55 Little W 12th St", "Multi-level bar with roof deck", "Fri,Sat", "$$"),
        ("The Top of the Standard", "Meatpacking", "standardhotels", "rooftop_bar", "848 Washington St", "18th floor rooftop bar", "Thu,Fri,Sat", "$$$$"),
        
        # Manhattan - SoHo
        ("Paul's Casablanca", "SoHo", "paulscasablanca", "cocktail_bar", "305 Spring St", "New Orleans-inspired cocktail bar", "Thu,Fri,Sat", "$$"),
        ("Pegu Club", "SoHo", "peguclubnyc", "cocktail_bar", "77 W Houston St", "Classic cocktail destination", "Wed,Thu,Fri,Sat", "$$$"),
        ("Temple Bar", "SoHo", "templebarmanhattan", "cocktail_bar", "332 Lafayette St", "Upscale cocktail lounge", "Thu,Fri,Sat", "$$$"),
        ("Fanelli Cafe", "SoHo", "fanellicafe", "bar", "94 Prince St", "Historic tavern since 1922", "Daily", "$$"),
        
        # Manhattan - Tribeca
        ("Ward III", "Tribeca", "wardiii", "cocktail_bar", "111 Reade St", "Neighborhood cocktail bar", "Thu,Fri,Sat", "$$"),
        ("Weather Up", "Tribeca", "weatheruptribeca", "cocktail_bar", "159 Duane St", "Intimate cocktail bar", "Wed,Thu,Fri,Sat", "$$"),
        ("The Brandy Library", "Tribeca", "brandylibrary", "cocktail_bar", "25 N Moore St", "Brown spirits specialist", "Wed,Thu,Fri,Sat", "$$$"),
        
        # Manhattan - Midtown
        ("Press Lounge", "Midtown", "presslounge", "rooftop_bar", "653 11th Ave", "Rooftop bar with Hudson views", "Thu,Fri,Sat", "$$$"),
        ("The Campbell", "Midtown", "thecampbellnyc", "cocktail_bar", "15 Vanderbilt Ave", "Historic bar in Grand Central", "Wed,Thu,Fri", "$$$"),
        ("Rainbow Room", "Midtown", "rainbowroomnyc", "lounge", "30 Rockefeller Plaza", "Iconic supper club with views", "Fri,Sat", "$$$$"),
        ("Birdland", "Midtown", "birdlandjazz", "live_music_venue", "315 W 44th St", "Historic jazz club", "Daily", "$$$"),
        ("230 Fifth", "Midtown", "230fifth", "rooftop_bar", "230 5th Ave", "Rooftop bar with Empire State views", "Thu,Fri,Sat", "$$"),
        ("The Gansevoort", "Midtown", "gansevoortpark", "rooftop_bar", "2 9th Ave", "Rooftop bar and pool", "Thu,Fri,Sat,Sun", "$$$"),
        
        # Manhattan - Upper East Side
        ("The Penrose", "Upper East Side", "thepenrosenyc", "bar", "1590 2nd Ave", "Cork-lined gastropub", "Thu,Fri,Sat", "$$"),
        ("Bemelmans Bar", "Upper East Side", "bemelmansbar", "cocktail_bar", "35 E 76th St", "Classic piano bar at The Carlyle", "Tue,Wed,Thu,Fri,Sat", "$$$$"),
        ("Seamstress", "Upper East Side", "seamstressny", "cocktail_bar", "339 E 75th St", "Cocktail bar with secret back room", "Thu,Fri,Sat", "$$$"),
        ("Iguana", "Upper East Side", "iguananyc", "bar", "240 E 54th St", "Mexican cantina and bar", "Thu,Fri,Sat", "$$"),
        
        # Manhattan - Upper West Side
        ("Dead Poet", "Upper West Side", "deadpoetbar", "bar", "450 Amsterdam Ave", "Literary-themed bar", "Thu,Fri,Sat", "$$"),
        ("Prohibition", "Upper West Side", "prohibitionbar", "cocktail_bar", "503 Columbus Ave", "Speakeasy-style cocktail bar", "Wed,Thu,Fri,Sat", "$$"),
        
        # Manhattan - Harlem
        ("Ginny's Supper Club", "Harlem", "ginnysupperclub", "live_music_venue", "310 Lenox Ave", "Supper club with live music", "Thu,Fri,Sat", "$$$"),
        ("67 Orange Street", "Harlem", "67orangestreet", "bar", "2082 Frederick Douglass Blvd", "Cocktail bar and restaurant", "Thu,Fri,Sat", "$$"),
        
        # Brooklyn - Williamsburg
        ("Brooklyn Bowl", "Williamsburg", "brooklynbowl", "live_music_venue", "61 Wythe Ave", "Bowling, music venue, and restaurant", "Thu,Fri,Sat", "$$"),
        ("Output", "Williamsburg", "outputclub", "nightclub", "74 Wythe Ave", "Underground dance club", "Fri,Sat", "$$$"),
        ("Union Pool", "Williamsburg", "unionpool", "bar", "484 Union Ave", "Bar with taco truck and fire pit", "Thu,Fri,Sat", "$$"),
        ("Baby's All Right", "Williamsburg", "babysallright", "live_music_venue", "146 Broadway", "Music venue and restaurant", "Wed,Thu,Fri,Sat", "$$"),
        ("The Ides", "Williamsburg", "theidesbar", "rooftop_bar", "80 Wythe Ave", "Rooftop bar at Wythe Hotel", "Thu,Fri,Sat,Sun", "$$$"),
        ("Westlight", "Williamsburg", "westlightnyc", "rooftop_bar", "111 N 12th St", "22nd floor rooftop bar", "Wed,Thu,Fri,Sat", "$$$"),
        ("House of Yes", "Williamsburg", "houseofyes", "nightclub", "2 Wyckoff Ave", "Creative nightclub with themed parties", "Thu,Fri,Sat", "$$"),
        ("Macri Park", "Williamsburg", "macripark", "bar", "462 Union Ave", "Italian-American bar", "Thu,Fri,Sat", "$$"),
        
        # Brooklyn - Bushwick
        ("Mood Ring", "Bushwick", "moodringbar", "bar", "1260 Myrtle Ave", "Astrology-themed bar", "Wed,Thu,Fri,Sat", "$$"),
        ("The Keep", "Bushwick", "thekeepny", "bar", "205 Cypress Ave", "Board game bar", "Thu,Fri,Sat", "$$"),
        ("Bossa Nova Civic Club", "Bushwick", "bossanovacivicclub", "nightclub", "1271 Myrtle Ave", "Underground dance club", "Fri,Sat", "$$"),
        ("Alphaville", "Bushwick", "alphavillecinema", "bar", "1168 Myrtle Ave", "Video bar and cinema", "Wed,Thu,Fri,Sat", "$"),
        ("The Johnson's", "Bushwick", "thejohnsonsnyc", "dive_bar", "931 Bushwick Ave", "Dive bar with live music", "Thu,Fri,Sat", "$"),
        
        # Brooklyn - Park Slope
        ("Union Hall", "Park Slope", "unionhallny", "bar", "702 Union St", "Bar with bocce courts", "Thu,Fri,Sat", "$$"),
        ("Barbès", "Park Slope", "barbesbrooklyn", "live_music_venue", "376 9th St", "World music venue", "Daily", "$"),
        ("The Bell House", "Park Slope", "thebellhouseny", "live_music_venue", "149 7th St", "Music venue and event space", "Thu,Fri,Sat", "$$"),
        
        # Brooklyn - Crown Heights
        ("Butter & Scotch", "Crown Heights", "butterandscotch", "bar", "818 Franklin Ave", "Dessert bar with cocktails", "Thu,Fri,Sat", "$$"),
        ("Friends and Lovers", "Crown Heights", "friendsandlovers", "nightclub", "641 Classon Ave", "Dance club and music venue", "Fri,Sat", "$$"),
        ("Franklin Park", "Crown Heights", "franklinparkbar", "bar", "618 St Johns Pl", "Beer garden and bar", "Thu,Fri,Sat", "$$"),
        
        # Brooklyn - DUMBO
        ("1 Rooftop", "DUMBO", "1rooftopnyc", "rooftop_bar", "1 Hotel Brooklyn Bridge", "Rooftop bar with bridge views", "Thu,Fri,Sat,Sun", "$$$"),
        ("Time Out Market", "DUMBO", "timeoutmarket", "misc", "55 Water St", "Food hall with bars", "Daily", "$$"),
        
        # Queens - Long Island City
        ("Dutch Kills", "Long Island City", "dutchkillsbar", "cocktail_bar", "27-24 Jackson Ave", "Craft cocktail bar", "Wed,Thu,Fri,Sat", "$$"),
        ("LIC Bar", "Long Island City", "licbar", "dive_bar", "45-58 Vernon Blvd", "Dive bar with outdoor space", "Thu,Fri,Sat", "$"),
        ("Anable Basin Sailing Bar", "Long Island City", "anablebasin", "bar", "4-40 44th Dr", "Waterfront bar", "Thu,Fri,Sat,Sun", "$$"),
        
        # Queens - Astoria
        ("Bohemian Hall & Beer Garden", "Astoria", "bohemianhall", "bar", "29-19 24th Ave", "Historic Czech beer garden", "Thu,Fri,Sat,Sun", "$$"),
        ("The Wolfhound", "Astoria", "wolfhoundnyc", "bar", "33-35 E 27th St", "Irish pub", "Thu,Fri,Sat", "$$"),
        
        # Events and Organizations
        ("Bushwig", "Brooklyn", "bushwig", "events", "Various Locations", "Annual drag festival", "September", "$$"),
        ("Brooklyn Mirage", "Brooklyn", "brooklynmirage", "events", "140 Stewart Ave", "Outdoor electronic music venue", "Fri,Sat,Sun", "$$$"),
        ("House of X", "Manhattan", "houseofx", "events", "Various Locations", "Queer party collective", "Monthly", "$$"),
        ("Nowadays", "Queens", "nowadaysnyc", "events", "56-06 Cooper Ave", "Outdoor dance music venue", "Fri,Sat,Sun", "$$"),
        ("The Great Hall at Avant Gardner", "Brooklyn", "avantgardner", "events", "140 Stewart Ave", "Large-scale music events", "Weekends", "$$$"),
        
        # Dive Bars and Miscellaneous
        ("Lucy's", "Lower East Side", "lucysnyc", "dive_bar", "135 Avenue A", "Classic dive bar", "Daily", "$"),
        ("Milano's", "SoHo", "milanosnyc", "dive_bar", "51 E Houston St", "Old-school dive bar", "Daily", "$"),
        ("Rudy's Bar & Grill", "Midtown", "rudysbar", "dive_bar", "627 9th Ave", "Free hot dogs dive bar", "Daily", "$"),
        ("The Patriot Saloon", "Tribeca", "patriotsaloon", "dive_bar", "110 Chambers St", "Biker bar", "Daily", "$"),
    ]
    
    # Insert all venues
    added = 0
    skipped = 0
    
    for venue in all_venues:
        try:
            cursor.execute("""
                INSERT INTO venues (name, neighborhood, instagram_handle, venue_type, address, description, busy_nights, price_range)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, venue)
            added += 1
            print(f"✅ Added: {venue[0]} ({venue[1]})")
        except sqlite3.IntegrityError:
            skipped += 1
            print(f"⏭️  Exists: {venue[0]} ({venue[1]})")
    
    # Commit changes
    conn.commit()
    
    # Final statistics
    cursor.execute("SELECT COUNT(*) FROM venues")
    final_count = cursor.fetchone()[0]
    
    print(f"\n" + "="*50)
    print(f"📊 Import Summary:")
    print(f"   Started with: {len(existing_venues)} venues")
    print(f"   Added: {added} new venues")
    print(f"   Skipped: {skipped} existing venues")
    print(f"   Total now: {final_count} venues")
    
    # Show distribution by neighborhood
    cursor.execute("SELECT neighborhood, COUNT(*) FROM venues GROUP BY neighborhood ORDER BY COUNT(*) DESC")
    neighborhoods = cursor.fetchall()
    
    print(f"\n📍 Venues by neighborhood:")
    for neighborhood, count in neighborhoods:
        print(f"   {neighborhood}: {count}")
    
    # Show distribution by type
    cursor.execute("SELECT venue_type, COUNT(*) FROM venues GROUP BY venue_type ORDER BY COUNT(*) DESC")
    types = cursor.fetchall()
    
    print(f"\n🎭 Venues by type:")
    for venue_type, count in types:
        print(f"   {venue_type}: {count}")
    
    conn.close()
    print(f"\n✨ Database update complete!")

if __name__ == "__main__":
    main()