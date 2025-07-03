# ML System - Original NYC Nightlife AI Vision

This directory contains the **original ML/AI system** that was envisioned for the NYC nightlife platform. It's kept separate from the production system for future development or reference.

## ⚠️ IMPORTANT DISCLAIMER

This code is **NOT ACTIVE** and **NOT CONNECTED** to the production system. It's maintained here for:
- Educational purposes
- Future development reference
- Potential pivot back to ML features
- Research and experimentation

**DO NOT USE** the Instagram scraping functionality without proper authorization and compliance with Instagram's Terms of Service.

## 🏗️ Architecture Overview

### 1. **Instagram Scraper** (`instagram_scraper.py`)
- Multiple scraping strategies (Instaloader, Selenium)
- Rate limiting and checkpoint system
- Data extraction for venues and hashtags
- Engagement analysis

### 2. **ML Models** (`ml_models.py`)
- **VenuePopularityModel**: Neural network for popularity prediction
- **TrendPredictionModel**: Time series forecasting with Prophet
- **RecommendationEngine**: Collaborative filtering for venue recommendations
- **CrowdPredictionModel**: Ensemble model for crowd level prediction

### 3. **ML Database** (`ml_database.py`)
- Separate SQLite database for ML data
- Tables for Instagram posts, analytics, predictions
- Time series data storage
- User interaction tracking

### 4. **Data Pipeline** (`data_pipeline.py`)
- Orchestrates data collection and processing
- Feature engineering
- Model training coordination
- Real-time prediction serving

### 5. **API Integration** (`ml_api.py`)
- FastAPI endpoints for ML features
- Real-time predictions
- Analytics dashboard data
- A/B testing framework

## 🚀 Potential Features

### Real-Time Features
- Live crowd predictions
- Trending venue alerts
- Personalized recommendations
- Peak time predictions

### Analytics Features
- Venue popularity trends
- Neighborhood heat maps
- User behavior analysis
- Revenue optimization

### Social Features
- Instagram story tracking
- Influencer identification
- Viral content detection
- Sentiment analysis

## 🔧 Setup (For Development Only)

1. **Create virtual environment**
```bash
cd ml_system
python -m venv ml_env
source ml_env/bin/activate  # On Windows: ml_env\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Initialize ML database**
```python
from ml_database import MLDatabase
ml_db = MLDatabase()
```

## 📊 How It Would Work

1. **Data Collection**
   - Scrape Instagram posts (with proper authorization)
   - Collect venue check-ins
   - Track user interactions
   - Gather external data (weather, events)

2. **Feature Engineering**
   - Time-based features
   - Social media metrics
   - Historical patterns
   - External factors

3. **Model Training**
   - Train models on historical data
   - Validate predictions
   - A/B test recommendations
   - Continuous learning

4. **Serving Predictions**
   - Real-time API endpoints
   - Cached predictions
   - Fallback mechanisms
   - Performance monitoring

## 🔄 Integration Path

To integrate ML features with the current system:

1. **Phase 1**: Analytics Only
   - Use manual data entry
   - Build historical dataset
   - Train initial models

2. **Phase 2**: Predictions
   - Add prediction endpoints
   - A/B test with small user group
   - Monitor accuracy

3. **Phase 3**: Full Integration
   - Enable all ML features
   - Scale infrastructure
   - Add real-time updates

## 📈 Future Enhancements

- **Computer Vision**: Analyze venue photos
- **NLP**: Review sentiment analysis
- **Graph Networks**: Social influence modeling
- **Reinforcement Learning**: Dynamic pricing
- **AutoML**: Automated model optimization

## 🔒 Security & Privacy

- User data anonymization
- GDPR compliance ready
- Secure model storage
- API rate limiting
- Audit logging

## 📝 Notes

This system represents the original ambitious vision for the platform. While the current production system is simpler and more legally compliant, this ML system could be activated in the future with:

1. Proper Instagram API partnership
2. User consent for data collection
3. Sufficient historical data
4. Infrastructure scaling
5. Legal compliance verification

Keep this code as a blueprint for future AI-powered features!