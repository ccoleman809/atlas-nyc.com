"""
Data Pipeline for ML System
Orchestrates data collection, processing, and model training
"""

import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass
import logging
import json

from instagram_scraper import InstagramScraperManager
from ml_models import MLModelManager
from ml_database import MLDatabase

logger = logging.getLogger(__name__)

@dataclass
class PipelineConfig:
    """Configuration for data pipeline"""
    scraping_enabled: bool = False  # Set to True only with proper authorization
    scraping_interval_hours: int = 6
    model_training_interval_days: int = 7
    prediction_interval_hours: int = 1
    venues_to_track: List[str] = None
    hashtags_to_track: List[str] = None
    
    def __post_init__(self):
        if self.venues_to_track is None:
            self.venues_to_track = [
                "House of Yes", "Brooklyn Mirage", "Elsewhere",
                "Good Room", "Nowadays", "Public Records"
            ]
        if self.hashtags_to_track is None:
            self.hashtags_to_track = [
                "nycnightlife", "brooklynclubs", "nycevents"
            ]

class DataCollector:
    """Collects data from various sources"""
    
    def __init__(self, ml_db: MLDatabase, config: PipelineConfig):
        self.ml_db = ml_db
        self.config = config
        self.scraper = InstagramScraperManager() if config.scraping_enabled else None
        
    async def collect_instagram_data(self):
        """Collect Instagram data (only if authorized)"""
        if not self.config.scraping_enabled:
            logger.info("Instagram scraping disabled")
            return
            
        logger.info("Starting Instagram data collection...")
        
        try:
            # Scrape posts
            posts = await self.scraper.scrape_nyc_nightlife(
                self.config.venues_to_track,
                self.config.hashtags_to_track
            )
            
            # Save to database
            for post in posts:
                post_data = {
                    'post_id': post.post_id,
                    'username': post.username,
                    'venue_id': self._get_venue_id(post.venue_tag),
                    'venue_name': post.venue_tag,
                    'caption': post.caption,
                    'likes': post.likes,
                    'comments': post.comments,
                    'engagement_rate': post.engagement_rate,
                    'hashtags': post.hashtags,
                    'location_lat': post.location.get('lat') if post.location else None,
                    'location_lng': post.location.get('lng') if post.location else None,
                    'posted_at': post.timestamp,
                    'image_url': post.image_url
                }
                self.ml_db.insert_instagram_post(post_data)
            
            logger.info(f"Collected {len(posts)} Instagram posts")
            
        except Exception as e:
            logger.error(f"Error collecting Instagram data: {e}")
    
    def collect_external_data(self):
        """Collect external data (weather, events, etc.)"""
        external_data = {}
        
        # Weather data (would use weather API)
        external_data['weather'] = {
            'temperature': 72,
            'condition': 'clear',
            'precipitation_prob': 0.1
        }
        
        # Events data (would use event APIs)
        external_data['events'] = []
        
        # Traffic/transportation (would use transit APIs)
        external_data['transit_delays'] = False
        
        return external_data
    
    def collect_user_feedback(self):
        """Collect user interaction data"""
        # This would integrate with the production system
        # to get anonymous user interaction data
        pass
    
    def _get_venue_id(self, venue_name: str) -> str:
        """Convert venue name to ID"""
        # Simple implementation - would use lookup table in production
        return venue_name.lower().replace(' ', '_') if venue_name else None

