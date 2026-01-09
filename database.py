"""
Database module for the Telegram bot.
Handles all SQLite database operations including user management, referrals, and usage tracking.
"""

import aiosqlite
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)


class Database:
    """Handles all database operations for the bot."""
    
    def __init__(self, db_path: str):
        """Initialize database connection."""
        self.db_path = db_path
        
    async def initialize(self):
        """Create database tables if they don't exist."""
        async with aiosqlite.connect(self.db_path) as db:
            # Users table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    language_code TEXT,
                    is_premium BOOLEAN DEFAULT 0,
                    referred_by INTEGER,
                    referral_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Usage tracking table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    date DATE,
                    count INTEGER DEFAULT 0,
                    UNIQUE(user_id, date),
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Referrals table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER,
                    referred_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                    FOREIGN KEY (referred_id) REFERENCES users (user_id)
                )
            ''')
            
            # Flood control table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS flood_control (
                    user_id INTEGER PRIMARY KEY,
                    request_count INTEGER DEFAULT 0,
                    window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await db.commit()
            logger.info("Database initialized successfully")
    
    async def add_user(self, user_id: int, username: str = None, 
                      first_name: str = None, language_code: str = None,
                      referred_by: int = None) -> bool:
        """Add a new user to the database."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR IGNORE INTO users 
                    (user_id, username, first_name, language_code, referred_by)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, username, first_name, language_code, referred_by))
                
                # Update last_active for existing users
                await db.execute('''
                    UPDATE users SET last_active = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (user_id,))
                
                await db.commit()
                
                # If referred, update referrer's count
                if referred_by:
                    await self._update_referral_count(referred_by)
                    
                return True
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            return False
    
    async def _update_referral_count(self, referrer_id: int):
        """Update the referral count for a referrer."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE users 
                    SET referral_count = referral_count + 1
                    WHERE user_id = ?
                ''', (referrer_id,))
                await db.commit()
        except Exception as e:
            logger.error(f"Error updating referral count for {referrer_id}: {e}")
    
    async def get_user(self, user_id: int) -> Optional[dict]:
        """Get user information."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('''
                    SELECT * FROM users WHERE user_id = ?
                ''', (user_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def is_premium(self, user_id: int) -> bool:
        """Check if user is premium."""
        user = await self.get_user(user_id)
        return user.get('is_premium', False) if user else False
    
    async def set_premium(self, user_id: int, is_premium: bool = True):
        """Set user premium status."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE users SET is_premium = ? WHERE user_id = ?
                ''', (is_premium, user_id))
                await db.commit()
        except Exception as e:
            logger.error(f"Error setting premium for {user_id}: {e}")
    
    async def get_daily_usage(self, user_id: int) -> int:
        """Get user's usage count for today."""
        try:
            today = datetime.now().date()
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT count FROM usage 
                    WHERE user_id = ? AND date = ?
                ''', (user_id, today)) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else 0
        except Exception as e:
            logger.error(f"Error getting daily usage for {user_id}: {e}")
            return 0
    
    async def increment_usage(self, user_id: int):
        """Increment user's daily usage."""
        try:
            today = datetime.now().date()
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO usage (user_id, date, count)
                    VALUES (?, ?, 1)
                    ON CONFLICT(user_id, date) 
                    DO UPDATE SET count = count + 1
                ''', (user_id, today))
                await db.commit()
        except Exception as e:
            logger.error(f"Error incrementing usage for {user_id}: {e}")
    
    async def check_flood_control(self, user_id: int, threshold: int, 
                                  window_seconds: int) -> Tuple[bool, int]:
        """
        Check if user is flooding.
        Returns (is_flooding, wait_time).
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT request_count, window_start FROM flood_control
                    WHERE user_id = ?
                ''', (user_id,)) as cursor:
                    row = await cursor.fetchone()
                    
                    current_time = datetime.now()
                    
                    if not row:
                        # First request
                        await db.execute('''
                            INSERT INTO flood_control (user_id, request_count, window_start)
                            VALUES (?, 1, ?)
                        ''', (user_id, current_time))
                        await db.commit()
                        return False, 0
                    
                    request_count, window_start_str = row
                    window_start = datetime.fromisoformat(window_start_str)
                    time_elapsed = (current_time - window_start).total_seconds()
                    
                    if time_elapsed > window_seconds:
                        # Window expired, reset
                        await db.execute('''
                            UPDATE flood_control 
                            SET request_count = 1, window_start = ?
                            WHERE user_id = ?
                        ''', (current_time, user_id))
                        await db.commit()
                        return False, 0
                    
                    if request_count >= threshold:
                        # User is flooding
                        wait_time = int(window_seconds - time_elapsed)
                        return True, wait_time
                    
                    # Increment count
                    await db.execute('''
                        UPDATE flood_control 
                        SET request_count = request_count + 1
                        WHERE user_id = ?
                    ''', (user_id,))
                    await db.commit()
                    return False, 0
                    
        except Exception as e:
            logger.error(f"Error checking flood control for {user_id}: {e}")
            return False, 0
    
    async def get_referral_count(self, user_id: int) -> int:
        """Get number of successful referrals for a user."""
        user = await self.get_user(user_id)
        return user.get('referral_count', 0) if user else 0
    
    async def get_referral_link(self, user_id: int, bot_username: str) -> str:
        """Generate referral link for a user."""
        return f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    async def get_stats(self) -> dict:
        """Get overall bot statistics."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Total users
                async with db.execute('SELECT COUNT(*) FROM users') as cursor:
                    total_users = (await cursor.fetchone())[0]
                
                # Premium users
                async with db.execute(
                    'SELECT COUNT(*) FROM users WHERE is_premium = 1'
                ) as cursor:
                    premium_users = (await cursor.fetchone())[0]
                
                # Total requests today
                today = datetime.now().date()
                async with db.execute(
                    'SELECT SUM(count) FROM usage WHERE date = ?', (today,)
                ) as cursor:
                    row = await cursor.fetchone()
                    today_requests = row[0] if row[0] else 0
                
                return {
                    'total_users': total_users,
                    'premium_users': premium_users,
                    'today_requests': today_requests
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'total_users': 0,
                'premium_users': 0,
                'today_requests': 0
            }
