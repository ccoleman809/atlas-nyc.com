"""
Content Moderation and ML Training System
Allows admin approval/denial of AI-generated content to train the ML models
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
import logging

class ModerationStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved" 
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"

class ContentType(Enum):
    VENUE_DESCRIPTION = "venue_description"
    ATMOSPHERE_TAGS = "atmosphere_tags"
    DEMOGRAPHICS = "demographics"
    DISCOVERY_RESULT = "discovery_result"
    ENHANCEMENT = "enhancement"

@dataclass
class ModerationItem:
    id: Optional[int]
    venue_id: str
    content_type: ContentType
    original_content: str
    ai_generated_content: str
    admin_feedback: Optional[str]
    status: ModerationStatus
    confidence_score: float
    created_at: str
    reviewed_at: Optional[str]
    reviewed_by: Optional[str]
    revision_notes: Optional[str]

@dataclass
class TrainingData:
    input_features: Dict
    expected_output: str
    feedback_type: str  # 'positive', 'negative', 'neutral'
    admin_notes: str
    venue_context: Dict

class ContentModerationSystem:
    """Manages content approval workflow and ML training data collection"""
    
    def __init__(self, db_path: str = "nightlife.db"):
        self.db_path = db_path
        self.init_moderation_tables()
        self.logger = logging.getLogger(__name__)
    
    def init_moderation_tables(self):
        """Initialize moderation and training tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Content moderation queue
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS content_moderation (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venue_id TEXT NOT NULL,
                    content_type TEXT NOT NULL,
                    original_content TEXT,
                    ai_generated_content TEXT NOT NULL,
                    admin_feedback TEXT,
                    status TEXT DEFAULT 'pending',
                    confidence_score REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reviewed_at TIMESTAMP,
                    reviewed_by TEXT,
                    revision_notes TEXT,
                    FOREIGN KEY (venue_id) REFERENCES venues (id)
                )
            ''')
            
            # Training data collected from admin feedback
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ml_training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    moderation_id INTEGER,
                    venue_id TEXT,
                    content_type TEXT,
                    input_features TEXT,  -- JSON
                    expected_output TEXT,
                    feedback_type TEXT,   -- positive, negative, neutral
                    admin_notes TEXT,
                    venue_context TEXT,   -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    used_for_training BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (moderation_id) REFERENCES content_moderation (id)
                )
            ''')
            
            # Admin preferences and guidelines
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_content_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    preference_type TEXT NOT NULL,  -- description_style, atmosphere_keywords, etc.
                    preference_value TEXT NOT NULL,
                    examples TEXT,  -- JSON array of examples
                    weight REAL DEFAULT 1.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    def submit_for_moderation(self, venue_id: str, content_type: ContentType, 
                            original_content: str, ai_generated_content: str, 
                            confidence_score: float) -> int:
        """Submit AI-generated content for admin moderation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO content_moderation 
                (venue_id, content_type, original_content, ai_generated_content, confidence_score)
                VALUES (?, ?, ?, ?, ?)
            ''', (venue_id, content_type.value, original_content, ai_generated_content, confidence_score))
            
            moderation_id = cursor.lastrowid
            conn.commit()
            
            self.logger.info(f"Submitted content for moderation: {moderation_id}")
            return moderation_id
    
    def get_pending_moderation_items(self, limit: int = 50) -> List[ModerationItem]:
        """Get pending items for admin review"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT cm.*, v.name as venue_name 
                FROM content_moderation cm
                LEFT JOIN venues v ON cm.venue_id = v.id
                WHERE cm.status = 'pending'
                ORDER BY cm.created_at DESC
                LIMIT ?
            ''', (limit,))
            
            items = []
            for row in cursor.fetchall():
                item = ModerationItem(
                    id=row['id'],
                    venue_id=row['venue_id'],
                    content_type=ContentType(row['content_type']),
                    original_content=row['original_content'] or '',
                    ai_generated_content=row['ai_generated_content'],
                    admin_feedback=row['admin_feedback'],
                    status=ModerationStatus(row['status']),
                    confidence_score=row['confidence_score'] or 0.0,
                    created_at=row['created_at'],
                    reviewed_at=row['reviewed_at'],
                    reviewed_by=row['reviewed_by'],
                    revision_notes=row['revision_notes']
                )
                items.append(item)
            
            return items
    
    def moderate_content(self, moderation_id: int, status: ModerationStatus, 
                        admin_username: str, feedback: str = None, 
                        revision_notes: str = None) -> bool:
        """Admin approves/rejects content and trains ML"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Update moderation status
            cursor.execute('''
                UPDATE content_moderation 
                SET status = ?, reviewed_at = CURRENT_TIMESTAMP, 
                    reviewed_by = ?, admin_feedback = ?, revision_notes = ?
                WHERE id = ?
            ''', (status.value, admin_username, feedback, revision_notes, moderation_id))
            
            # Get the moderation item for training data
            cursor.execute('''
                SELECT cm.*, v.name, v.venue_type, v.neighborhood, v.instagram_handle
                FROM content_moderation cm
                LEFT JOIN venues v ON cm.venue_id = v.id
                WHERE cm.id = ?
            ''', (moderation_id,))
            
            row = cursor.fetchone()
            if not row:
                return False
            
            # Create training data based on admin decision
            self._create_training_data(cursor, row, status, feedback or '')
            
            # If approved, apply the content to the venue
            if status == ModerationStatus.APPROVED:
                self._apply_approved_content(cursor, row)
            
            conn.commit()
            return True
    
    def _create_training_data(self, cursor, moderation_row, status: ModerationStatus, feedback: str):
        """Create training data from admin feedback"""
        venue_context = {
            'name': moderation_row[8],  # venue name
            'venue_type': moderation_row[9],
            'neighborhood': moderation_row[10],
            'instagram_handle': moderation_row[11]
        }
        
        # Determine feedback type
        feedback_type = 'positive' if status == ModerationStatus.APPROVED else 'negative'
        if status == ModerationStatus.NEEDS_REVISION:
            feedback_type = 'neutral'
        
        # Create input features based on content type
        input_features = self._extract_input_features(moderation_row, venue_context)
        
        # Expected output is the approved content or admin's preferred version
        expected_output = moderation_row[4]  # ai_generated_content
        if status == ModerationStatus.REJECTED and feedback:
            # Admin provided better content
            expected_output = feedback
        
        cursor.execute('''
            INSERT INTO ml_training_data 
            (moderation_id, venue_id, content_type, input_features, expected_output, 
             feedback_type, admin_notes, venue_context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            moderation_row[0],  # moderation_id
            moderation_row[1],  # venue_id
            moderation_row[2],  # content_type
            json.dumps(input_features),
            expected_output,
            feedback_type,
            feedback,
            json.dumps(venue_context)
        ))
    
    def _extract_input_features(self, moderation_row, venue_context: Dict) -> Dict:
        """Extract input features for ML training"""
        content_type = moderation_row[2]
        
        base_features = {
            'venue_name': venue_context['name'],
            'venue_type': venue_context['venue_type'],
            'neighborhood': venue_context['neighborhood'],
            'has_instagram': bool(venue_context.get('instagram_handle')),
            'original_content_length': len(moderation_row[3] or ''),
            'confidence_score': moderation_row[6] or 0.0
        }
        
        # Add content-type specific features
        if content_type == ContentType.VENUE_DESCRIPTION.value:
            base_features.update({
                'description_type': 'enhancement',
                'has_original_description': bool(moderation_row[3])
            })
        elif content_type == ContentType.ATMOSPHERE_TAGS.value:
            base_features.update({
                'tag_generation': True,
                'venue_category': venue_context['venue_type']
            })
        
        return base_features
    
    def _apply_approved_content(self, cursor, moderation_row):
        """Apply approved content to the venue"""
        venue_id = moderation_row[1]
        content_type = moderation_row[2]
        approved_content = moderation_row[4]
        
        if content_type == ContentType.VENUE_DESCRIPTION.value:
            cursor.execute('''
                UPDATE venues 
                SET ml_enhanced_description = ?, ml_last_enhanced = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (approved_content, venue_id))
        
        elif content_type == ContentType.ATMOSPHERE_TAGS.value:
            cursor.execute('''
                UPDATE venues 
                SET ml_atmosphere_tags = ?, ml_last_enhanced = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (approved_content, venue_id))
    
    def set_admin_preference(self, preference_type: str, preference_value: str, 
                           examples: List[str] = None, weight: float = 1.0):
        """Set admin content preferences for ML training"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if preference exists
            cursor.execute('''
                SELECT id FROM admin_content_preferences 
                WHERE preference_type = ?
            ''', (preference_type,))
            
            examples_json = json.dumps(examples or [])
            
            if cursor.fetchone():
                # Update existing preference
                cursor.execute('''
                    UPDATE admin_content_preferences 
                    SET preference_value = ?, examples = ?, weight = ?, 
                        updated_at = CURRENT_TIMESTAMP
                    WHERE preference_type = ?
                ''', (preference_value, examples_json, weight, preference_type))
            else:
                # Insert new preference
                cursor.execute('''
                    INSERT INTO admin_content_preferences 
                    (preference_type, preference_value, examples, weight)
                    VALUES (?, ?, ?, ?)
                ''', (preference_type, preference_value, examples_json, weight))
            
            conn.commit()
    
    def get_admin_preferences(self) -> Dict[str, Dict]:
        """Get all admin content preferences"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM admin_content_preferences 
                ORDER BY preference_type, weight DESC
            ''')
            
            preferences = {}
            for row in cursor.fetchall():
                preferences[row['preference_type']] = {
                    'value': row['preference_value'],
                    'examples': json.loads(row['examples']),
                    'weight': row['weight'],
                    'updated_at': row['updated_at']
                }
            
            return preferences
    
    def get_training_data(self, content_type: ContentType = None, 
                         feedback_type: str = None, limit: int = 1000) -> List[TrainingData]:
        """Get training data for ML model training"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = 'SELECT * FROM ml_training_data WHERE 1=1'
            params = []
            
            if content_type:
                query += ' AND content_type = ?'
                params.append(content_type.value)
            
            if feedback_type:
                query += ' AND feedback_type = ?'
                params.append(feedback_type)
            
            query += ' ORDER BY created_at DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            
            training_items = []
            for row in cursor.fetchall():
                item = TrainingData(
                    input_features=json.loads(row['input_features']),
                    expected_output=row['expected_output'],
                    feedback_type=row['feedback_type'],
                    admin_notes=row['admin_notes'],
                    venue_context=json.loads(row['venue_context'])
                )
                training_items.append(item)
            
            return training_items
    
    def get_moderation_stats(self) -> Dict:
        """Get moderation statistics for admin dashboard"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Pending items count
            cursor.execute("SELECT COUNT(*) FROM content_moderation WHERE status = 'pending'")
            pending_count = cursor.fetchone()[0]
            
            # Approval rate
            cursor.execute('''
                SELECT 
                    COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved,
                    COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected,
                    COUNT(*) as total
                FROM content_moderation 
                WHERE status IN ('approved', 'rejected')
            ''')
            approval_stats = cursor.fetchone()
            
            # Training data count
            cursor.execute("SELECT COUNT(*) FROM ml_training_data")
            training_data_count = cursor.fetchone()[0]
            
            # Recent activity
            cursor.execute('''
                SELECT status, COUNT(*) 
                FROM content_moderation 
                WHERE created_at >= datetime('now', '-7 days')
                GROUP BY status
            ''')
            recent_activity = dict(cursor.fetchall())
            
            approval_rate = 0
            if approval_stats[2] > 0:  # total > 0
                approval_rate = approval_stats[0] / approval_stats[2]  # approved / total
            
            return {
                'pending_items': pending_count,
                'approval_rate': approval_rate,
                'total_approved': approval_stats[0],
                'total_rejected': approval_stats[1],
                'training_data_points': training_data_count,
                'recent_activity': recent_activity
            }

    def bulk_approve_by_criteria(self, content_type: ContentType = None, 
                               min_confidence: float = 0.8) -> int:
        """Bulk approve high-confidence items matching criteria"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = '''
                UPDATE content_moderation 
                SET status = 'approved', reviewed_at = CURRENT_TIMESTAMP, 
                    reviewed_by = 'system_auto_approve'
                WHERE status = 'pending' AND confidence_score >= ?
            '''
            params = [min_confidence]
            
            if content_type:
                query += ' AND content_type = ?'
                params.append(content_type.value)
            
            cursor.execute(query, params)
            approved_count = cursor.rowcount
            
            # Apply approved content to venues
            cursor.execute('''
                SELECT cm.*, v.name, v.venue_type, v.neighborhood, v.instagram_handle
                FROM content_moderation cm
                LEFT JOIN venues v ON cm.venue_id = v.id
                WHERE cm.status = 'approved' AND cm.reviewed_by = 'system_auto_approve'
            ''')
            
            for row in cursor.fetchall():
                self._apply_approved_content(cursor, row)
                # Create positive training data
                self._create_training_data(cursor, row, ModerationStatus.APPROVED, 'Auto-approved for high confidence')
            
            conn.commit()
            return approved_count

# Integration with existing ML system
class ModeratedMLEnhancer:
    """ML Enhancer that uses moderation system for training"""
    
    def __init__(self, moderation_system: ContentModerationSystem):
        self.moderation_system = moderation_system
        
    async def enhance_venue_with_moderation(self, venue_data: Dict) -> Dict:
        """Enhanced venue processing with moderation queue"""
        from .smart_content_enhancer import SmartContentEnhancer
        
        enhancer = SmartContentEnhancer()
        enhancement = await enhancer.enhance_venue(venue_data)
        
        # Submit each type of content for moderation
        venue_id = venue_data['id']
        
        # Description moderation
        desc_mod_id = self.moderation_system.submit_for_moderation(
            venue_id=venue_id,
            content_type=ContentType.VENUE_DESCRIPTION,
            original_content=venue_data.get('description', ''),
            ai_generated_content=enhancement.enhanced_description,
            confidence_score=0.8  # Would use actual confidence from ML
        )
        
        # Atmosphere tags moderation
        tags_mod_id = self.moderation_system.submit_for_moderation(
            venue_id=venue_id,
            content_type=ContentType.ATMOSPHERE_TAGS,
            original_content='',
            ai_generated_content=','.join(enhancement.atmosphere_tags),
            confidence_score=0.75
        )
        
        return {
            'enhancement': enhancement,
            'moderation_ids': {
                'description': desc_mod_id,
                'atmosphere_tags': tags_mod_id
            },
            'status': 'pending_moderation'
        }

if __name__ == "__main__":
    # Example usage
    moderation = ContentModerationSystem()
    
    # Set admin preferences
    moderation.set_admin_preference(
        'description_style',
        'concise_engaging',
        examples=[
            'A vibrant cocktail lounge with craft drinks and intimate lighting',
            'Classic dive bar with authentic neighborhood charm'
        ]
    )
    
    # Get moderation stats
    stats = moderation.get_moderation_stats()
    print(f"Moderation stats: {stats}")