class FeatureEngineer:
    """Generates features for ML models"""
    
    def __init__(self, ml_db: MLDatabase):
        self.ml_db = ml_db
        
    def generate_venue_features(self, venue_id: str) -> Dict:
        """Generate ML features for a venue"""
        features = {}
        
        # Time features
        now = datetime.now()
        features['hour'] = now.hour
        features['day_of_week'] = now.weekday()
        features['day_of_month'] = now.day
        features['month'] = now.month
        features['is_weekend'] = 1 if now.weekday() >= 5 else 0
        features['is_friday'] = 1 if now.weekday() == 4 else 0
        features['is_saturday'] = 1 if now.weekday() == 5 else 0
        
        # Instagram features (last 24 hours)
        posts = self.ml_db.get_venue_instagram_posts(venue_id, days=1)
        features['instagram_posts_24h'] = len(posts)
        features['instagram_likes_24h'] = sum(p['likes'] for p in posts)
        features['instagram_engagement_24h'] = np.mean([p['engagement_rate'] for p in posts]) if posts else 0
        
        # Historical features
        features.update(self._get_historical_features(venue_id))
        
        # Venue characteristics
        venue_data = self._get_venue_characteristics(venue_id)
        features.update(venue_data)
        
        return features
    
    def _get_historical_features(self, venue_id: str) -> Dict:
        """Get historical average features"""
        # Would calculate from historical data
        return {
            'avg_crowd_same_hour': 75,
            'avg_crowd_same_day': 80,
            'avg_crowd_last_week': 70,
            'trend_last_month': 0.05  # 5% growth
        }
    
    def _get_venue_characteristics(self, venue_id: str) -> Dict:
        """Get static venue characteristics"""
        # Would fetch from venue_features table
        return {
            'capacity': 200,
            'price_range': 3,
            'has_outdoor': 0,
            'accepts_reservations': 1
        }
    
    def generate_training_dataset(self, days_back: int = 90) -> pd.DataFrame:
        """Generate dataset for model training"""
        # Get all venues
        venues = self.config.venues_to_track
        
        training_data = []
        
        for venue in venues:
            venue_id = venue.lower().replace(' ', '_')
            
            # Get historical data for each day
            for day_offset in range(days_back):
                date = datetime.now() - timedelta(days=day_offset)
                
                # Generate features for that day
                features = self.generate_venue_features(venue_id)
                features['date'] = date.date()
                
                # Get target variable (actual crowd/popularity)
                # This would come from actual data in production
                features['target_crowd'] = np.random.randint(20, 100)
                
                training_data.append(features)
        
        return pd.DataFrame(training_data)

class ModelTrainer:
    """Handles model training and evaluation"""
    
    def __init__(self, ml_db: MLDatabase, model_manager: MLModelManager):
        self.ml_db = ml_db
        self.model_manager = model_manager
        
    def train_all_models(self):
        """Train all ML models"""
        logger.info("Starting model training...")
        
        # Generate training data
        engineer = FeatureEngineer(self.ml_db)
        training_data = engineer.generate_training_dataset()
        
        # Train popularity model
        self._train_popularity_model(training_data)
        
        # Train trend models
        self._train_trend_models()
        
        # Train recommendation model
        self._train_recommendation_model()
        
        # Save models
        self.model_manager.save_models()
        
        logger.info("Model training completed")
    
    def _train_popularity_model(self, training_data: pd.DataFrame):
        """Train venue popularity prediction model"""
        logger.info("Training popularity model...")
        
        # Prepare features and target
        feature_cols = [col for col in training_data.columns 
                       if col not in ['target_crowd', 'date', 'venue_id']]
        
        X = training_data[feature_cols]
        y = training_data['target_crowd'] / 100  # Normalize to 0-1
        
        # Train model
        self.model_manager.popularity_model.train(
            pd.concat([X, y.rename('popularity_score')], axis=1)
        )
    
    def _train_trend_models(self):
        """Train time series trend models"""
        logger.info("Training trend models...")
        
        # Get time series data for each venue
        for venue_id in self.config.venues_to_track:
            venue_id_clean = venue_id.lower().replace(' ', '_')
            
            # Get historical metrics
            ts_data = self.ml_db.get_time_series(
                venue_id_clean, 
                'instagram_mentions',
                start_date=(datetime.now() - timedelta(days=180)).isoformat()
            )
            
            if not ts_data.empty:
                # Train Prophet model
                self.model_manager.trend_model.build_prophet_model(
                    ts_data.reset_index(),
                    f'venue_{venue_id_clean}'
                )
    
    def _train_recommendation_model(self):
        """Train recommendation model"""
        logger.info("Training recommendation model...")
        
        # Get user interaction data
        # Build user-venue interaction matrix
        # Train collaborative filtering model
        pass
    
    def evaluate_models(self):
        """Evaluate model performance"""
        results = {}
        
        # Evaluate popularity predictions
        popularity_metrics = self.ml_db.get_prediction_accuracy('popularity', days=30)
        results['popularity_model'] = popularity_metrics
        
        # Evaluate other models...
        
        logger.info(f"Model evaluation results: {results}")
        return results

