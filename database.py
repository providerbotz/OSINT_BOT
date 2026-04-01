import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict

class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Initialize all database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                join_date TEXT,
                total_searches INTEGER DEFAULT 0,
                last_search TEXT,
                is_blacklisted INTEGER DEFAULT 0
            )
        """)
        
        # Force join channels table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS force_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id TEXT UNIQUE,
                invite_link TEXT,
                added_date TEXT
            )
        """)
        
        # Search logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                group_id INTEGER,
                group_name TEXT,
                command TEXT,
                query TEXT,
                timestamp TEXT,
                success INTEGER DEFAULT 1
            )
        """)
        
        # Admin list table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY,
                added_date TEXT
            )
        """)
        
        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        # Groups/Channels table (for broadcast)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                chat_id INTEGER PRIMARY KEY,
                chat_title TEXT,
                chat_type TEXT,
                added_date TEXT
            )
        """)
        
        # Rate limiting table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                user_id INTEGER PRIMARY KEY,
                last_request TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    # ==========================================
    # USER OPERATIONS
    # ==========================================
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None):
        """Add or update user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO users (user_id, username, first_name, join_date)
            VALUES (?, ?, ?, ?)
        """, (user_id, username, first_name, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user details"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "user_id": row[0],
                "username": row[1],
                "first_name": row[2],
                "join_date": row[3],
                "total_searches": row[4],
                "last_search": row[5],
                "is_blacklisted": row[6]
            }
        return None
    
    def is_blacklisted(self, user_id: int) -> bool:
        """Check if user is blacklisted"""
        user = self.get_user(user_id)
        return user and user["is_blacklisted"] == 1
    
    def blacklist_user(self, user_id: int):
        """Blacklist a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_blacklisted = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    def unblacklist_user(self, user_id: int):
        """Remove user from blacklist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_blacklisted = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        conn.close()
    
    def get_all_users(self) -> List[Dict]:
        """Get all users"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        conn.close()
        
        users = []
        for row in rows:
            users.append({
                "user_id": row[0],
                "username": row[1],
                "first_name": row[2],
                "total_searches": row[4]
            })
        return users
    
    # ==========================================
    # FORCE CHANNEL OPERATIONS
    # ==========================================
    
    def add_force_channel(self, channel_id: str, invite_link: str):
        """Add force join channel"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO force_channels (channel_id, invite_link, added_date)
                VALUES (?, ?, ?)
            """, (channel_id, invite_link, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
    
    def remove_force_channel(self, channel_id: str):
        """Remove force join channel"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM force_channels WHERE channel_id = ?", (channel_id,))
        conn.commit()
        conn.close()
    
    def get_all_force_channels(self) -> List[Dict]:
        """Get all force join channels"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM force_channels")
        rows = cursor.fetchall()
        conn.close()
        
        channels = []
        for row in rows:
            channels.append({
                "id": row[0],
                "channel_id": row[1],
                "invite_link": row[2],
                "added_date": row[3]
            })
        return channels
    
    # ==========================================
    # SEARCH LOG OPERATIONS
    # ==========================================
    
    def log_search(self, user_id: int, username: str, group_id: int, 
                   group_name: str, command: str, query: str, success: bool = True):
        """Log a search"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO search_logs (user_id, username, group_id, group_name, command, query, timestamp, success)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username, group_id, group_name, command, query, 
              datetime.now().isoformat(), 1 if success else 0))
        
        # Update user's total searches
        cursor.execute("""
            UPDATE users 
            SET total_searches = total_searches + 1,
                last_search = ?
            WHERE user_id = ?
        """, (datetime.now().isoformat(), user_id))
        
        conn.commit()
        conn.close()
    
    def get_user_searches(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's recent searches"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM search_logs 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        
        searches = []
        for row in rows:
            searches.append({
                "command": row[4],
                "query": row[5],
                "timestamp": row[6]
            })
        return searches
    
    def get_total_searches(self) -> int:
        """Get total searches count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM search_logs")
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def get_command_stats(self) -> Dict[str, int]:
        """Get usage stats per command"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT command, COUNT(*) as count 
            FROM search_logs 
            GROUP BY command 
            ORDER BY count DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        
        stats = {}
        for row in rows:
            stats[row[0]] = row[1]
        return stats
    
    # ==========================================
    # ADMIN OPERATIONS
    # ==========================================
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
    def add_admin(self, user_id: int):
        """Add admin"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO admins (user_id, added_date)
            VALUES (?, ?)
        """, (user_id, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    # ==========================================
    # RATE LIMITING
    # ==========================================
    
    def check_rate_limit(self, user_id: int, seconds: int) -> tuple[bool, int]:
        """Check if user can make request (returns: can_request, seconds_remaining)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT last_request FROM rate_limits WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        
        if row:
            last_request = datetime.fromisoformat(row[0])
            time_diff = (datetime.now() - last_request).total_seconds()
            
            if time_diff < seconds:
                conn.close()
                return False, int(seconds - time_diff)
        
        conn.close()
        return True, 0
    
    def update_rate_limit(self, user_id: int):
        """Update user's last request time"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO rate_limits (user_id, last_request)
            VALUES (?, ?)
        """, (user_id, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    # ==========================================
    # BROADCAST OPERATIONS
    # ==========================================
    
    def get_all_user_ids(self) -> List[int]:
        """Get all user IDs for broadcast"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE is_blacklisted = 0")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]
    
    def add_group(self, chat_id: int, chat_title: str, chat_type: str):
        """Add group/channel to database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO groups (chat_id, chat_title, chat_type, added_date)
            VALUES (?, ?, ?, ?)
        """, (chat_id, chat_title, chat_type, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_all_chat_ids(self) -> List[int]:
        """Get all chat IDs (users + groups) for broadcast"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get user IDs
        cursor.execute("SELECT user_id FROM users WHERE is_blacklisted = 0")
        user_ids = [row[0] for row in cursor.fetchall()]
        
        # Get group IDs
        cursor.execute("SELECT chat_id FROM groups")
        group_ids = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        
        # Combine both
        return user_ids + group_ids
    
    # ==========================================
    # SETTINGS OPERATIONS
    # ==========================================
    
    def get_setting(self, key: str, default: str = None) -> str:
        """Get setting value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else default
    
    def set_setting(self, key: str, value: str):
        """Set setting value"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
        """, (key, value))
        conn.commit()
        conn.close()
    
    def is_maintenance_mode(self) -> bool:
        """Check if maintenance mode is enabled"""
        return self.get_setting("maintenance_mode", "off") == "on"
    
    def set_maintenance_mode(self, enabled: bool):
        """Enable or disable maintenance mode"""
        self.set_setting("maintenance_mode", "on" if enabled else "off")
