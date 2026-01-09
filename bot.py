"""
Main bot module for YouTube Thumbnail Extractor Telegram Bot - 2026 Edition.
Built with python-telegram-bot v20+ with complete support system and ReplyKeyboard UI.
"""

import logging
import configparser
import sys
import os
import zipfile
import tempfile
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler,
)

from database import Database
from youtube_utils import YouTubeExtractor
from i18n import I18n

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
(MAIN_MENU, ADMIN_MENU, SUPPORT_MENU, TICKET_SUBJECT, TICKET_MESSAGE, 
 TICKET_ATTACHMENT, VIDEO_QUALITY_SELECT, AGENT_MENU) = range(8)


class ThumbnailBot:
    """Main bot class with ReplyKeyboard interface."""
    
    def __init__(self, config_path: str = 'config.ini'):
        """Initialize the bot with configuration."""
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # Get configuration values
        self.token = self.config.get('bot', 'token')
        self.admin_ids = [
            int(id.strip()) 
            for id in self.config.get('bot', 'admin_ids', fallback='').split(',')
            if id.strip()
        ]
        
        db_path = self.config.get('database', 'path', fallback='bot_data.db')
        self.db = Database(db_path)
        
        self.free_limit = self.config.getint('limits', 'free_daily_limit', fallback=10)
        self.premium_limit = self.config.getint('limits', 'premium_daily_limit', fallback=1000)
        self.flood_threshold = self.config.getint('limits', 'flood_threshold', fallback=5)
        self.flood_window = self.config.getint('limits', 'flood_window', fallback=60)
        
        self.referral_bonus = self.config.getint('referral', 'bonus_uses', fallback=5)
        self.premium_referrals = self.config.getint('referral', 'premium_referrals_required', fallback=10)
        
        default_lang = self.config.get('languages', 'default', fallback='en')
        self.i18n = I18n(default_lang)
        
        self.youtube = YouTubeExtractor()
        
        # Store active tickets for users
        self.user_contexts = {}
        
        logger.info("Bot initialized successfully")
    
    def get_main_keyboard(self, user_id: int, is_premium: bool = False, 
                         is_admin: bool = False, is_agent: bool = False):
        """Get main menu keyboard based on user role."""
        keyboard = [
            ['📹 Get Thumbnail', '📊 My Stats'],
            ['🎁 Referrals', '💎 Premium'],
            ['❓ Help', '💬 Support'],
        ]
        
        if is_admin:
            keyboard.append(['👑 Admin Panel'])
        
        if is_agent:
            keyboard.append(['🎫 Agent Panel'])
        
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    def get_admin_keyboard(self):
        """Get admin panel keyboard."""
        keyboard = [
            ['📊 Bot Stats', '👥 User Management'],
            ['📢 Broadcast', '🎫 Support Tickets'],
            ['⚙️ Settings', '👨‍💼 Agent Management'],
            ['🔙 Back to Main']
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    def get_settings_keyboard(self):
        """Get settings keyboard."""
        keyboard = [
            ['🔧 Maintenance Mode', '🔗 Force Join'],
            ['📝 FAQ Management', '💰 Limits'],
            ['🔙 Back to Admin']
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    def get_support_keyboard(self):
        """Get support menu keyboard."""
        keyboard = [
            ['🎫 Create Ticket', '📋 My Tickets'],
            ['❓ FAQ', '🔙 Back to Main']
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    def get_agent_keyboard(self):
        """Get agent panel keyboard."""
        keyboard = [
            ['📋 Open Tickets', '✅ My Tickets'],
            ['🟢 Go Online', '🔴 Go Offline'],
            ['📊 My Stats', '🔙 Back to Main']
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    def get_quality_keyboard(self):
        """Get thumbnail quality selection keyboard."""
        keyboard = [
            ['🎨 MaxRes', '📺 HD'],
            ['📱 Medium', '⚡ All Qualities'],
            ['🔙 Cancel']
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        user_id = user.id
        
        # Check maintenance mode
        maintenance = await self.db.get_setting('maintenance_mode')
        if maintenance == '1' and user_id not in self.admin_ids:
            await update.message.reply_text(
                "🚧 Bot is under maintenance. Please try again later."
            )
            return
        
        # Check for referral
        referred_by = None
        if context.args and context.args[0].startswith('ref_'):
            try:
                referred_by = int(context.args[0][4:])
                if referred_by == user_id:
                    referred_by = None  # Can't refer yourself
            except ValueError:
                pass
        
        # Add user to database
        await self.db.add_user(
            user_id=user_id,
            username=user.username,
            first_name=user.first_name,
            language_code=user.language_code,
            referred_by=referred_by
        )
        
        # Check force join channel
        force_join = await self.db.get_setting('force_join_enabled')
        if force_join == '1':
            channel = await self.db.get_setting('force_join_channel')
            if channel:
                try:
                    member = await context.bot.get_chat_member(channel, user_id)
                    if member.status not in ['member', 'administrator', 'creator']:
                        keyboard = [[KeyboardButton(f'✅ Join {channel}')]]
                        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
                        await update.message.reply_text(
                            f"⚠️ Please join our channel {channel} to use this bot.",
                            reply_markup=reply_markup
                        )
                        return
                except Exception as e:
                    logger.error(f"Error checking channel membership: {e}")
        
        # Handle referral bonus
        if referred_by:
            referral_count = await self.db.get_referral_count(referred_by)
            if referral_count >= self.premium_referrals:
                await self.db.set_premium(referred_by, True)
                try:
                    await context.bot.send_message(
                        chat_id=referred_by,
                        text="🎉 You've earned Premium status through referrals! 💎"
                    )
                except Exception as e:
                    logger.error(f"Could not notify referrer {referred_by}: {e}")
        
        is_premium = await self.db.is_premium(user_id)
        is_admin = user_id in self.admin_ids
        is_agent = await self.db.is_agent(user_id)
        
        welcome_text = (
            f"👋 Welcome to YouTube Thumbnail Extractor, {user.first_name}!\n\n"
            f"🎥 Get high-quality YouTube thumbnails in seconds\n"
            f"💎 {'Premium User' if is_premium else 'Free User'}\n\n"
            f"Use the menu below to navigate:"
        )
        
        keyboard = self.get_main_keyboard(user_id, is_premium, is_admin, is_agent)
        await update.message.reply_text(welcome_text, reply_markup=keyboard)
        
        return MAIN_MENU
    
    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle main menu selections."""
        user_id = update.effective_user.id
        text = update.message.text
        
        # Check maintenance mode
        maintenance = await self.db.get_setting('maintenance_mode')
        if maintenance == '1' and user_id not in self.admin_ids:
            await update.message.reply_text(
                "🚧 Bot is under maintenance. Please try again later."
            )
            return MAIN_MENU
        
        is_premium = await self.db.is_premium(user_id)
        is_admin = user_id in self.admin_ids
        is_agent = await self.db.is_agent(user_id)
        
        if text == '📹 Get Thumbnail':
            await update.message.reply_text(
                "📹 Please send me a YouTube link or video ID:\n\n"
                "Examples:\n"
                "• https://youtube.com/watch?v=VIDEO_ID\n"
                "• https://youtu.be/VIDEO_ID\n"
                "• https://youtube.com/shorts/VIDEO_ID\n"
                "• VIDEO_ID",
                reply_markup=self.get_main_keyboard(user_id, is_premium, is_admin, is_agent)
            )
            return MAIN_MENU
        
        elif text == '📊 My Stats':
            await self.show_stats(update, context)
            return MAIN_MENU
        
        elif text == '🎁 Referrals':
            await self.show_referrals(update, context)
            return MAIN_MENU
        
        elif text == '💎 Premium':
            await self.show_premium(update, context)
            return MAIN_MENU
        
        elif text == '❓ Help':
            await self.show_help(update, context)
            return MAIN_MENU
        
        elif text == '💬 Support':
            keyboard = self.get_support_keyboard()
            await update.message.reply_text(
                "💬 Support Center\n\n"
                "How can we help you today?",
                reply_markup=keyboard
            )
            return SUPPORT_MENU
        
        elif text == '👑 Admin Panel' and is_admin:
            keyboard = self.get_admin_keyboard()
            await update.message.reply_text(
                "👑 Admin Panel\n\n"
                "Select an option:",
                reply_markup=keyboard
            )
            return ADMIN_MENU
        
        elif text == '🎫 Agent Panel' and is_agent:
            keyboard = self.get_agent_keyboard()
            await update.message.reply_text(
                "🎫 Agent Panel\n\n"
                "Select an option:",
                reply_markup=keyboard
            )
            return AGENT_MENU
        
        else:
            # Try to process as YouTube link
            return await self.handle_youtube_link(update, context)
    
    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user statistics."""
        user_id = update.effective_user.id
        user_data = await self.db.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ Error loading your data.")
            return
        
        usage = await self.db.get_daily_usage(user_id)
        is_premium = await self.db.is_premium(user_id)
        limit = self.premium_limit if is_premium else self.free_limit
        referrals = await self.db.get_referral_count(user_id)
        
        stats_text = (
            f"📊 Your Statistics\n\n"
            f"📈 Daily Usage: {usage}/{limit}\n"
            f"👥 Referrals: {referrals}\n"
            f"💎 Status: {'Premium ✅' if is_premium else 'Free'}\n"
            f"📅 Member Since: {user_data['created_at'][:10]}"
        )
        
        await update.message.reply_text(stats_text)
    
    async def show_referrals(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show referral information."""
        user_id = update.effective_user.id
        bot_user = await context.bot.get_me()
        
        referral_link = await self.db.get_referral_link(user_id, bot_user.username)
        referral_count = await self.db.get_referral_count(user_id)
        
        referral_text = (
            f"🎁 Referral Program\n\n"
            f"📊 Your Referrals: {referral_count}\n"
            f"🎯 Needed for Premium: {self.premium_referrals}\n\n"
            f"💰 Each referral gives you {self.referral_bonus} bonus requests!\n"
            f"💎 Get {self.premium_referrals} referrals for FREE Premium!\n\n"
            f"🔗 Your Link:\n{referral_link}"
        )
        
        await update.message.reply_text(referral_text)
    
    async def show_premium(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show premium information."""
        user_id = update.effective_user.id
        is_premium = await self.db.is_premium(user_id)
        referrals = await self.db.get_referral_count(user_id)
        
        if is_premium:
            premium_text = (
                f"💎 You are a Premium Member!\n\n"
                f"✅ {self.premium_limit} requests/day\n"
                f"✅ Priority processing\n"
                f"✅ No ads\n"
                f"✅ ZIP downloads\n"
                f"✅ Premium support"
            )
        else:
            premium_text = (
                f"💎 Premium Benefits\n\n"
                f"✅ {self.premium_limit} requests/day (vs {self.free_limit})\n"
                f"✅ Priority processing\n"
                f"✅ No ads\n"
                f"✅ ZIP downloads\n"
                f"✅ Premium support\n\n"
                f"🎁 Ways to get Premium:\n"
                f"1. Refer {self.premium_referrals} friends (You have {referrals})\n"
                f"2. Use /premium command for payment options"
            )
        
        await update.message.reply_text(premium_text)
    
    async def show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help information."""
        help_text = (
            "❓ How to Use\n\n"
            "📹 Get Thumbnail:\n"
            "• Click '📹 Get Thumbnail'\n"
            "• Send any YouTube link or video ID\n"
            "• Choose quality (MaxRes, HD, Medium, or All)\n"
            "• Receive thumbnails instantly!\n\n"
            "💬 Support:\n"
            "• Create support tickets\n"
            "• Attach files/screenshots\n"
            "• Track ticket status\n\n"
            "🎁 Referrals:\n"
            "• Share your link\n"
            "• Earn bonuses\n"
            "• Get free premium!\n\n"
            "💎 Premium:\n"
            "• Higher limits\n"
            "• Premium features\n"
            "• Priority support"
        )
        
        await update.message.reply_text(help_text)
    
    async def handle_youtube_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle YouTube link processing."""
        user_id = update.effective_user.id
        text = update.message.text
        
        # Check if user is banned
        is_banned = await self.db.is_banned(user_id)
        if is_banned:
            await update.message.reply_text("🚫 You have been banned from using this bot.")
            return
        
        # Check flood control
        is_flooding, wait_time = await self.db.check_flood_control(
            user_id, self.flood_threshold, self.flood_window
        )
        
        if is_flooding:
            await update.message.reply_text(
                f"⚠️ Please slow down! Wait {wait_time} seconds before trying again."
            )
            return
        
        # Check daily limit
        is_premium = await self.db.is_premium(user_id)
        limit = self.premium_limit if is_premium else self.free_limit
        usage = await self.db.get_daily_usage(user_id)
        
        if usage >= limit:
            await update.message.reply_text(
                f"⚠️ Daily limit reached ({limit} requests).\n"
                f"💎 Upgrade to Premium for {self.premium_limit} requests/day!\n"
                f"🎁 Or refer friends: /referral"
            )
            return
        
        # Extract video ID
        video_id = self.youtube.extract_video_id(text)
        
        if not video_id:
            await update.message.reply_text(
                "❌ Invalid YouTube link or video ID.\n\n"
                "Please send a valid YouTube link or video ID."
            )
            return
        
        # Store video ID in context
        context.user_data['video_id'] = video_id
        
        # Show quality selection
        keyboard = self.get_quality_keyboard()
        await update.message.reply_text(
            f"✅ Video ID: {video_id}\n\n"
            f"📸 Choose thumbnail quality:",
            reply_markup=keyboard
        )
        
        return VIDEO_QUALITY_SELECT
    
    async def handle_quality_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle thumbnail quality selection."""
        user_id = update.effective_user.id
        text = update.message.text
        video_id = context.user_data.get('video_id')
        
        if not video_id:
            await update.message.reply_text("❌ Error: No video ID found. Please try again.")
            is_premium = await self.db.is_premium(user_id)
            is_admin = user_id in self.admin_ids
            is_agent = await self.db.is_agent(user_id)
            keyboard = self.get_main_keyboard(user_id, is_premium, is_admin, is_agent)
            await update.message.reply_text("Returning to main menu...", reply_markup=keyboard)
            return MAIN_MENU
        
        if text == '🔙 Cancel':
            is_premium = await self.db.is_premium(user_id)
            is_admin = user_id in self.admin_ids
            is_agent = await self.db.is_agent(user_id)
            keyboard = self.get_main_keyboard(user_id, is_premium, is_admin, is_agent)
            await update.message.reply_text("❌ Cancelled.", reply_markup=keyboard)
            return MAIN_MENU
        
        # Get thumbnails
        thumbnails = self.youtube.get_thumbnails(video_id)
        
        # Filter based on quality selection using quality field
        selected_thumbnails = []
        
        if text == '🎨 MaxRes':
            # MaxRes quality thumbnails
            selected_thumbnails = [t for t in thumbnails if 'Maximum' in t['quality'] or 'maxres' in t['filename'].lower()]
        elif text == '📺 HD':
            # HD quality thumbnails (SD and HQ)
            selected_thumbnails = [t for t in thumbnails if 'High' in t['quality'] or 'Standard' in t['quality']]
        elif text == '📱 Medium':
            # Medium quality thumbnails
            selected_thumbnails = [t for t in thumbnails if 'Medium' in t['quality']]
        elif text == '⚡ All Qualities':
            selected_thumbnails = thumbnails
        else:
            await update.message.reply_text("❌ Invalid selection. Please choose a quality option.")
            return VIDEO_QUALITY_SELECT
        
        if not selected_thumbnails:
            await update.message.reply_text(
                f"❌ No thumbnails found for quality: {text}\n\n"
                f"Try selecting '⚡ All Qualities' instead."
            )
            return VIDEO_QUALITY_SELECT
        
        # Send processing message
        processing_msg = await update.message.reply_text("⏳ Downloading thumbnails...")
        
        # Send thumbnails
        sent_count = 0
        for thumb in selected_thumbnails:
            if await self.youtube.check_thumbnail_exists(thumb['url']):
                try:
                    await update.message.reply_photo(
                        photo=thumb['url'],
                        caption=f"🎨 {thumb['quality']}"
                    )
                    sent_count += 1
                except Exception as e:
                    logger.warning(f"Could not send thumbnail {thumb['quality']}: {e}")
        
        if sent_count > 0:
            await processing_msg.edit_text(
                f"✅ Sent {sent_count} thumbnail(s)!\n\n"
                f"Need more? Send another link!"
            )
            
            # Increment usage
            await self.db.increment_usage(user_id)
        else:
            await processing_msg.edit_text("❌ No thumbnails could be sent.")
        
        # Return to main menu
        is_premium = await self.db.is_premium(user_id)
        is_admin = user_id in self.admin_ids
        is_agent = await self.db.is_agent(user_id)
        keyboard = self.get_main_keyboard(user_id, is_premium, is_admin, is_agent)
        await update.message.reply_text("What would you like to do next?", reply_markup=keyboard)
        
        return MAIN_MENU
    
    async def handle_support_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle support menu selections."""
        user_id = update.effective_user.id
        text = update.message.text
        
        if text == '🎫 Create Ticket':
            await update.message.reply_text(
                "🎫 Create Support Ticket\n\n"
                "Please enter the subject of your issue:",
                reply_markup=ReplyKeyboardRemove()
            )
            return TICKET_SUBJECT
        
        elif text == '📋 My Tickets':
            tickets = await self.db.get_user_tickets(user_id)
            
            if not tickets:
                await update.message.reply_text(
                    "📋 You have no support tickets yet.\n\n"
                    "Create a new ticket to get help!"
                )
            else:
                ticket_list = "📋 Your Support Tickets:\n\n"
                for ticket in tickets[:10]:  # Show last 10
                    status_emoji = "🟢" if ticket['status'] == 'open' else "🔴"
                    ticket_list += (
                        f"{status_emoji} {ticket['ticket_id']}\n"
                        f"Subject: {ticket['subject']}\n"
                        f"Status: {ticket['status']}\n"
                        f"Created: {ticket['created_at'][:16]}\n\n"
                    )
                
                await update.message.reply_text(ticket_list)
            
            return SUPPORT_MENU
        
        elif text == '❓ FAQ':
            await self.show_faq(update, context)
            return SUPPORT_MENU
        
        elif text == '🔙 Back to Main':
            is_premium = await self.db.is_premium(user_id)
            is_admin = user_id in self.admin_ids
            is_agent = await self.db.is_agent(user_id)
            keyboard = self.get_main_keyboard(user_id, is_premium, is_admin, is_agent)
            await update.message.reply_text("Returning to main menu...", reply_markup=keyboard)
            return MAIN_MENU
        
        else:
            # Check FAQ for auto-reply
            faq = await self.db.search_faq(text)
            if faq:
                await update.message.reply_text(
                    f"💡 FAQ Answer:\n\n{faq['answer']}\n\n"
                    f"Need more help? Create a support ticket!"
                )
            else:
                await update.message.reply_text(
                    "❌ Unknown command. Please use the menu buttons."
                )
            
            return SUPPORT_MENU
    
    async def handle_ticket_subject(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle ticket subject input."""
        user_id = update.effective_user.id
        subject = update.message.text
        
        # Store subject in context
        context.user_data['ticket_subject'] = subject
        
        await update.message.reply_text(
            f"📝 Subject: {subject}\n\n"
            f"Now, please describe your issue in detail:"
        )
        
        return TICKET_MESSAGE
    
    async def handle_ticket_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle ticket message input."""
        user_id = update.effective_user.id
        message = update.message.text
        subject = context.user_data.get('ticket_subject', 'No Subject')
        
        # Create ticket
        ticket_id = await self.db.create_ticket(user_id, subject)
        
        if not ticket_id:
            await update.message.reply_text("❌ Error creating ticket. Please try again.")
            keyboard = self.get_support_keyboard()
            await update.message.reply_text("Returning to support menu...", reply_markup=keyboard)
            return SUPPORT_MENU
        
        # Add message to ticket
        await self.db.add_ticket_message(ticket_id, user_id, message)
        
        # Auto-assign to least busy agent
        agent = await self.db.get_least_busy_agent()
        if agent:
            await self.db.assign_ticket(ticket_id, agent['id'])
            # Notify agent
            try:
                await context.bot.send_message(
                    chat_id=agent['user_id'],
                    text=(
                        f"🎫 New Ticket Assigned: {ticket_id}\n"
                        f"Subject: {subject}\n"
                        f"User: {user_id}\n\n"
                        f"Message: {message}"
                    )
                )
            except Exception as e:
                logger.error(f"Could not notify agent {agent['user_id']}: {e}")
        
        # Store ticket in context
        context.user_data['active_ticket'] = ticket_id
        
        keyboard = [
            ['📎 Add Attachment', '✅ Submit Ticket'],
            ['🔙 Back to Support']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            f"✅ Ticket Created: {ticket_id}\n\n"
            f"Subject: {subject}\n\n"
            f"You can add attachments or submit the ticket now.",
            reply_markup=reply_markup
        )
        
        return TICKET_ATTACHMENT
    
    async def handle_ticket_attachment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle ticket attachment or submission."""
        user_id = update.effective_user.id
        text = update.message.text if update.message.text else None
        ticket_id = context.user_data.get('active_ticket')
        
        if not ticket_id:
            await update.message.reply_text("❌ Error: No active ticket. Please create a new ticket.")
            keyboard = self.get_support_keyboard()
            await update.message.reply_text("Returning to support menu...", reply_markup=keyboard)
            return SUPPORT_MENU
        
        if text == '✅ Submit Ticket':
            keyboard = self.get_support_keyboard()
            await update.message.reply_text(
                f"✅ Ticket {ticket_id} submitted successfully!\n\n"
                f"Our support team will respond soon.\n"
                f"You'll be notified when there's an update.",
                reply_markup=keyboard
            )
            context.user_data.pop('active_ticket', None)
            context.user_data.pop('ticket_subject', None)
            return SUPPORT_MENU
        
        elif text == '📎 Add Attachment':
            await update.message.reply_text(
                "📎 Please send your attachment (photo, document, video, or audio):"
            )
            return TICKET_ATTACHMENT
        
        elif text == '🔙 Back to Support':
            keyboard = self.get_support_keyboard()
            await update.message.reply_text(
                "⚠️ Ticket not submitted yet. Returning to support menu...",
                reply_markup=keyboard
            )
            context.user_data.pop('active_ticket', None)
            context.user_data.pop('ticket_subject', None)
            return SUPPORT_MENU
        
        else:
            # Handle file attachments
            if update.message.photo:
                file_id = update.message.photo[-1].file_id
                file_unique_id = update.message.photo[-1].file_unique_id
                await self.db.add_ticket_attachment(
                    ticket_id, file_id, file_unique_id, 'photo', 'photo.jpg'
                )
                await update.message.reply_text("✅ Photo attached!")
            
            elif update.message.document:
                file_id = update.message.document.file_id
                file_unique_id = update.message.document.file_unique_id
                file_name = update.message.document.file_name
                await self.db.add_ticket_attachment(
                    ticket_id, file_id, file_unique_id, 'document', file_name
                )
                await update.message.reply_text(f"✅ Document '{file_name}' attached!")
            
            elif update.message.video:
                file_id = update.message.video.file_id
                file_unique_id = update.message.video.file_unique_id
                await self.db.add_ticket_attachment(
                    ticket_id, file_id, file_unique_id, 'video', 'video.mp4'
                )
                await update.message.reply_text("✅ Video attached!")
            
            elif update.message.audio:
                file_id = update.message.audio.file_id
                file_unique_id = update.message.audio.file_unique_id
                file_name = update.message.audio.file_name or 'audio.mp3'
                await self.db.add_ticket_attachment(
                    ticket_id, file_id, file_unique_id, 'audio', file_name
                )
                await update.message.reply_text(f"✅ Audio '{file_name}' attached!")
            
            else:
                await update.message.reply_text("❌ Unsupported file type. Please use the menu buttons.")
            
            return TICKET_ATTACHMENT
    
    async def show_faq(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show FAQ list."""
        faq_text = (
            "❓ Frequently Asked Questions\n\n"
            "1️⃣ How do I get thumbnails?\n"
            "→ Click '📹 Get Thumbnail' and send a YouTube link\n\n"
            "2️⃣ How do I get premium?\n"
            "→ Refer friends or use /premium for payment options\n\n"
            "3️⃣ How many requests can I make?\n"
            "→ Free: 10/day, Premium: 1000/day\n\n"
            "4️⃣ How do I contact support?\n"
            "→ Use '🎫 Create Ticket' in support menu\n\n"
            "Need more help? Create a support ticket!"
        )
        
        await update.message.reply_text(faq_text)
    
    async def handle_admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle admin menu selections."""
        user_id = update.effective_user.id
        text = update.message.text
        
        if user_id not in self.admin_ids:
            await update.message.reply_text("❌ Access denied.")
            return MAIN_MENU
        
        if text == '📊 Bot Stats':
            await self.show_bot_stats(update, context)
            return ADMIN_MENU
        
        elif text == '⚙️ Settings':
            keyboard = self.get_settings_keyboard()
            await update.message.reply_text(
                "⚙️ Bot Settings\n\n"
                "Select a setting to configure:",
                reply_markup=keyboard
            )
            return ADMIN_MENU
        
        elif text == '🔙 Back to Main':
            is_premium = await self.db.is_premium(user_id)
            is_agent = await self.db.is_agent(user_id)
            keyboard = self.get_main_keyboard(user_id, is_premium, True, is_agent)
            await update.message.reply_text("Returning to main menu...", reply_markup=keyboard)
            return MAIN_MENU
        
        else:
            await update.message.reply_text("Feature coming soon!")
            return ADMIN_MENU
    
    async def show_bot_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show bot statistics."""
        stats = await self.db.get_stats()
        
        stats_text = (
            f"📊 Bot Statistics\n\n"
            f"👥 Total Users: {stats['total_users']}\n"
            f"💎 Premium Users: {stats['premium_users']}\n"
            f"📈 Today's Requests: {stats['today_requests']}\n"
        )
        
        await update.message.reply_text(stats_text)
    
    async def handle_agent_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle agent menu selections."""
        user_id = update.effective_user.id
        text = update.message.text
        
        if not await self.db.is_agent(user_id):
            await update.message.reply_text("❌ Access denied.")
            return MAIN_MENU
        
        if text == '🟢 Go Online':
            await self.db.set_agent_online(user_id, True)
            await update.message.reply_text("✅ You are now ONLINE for ticket assignments!")
            return AGENT_MENU
        
        elif text == '🔴 Go Offline':
            await self.db.set_agent_online(user_id, False)
            await update.message.reply_text("✅ You are now OFFLINE. No new tickets will be assigned.")
            return AGENT_MENU
        
        elif text == '📋 Open Tickets':
            tickets = await self.db.get_open_tickets()
            
            if not tickets:
                await update.message.reply_text("📋 No open tickets at the moment!")
            else:
                ticket_list = "📋 Open Tickets:\n\n"
                for ticket in tickets[:15]:
                    ticket_list += (
                        f"🎫 {ticket['ticket_id']}\n"
                        f"Subject: {ticket['subject']}\n"
                        f"Status: {ticket['status']}\n"
                        f"Created: {ticket['created_at'][:16]}\n\n"
                    )
                await update.message.reply_text(ticket_list)
            
            return AGENT_MENU
        
        elif text == '🔙 Back to Main':
            is_premium = await self.db.is_premium(user_id)
            is_admin = user_id in self.admin_ids
            keyboard = self.get_main_keyboard(user_id, is_premium, is_admin, True)
            await update.message.reply_text("Returning to main menu...", reply_markup=keyboard)
            return MAIN_MENU
        
        else:
            await update.message.reply_text("Feature coming soon!")
            return AGENT_MENU
    
    async def post_init(self, application: Application):
        """Initialize database after application starts."""
        await self.db.initialize()
        logger.info("Database initialized")
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel current operation and return to main menu."""
        user_id = update.effective_user.id
        is_premium = await self.db.is_premium(user_id)
        is_admin = user_id in self.admin_ids
        is_agent = await self.db.is_agent(user_id)
        
        keyboard = self.get_main_keyboard(user_id, is_premium, is_admin, is_agent)
        await update.message.reply_text("❌ Cancelled.", reply_markup=keyboard)
        
        return MAIN_MENU
    
    def run(self):
        """Run the bot."""
        # Create application
        application = Application.builder().token(self.token).post_init(self.post_init).build()
        
        # Create conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start_command)],
            states={
                MAIN_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_main_menu)
                ],
                ADMIN_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_admin_menu)
                ],
                SUPPORT_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_support_menu)
                ],
                TICKET_SUBJECT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_ticket_subject)
                ],
                TICKET_MESSAGE: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_ticket_message)
                ],
                TICKET_ATTACHMENT: [
                    MessageHandler(
                        (filters.TEXT | filters.PHOTO | filters.Document.ALL | 
                         filters.VIDEO | filters.AUDIO) & ~filters.COMMAND,
                        self.handle_ticket_attachment
                    )
                ],
                VIDEO_QUALITY_SELECT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_quality_selection)
                ],
                AGENT_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_agent_menu)
                ],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        
        application.add_handler(conv_handler)
        
        logger.info("Bot started successfully with ReplyKeyboard UI")
        
        # Run the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point."""
    try:
        bot = ThumbnailBot()
        bot.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
