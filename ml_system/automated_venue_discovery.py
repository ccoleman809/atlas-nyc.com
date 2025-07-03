"""
Automated Venue Discovery System with ML/AI
Discovers and adds venues, cultural organizations, and events to the database
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
import hashlib
import re
from urllib.parse import quote
import time

from ml_system.ml_models import MLModelManager
try:
    from ml_system.ml_database import MLDatabase
except ImportError:
    # Create a simple placeholder MLDatabase if the module doesn't exist
    class MLDatabase:
        def store_discovery_result(self, data):
            pass

@dataclass
class VenueCandidate:
    """Represents a potential venue discovered from external sources"""
    name: str
    address: str
    latitude: float
    longitude: float
    source: str
    venue_type: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    social_media: Optional[Dict] = None
    rating: Optional[float] = None
    price_level: Optional[int] = None
    hours: Optional[Dict] = None
    categories: Optional[List[str]] = None
    confidence_score: Optional[float] = None
    raw_data: Optional[Dict] = None

@dataclass
class EventCandidate:
    """Represents a potential event discovered from external sources"""
    name: str
    venue_name: str
    start_date: str
    end_date: Optional[str]
    description: str
    source: str
    event_type: Optional[str] = None
    price: Optional[str] = None
    url: Optional[str] = None
    organizer: Optional[str] = None
    confidence_score: Optional[float] = None

class DataSourceManager:
    """Manages connections to external data sources"""
    
    def __init__(self):
        self.session = None
        self.api_keys = {
            'google_places': None,  # Set from environment
            'yelp': None,
            'foursquare': None
        }
        self.rate_limits = {
            'google_places': {'calls_per_minute': 100, 'last_call': 0},
            'yelp': {'calls_per_minute': 83, 'last_call': 0},  # 5000/day = ~83/min
            'nyc_open_data': {'calls_per_minute': 1000, 'last_call': 0}
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def _rate_limit_wait(self, source: str):
        """Implement rate limiting"""
        if source in self.rate_limits:
            limit_info = self.rate_limits[source]
            time_since_last = time.time() - limit_info['last_call']
            min_interval = 60 / limit_info['calls_per_minute']
            
            if time_since_last < min_interval:
                await asyncio.sleep(min_interval - time_since_last)
            
            self.rate_limits[source]['last_call'] = time.time()
    
    async def fetch_nyc_cultural_organizations(self) -> List[VenueCandidate]:
        """Fetch cultural organizations from NYC Open Data"""
        await self._rate_limit_wait('nyc_open_data')
        
        url = "https://data.cityofnewyork.us/resource/u35m-9t32.json"
        params = {
            '$limit': 1000,
            '$where': "discipline IN ('Music', 'Theater', 'Dance', 'Multi-Disciplinary')"
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [self._parse_cultural_org(org) for org in data]
        except Exception as e:
            logging.error(f"Error fetching NYC cultural orgs: {e}")
        
        return []
    
    async def fetch_google_places(self, query: str, location: str = "New York City") -> List[VenueCandidate]:
        """Fetch venues from Google Places API"""
        if not self.api_keys['google_places']:
            return []
        
        await self._rate_limit_wait('google_places')
        
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': f"{query} in {location}",
            'key': self.api_keys['google_places'],
            'type': 'establishment'
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [self._parse_google_place(place) for place in data.get('results', [])]
        except Exception as e:
            logging.error(f"Error fetching Google Places: {e}")
        
        return []
    
    async def fetch_yelp_businesses(self, term: str, location: str = "New York, NY") -> List[VenueCandidate]:
        """Fetch businesses from Yelp API"""
        if not self.api_keys['yelp']:
            return []
        
        await self._rate_limit_wait('yelp')
        
        url = "https://api.yelp.com/v3/businesses/search"
        headers = {'Authorization': f"Bearer {self.api_keys['yelp']}"}
        params = {
            'term': term,
            'location': location,
            'limit': 50,
            'categories': 'nightlife,arts,eventservices'
        }
        
        try:
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [self._parse_yelp_business(biz) for biz in data.get('businesses', [])]
        except Exception as e:
            logging.error(f"Error fetching Yelp businesses: {e}")
        
        return []
    
    async def fetch_nyc_events(self) -> List[EventCandidate]:
        """Fetch events from NYC Open Data"""
        await self._rate_limit_wait('nyc_open_data')
        
        url = "https://data.cityofnewyork.us/resource/tvpp-9vvx.json"
        params = {
            '$limit': 500,
            '$where': f"start_date_time >= '{datetime.now().isoformat()}'"
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [self._parse_nyc_event(event) for event in data]
        except Exception as e:
            logging.error(f"Error fetching NYC events: {e}")
        
        return []
    
    def _parse_cultural_org(self, org: Dict) -> VenueCandidate:
        """Parse cultural organization data"""
        return VenueCandidate(
            name=org.get('organization', ''),
            address=f"{org.get('address', '')} {org.get('city', 'New York')}",
            latitude=float(org.get('latitude', 0)) if org.get('latitude') else 0,
            longitude=float(org.get('longitude', 0)) if org.get('longitude') else 0,
            source='nyc_cultural_orgs',
            venue_type='cultural_organization',
            phone=org.get('phone', ''),
            website=org.get('website', ''),
            categories=[org.get('discipline', '')],
            raw_data=org
        )
    
    def _parse_google_place(self, place: Dict) -> VenueCandidate:
        """Parse Google Places data"""
        location = place.get('geometry', {}).get('location', {})
        return VenueCandidate(
            name=place.get('name', ''),
            address=place.get('formatted_address', ''),
            latitude=location.get('lat', 0),
            longitude=location.get('lng', 0),
            source='google_places',
            rating=place.get('rating'),
            price_level=place.get('price_level'),
            categories=place.get('types', []),
            raw_data=place
        )
    
    def _parse_yelp_business(self, biz: Dict) -> VenueCandidate:
        """Parse Yelp business data"""
        coordinates = biz.get('coordinates', {})
        location = biz.get('location', {})
        
        return VenueCandidate(
            name=biz.get('name', ''),
            address=location.get('display_address', [''])[0] if location.get('display_address') else '',
            latitude=coordinates.get('latitude', 0),
            longitude=coordinates.get('longitude', 0),
            source='yelp',
            phone=biz.get('phone', ''),
            website=biz.get('url', ''),
            rating=biz.get('rating'),
            categories=[cat['title'] for cat in biz.get('categories', [])],
            raw_data=biz
        )
    
    def _parse_nyc_event(self, event: Dict) -> EventCandidate:
        """Parse NYC event data"""
        return EventCandidate(
            name=event.get('event_name', ''),
            venue_name=event.get('event_location', ''),
            start_date=event.get('start_date_time', ''),
            end_date=event.get('end_date_time'),
            description=event.get('event_description', ''),
            source='nyc_events',
            event_type=event.get('event_type', ''),
            url=event.get('event_website', ''),
            organizer=event.get('event_agency', '')
        )

class VenueClassifier:
    """ML-powered venue classification system"""
    
    def __init__(self, ml_manager: MLModelManager):
        self.ml_manager = ml_manager
        self.venue_type_mapping = {
            'bar': ['Bar', 'Dive Bar', 'Sports Bar', 'Wine Bar'],
            'club': ['Dance Club', 'Nightclub', 'Music Venue'],
            'restaurant': ['Restaurant', 'Cocktail Lounge', 'Rooftop'],
            'cultural': ['Museum', 'Theater', 'Art Gallery', 'Cultural Organization'],
            'event_space': ['Event Venue', 'Concert Hall', 'Performance Space']
        }
    
    def classify_venue_type(self, candidate: VenueCandidate) -> Tuple[str, float]:
        """Classify venue type using ML and rule-based logic"""
        
        # Rule-based classification
        name_lower = candidate.name.lower()
        categories = [cat.lower() for cat in (candidate.categories or [])]
        
        # Define keywords for each type
        type_keywords = {
            'dive_bar': ['bar', 'pub', 'tavern', 'saloon'],
            'dance_club': ['club', 'nightclub', 'disco', 'dance'],
            'cocktail_lounge': ['lounge', 'cocktail', 'speakeasy'],
            'rooftop': ['rooftop', 'roof', 'sky'],
            'cultural_organization': ['museum', 'gallery', 'theater', 'theatre', 'cultural'],
            'music_venue': ['music', 'concert', 'venue', 'hall', 'stage']
        }
        
        scores = {}
        for venue_type, keywords in type_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in name_lower:
                    score += 0.3
                if any(keyword in cat for cat in categories):
                    score += 0.4
            scores[venue_type] = score
        
        # Find best match
        if scores:
            best_type = max(scores, key=scores.get)
            confidence = min(scores[best_type], 1.0)
            
            if confidence > 0.3:
                return best_type, confidence
        
        # Default classification
        return 'venue', 0.5
    
    def calculate_quality_score(self, candidate: VenueCandidate) -> float:
        """Calculate quality score for venue candidate"""
        score = 0.0
        
        # Name quality
        if candidate.name and len(candidate.name.strip()) > 2:
            score += 0.2
        
        # Address quality
        if candidate.address and 'new york' in candidate.address.lower():
            score += 0.2
        
        # Location coordinates
        if candidate.latitude != 0 and candidate.longitude != 0:
            # Check if coordinates are in NYC area
            if 40.4 < candidate.latitude < 41.0 and -74.3 < candidate.longitude < -73.7:
                score += 0.3
        
        # Rating information
        if candidate.rating and candidate.rating > 3.0:
            score += 0.15
        
        # Contact information
        if candidate.phone or candidate.website:
            score += 0.1
        
        # Categories/types
        if candidate.categories:
            score += 0.05
        
        return min(score, 1.0)

class DeduplicationEngine:
    """Intelligent deduplication to prevent duplicate venues"""
    
    def __init__(self, existing_venues: List[Dict]):
        self.existing_venues = existing_venues
        self.name_hashes = self._create_name_hashes()
    
    def _create_name_hashes(self) -> Dict[str, Dict]:
        """Create hashes for existing venue names"""
        hashes = {}
        for venue in self.existing_venues:
            normalized_name = self._normalize_name(venue.get('name', ''))
            name_hash = hashlib.md5(normalized_name.encode()).hexdigest()
            hashes[name_hash] = venue
        return hashes
    
    def _normalize_name(self, name: str) -> str:
        """Normalize venue name for comparison"""
        # Remove common suffixes and prefixes
        name = re.sub(r'\b(the|a|an)\b', '', name, flags=re.IGNORECASE)
        # Remove special characters and extra spaces
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name).strip().lower()
        return name
    
    def is_duplicate(self, candidate: VenueCandidate) -> Tuple[bool, Optional[Dict]]:
        """Check if candidate is a duplicate of existing venue"""
        
        # Check name similarity
        normalized_candidate = self._normalize_name(candidate.name)
        candidate_hash = hashlib.md5(normalized_candidate.encode()).hexdigest()
        
        if candidate_hash in self.name_hashes:
            return True, self.name_hashes[candidate_hash]
        
        # Check location proximity (within 100 meters)
        for venue in self.existing_venues:
            if self._calculate_distance(
                candidate.latitude, candidate.longitude,
                venue.get('latitude', 0), venue.get('longitude', 0)
            ) < 0.1:  # 100 meters
                # Also check name similarity
                similarity = self._name_similarity(candidate.name, venue.get('name', ''))
                if similarity > 0.8:
                    return True, venue
        
        return False, None
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = np.radians(lat1)
        lat2_rad = np.radians(lat2)
        delta_lat = np.radians(lat2 - lat1)
        delta_lon = np.radians(lon2 - lon1)
        
        a = (np.sin(delta_lat/2)**2 + 
             np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(delta_lon/2)**2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        
        return R * c
    
    def _name_similarity(self, name1: str, name2: str) -> float:
        """Calculate name similarity using Jaccard similarity"""
        set1 = set(self._normalize_name(name1).split())
        set2 = set(self._normalize_name(name2).split())
        
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union)

class AutomatedVenueDiscovery:
    """Main orchestrator for automated venue discovery"""
    
    def __init__(self, db_connection=None):
        self.ml_manager = MLModelManager()
        self.ml_db = MLDatabase()
        self.classifier = VenueClassifier(self.ml_manager)
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the discovery system"""
        logger = logging.getLogger('venue_discovery')
        logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler('venue_discovery.log')
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    async def discover_venues(self, search_terms: List[str] = None) -> Dict[str, int]:
        """Main method to discover and add new venues"""
        if search_terms is None:
            search_terms = [
                'nightlife venues', 'bars clubs', 'music venues',
                'art galleries', 'theaters', 'cultural centers'
            ]
        
        self.logger.info("Starting automated venue discovery")
        stats = {'total_found': 0, 'added': 0, 'duplicates': 0, 'rejected': 0}
        
        # Get existing venues for deduplication
        existing_venues = await self._get_existing_venues()
        dedup_engine = DeduplicationEngine(existing_venues)
        
        async with DataSourceManager() as source_manager:
            all_candidates = []
            
            # Fetch from multiple sources
            tasks = [
                source_manager.fetch_nyc_cultural_organizations(),
                source_manager.fetch_nyc_events()
            ]
            
            # Add search-based tasks
            for term in search_terms:
                tasks.extend([
                    source_manager.fetch_google_places(term),
                    source_manager.fetch_yelp_businesses(term)
                ])
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            for result in results:
                if isinstance(result, list):
                    all_candidates.extend(result)
                elif isinstance(result, Exception):
                    self.logger.error(f"Error in data fetching: {result}")
            
            stats['total_found'] = len(all_candidates)
            self.logger.info(f"Found {len(all_candidates)} venue candidates")
            
            # Process candidates
            for candidate in all_candidates:
                try:
                    processed = await self._process_candidate(candidate, dedup_engine)
                    
                    if processed['action'] == 'added':
                        stats['added'] += 1
                    elif processed['action'] == 'duplicate':
                        stats['duplicates'] += 1
                    else:
                        stats['rejected'] += 1
                        
                except Exception as e:
                    self.logger.error(f"Error processing candidate {candidate.name}: {e}")
                    stats['rejected'] += 1
        
        self.logger.info(f"Discovery complete: {stats}")
        return stats
    
    async def _process_candidate(self, candidate: VenueCandidate, dedup_engine: DeduplicationEngine) -> Dict:
        """Process a single venue candidate"""
        
        # Check for duplicates
        is_dup, existing_venue = dedup_engine.is_duplicate(candidate)
        if is_dup:
            return {'action': 'duplicate', 'existing_venue': existing_venue}
        
        # Classify venue type
        venue_type, type_confidence = self.classifier.classify_venue_type(candidate)
        
        # Calculate quality score
        quality_score = self.classifier.calculate_quality_score(candidate)
        
        # Set overall confidence
        candidate.confidence_score = (type_confidence + quality_score) / 2
        candidate.venue_type = venue_type
        
        # Quality threshold
        if candidate.confidence_score < 0.6:
            return {'action': 'rejected', 'reason': 'low_quality', 'score': candidate.confidence_score}
        
        # Add to database
        venue_id = await self._add_venue_to_database(candidate)
        
        if venue_id:
            self.logger.info(f"Added venue: {candidate.name} (ID: {venue_id})")
            return {'action': 'added', 'venue_id': venue_id, 'confidence': candidate.confidence_score}
        else:
            return {'action': 'rejected', 'reason': 'database_error'}
    
    async def _get_existing_venues(self) -> List[Dict]:
        """Get existing venues from database"""
        # This would connect to your actual database
        # For now, return empty list
        return []
    
    async def _add_venue_to_database(self, candidate: VenueCandidate) -> Optional[int]:
        """Add venue to the main database"""
        try:
            venue_data = {
                'name': candidate.name,
                'address': candidate.address,
                'latitude': candidate.latitude,
                'longitude': candidate.longitude,
                'venue_type': candidate.venue_type,
                'phone': candidate.phone,
                'website': candidate.website,
                'rating': candidate.rating,
                'source': candidate.source,
                'confidence_score': candidate.confidence_score,
                'discovered_at': datetime.now().isoformat(),
                'raw_data': json.dumps(candidate.raw_data) if candidate.raw_data else None
            }
            
            # This would use your actual database connection
            # venue_id = database.add_venue(venue_data)
            venue_id = hash(candidate.name) % 10000  # Placeholder
            
            # Also add to ML database for analytics
            await self.ml_db.store_discovery_result(venue_data)
            
            return venue_id
            
        except Exception as e:
            self.logger.error(f"Database error adding venue {candidate.name}: {e}")
            return None

# Usage example and scheduler
async def run_discovery_pipeline():
    """Run the discovery pipeline"""
    discovery = AutomatedVenueDiscovery()
    
    # Custom search terms for NYC nightlife
    search_terms = [
        'Brooklyn nightlife venues',
        'Manhattan bars clubs',
        'Queens music venues',
        'NYC art galleries',
        'Brooklyn theaters',
        'Manhattan cultural centers',
        'rooftop bars NYC',
        'speakeasy bars NYC',
        'live music venues Brooklyn'
    ]
    
    results = await discovery.discover_venues(search_terms)
    print(f"Discovery Results: {results}")
    
    return results

if __name__ == "__main__":
    # Run the discovery pipeline
    asyncio.run(run_discovery_pipeline())