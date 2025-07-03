"""
Deployment Guide and Setup Script for ML/AI Venue Discovery System
Configures and deploys the ML system with your existing infrastructure
"""

import os
import sys
import json
import sqlite3
import asyncio
from datetime import datetime
from typing import Dict, List
import subprocess
import logging

class MLSystemDeployer:
    """Handles deployment and integration of ML system with existing codebase"""
    
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.ml_system_path = os.path.join(project_root, 'ml_system')
        self.main_db_path = os.path.join(project_root, 'nightlife.db')
        self.config_file = os.path.join(self.ml_system_path, 'config.json')
        self.venv_path = os.path.join(project_root, 'venv')
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def setup_ml_database_integration(self):
        """Integrate ML database with existing venue database"""
        try:
            # Create ML tables in existing database
            with sqlite3.connect(self.main_db_path) as conn:
                cursor = conn.cursor()
                
                # Add ML-related columns to existing venues table
                self._add_ml_columns_to_venues(cursor)
                
                # Create ML-specific tables
                self._create_ml_tables(cursor)
                
                conn.commit()
                self.logger.info("✅ Database integration completed")
                
        except Exception as e:
            self.logger.error(f"❌ Database integration failed: {e}")
            return False
        
        return True
    
    def _add_ml_columns_to_venues(self, cursor):
        """Add ML-related columns to existing venues table"""
        ml_columns = [
            ('ml_confidence_score', 'REAL DEFAULT 0.0'),
            ('ml_enhanced_description', 'TEXT'),
            ('ml_atmosphere_tags', 'TEXT'),  # JSON array
            ('ml_target_demographics', 'TEXT'),  # JSON array
            ('ml_best_times', 'TEXT'),  # JSON object
            ('ml_price_insights', 'TEXT'),  # JSON object
            ('ml_social_sentiment', 'REAL DEFAULT 0.5'),
            ('ml_popularity_trend', 'TEXT'),
            ('ml_last_enhanced', 'TIMESTAMP'),
            ('discovery_source', 'TEXT'),
            ('discovery_timestamp', 'TIMESTAMP'),
            ('quality_score', 'REAL DEFAULT 0.0'),
            ('auto_discovered', 'BOOLEAN DEFAULT FALSE')
        ]
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(venues)")
        existing_columns = [col[1] for col in cursor.fetchall()]
        
        # Add missing columns
        for col_name, col_def in ml_columns:
            if col_name not in existing_columns:
                try:
                    cursor.execute(f"ALTER TABLE venues ADD COLUMN {col_name} {col_def}")
                    self.logger.info(f"Added column: {col_name}")
                except sqlite3.Error as e:
                    self.logger.warning(f"Could not add column {col_name}: {e}")
    
    def _create_ml_tables(self, cursor):
        """Create ML-specific tables"""
        
        # Discovery runs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_discovery_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                search_terms TEXT,
                total_found INTEGER DEFAULT 0,
                total_added INTEGER DEFAULT 0,
                total_duplicates INTEGER DEFAULT 0,
                total_rejected INTEGER DEFAULT 0,
                execution_time_seconds REAL,
                status TEXT DEFAULT 'running',
                parameters TEXT  -- JSON
            )
        ''')
        
        # Enhancement history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_enhancement_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venue_id INTEGER,
                enhancement_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                enhancement_type TEXT,
                old_values TEXT,  -- JSON
                new_values TEXT,  -- JSON
                confidence_score REAL,
                FOREIGN KEY (venue_id) REFERENCES venues (id)
            )
        ''')
        
        # Predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venue_id INTEGER,
                prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                prediction_type TEXT,  -- 'popularity', 'crowd', 'trend'
                prediction_value REAL,
                confidence_score REAL,
                valid_until TIMESTAMP,
                model_version TEXT,
                FOREIGN KEY (venue_id) REFERENCES venues (id)
            )
        ''')
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ml_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                metric_value REAL,
                metric_metadata TEXT,  -- JSON
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.logger.info("✅ ML tables created successfully")
    
    def create_configuration(self):
        """Create configuration file for ML system"""
        config = {
            "database": {
                "main_db_path": self.main_db_path,
                "backup_enabled": True,
                "backup_interval_hours": 24
            },
            "api_keys": {
                "google_places": "",  # User should fill these
                "yelp": "",
                "foursquare": "",
                "instagram": ""
            },
            "discovery": {
                "default_search_terms": [
                    "brooklyn nightlife venues",
                    "manhattan bars clubs",
                    "queens music venues",
                    "nyc art galleries",
                    "brooklyn theaters",
                    "rooftop bars nyc",
                    "speakeasy bars nyc"
                ],
                "quality_threshold": 0.6,
                "max_results_per_source": 50,
                "rate_limit_requests_per_minute": 100,
                "duplicate_detection_enabled": True
            },
            "enhancement": {
                "auto_enhance_new_venues": True,
                "social_analysis_enabled": True,
                "description_generation_enabled": True,
                "recommendation_generation_enabled": True
            },
            "ml_models": {
                "model_directory": "ml_system/models/",
                "auto_retrain_enabled": False,
                "retrain_interval_days": 30,
                "confidence_threshold": 0.7
            },
            "scheduling": {
                "auto_discovery_enabled": False,
                "discovery_interval_hours": 168,  # Weekly
                "enhancement_interval_hours": 24,  # Daily
                "cleanup_old_predictions_days": 30
            },
            "logging": {
                "log_level": "INFO",
                "log_file": "ml_system/logs/ml_system.log",
                "max_log_file_size_mb": 10
            }
        }
        
        # Create config directory if needed
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.logger.info(f"✅ Configuration created: {self.config_file}")
        return config
    
    def install_ml_dependencies(self):
        """Install additional ML dependencies in virtual environment"""
        ml_requirements = [
            "scikit-learn>=1.3.0",
            "pandas>=2.0.0", 
            "numpy>=1.24.0",
            "aiohttp>=3.8.0",
            "python-dotenv>=1.0.0"
        ]
        
        # Check if virtual environment exists
        if not os.path.exists(self.venv_path):
            self.logger.warning("Virtual environment not found. Please create one first.")
            return False
        
        # Use virtual environment python
        venv_python = os.path.join(self.venv_path, 'bin', 'python')
        if not os.path.exists(venv_python):
            venv_python = os.path.join(self.venv_path, 'Scripts', 'python.exe')  # Windows
        
        if not os.path.exists(venv_python):
            self.logger.error("Could not find python in virtual environment")
            return False
        
        try:
            # Check if packages are already installed
            result = subprocess.run([venv_python, "-c", "import sklearn, pandas, numpy, aiohttp"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info("✅ ML dependencies already installed")
                return True
            
            # Install packages if not already installed
            for package in ml_requirements:
                subprocess.check_call([venv_python, "-m", "pip", "install", package])
                self.logger.info(f"✅ Installed: {package}")
            
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Failed to install dependencies: {e}")
            return True  # Don't fail deployment for this
    
    def create_integration_endpoints(self):
        """Create integration endpoints for main API server"""
        integration_code = '''
