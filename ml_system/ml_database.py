"""
ML System Database Schema
Separate database for ML/AI features and scraped data
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json
import pandas as pd

class MLDatabase:
    """Database for ML system - separate from production database"""
    
    def __init__(self, db_path: str = "ml_system/ml_nightlife.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize ML database with required tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Instagram posts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS instagram_posts (
                    post_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    venue_id TEXT,
                    venue_name TEXT,
                    caption TEXT,
                    likes INTEGER,
                    comments INTEGER,
                    engagement_rate REAL,
                    hashtags TEXT,  -- JSON array
                    location_lat REAL,
                    location_lng REAL,
                    posted_at TIMESTAMP,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    image_url TEXT,
                    is_story BOOLEAN DEFAULT FALSE
                )
            """)
            
            # Venue analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS venue_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venue_id TEXT NOT NULL,
                    date DATE NOT NULL,
                    instagram_mentions INTEGER DEFAULT 0,
                    avg_engagement REAL,
                    sentiment_score REAL,
                    trending_score REAL,
                    predicted_crowd INTEGER,
                    actual_crowd INTEGER,
                    weather_condition TEXT,
                    special_events TEXT,  -- JSON array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(venue_id, date)
                )
            """)
            
            # User interactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    venue_id TEXT NOT NULL,
                    interaction_type TEXT,  -- 'view', 'like', 'visit', 'share'
                    rating REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    session_id TEXT,
                    source TEXT  -- 'web', 'mobile', 'instagram'
                )
            """)
            
            # ML predictions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ml_predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venue_id TEXT NOT NULL,
                    prediction_type TEXT,  -- 'popularity', 'crowd', 'trend'
                    predicted_value REAL,
                    confidence_score REAL,
                    prediction_date DATE,
                    features_used TEXT,  -- JSON
                    model_version TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Venue features table (for ML)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS venue_features (
                    venue_id TEXT PRIMARY KEY,
                    venue_type TEXT,
                    capacity INTEGER,
                    price_range INTEGER,  -- 1-4 scale
                    music_genres TEXT,  -- JSON array
                    avg_age INTEGER,
                    dress_code TEXT,
                    vibe_descriptors TEXT,  -- JSON array
                    neighborhood_cluster INTEGER,
                    opened_date DATE,
                    renovated_date DATE,
                    owner_group TEXT,
                    accepts_reservations BOOLEAN,
                    has_vip_area BOOLEAN,
                    outdoor_space BOOLEAN,
                    food_served BOOLEAN,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Time series data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS time_series_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venue_id TEXT NOT NULL,
                    metric_name TEXT NOT NULL,  -- 'instagram_posts', 'checkins', 'revenue'
                    metric_value REAL,
                    timestamp TIMESTAMP NOT NULL,
                    UNIQUE(venue_id, metric_name, timestamp)
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_instagram_venue ON instagram_posts(venue_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_instagram_date ON instagram_posts(posted_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_analytics_venue_date ON venue_analytics(venue_id, date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_interactions_user ON user_interactions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_venue ON ml_predictions(venue_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timeseries ON time_series_data(venue_id, metric_name)")
            
            conn.commit()
    
    # Instagram data methods
    def insert_instagram_post(self, post_data: Dict):
        """Insert scraped Instagram post"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO instagram_posts 
                (post_id, username, venue_id, venue_name, caption, likes, comments, 
                 engagement_rate, hashtags, location_lat, location_lng, posted_at, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_data['post_id'],
                post_data['username'],
                post_data.get('venue_id'),
                post_data.get('venue_name'),
                post_data['caption'],
                post_data['likes'],
                post_data['comments'],
                post_data['engagement_rate'],
                json.dumps(post_data.get('hashtags', [])),
                post_data.get('location_lat'),
                post_data.get('location_lng'),
                post_data['posted_at'],
                post_data.get('image_url')
            ))
            
            conn.commit()
    
    def get_venue_instagram_posts(self, venue_id: str, days: int = 30) -> List[Dict]:
        """Get recent Instagram posts for a venue"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM instagram_posts
                WHERE venue_id = ? 
                AND posted_at > datetime('now', '-' || ? || ' days')
                ORDER BY posted_at DESC
            """, (venue_id, days))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    # Analytics methods
    def update_venue_analytics(self, venue_id: str, date: str, analytics: Dict):
        """Update daily analytics for a venue"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO venue_analytics
                (venue_id, date, instagram_mentions, avg_engagement, sentiment_score,
                 trending_score, predicted_crowd, weather_condition, special_events)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                venue_id,
                date,
                analytics.get('instagram_mentions', 0),
                analytics.get('avg_engagement', 0),
                analytics.get('sentiment_score', 0),
                analytics.get('trending_score', 0),
                analytics.get('predicted_crowd', 0),
                analytics.get('weather_condition'),
                json.dumps(analytics.get('special_events', []))
            ))
            
            conn.commit()
    
    # User interaction methods
    def log_user_interaction(self, user_id: str, venue_id: str, 
                           interaction_type: str, rating: Optional[float] = None):
        """Log user interaction with a venue"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO user_interactions
                (user_id, venue_id, interaction_type, rating)
                VALUES (?, ?, ?, ?)
            """, (user_id, venue_id, interaction_type, rating))
            
            conn.commit()
    
    def get_user_interactions(self, user_id: str) -> pd.DataFrame:
        """Get user interaction history as DataFrame"""
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql_query("""
                SELECT * FROM user_interactions
                WHERE user_id = ?
                ORDER BY timestamp DESC
            """, conn, params=(user_id,))
    
    # ML prediction methods
    def save_prediction(self, venue_id: str, prediction_type: str, 
                       value: float, confidence: float, features: Dict):
        """Save ML model prediction"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ml_predictions
                (venue_id, prediction_type, predicted_value, confidence_score,
                 prediction_date, features_used, model_version)
                VALUES (?, ?, ?, ?, date('now'), ?, ?)
            """, (
                venue_id,
                prediction_type,
                value,
                confidence,
                json.dumps(features),
                '1.0'  # Model version
            ))
            
            conn.commit()
    
    def get_prediction_accuracy(self, prediction_type: str, days: int = 30) -> Dict:
        """Calculate prediction accuracy metrics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get predictions with actual values
            cursor.execute("""
                SELECT 
                    p.venue_id,
                    p.predicted_value,
                    p.confidence_score,
                    a.actual_crowd as actual_value
                FROM ml_predictions p
                JOIN venue_analytics a ON p.venue_id = a.venue_id 
                    AND p.prediction_date = a.date
                WHERE p.prediction_type = ?
                AND p.created_at > datetime('now', '-' || ? || ' days')
                AND a.actual_crowd IS NOT NULL
            """, (prediction_type, days))
            
            predictions = cursor.fetchall()
            
            if not predictions:
                return {'accuracy': 0, 'mae': 0, 'sample_size': 0}
            
            # Calculate metrics
            errors = [abs(pred[1] - pred[3]) for pred in predictions]
            mae = sum(errors) / len(errors)
            
            # Accuracy within 20% threshold
            accurate = sum(1 for e in errors if e < 20)
            accuracy = accurate / len(predictions)
            
            return {
                'accuracy': accuracy,
                'mae': mae,
                'sample_size': len(predictions)
            }
    
    # Time series methods
    def add_time_series_data(self, venue_id: str, metric_name: str, 
                            value: float, timestamp: datetime):
        """Add time series data point"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO time_series_data
                (venue_id, metric_name, metric_value, timestamp)
                VALUES (?, ?, ?, ?)
            """, (venue_id, metric_name, value, timestamp))
            
            conn.commit()
    
    def get_time_series(self, venue_id: str, metric_name: str, 
                       start_date: str = None) -> pd.DataFrame:
        """Get time series data as DataFrame"""
        with sqlite3.connect(self.db_path) as conn:
            query = """
                SELECT timestamp, metric_value
                FROM time_series_data
                WHERE venue_id = ? AND metric_name = ?
            """
            params = [venue_id, metric_name]
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            query += " ORDER BY timestamp"
            
            return pd.read_sql_query(query, conn, params=params,
                                    parse_dates=['timestamp'],
                                    index_col='timestamp')
    
    # Feature engineering methods
    def update_venue_features(self, venue_id: str, features: Dict):
        """Update ML features for a venue"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build dynamic update query
            set_clauses = []
            values = []
            
            for key, value in features.items():
                if key in ['music_genres', 'vibe_descriptors']:
                    set_clauses.append(f"{key} = ?")
                    values.append(json.dumps(value))
                else:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
            
            values.append(venue_id)
            
            cursor.execute(f"""
                UPDATE venue_features
                SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
                WHERE venue_id = ?
            """, values)
            
            if cursor.rowcount == 0:
                # Insert if not exists
                cursor.execute("""
                    INSERT INTO venue_features (venue_id) VALUES (?)
                """, (venue_id,))
                
                # Update with features
                cursor.execute(f"""
                    UPDATE venue_features
                    SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
                    WHERE venue_id = ?
                """, values)
            
            conn.commit()
    
    def get_training_data(self, feature_cols: List[str], 
                         target_col: str, days: int = 90) -> pd.DataFrame:
        """Get training data for ML models"""
        with sqlite3.connect(self.db_path) as conn:
            # Join relevant tables for training data
            query = f"""
                SELECT 
                    vf.*,
                    va.{target_col} as target,
                    va.date
                FROM venue_features vf
                JOIN venue_analytics va ON vf.venue_id = va.venue_id
                WHERE va.date > date('now', '-' || ? || ' days')
                AND va.{target_col} IS NOT NULL
            """
            
            df = pd.read_sql_query(query, conn, params=(days,))
            
            # Process JSON columns
            if 'music_genres' in df.columns:
                df['music_genres'] = df['music_genres'].apply(
                    lambda x: json.loads(x) if x else []
                )
            
            return df

# Example usage
if __name__ == "__main__":
    # Initialize ML database
    ml_db = MLDatabase()
    
    print("✅ ML Database initialized successfully")
    print("📊 Tables created: instagram_posts, venue_analytics, user_interactions, etc.")
    print("🔒 This database is separate from production and ready for ML experiments")