class PredictionService:
    """Generates and serves predictions"""
    
    def __init__(self, ml_db: MLDatabase, model_manager: MLModelManager):
        self.ml_db = ml_db
        self.model_manager = model_manager
        self.engineer = FeatureEngineer(ml_db)
        
    def generate_predictions(self):
        """Generate predictions for all venues"""
        logger.info("Generating predictions...")
        
        predictions = {}
        
        for venue in self.config.venues_to_track:
            venue_id = venue.lower().replace(' ', '_')
            
            # Generate features
            features = self.engineer.generate_venue_features(venue_id)
            
            # Get predictions from each model
            venue_data = {'id': venue_id, 'name': venue}
            external_data = {'temperature': 72}  # Would get real data
            
            # Popularity prediction
            popularity = self.model_manager.popularity_model.predict(
                venue_data, external_data
            )
            
            # Save prediction
            self.ml_db.save_prediction(
                venue_id,
                'popularity',
                popularity.predicted_popularity,
                popularity.confidence_score,
                features
            )
            
            predictions[venue_id] = {
                'popularity': popularity.predicted_popularity,
                'peak_hour': popularity.predicted_peak_hour,
                'crowd_estimate': popularity.crowd_size_estimate
            }
        
        logger.info(f"Generated predictions for {len(predictions)} venues")
        return predictions
    
    def get_real_time_prediction(self, venue_id: str) -> Dict:
        """Get real-time prediction for a venue"""
        # Generate current features
        features = self.engineer.generate_venue_features(venue_id)
        
        # Get venue insights
        insights = self.model_manager.get_venue_insights(venue_id)
        
        return insights

class DataPipeline:
    """Main data pipeline orchestrator"""
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.ml_db = MLDatabase()
        self.model_manager = MLModelManager()
        self.collector = DataCollector(self.ml_db, config)
        self.trainer = ModelTrainer(self.ml_db, self.model_manager)
        self.predictor = PredictionService(self.ml_db, self.model_manager)
        
    def run_collection(self):
        """Run data collection tasks"""
        logger.info("Running data collection...")
        
        # Collect Instagram data
        if self.config.scraping_enabled:
            asyncio.run(self.collector.collect_instagram_data())
        
        # Collect external data
        external_data = self.collector.collect_external_data()
        
        # Update analytics
        for venue in self.config.venues_to_track:
            venue_id = venue.lower().replace(' ', '_')
            
            # Calculate daily analytics
            posts = self.ml_db.get_venue_instagram_posts(venue_id, days=1)
            
            analytics = {
                'instagram_mentions': len(posts),
                'avg_engagement': np.mean([p['engagement_rate'] for p in posts]) if posts else 0,
                'weather_condition': external_data['weather']['condition']
            }
            
            self.ml_db.update_venue_analytics(
                venue_id,
                datetime.now().date().isoformat(),
                analytics
            )
    
    def run_training(self):
        """Run model training"""
        logger.info("Running model training...")
        self.trainer.train_all_models()
        self.trainer.evaluate_models()
    
    def run_predictions(self):
        """Run prediction generation"""
        logger.info("Running predictions...")
        self.predictor.generate_predictions()
    
    def schedule_jobs(self):
        """Schedule periodic jobs"""
        # Data collection
        schedule.every(self.config.scraping_interval_hours).hours.do(
            self.run_collection
        )
        
        # Model training
        schedule.every(self.config.model_training_interval_days).days.do(
            self.run_training
        )
        
        # Predictions
        schedule.every(self.config.prediction_interval_hours).hours.do(
            self.run_predictions
        )
        
        logger.info("Jobs scheduled")
    
    def run(self):
        """Run the pipeline"""
        logger.info("Starting ML data pipeline...")
        
        # Initial run
        self.run_collection()
        self.run_training()
        self.run_predictions()
        
        # Schedule future runs
        self.schedule_jobs()
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

# Example usage
if __name__ == "__main__":
    # Configure pipeline
    config = PipelineConfig(
        scraping_enabled=False,  # Only enable with proper authorization
        venues_to_track=[
            "House of Yes",
            "Brooklyn Mirage",
            "Elsewhere"
        ],
        hashtags_to_track=["nycnightlife"]
    )
    
    # Create pipeline
    pipeline = DataPipeline(config)
    
    # Run once for testing
    pipeline.run_collection()
    
    print("✅ Data pipeline ready")
    print("⚠️  Instagram scraping is disabled by default")
    print("📊 Models can be trained on synthetic data for testing")