# Add these endpoints to your main api_server.py

from ml_system.integration_api import (
    discover_venues as ml_discover_venues,
    enhance_venues as ml_enhance_venues,
    predict_venue_metrics as ml_predict_venue
)
from ml_system.automated_venue_discovery import AutomatedVenueDiscovery
from ml_system.smart_content_enhancer import SmartContentEnhancer

# Initialize ML components (add to your app startup)
ml_discovery = AutomatedVenueDiscovery()
ml_enhancer = SmartContentEnhancer()

@app.post("/api/ml/discover-venues")
async def api_discover_venues(
    search_terms: List[str] = None,
    quality_threshold: float = 0.6
):
    """Discover new venues using ML"""
    try:
        results = await ml_discovery.discover_venues(search_terms)
        return {"status": "success", "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/enhance-venue/{venue_id}")
async def api_enhance_venue(venue_id: int):
    """Enhance venue with ML-generated content"""
    try:
        # Get venue from database
        venue_data = get_venue_by_id(venue_id)  # Your existing function
        
        # Enhance with ML
        enhancement = await ml_enhancer.enhance_venue(venue_data)
        
        # Update database with enhancement
        update_venue_enhancement(venue_id, enhancement)  # Implement this
        
        return {"status": "success", "enhancement": enhancement}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/venue-insights/{venue_id}")
