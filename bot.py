"""
Main bot module for YouTube Thumbnail Extractor Telegram Bot.
Built with python-telegram-bot v20.
"""

import logging
import configparser
import sys
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
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


class ThumbnailBot:
    """Main bot class."""
    
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
        
        logger.info("Bot initialized successfully")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        user_id = user.id
        
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
        
        # Get bot username for referral link
        bot_user = await context.bot.get_me()
        
        if referred_by:
            # Check if referrer should get premium
            referral_count = await self.db.get_referral_count(referred_by)
            if referral_count >= self.premium_referrals:
                await self.db.set_premium(referred_by, True)
                # Notify referrer about premium
                try:
                    await context.bot.send_message(
                        chat_id=referred_by,
                        text=self.i18n.get_text('premium_granted', referred_by)
                    )
                except Exception as e:
                    logger.error(f"Could not notify referrer {referred_by}: {e}")
            
            message = self.i18n.get_text(
                'welcome_referred',
                user_id,
                user.language_code,
                referrer_id=referred_by,
                bonus=self.referral_bonus
            )
        else:
            message = self.i18n.get_text('welcome', user_id, user.language_code)
        
        await update.message.reply_text(message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        user_id = update.effective_user.id
        message = self.i18n.get_text('help', user_id)
        await update.message.reply_text(message)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command."""
        user_id = update.effective_user.id
        user_data = await self.db.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text(
                self.i18n.get_text('error', user_id)
            )
            return
        
        usage = await self.db.get_daily_usage(user_id)
        is_premium = await self.db.is_premium(user_id)
        limit = self.premium_limit if is_premium else self.free_limit
        referrals = await self.db.get_referral_count(user_id)
        
        created_at = user_data.get('created_at', 'Unknown')
        
        message = self.i18n.get_text(
            'stats',
            user_id,
            used=usage,
            limit=limit,
            referrals=referrals,
            premium=self.i18n.get_text('yes', user_id) if is_premium else self.i18n.get_text('no', user_id),
            joined=created_at
        )
        
        await update.message.reply_text(message)
    
    async def referral_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /referral command."""
        user_id = update.effective_user.id
        bot_user = await context.bot.get_me()
        
        referral_link = await self.db.get_referral_link(user_id, bot_user.username)
        referral_count = await self.db.get_referral_count(user_id)
        
        message = self.i18n.get_text(
            'referral_info',
            user_id,
            bonus=self.referral_bonus,
            required=self.premium_referrals,
            link=referral_link,
            count=referral_count
        )
        
        await update.message.reply_text(message)
    
    async def premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /premium command."""
        user_id = update.effective_user.id
        referral_count = await self.db.get_referral_count(user_id)
        
        message = self.i18n.get_text(
            'premium_info',
            user_id,
            premium_limit=self.premium_limit,
            required=self.premium_referrals,
            count=referral_count
        )
        
        await update.message.reply_text(message)
    
    async def language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /language command."""
        user_id = update.effective_user.id
        
        # Create keyboard with available languages
        keyboard = []
        languages = self.i18n.get_available_languages()
        
        for code, name in languages.items():
            keyboard.append([InlineKeyboardButton(name, callback_data=f"lang_{code}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = self.i18n.get_text('choose_language', user_id)
        await update.message.reply_text(message, reply_markup=reply_markup)
    
    async def language_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle language selection callback."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        language_code = query.data.replace('lang_', '')
        
        self.i18n.set_user_language(user_id, language_code)
        
        language_name = self.i18n.get_available_languages().get(language_code, language_code)
        message = self.i18n.get_text(
            'language_changed',
            user_id,
            language=language_name
        )
        
        await query.edit_message_text(message)
    
    async def admin_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /adminstats command (admin only)."""
        user_id = update.effective_user.id
        
        if user_id not in self.admin_ids:
            return
        
        stats = await self.db.get_stats()
        
        message = (
            "📊 Bot Statistics:\n\n"
            f"Total users: {stats['total_users']}\n"
            f"Premium users: {stats['premium_users']}\n"
            f"Requests today: {stats['today_requests']}"
        )
        
        await update.message.reply_text(message)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages containing YouTube links or video IDs."""
        user = update.effective_user
        user_id = user.id
        text = update.message.text
        
        # Check flood control
        is_flooding, wait_time = await self.db.check_flood_control(
            user_id, self.flood_threshold, self.flood_window
        )
        
        if is_flooding:
            message = self.i18n.get_text('flood_warning', user_id, seconds=wait_time)
            await update.message.reply_text(message)
            return
        
        # Check daily limit
        is_premium = await self.db.is_premium(user_id)
        limit = self.premium_limit if is_premium else self.free_limit
        usage = await self.db.get_daily_usage(user_id)
        
        if usage >= limit:
            message = self.i18n.get_text(
                'limit_reached',
                user_id,
                limit=limit,
                premium_limit=self.premium_limit
            )
            await update.message.reply_text(message)
            return
        
        # Extract video ID
        video_id = self.youtube.extract_video_id(text)
        
        if not video_id:
            message = self.i18n.get_text('invalid_link', user_id)
            await update.message.reply_text(message)
            return
        
        # Send processing message
        processing_msg = await update.message.reply_text(
            self.i18n.get_text('processing', user_id)
        )
        
        try:
            # Get thumbnails
            thumbnails = self.youtube.get_thumbnails(video_id)
            
            # Send confirmation message
            message = self.i18n.get_text(
                'thumbnails_found',
                user_id,
                count=len(thumbnails),
                video_id=video_id
            )
            await processing_msg.edit_text(message)
            
            # Send each thumbnail
            for thumb in thumbnails:
                try:
                    caption = f"{thumb['quality']}\n{thumb['url']}"
                    await update.message.reply_photo(
                        photo=thumb['url'],
                        caption=caption
                    )
                except Exception as e:
                    logger.warning(f"Could not send thumbnail {thumb['quality']}: {e}")
            
            # Increment usage
            await self.db.increment_usage(user_id)
            
        except Exception as e:
            logger.error(f"Error processing request for user {user_id}: {e}")
            await processing_msg.edit_text(
                self.i18n.get_text('error', user_id)
            )
    
    async def post_init(self, application: Application):
        """Initialize database after application starts."""
        await self.db.initialize()
        logger.info("Database initialized")
    
    def run(self):
        """Run the bot."""
        # Create application
        application = Application.builder().token(self.token).post_init(self.post_init).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("stats", self.stats_command))
        application.add_handler(CommandHandler("referral", self.referral_command))
        application.add_handler(CommandHandler("premium", self.premium_command))
        application.add_handler(CommandHandler("language", self.language_command))
        application.add_handler(CommandHandler("adminstats", self.admin_stats_command))
        
        # Callback query handler for language selection
        application.add_handler(CallbackQueryHandler(
            self.language_callback,
            pattern='^lang_'
        ))
        
        # Message handler for YouTube links
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_message
        ))
        
        logger.info("Bot started successfully")
        
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
