from typing import Dict, List, Optional, Any
from datetime import datetime
import re
import json
from urllib.parse import quote
from fastapi import Request

class SEOHelper:
    """SEO utilities and helpers for Atlas-NYC"""
    
    BASE_URL = "https://atlas-nyc.com"  # Update with actual domain
    SITE_NAME = "Atlas-NYC"
    TAGLINE = "Discover NYC's Hottest Nightlife Scene"
    
    @staticmethod
    def clean_text_for_seo(text: str) -> str:
        """Clean text for SEO-friendly URLs and meta descriptions"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove special characters for URLs
        text = re.sub(r'[^\w\s-]', '', text)
        # Replace spaces with hyphens
        text = re.sub(r'\s+', '-', text.strip())
        # Convert to lowercase
        return text.lower()
    
    @staticmethod
    def generate_meta_title(page_type: str, entity_name: str = None, neighborhood: str = None) -> str:
        """Generate SEO-optimized meta titles"""
        base_title = f"{SEOHelper.SITE_NAME} - {SEOHelper.TAGLINE}"
        
        if page_type == "home":
            return f"{SEOHelper.SITE_NAME} - {SEOHelper.TAGLINE} | NYC Nightlife Guide"
        
        elif page_type == "venue":
            if neighborhood:
                return f"{entity_name} - {neighborhood} NYC Nightlife | {SEOHelper.SITE_NAME}"
            return f"{entity_name} - NYC Nightlife Venue | {SEOHelper.SITE_NAME}"
        
        elif page_type == "neighborhood":
            return f"{entity_name} Nightlife Guide - Best Bars & Clubs | {SEOHelper.SITE_NAME}"
        
        elif page_type == "venues":
            return f"NYC Nightlife Venues - Bars, Clubs & Lounges | {SEOHelper.SITE_NAME}"
        
        elif page_type == "content":
            return f"Latest NYC Nightlife Updates | {SEOHelper.SITE_NAME}"
        
        return base_title
    
    @staticmethod
    def generate_meta_description(page_type: str, entity_data: Dict = None) -> str:
        """Generate SEO-optimized meta descriptions"""
        
        if page_type == "home":
            return ("Discover NYC's hottest nightlife with Atlas-NYC. Find the best bars, clubs, "
                   "lounges and events across Manhattan, Brooklyn, Queens and the Bronx. "
                   "Real-time updates and insider tips.")
        
        elif page_type == "venue" and entity_data:
            venue = entity_data
            desc = f"Experience {venue.get('name', 'this venue')} in {venue.get('neighborhood', 'NYC')}"
            if venue.get('venue_type'):
                desc += f" - a premier {venue.get('venue_type')} in NYC's nightlife scene"
            if venue.get('description'):
                # Truncate description to fit within meta description limits
                short_desc = venue['description'][:100] + "..." if len(venue['description']) > 100 else venue['description']
                desc += f". {short_desc}"
            desc += f" | {SEOHelper.SITE_NAME}"
            return desc
        
        elif page_type == "neighborhood" and entity_data:
            neighborhood = entity_data.get('name', 'NYC')
            return (f"Explore {neighborhood}'s vibrant nightlife scene. Discover the best bars, "
                   f"clubs, and entertainment venues in {neighborhood}, NYC. "
                   f"Updated daily with the latest hotspots | {SEOHelper.SITE_NAME}")
        
        elif page_type == "venues":
            return ("Browse NYC's complete nightlife directory. Find bars, clubs, lounges, and "
                   "rooftop venues across all neighborhoods. Filter by type, location, and vibe "
                   f"to discover your perfect night out | {SEOHelper.SITE_NAME}")
        
        elif page_type == "content":
            return ("Stay updated with NYC's latest nightlife content. Live updates, events, "
                   "stories and insider tips from the city's hottest venues. "
                   f"Real-time nightlife intelligence | {SEOHelper.SITE_NAME}")
        
        return f"NYC Nightlife Guide | {SEOHelper.SITE_NAME}"
    
    @staticmethod
    def generate_venue_slug(venue_name: str, venue_id: int) -> str:
        """Generate SEO-friendly venue URL slug"""
        clean_name = SEOHelper.clean_text_for_seo(venue_name)
        return f"{clean_name}-{venue_id}"
    
    @staticmethod
    def generate_canonical_url(request: Request, path_override: str = None) -> str:
        """Generate canonical URL for the page"""
        if path_override:
            return f"{SEOHelper.BASE_URL}{path_override}"
        
        # Remove query parameters for canonical URL
        path = str(request.url.path)
        return f"{SEOHelper.BASE_URL}{path}"
    
    @staticmethod
    def generate_venue_structured_data(venue: Dict) -> Dict:
        """Generate JSON-LD structured data for venues"""
        structured_data = {
            "@context": "https://schema.org",
            "@type": "NightClub" if venue.get('venue_type') == 'club' else "BarOrPub",
            "name": venue.get('name'),
            "description": venue.get('description', f"Experience {venue.get('name')} - a premier nightlife destination in {venue.get('neighborhood', 'NYC')}"),
            "url": f"{SEOHelper.BASE_URL}/venues/{SEOHelper.generate_venue_slug(venue.get('name', ''), venue.get('id', 0))}",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": venue.get('neighborhood', 'New York'),
                "addressRegion": "NY",
                "addressCountry": "US"
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": venue.get('latitude', 40.7589),  # Default to NYC
                "longitude": venue.get('longitude', -73.9851)
            },
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": "4.5",  # Default rating - update with real data
                "reviewCount": "50"    # Default count - update with real data
            },
            "priceRange": venue.get('price_range', '$$'),
            "servesCuisine": "American",  # Default - customize per venue
            "hasMenu": f"{SEOHelper.BASE_URL}/venues/{SEOHelper.generate_venue_slug(venue.get('name', ''), venue.get('id', 0))}/menu"
        }
        
        # Add address if available
        if venue.get('address'):
            structured_data["address"]["streetAddress"] = venue['address']
        
        # Add social media if available
        if venue.get('instagram_handle'):
            structured_data["sameAs"] = [f"https://instagram.com/{venue['instagram_handle']}"]
        
        # Add image if available
        if venue.get('photo'):
            structured_data["image"] = f"{SEOHelper.BASE_URL}/uploads/{venue['photo']}"
        
        return structured_data
    
    @staticmethod
    def generate_organization_structured_data() -> Dict:
        """Generate JSON-LD structured data for Atlas-NYC organization"""
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": SEOHelper.SITE_NAME,
            "url": SEOHelper.BASE_URL,
            "description": "NYC's premier nightlife discovery platform",
            "logo": f"{SEOHelper.BASE_URL}/static/logo.png",
            "contactPoint": {
                "@type": "ContactPoint",
                "contactType": "customer service",
                "url": f"{SEOHelper.BASE_URL}/contact"
            },
            "sameAs": [
                "https://twitter.com/atlasnyc",
                "https://instagram.com/atlasnyc",
                "https://facebook.com/atlasnyc"
            ],
            "areaServed": {
                "@type": "City",
                "name": "New York",
                "sameAs": "https://en.wikipedia.org/wiki/New_York_City"
            }
        }
    
    @staticmethod
    def generate_breadcrumb_structured_data(breadcrumbs: List[Dict]) -> Dict:
        """Generate JSON-LD structured data for breadcrumbs"""
        items = []
        for i, crumb in enumerate(breadcrumbs, 1):
            items.append({
                "@type": "ListItem",
                "position": i,
                "name": crumb['name'],
                "item": f"{SEOHelper.BASE_URL}{crumb['url']}"
            })
        
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": items
        }
    
    @staticmethod
    def generate_open_graph_tags(page_type: str, title: str, description: str, 
                                url: str, image: str = None, entity_data: Dict = None) -> Dict:
        """Generate Open Graph meta tags"""
        
        og_tags = {
            "og:site_name": SEOHelper.SITE_NAME,
            "og:type": "website",
            "og:title": title,
            "og:description": description,
            "og:url": url,
            "og:image": image or f"{SEOHelper.BASE_URL}/static/og-default.jpg",
            "og:image:width": "1200",
            "og:image:height": "630",
            "og:locale": "en_US"
        }
        
        # Add Twitter Card tags
        twitter_tags = {
            "twitter:card": "summary_large_image",
            "twitter:site": "@atlasnyc",
            "twitter:title": title,
            "twitter:description": description,
            "twitter:image": og_tags["og:image"]
        }
        
        # Venue-specific Open Graph
        if page_type == "venue" and entity_data:
            og_tags["og:type"] = "business.business"
            if entity_data.get('address'):
                og_tags["business:contact_data:street_address"] = entity_data['address']
                og_tags["business:contact_data:locality"] = entity_data.get('neighborhood', 'New York')
                og_tags["business:contact_data:region"] = "NY"
                og_tags["business:contact_data:country_name"] = "USA"
        
        return {**og_tags, **twitter_tags}
    
    @staticmethod
    def generate_keywords(page_type: str, entity_data: Dict = None) -> str:
        """Generate meta keywords for the page"""
        base_keywords = [
            "NYC nightlife", "New York bars", "NYC clubs", "Manhattan nightlife",
            "Brooklyn bars", "NYC entertainment", "nightlife guide", "Atlas-NYC"
        ]
        
        if page_type == "venue" and entity_data:
            venue_keywords = [
                entity_data.get('name', ''),
                entity_data.get('neighborhood', ''),
                entity_data.get('venue_type', ''),
                f"{entity_data.get('neighborhood', '')} {entity_data.get('venue_type', '')}",
                f"NYC {entity_data.get('venue_type', '')}",
                f"{entity_data.get('neighborhood', '')} nightlife"
            ]
            base_keywords.extend([k for k in venue_keywords if k])
        
        elif page_type == "neighborhood" and entity_data:
            neighborhood = entity_data.get('name', '')
            neighborhood_keywords = [
                f"{neighborhood} nightlife",
                f"{neighborhood} bars",
                f"{neighborhood} clubs",
                f"{neighborhood} NYC",
                f"best bars {neighborhood}",
                f"{neighborhood} entertainment"
            ]
            base_keywords.extend(neighborhood_keywords)
        
        # Remove duplicates and empty strings
        keywords = list(dict.fromkeys([k for k in base_keywords if k]))
        return ", ".join(keywords[:20])  # Limit to 20 keywords
    
    @staticmethod
    def get_neighborhood_venues_count(neighborhood: str) -> int:
        """Get count of venues in a neighborhood (for SEO content)"""
        # This would typically query the database
        # For now, return a placeholder
        return 25
    
    @staticmethod
    def generate_hreflang_tags(current_url: str) -> List[Dict]:
        """Generate hreflang tags for international SEO (future expansion)"""
        return [
            {"hreflang": "en-us", "href": current_url},
            {"hreflang": "x-default", "href": current_url}
        ]

class SitemapGenerator:
    """Generate XML sitemaps for Atlas-NYC"""
    
    @staticmethod
    def generate_sitemap_index() -> str:
        """Generate sitemap index XML"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        return f'''<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>{SEOHelper.BASE_URL}/sitemap-main.xml</loc>
        <lastmod>{current_date}</lastmod>
    </sitemap>
    <sitemap>
        <loc>{SEOHelper.BASE_URL}/sitemap-venues.xml</loc>
        <lastmod>{current_date}</lastmod>
    </sitemap>
    <sitemap>
        <loc>{SEOHelper.BASE_URL}/sitemap-neighborhoods.xml</loc>
        <lastmod>{current_date}</lastmod>
    </sitemap>
