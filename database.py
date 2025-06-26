import sqlite3
from typing import Optional, List
from datetime import datetime
from auth import AdminUserInDB, get_password_hash
import json

class Database:
    def __init__(self, db_path: str = "nightlife.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create admin users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admin_users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE,
                    full_name TEXT,
                    hashed_password TEXT NOT NULL,
                    disabled BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            ''')
            
            # Create API keys table for future use
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    created_by INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (created_by) REFERENCES admin_users (id)
                )
            ''')
            
            # Create audit log table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    resource_type TEXT,
                    resource_id INTEGER,
                    details TEXT,
                    ip_address TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES admin_users (id)
                )
            ''')
            
            # Add admin_id to venues table if not exists
            cursor.execute('''
                PRAGMA table_info(venues)
            ''')
            columns = [column[1] for column in cursor.fetchall()]
            if 'created_by' not in columns:
                cursor.execute('''
                    ALTER TABLE venues ADD COLUMN created_by INTEGER REFERENCES admin_users(id)
                ''')
            if 'updated_at' not in columns:
                cursor.execute('''
                    ALTER TABLE venues ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ''')
            
            # Add admin_id to content table if not exists
            cursor.execute('''
                PRAGMA table_info(content)
            ''')
            columns = [column[1] for column in cursor.fetchall()]
            if 'created_by' not in columns:
                cursor.execute('''
                    ALTER TABLE content ADD COLUMN created_by INTEGER REFERENCES admin_users(id)
                ''')
            if 'updated_at' not in columns:
                cursor.execute('''
                    ALTER TABLE content ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ''')
            
            conn.commit()
    
    def create_admin_user(self, username: str, password: str, email: Optional[str] = None, 
                         full_name: Optional[str] = None) -> bool:
        """Create a new admin user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                hashed_password = get_password_hash(password)
                cursor.execute('''
                    INSERT INTO admin_users (username, email, full_name, hashed_password)
                    VALUES (?, ?, ?, ?)
                ''', (username, email, full_name, hashed_password))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_admin_user(self, username: str) -> Optional[AdminUserInDB]:
        """Get admin user by username"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM admin_users WHERE username = ?
            ''', (username,))
            row = cursor.fetchone()
            if row:
                return AdminUserInDB(
                    username=row['username'],
                    email=row['email'],
                    full_name=row['full_name'],
                    hashed_password=row['hashed_password'],
                    disabled=bool(row['disabled'])
                )
        return None
    
    def update_last_login(self, username: str):
        """Update last login timestamp"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE admin_users SET last_login = CURRENT_TIMESTAMP WHERE username = ?
            ''', (username,))
            conn.commit()
    
    def log_action(self, user_id: int, action: str, resource_type: Optional[str] = None,
                   resource_id: Optional[int] = None, details: Optional[dict] = None,
                   ip_address: Optional[str] = None):
        """Log admin actions for audit trail"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            details_json = json.dumps(details) if details else None
            cursor.execute('''
                INSERT INTO audit_log (user_id, action, resource_type, resource_id, details, ip_address)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, action, resource_type, resource_id, details_json, ip_address))
            conn.commit()
    
    def get_admin_user_id(self, username: str) -> Optional[int]:
        """Get admin user ID by username"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM admin_users WHERE username = ?', (username,))
            result = cursor.fetchone()
            return result[0] if result else None

# Initialize database
db = Database()

# Helper functions for auth.py
def get_admin_user(username: str) -> Optional[AdminUserInDB]:
    return db.get_admin_user(username)