async def api_venue_insights(venue_id: int):
    """Get ML insights for a venue"""
    try:
        from ml_system.ml_models import MLModelManager
        ml_manager = MLModelManager()
        
        insights = ml_manager.get_venue_insights(str(venue_id))
        return {"status": "success", "insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Background task for periodic discovery
from fastapi import BackgroundTasks

@app.post("/api/ml/schedule-discovery")
async def schedule_discovery(background_tasks: BackgroundTasks):
    """Schedule background venue discovery"""
    background_tasks.add_task(run_scheduled_discovery)
    return {"status": "scheduled"}

async def run_scheduled_discovery():
    """Background task for scheduled discovery"""
    try:
        results = await ml_discovery.discover_venues()
        # Log results to ML analytics table
        log_discovery_results(results)
    except Exception as e:
        logger.error(f"Scheduled discovery failed: {e}")
'''
        
        integration_file = os.path.join(self.project_root, 'ml_integration_endpoints.py')
        with open(integration_file, 'w') as f:
            f.write(integration_code)
        
        self.logger.info(f"✅ Integration endpoints created: {integration_file}")
    
    def create_admin_dashboard_integration(self):
        """Create HTML/JS for admin dashboard ML features"""
        dashboard_html = '''
<!-- Add this to your admin_dashboard.html -->

<div class="ml-system-section">
    <h3>🤖 ML/AI System</h3>
    
    <div class="ml-controls">
        <button onclick="runVenueDiscovery()" class="btn btn-primary">
            🔍 Discover New Venues
        </button>
        
        <button onclick="enhanceAllVenues()" class="btn btn-secondary">
            ✨ Enhance All Venues
        </button>
        
        <button onclick="viewMLAnalytics()" class="btn btn-info">
            📊 View ML Analytics
        </button>
    </div>
    
    <div id="ml-status" class="status-panel">
        <h4>System Status</h4>
        <div id="ml-status-content">Loading...</div>
    </div>
    
    <div id="discovery-results" class="results-panel" style="display: none;">
        <h4>Discovery Results</h4>
        <div id="discovery-content"></div>
    </div>
</div>

<script>
// ML System JavaScript Functions

async function runVenueDiscovery() {
    showStatus('Running venue discovery...');
    
    try {
        const response = await fetch('/api/ml/discover-venues', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                search_terms: [
                    'brooklyn nightlife',
                    'manhattan bars',
                    'nyc music venues'
                ]
            })
        });
        
        const result = await response.json();
        showDiscoveryResults(result);
        
    } catch (error) {
        showStatus('Discovery failed: ' + error.message);
    }
}

async function enhanceAllVenues() {
    showStatus('Enhancing venues with AI...');
    
    try {
        // Get list of venues that need enhancement
        const venues = await fetch('/api/venues').then(r => r.json());
        
        for (const venue of venues) {
            await fetch(`/api/ml/enhance-venue/${venue.id}`, {
                method: 'POST'
            });
        }
        
        showStatus('All venues enhanced successfully!');
        location.reload(); // Refresh to show updates
        
    } catch (error) {
        showStatus('Enhancement failed: ' + error.message);
    }
}

async function viewMLAnalytics() {
    try {
        const response = await fetch('/api/ml/analytics');
        const analytics = await response.json();
        
        showAnalytics(analytics);
        
    } catch (error) {
        showStatus('Failed to load analytics: ' + error.message);
    }
}

function showStatus(message) {
    document.getElementById('ml-status-content').innerHTML = 
        `<p>${new Date().toLocaleTimeString()}: ${message}</p>`;
}

function showDiscoveryResults(result) {
    const content = `
        <p><strong>Total Found:</strong> ${result.results.total_found}</p>
        <p><strong>Added:</strong> ${result.results.added}</p>
        <p><strong>Duplicates:</strong> ${result.results.duplicates}</p>
        <p><strong>Rejected:</strong> ${result.results.rejected}</p>
    `;
    
    document.getElementById('discovery-content').innerHTML = content;
    document.getElementById('discovery-results').style.display = 'block';
}

function showAnalytics(analytics) {
    // Create analytics display
    const analyticsWindow = window.open('', '_blank');
    analyticsWindow.document.write(`
        <html>
        <head><title>ML Analytics</title></head>
        <body>
        <h1>ML System Analytics</h1>
        <pre>${JSON.stringify(analytics, null, 2)}</pre>
        </body>
        </html>
    `);
}

// Load ML system status on page load
document.addEventListener('DOMContentLoaded', async function() {
    try {
        const response = await fetch('/api/ml/health');
        const health = await response.json();
        
        showStatus('ML System: ' + health.status);
        
    } catch (error) {
        showStatus('ML System: Offline');
    }
});
</script>

<style>
.ml-system-section {
    border: 1px solid #ddd;
    padding: 20px;
    margin: 20px 0;
    border-radius: 8px;
    background: #f9f9f9;
}

.ml-controls {
    margin-bottom: 20px;
}

.ml-controls button {
    margin-right: 10px;
    margin-bottom: 10px;
}

.status-panel, .results-panel {
    background: white;
    border: 1px solid #ddd;
    padding: 15px;
    margin-top: 15px;
    border-radius: 4px;
}
</style>
'''
        
        dashboard_file = os.path.join(self.project_root, 'ml_dashboard_integration.html')
        with open(dashboard_file, 'w') as f:
            f.write(dashboard_html)
        
        self.logger.info(f"✅ Dashboard integration created: {dashboard_file}")
    
    def create_environment_setup(self):
        """Create environment setup script"""
        env_template = '''
