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
                    premium_expiry DATE,
                    referred_by INTEGER,
                    referral_count INTEGER DEFAULT 0,
                    is_banned BOOLEAN DEFAULT 0,
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
            
            # Payment proofs table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS payment_proofs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    file_id TEXT,
                    file_unique_id TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Support tickets table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS support_tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id TEXT UNIQUE,
                    user_id INTEGER,
                    subject TEXT,
                    status TEXT DEFAULT 'open',
                    priority TEXT DEFAULT 'normal',
                    assigned_agent_id INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    first_reply_at TIMESTAMP,
                    resolved_at TIMESTAMP,
                    sla_first_reply INTEGER DEFAULT 3600,
                    sla_resolution INTEGER DEFAULT 86400,
                    escalated BOOLEAN DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (assigned_agent_id) REFERENCES agents (id)
                )
            ''')
            
            # Support messages table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS support_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id TEXT,
                    sender_id INTEGER,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ticket_id) REFERENCES support_tickets (ticket_id)
                )
            ''')
            
            # Support attachments table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS support_attachments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id TEXT,
                    file_id TEXT,
                    file_unique_id TEXT,
                    file_type TEXT,
                    file_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ticket_id) REFERENCES support_tickets (ticket_id)
                )
            ''')
            
            # Agents table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    role TEXT DEFAULT 'support',
                    is_online BOOLEAN DEFAULT 0,
                    assigned_tickets INTEGER DEFAULT 0,
                    total_tickets_handled INTEGER DEFAULT 0,
                    total_tickets_closed INTEGER DEFAULT 0,
                    avg_reply_time INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # FAQ table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS faq (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keywords TEXT,
                    answer TEXT,
                    language TEXT DEFAULT 'en',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Bot settings table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS bot_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Initialize default settings
            await db.execute('''
                INSERT OR IGNORE INTO bot_settings (key, value) VALUES
                ('maintenance_mode', '0'),
                ('force_join_enabled', '0'),
                ('force_join_channel', ''),
                ('free_limit', '10'),
                ('premium_limit', '1000'),
                ('referral_bonus', '5'),
                ('flood_time', '60')
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
        if not user or not user.get('is_premium', False):
            return False
        
        # Check if premium has expired
        premium_expiry = user.get('premium_expiry')
        if premium_expiry:
            expiry_date = datetime.fromisoformat(premium_expiry)
            if datetime.now() > expiry_date:
                # Premium has expired, update status
                await self.set_premium(user_id, False)
                return False
        
        return True
    
    async def set_premium(self, user_id: int, is_premium: bool = True):
        """Set user premium status."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE users SET is_premium = ?, premium_expiry = NULL WHERE user_id = ?
                ''', (is_premium, user_id))
                await db.commit()
        except Exception as e:
            logger.error(f"Error setting premium for {user_id}: {e}")
    
    async def set_premium_with_expiry(self, user_id: int, days: int):
        """Set user premium status with expiry."""
        try:
            expiry_date = datetime.now() + timedelta(days=days)
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE users SET is_premium = 1, premium_expiry = ? WHERE user_id = ?
                ''', (expiry_date, user_id))
                await db.commit()
        except Exception as e:
            logger.error(f"Error setting premium with expiry for {user_id}: {e}")
    
    async def is_banned(self, user_id: int) -> bool:
        """Check if user is banned."""
        user = await self.get_user(user_id)
        return user.get('is_banned', False) if user else False
    
    async def ban_user(self, user_id: int, is_banned: bool = True):
        """Ban or unban a user."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE users SET is_banned = ? WHERE user_id = ?
                ''', (is_banned, user_id))
                await db.commit()
        except Exception as e:
            logger.error(f"Error banning user {user_id}: {e}")
    
    async def add_payment_proof(self, user_id: int, file_id: str, file_unique_id: str):
        """Add a payment proof."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO payment_proofs (user_id, file_id, file_unique_id)
                    VALUES (?, ?, ?)
                ''', (user_id, file_id, file_unique_id))
                await db.commit()
        except Exception as e:
            logger.error(f"Error adding payment proof for {user_id}: {e}")
    
    async def update_payment_status(self, user_id: int, status: str):
        """Update payment proof status."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE payment_proofs 
                    SET status = ?
                    WHERE user_id = ? AND status = 'pending'
                    ORDER BY created_at DESC
                    LIMIT 1
                ''', (status, user_id))
                await db.commit()
        except Exception as e:
            logger.error(f"Error updating payment status for {user_id}: {e}")
    
    async def get_all_users(self) -> List[dict]:
        """Get all users for broadcasting."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('SELECT * FROM users WHERE is_banned = 0') as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
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
    
    # Support Ticket Methods
    async def create_ticket(self, user_id: int, subject: str) -> str:
        """Create a new support ticket with unique ID."""
        import random
        import string
        
        # Generate unique ticket ID with retry logic
        max_attempts = 10
        for attempt in range(max_attempts):
            ticket_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            
            try:
                async with aiosqlite.connect(self.db_path) as db:
                    # Check if ticket ID already exists
                    async with db.execute(
                        'SELECT ticket_id FROM support_tickets WHERE ticket_id = ?',
                        (ticket_id,)
                    ) as cursor:
                        existing = await cursor.fetchone()
                    
                    if not existing:
                        # ID is unique, create ticket
                        await db.execute('''
                            INSERT INTO support_tickets (ticket_id, user_id, subject)
                            VALUES (?, ?, ?)
                        ''', (ticket_id, user_id, subject))
                        await db.commit()
                        return ticket_id
            except Exception as e:
                logger.error(f"Error creating ticket (attempt {attempt + 1}): {e}")
        
        # If all attempts failed, return None
        logger.error(f"Failed to create unique ticket ID after {max_attempts} attempts")
        return None
    
    async def get_ticket(self, ticket_id: str) -> Optional[dict]:
        """Get ticket information."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('''
                    SELECT * FROM support_tickets WHERE ticket_id = ?
                ''', (ticket_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error getting ticket {ticket_id}: {e}")
            return None
    
    async def add_ticket_message(self, ticket_id: str, sender_id: int, message: str):
        """Add a message to a ticket."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO support_messages (ticket_id, sender_id, message)
                    VALUES (?, ?, ?)
                ''', (ticket_id, sender_id, message))
                
                # Update first_reply_at if this is the first agent reply
                ticket = await self.get_ticket(ticket_id)
                if ticket and not ticket.get('first_reply_at'):
                    # Check if sender is an agent
                    is_agent = await self.is_agent(sender_id)
                    if is_agent:
                        await db.execute('''
                            UPDATE support_tickets 
                            SET first_reply_at = CURRENT_TIMESTAMP
                            WHERE ticket_id = ?
                        ''', (ticket_id,))
                
                await db.commit()
        except Exception as e:
            logger.error(f"Error adding message to ticket {ticket_id}: {e}")
    
    async def add_ticket_attachment(self, ticket_id: str, file_id: str, 
                                   file_unique_id: str, file_type: str, file_name: str = None):
        """Add an attachment to a ticket."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO support_attachments 
                    (ticket_id, file_id, file_unique_id, file_type, file_name)
                    VALUES (?, ?, ?, ?, ?)
                ''', (ticket_id, file_id, file_unique_id, file_type, file_name))
                await db.commit()
        except Exception as e:
            logger.error(f"Error adding attachment to ticket {ticket_id}: {e}")
    
    async def get_ticket_messages(self, ticket_id: str) -> List[dict]:
        """Get all messages for a ticket."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('''
                    SELECT * FROM support_messages 
                    WHERE ticket_id = ?
                    ORDER BY created_at ASC
                ''', (ticket_id,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting messages for ticket {ticket_id}: {e}")
            return []
    
    async def get_ticket_attachments(self, ticket_id: str) -> List[dict]:
        """Get all attachments for a ticket."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('''
                    SELECT * FROM support_attachments 
                    WHERE ticket_id = ?
                    ORDER BY created_at ASC
                ''', (ticket_id,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting attachments for ticket {ticket_id}: {e}")
            return []
    
    async def update_ticket_status(self, ticket_id: str, status: str):
        """Update ticket status."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                if status == 'resolved':
                    await db.execute('''
                        UPDATE support_tickets 
                        SET status = ?, resolved_at = CURRENT_TIMESTAMP
                        WHERE ticket_id = ?
                    ''', (status, ticket_id))
                else:
                    await db.execute('''
                        UPDATE support_tickets 
                        SET status = ?
                        WHERE ticket_id = ?
                    ''', (status, ticket_id))
                await db.commit()
        except Exception as e:
            logger.error(f"Error updating ticket status {ticket_id}: {e}")
    
    async def assign_ticket(self, ticket_id: str, agent_id: int):
        """Assign a ticket to an agent."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE support_tickets 
                    SET assigned_agent_id = ?
                    WHERE ticket_id = ?
                ''', (agent_id, ticket_id))
                
                # Update agent assigned_tickets count
                await db.execute('''
                    UPDATE agents 
                    SET assigned_tickets = assigned_tickets + 1
                    WHERE id = ?
                ''', (agent_id,))
                
                await db.commit()
        except Exception as e:
            logger.error(f"Error assigning ticket {ticket_id} to agent {agent_id}: {e}")
    
    async def get_user_tickets(self, user_id: int) -> List[dict]:
        """Get all tickets for a user."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('''
                    SELECT * FROM support_tickets 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting tickets for user {user_id}: {e}")
            return []
    
    async def get_open_tickets(self) -> List[dict]:
        """Get all open tickets."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('''
                    SELECT * FROM support_tickets 
                    WHERE status != 'resolved'
                    ORDER BY created_at ASC
                ''', ()) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting open tickets: {e}")
            return []
    
    # Agent Methods
    async def add_agent(self, user_id: int, role: str = 'support') -> bool:
        """Add a new agent."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR IGNORE INTO agents (user_id, role)
                    VALUES (?, ?)
                ''', (user_id, role))
                await db.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding agent {user_id}: {e}")
            return False
    
    async def is_agent(self, user_id: int) -> bool:
        """Check if user is an agent."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT id FROM agents WHERE user_id = ?
                ''', (user_id,)) as cursor:
                    row = await cursor.fetchone()
                    return row is not None
        except Exception as e:
            logger.error(f"Error checking if user {user_id} is agent: {e}")
            return False
    
    async def get_agent_by_user_id(self, user_id: int) -> Optional[dict]:
        """Get agent by user ID."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('''
                    SELECT * FROM agents WHERE user_id = ?
                ''', (user_id,)) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error getting agent for user {user_id}: {e}")
            return None
    
    async def get_least_busy_agent(self) -> Optional[dict]:
        """Get the agent with the fewest assigned tickets."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('''
                    SELECT * FROM agents 
                    WHERE is_online = 1
                    ORDER BY assigned_tickets ASC
                    LIMIT 1
                ''', ()) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error getting least busy agent: {e}")
            return None
    
    async def set_agent_online(self, user_id: int, is_online: bool):
        """Set agent online/offline status."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    UPDATE agents 
                    SET is_online = ?, last_active = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (is_online, user_id))
                await db.commit()
        except Exception as e:
            logger.error(f"Error setting agent {user_id} online status: {e}")
    
    async def get_all_agents(self) -> List[dict]:
        """Get all agents."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute('SELECT * FROM agents') as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting all agents: {e}")
            return []
    
    async def get_agent_tickets(self, user_id: int) -> List[dict]:
        """Get tickets assigned to a specific agent."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                # First get the agent's id from user_id
                async with db.execute(
                    'SELECT id FROM agents WHERE user_id = ?', (user_id,)
                ) as cursor:
                    agent = await cursor.fetchone()
                    if not agent:
                        return []
                    
                    agent_id = agent['id']
                
                # Get tickets assigned to this agent
                async with db.execute('''
                    SELECT * FROM support_tickets 
                    WHERE assigned_agent_id = ?
                    ORDER BY created_at DESC
                ''', (agent_id,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting agent tickets for user {user_id}: {e}")
            return []
    
    async def get_agent_stats(self, user_id: int) -> Optional[dict]:
        """Get statistics for a specific agent."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                # Get agent info
                async with db.execute(
                    'SELECT * FROM agents WHERE user_id = ?', (user_id,)
                ) as cursor:
                    agent = await cursor.fetchone()
                    if not agent:
                        return None
                    
                    agent_id = agent['id']
                
                # Count assigned tickets
                async with db.execute(
                    'SELECT COUNT(*) as count FROM support_tickets WHERE assigned_agent_id = ?',
                    (agent_id,)
                ) as cursor:
                    assigned = await cursor.fetchone()
                
                # Count resolved tickets
                async with db.execute(
                    'SELECT COUNT(*) as count FROM support_tickets WHERE assigned_agent_id = ? AND status = "closed"',
                    (agent_id,)
                ) as cursor:
                    resolved = await cursor.fetchone()
                
                return {
                    'assigned_tickets': assigned['count'] if assigned else 0,
                    'resolved_tickets': resolved['count'] if resolved else 0,
                    'is_online': bool(agent['is_online'])
                }
        except Exception as e:
            logger.error(f"Error getting agent stats for user {user_id}: {e}")
            return None
    
    # FAQ Methods
    async def search_faq(self, keywords: str, language: str = 'en') -> Optional[dict]:
        """Search FAQ by keywords."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                # Simple keyword matching
                keywords_lower = keywords.lower()
                async with db.execute('''
                    SELECT * FROM faq 
                    WHERE is_active = 1 
                    AND language = ?
                    AND LOWER(keywords) LIKE ?
                    LIMIT 1
                ''', (language, f'%{keywords_lower}%')) as cursor:
                    row = await cursor.fetchone()
                    if row:
                        return dict(row)
            return None
        except Exception as e:
            logger.error(f"Error searching FAQ: {e}")
            return None
    
    async def add_faq(self, keywords: str, answer: str, language: str = 'en'):
        """Add a new FAQ entry."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT INTO faq (keywords, answer, language)
                    VALUES (?, ?, ?)
                ''', (keywords, answer, language))
                await db.commit()
        except Exception as e:
            logger.error(f"Error adding FAQ: {e}")
    
    # Settings Methods
    async def get_setting(self, key: str) -> Optional[str]:
        """Get a bot setting."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.execute('''
                    SELECT value FROM bot_settings WHERE key = ?
                ''', (key,)) as cursor:
                    row = await cursor.fetchone()
                    return row[0] if row else None
        except Exception as e:
            logger.error(f"Error getting setting {key}: {e}")
            return None
    
    async def set_setting(self, key: str, value: str):
        """Set a bot setting."""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute('''
                    INSERT OR REPLACE INTO bot_settings (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, value))
                await db.commit()
        except Exception as e:
            logger.error(f"Error setting {key}: {e}")
