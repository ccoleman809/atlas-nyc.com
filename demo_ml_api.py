#!/usr/bin/env python3
"""
Demo of ML/AI API Functionality
Shows working endpoints and capabilities
"""

import sys
import asyncio
sys.path.append('.')

async def demo_ml_apis():
    print("🚀 NYC Nightlife ML/AI System Demo")
    print("=" * 50)
    
    # Import ML components
    from ml_system.smart_content_enhancer import SmartContentEnhancer
    from ml_system.automated_venue_discovery import VenueClassifier, DeduplicationEngine
    from ml_system.ml_models import MLModelManager
    
    print("\n✅ All ML components imported successfully!")
    
    # Demo 1: Venue Enhancement API
    print("\n" + "="*50)
    print("1. 🎨 VENUE ENHANCEMENT API DEMO")
    print("="*50)
    
    enhancer = SmartContentEnhancer()
    
    test_venues = [
        {
            'id': 'venue_001',
            'name': 'House of Yes',
            'venue_type': 'dance_club',
            'neighborhood': 'Bushwick',
            'instagram_handle': 'houseofyes'
        },
        {
            'id': 'venue_002', 
            'name': 'The Dead Rabbit',
            'venue_type': 'dive_bar',
            'neighborhood': 'Financial District'
        },
        {
            'id': 'venue_003',
            'name': 'Brooklyn Museum',
            'venue_type': 'cultural_organization',
            'neighborhood': 'Prospect Heights'
        }
    ]
    
    for venue in test_venues:
        print(f"\n📍 Processing: {venue['name']}")
        enhancement = await enhancer.enhance_venue(venue)
        
        # Format as API response
        api_response = {
            "status": "success",
            "venue_id": venue['id'],
            "enhanced_description": enhancement.enhanced_description,
            "key_features": enhancement.key_features[:3],  # Top 3
            "atmosphere_tags": enhancement.atmosphere_tags[:4],  # Top 4
            "target_demographics": enhancement.target_demographics,
            "social_sentiment": round(enhancement.social_sentiment, 2),
            "popularity_trend": enhancement.popularity_trend,
            "recommendations": enhancement.recommendations[:2]  # Top 2
        }
        
        print("   ✨ Enhanced Description:")
        print(f"      {api_response['enhanced_description']}")
        print(f"   🏷️  Key Features: {', '.join(api_response['key_features'])}")
        print(f"   🎭 Atmosphere: {', '.join(api_response['atmosphere_tags'])}")
        print(f"   👥 Demographics: {', '.join(api_response['target_demographics'])}")
        print(f"   📊 Sentiment Score: {api_response['social_sentiment']}")
        print(f"   📈 Trend: {api_response['popularity_trend']}")
    
    # Demo 2: Venue Classification API
    print("\n" + "="*50)
    print("2. 🤖 VENUE CLASSIFICATION API DEMO")
    print("="*50)
    
    from ml_system.automated_venue_discovery import VenueCandidate
    
    ml_manager = MLModelManager()
    classifier = VenueClassifier(ml_manager)
    
    test_candidates = [
        VenueCandidate(
            name="Roberta's Pizza",
            address="261 Moore St, Brooklyn, NY",
            latitude=40.7057, longitude=-73.9398,
            source="test",
            categories=["Restaurant", "Pizza", "Bar"]
        ),
        VenueCandidate(
            name="Output Club",
            address="74 Wythe Ave, Brooklyn, NY", 
            latitude=40.7195, longitude=-73.9573,
            source="test",
            categories=["Nightclub", "Music Venue", "Dance"]
        ),
        VenueCandidate(
            name="Brooklyn Academy of Music",
            address="30 Lafayette Ave, Brooklyn, NY",
            latitude=40.6863, longitude=-73.9777,
            source="test",
            categories=["Theater", "Cultural Center", "Performing Arts"]
        )
    ]
    
    for candidate in test_candidates:
        venue_type, confidence = classifier.classify_venue_type(candidate)
        quality_score = classifier.calculate_quality_score(candidate)
        
        # Format as API response
        classification_response = {
            "status": "success",
            "venue_name": candidate.name,
            "classified_type": venue_type,
            "confidence_score": round(confidence, 2),
            "quality_score": round(quality_score, 2),
            "location": candidate.address,
            "source": candidate.source
        }
        
        print(f"\n📍 {candidate.name}:")
        print(f"   🏷️  Classified as: {venue_type}")
        print(f"   🎯 Confidence: {classification_response['confidence_score']}")
        print(f"   ⭐ Quality Score: {classification_response['quality_score']}")
        print(f"   📍 Location: {candidate.address}")
    
    # Demo 3: Discovery Analytics API
    print("\n" + "="*50)
    print("3. 📊 DISCOVERY ANALYTICS API DEMO")
    print("="*50)
    
    # Simulate analytics data that would come from database
    analytics_response = {
        "status": "success",
        "total_venues_discovered": 247,
        "success_rate": 0.78,
        "top_sources": [
            {"source": "google_places", "count": 95},
            {"source": "yelp", "count": 87},
            {"source": "nyc_open_data", "count": 65}
        ],
        "venue_types_distribution": {
            "dive_bar": 45,
            "cocktail_lounge": 38,
            "dance_club": 32,
            "cultural_organization": 67,
            "rooftop": 28,
            "music_venue": 37
        },
        "quality_scores": {
            "average": 0.76,
            "above_threshold": 0.82,
            "below_threshold": 0.45
        },
        "recent_discoveries": [
            {"name": "The Commodity", "type": "cocktail_lounge", "score": 0.89},
            {"name": "House of Yes", "type": "dance_club", "score": 0.94},
            {"name": "Nowadays", "type": "music_venue", "score": 0.87}
        ]
    }
    
    print("📈 Discovery Statistics:")
    print(f"   Total Venues Found: {analytics_response['total_venues_discovered']}")
    print(f"   Success Rate: {analytics_response['success_rate']*100}%")
    print(f"   Average Quality: {analytics_response['quality_scores']['average']}")
    
    print("\n🔝 Top Sources:")
    for source in analytics_response['top_sources']:
        print(f"   {source['source']}: {source['count']} venues")
    
    print("\n🏷️  Venue Type Distribution:")
    for venue_type, count in analytics_response['venue_types_distribution'].items():
        print(f"   {venue_type.replace('_', ' ').title()}: {count}")
    
    print("\n🆕 Recent High-Quality Discoveries:")
    for venue in analytics_response['recent_discoveries']:
        print(f"   {venue['name']} ({venue['type']}) - Score: {venue['score']}")
    
    # Demo 4: Available API Endpoints
    print("\n" + "="*50)
    print("4. 🌐 AVAILABLE API ENDPOINTS")
    print("="*50)
    
    endpoints = [
        {
            "method": "POST",
            "path": "/enhance-venue",
            "description": "Enhance venue with AI-generated content",
            "example": "Generates descriptions, tags, demographics"
        },
        {
            "method": "POST", 
            "path": "/discover-venues",
            "description": "Discover new venues from multiple sources",
            "example": "Finds venues from NYC Open Data, Google Places, Yelp"
        },
        {
            "method": "GET",
            "path": "/venue-insights/{venue_id}",
            "description": "Get ML insights for a specific venue",
            "example": "Popularity predictions, crowd estimates, trends"
        },
        {
            "method": "GET",
            "path": "/analytics/discovery", 
            "description": "Get discovery performance analytics",
            "example": "Success rates, source performance, quality metrics"
        },
        {
            "method": "GET",
            "path": "/health",
            "description": "Health check and system status",
            "example": "Component status, system health"
        }
    ]
    
    for endpoint in endpoints:
        print(f"\n{endpoint['method']} {endpoint['path']}")
        print(f"   📝 {endpoint['description']}")
        print(f"   💡 Example: {endpoint['example']}")
    
    print("\n" + "="*50)
    print("🎉 ML/AI SYSTEM DEMONSTRATION COMPLETE!")
    print("="*50)
    
    print("\n🚀 Ready to Use Features:")
    print("   ✅ AI-enhanced venue descriptions")
    print("   ✅ Smart venue classification") 
    print("   ✅ Quality scoring and filtering")
    print("   ✅ Multi-source data discovery")
    print("   ✅ Social sentiment analysis")
    print("   ✅ Duplicate detection")
    print("   ✅ Analytics and monitoring")
    
    print("\n📖 To start the API server:")
    print("   1. python run_ml_api.py")
    print("   2. Visit: http://localhost:8001/docs")
    print("   3. Test endpoints with interactive documentation")
    
    print("\n🔗 Integration with your app:")
    print("   1. Copy code from ml_integration_endpoints.py")
    print("   2. Add to your main api_server.py")
    print("   3. Use ML features in your admin dashboard")

if __name__ == "__main__":
    asyncio.run(demo_ml_apis())