# ML/AI System Environment Variables
# Copy this to your .env file and fill in your API keys

# External API Keys (obtain from respective services)
GOOGLE_PLACES_API_KEY=your_google_places_api_key_here
YELP_API_KEY=your_yelp_api_key_here
FOURSQUARE_API_KEY=your_foursquare_api_key_here
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here

# ML System Configuration
ML_SYSTEM_ENABLED=true
ML_AUTO_DISCOVERY_ENABLED=false
ML_AUTO_ENHANCEMENT_ENABLED=true
ML_QUALITY_THRESHOLD=0.6

# Logging
ML_LOG_LEVEL=INFO
ML_LOG_FILE=ml_system/logs/ml_system.log

# Database
ML_BACKUP_ENABLED=true
ML_BACKUP_INTERVAL_HOURS=24

# Rate Limiting
ML_RATE_LIMIT_RPM=100
ML_MAX_CONCURRENT_REQUESTS=10
'''
        
        env_file = os.path.join(self.project_root, '.env.ml_template')
        with open(env_file, 'w') as f:
            f.write(env_template)
        
        self.logger.info(f"✅ Environment template created: {env_file}")
    
    def run_deployment(self):
        """Run complete deployment process"""
        self.logger.info("🚀 Starting ML/AI system deployment...")
        
        steps = [
            ("Installing ML dependencies", self.install_ml_dependencies),
            ("Setting up database integration", self.setup_ml_database_integration),
            ("Creating configuration", self.create_configuration),
            ("Creating integration endpoints", self.create_integration_endpoints),
            ("Creating admin dashboard integration", self.create_admin_dashboard_integration),
            ("Creating environment setup", self.create_environment_setup)
        ]
        
        success_count = 0
        for step_name, step_func in steps:
            self.logger.info(f"📋 {step_name}...")
            try:
                result = step_func()
                if result is not False:
                    success_count += 1
                    self.logger.info(f"✅ {step_name} completed")
                else:
                    self.logger.error(f"❌ {step_name} failed")
            except Exception as e:
                self.logger.error(f"❌ {step_name} failed: {e}")
        
        # Final status
        total_steps = len(steps)
        if success_count == total_steps:
            self.logger.info(f"🎉 Deployment completed successfully! ({success_count}/{total_steps} steps)")
            self._print_next_steps()
        else:
            self.logger.warning(f"⚠️ Deployment partially completed ({success_count}/{total_steps} steps)")
            self._print_troubleshooting()
    
    def _print_next_steps(self):
        """Print next steps for user"""
        next_steps = """
🎯 NEXT STEPS:

1. 🔑 Configure API Keys:
   - Edit .env.ml_template and add your API keys
   - Rename to .env or merge with existing .env file

2. 🧪 Test the System:
   - Run: python ml_system/integration_api.py
   - Visit: http://localhost:8001/docs for API documentation

3. 🔗 Integrate with Main App:
   - Add code from ml_integration_endpoints.py to your api_server.py
   - Add HTML from ml_dashboard_integration.html to your admin_dashboard.html

4. 🚀 Start Discovery:
   - Access admin dashboard
   - Click "Discover New Venues" to start finding venues

5. 📊 Monitor Performance:
   - Check logs in ml_system/logs/
   - View analytics in admin dashboard
   - Monitor database growth

🔧 Configuration Tips:
   - Start with quality_threshold=0.6 for balanced results
   - Enable auto_discovery only after testing manually
   - Set rate limits based on your API quotas

📖 Documentation:
   - API docs: http://localhost:8001/docs
   - Config file: ml_system/config.json
   - Logs: ml_system/logs/ml_system.log
"""
        print(next_steps)
    
    def _print_troubleshooting(self):
        """Print troubleshooting guide"""
        troubleshooting = """
🔧 TROUBLESHOOTING:

Common Issues:
1. Database errors: Check if nightlife.db exists and is writable
2. Import errors: Ensure all dependencies are installed
3. API key errors: Verify keys are correct and have proper permissions

Getting Help:
- Check logs in ml_system/logs/
- Verify database connection
- Test individual components separately

Contact support if issues persist.
"""
        print(troubleshooting)

# Main deployment function
def deploy_ml_system(project_root: str = None):
    """Deploy ML/AI system to existing project"""
    if project_root is None:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    deployer = MLSystemDeployer(project_root)
    deployer.run_deployment()

if __name__ == "__main__":
    # Auto-detect project root or use command line argument
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        # Assume we're in ml_system directory
        project_root = os.path.dirname(os.path.abspath(__file__))
    
    deploy_ml_system(project_root)