</sitemapindex>'''
    
    @staticmethod
    def generate_main_sitemap() -> str:
        """Generate main pages sitemap"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        pages = [
            {"url": "/", "priority": "1.0", "changefreq": "daily"},
            {"url": "/venues", "priority": "0.9", "changefreq": "daily"},
            {"url": "/neighborhoods", "priority": "0.8", "changefreq": "weekly"},
            {"url": "/content", "priority": "0.7", "changefreq": "daily"},
            {"url": "/about", "priority": "0.5", "changefreq": "monthly"},
            {"url": "/contact", "priority": "0.5", "changefreq": "monthly"}
        ]
        
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'''
        
        for page in pages:
            xml += f'''
    <url>
        <loc>{SEOHelper.BASE_URL}{page["url"]}</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>{page["changefreq"]}</changefreq>
        <priority>{page["priority"]}</priority>
    </url>'''
        
        xml += '\n</urlset>'
        return xml
    
    @staticmethod
    def generate_venues_sitemap(venues: List[Dict]) -> str:
        """Generate venues sitemap from venue data"""
        current_date = datetime.now().strftime('%Y-%m-%d')
        
        xml = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'''
        
        for venue in venues:
            slug = SEOHelper.generate_venue_slug(venue.get('name', ''), venue.get('id', 0))
            xml += f'''
    <url>
        <loc>{SEOHelper.BASE_URL}/venues/{slug}</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>'''
        
        xml += '\n</urlset>'
        return xml