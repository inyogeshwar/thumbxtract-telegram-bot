# YouTube Thumbnail Extractor Telegram Bot

A feature-rich Telegram bot that extracts YouTube video IDs from any link format and sends all available thumbnails. Built with python-telegram-bot v20.

## Features

### Core Functionality
- 🎯 **YouTube Video ID Extraction**: Supports multiple URL formats
  - `youtube.com/watch?v=VIDEO_ID`
  - `youtu.be/VIDEO_ID`
  - `youtube.com/shorts/VIDEO_ID`
  - `youtube.com/live/VIDEO_ID`
  - Direct video IDs
- 📸 **Thumbnail Extraction**: Sends all available thumbnail qualities
  - Maximum Resolution (1920x1080)
  - Standard Definition (640x480)
  - High Quality (480x360)
  - Medium Quality (320x180)
  - Default and numbered thumbnails

### Advanced Features
- 💾 **SQLite Database**: Persistent storage for users, referrals, and usage tracking
- 🎁 **Referral System**: Users earn bonus requests by referring friends
- 👑 **Premium Users**: Higher daily limits and priority processing
- 🌍 **Multi-language Support**: Auto-detection with manual override
  - English
  - Spanish (Español)
  - Hindi (हिंदी)
- 🛡️ **Flood Control**: Anti-spam protection with configurable thresholds
- 📊 **Daily Limits**: Configurable limits for free and premium users
- 📈 **Statistics Tracking**: User and bot-wide analytics

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/inyogeshwar/thumbxtract-telegram-bot.git
   cd thumbxtract-telegram-bot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**
   ```bash
   cp config.ini.example config.ini
   ```
   
   Edit `config.ini` and add your bot token:
   ```ini
   [bot]
   token = YOUR_BOT_TOKEN_HERE
   admin_ids = YOUR_TELEGRAM_USER_ID
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

## Configuration

The `config.ini` file contains all bot settings:

### Bot Settings
- `token`: Your Telegram bot token from BotFather
- `admin_ids`: Comma-separated list of admin user IDs

### Database Settings
- `path`: Path to SQLite database file (default: `bot_data.db`)

### Limits
- `free_daily_limit`: Daily request limit for free users (default: 10)
- `premium_daily_limit`: Daily request limit for premium users (default: 1000)
- `flood_threshold`: Maximum requests within flood window (default: 5)
- `flood_window`: Flood control window in seconds (default: 60)

### Referral System
- `bonus_uses`: Bonus requests per referral (default: 5)
- `premium_referrals_required`: Referrals needed for free premium (default: 10)

### Languages
- `default`: Default language code (default: en)

## Usage

### User Commands

- `/start` - Start the bot and register
- `/help` - Show help message with usage instructions
- `/stats` - View your usage statistics
- `/referral` - Get your referral link and see referral count
- `/premium` - View premium benefits and requirements
- `/language` - Change bot language

### Admin Commands

- `/adminstats` - View bot-wide statistics (admin only)

### Extracting Thumbnails

Simply send any YouTube link or video ID to the bot:

```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

The bot will extract the video ID and send all available thumbnails.

## Project Structure

```
thumbxtract-telegram-bot/
├── bot.py              # Main bot application
├── database.py         # SQLite database operations
├── youtube_utils.py    # YouTube video ID extraction and thumbnail generation
├── i18n.py            # Internationalization and language support
├── config.ini.example  # Example configuration file
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## Architecture

### Database Schema

**users table**
- `user_id` (PRIMARY KEY): Telegram user ID
- `username`: Telegram username
- `first_name`: User's first name
- `language_code`: User's language preference
- `is_premium`: Premium status (0/1)
- `referred_by`: User ID of referrer
- `referral_count`: Number of successful referrals
- `created_at`: Registration timestamp
- `last_active`: Last activity timestamp

**usage table**
- `id` (PRIMARY KEY): Auto-increment ID
- `user_id`: Foreign key to users
- `date`: Date of usage
- `count`: Number of requests on that date

**referrals table**
- `id` (PRIMARY KEY): Auto-increment ID
- `referrer_id`: User who referred
- `referred_id`: User who was referred
- `created_at`: Referral timestamp

**flood_control table**
- `user_id` (PRIMARY KEY): Telegram user ID
- `request_count`: Request count in current window
- `window_start`: Window start timestamp

## Features in Detail

### Referral System
Users can share their unique referral link to earn bonuses:
- Each successful referral grants bonus requests
- Accumulating enough referrals grants free premium status
- Referrers are notified when they earn premium

### Premium System
Premium users enjoy:
- Higher daily limits (default: 1000 vs 10)
- Priority processing
- No advertisements
- Early access to features

Earn premium by:
- Referring friends (10 referrals = free premium)
- Future payment options (planned)

### Multi-language Support
The bot automatically detects user language from:
1. User's manual selection via `/language`
2. Telegram's language setting
3. Message content analysis
4. Default fallback language

Supported languages:
- English (en)
- Spanish (es)
- Hindi (hi)

### Flood Control
Protects against spam and abuse:
- Tracks requests per user in a time window
- Temporarily blocks users exceeding threshold
- Automatically resets after window expires

## Development

### Adding New Languages

1. Add translations to `i18n.py` in the `TRANSLATIONS` dictionary
2. Add language name to `LANGUAGE_NAMES` dictionary
3. Update this README

### Adding New Features

1. Update database schema in `database.py` if needed
2. Implement feature logic
3. Add user-facing commands/handlers in `bot.py`
4. Update documentation

## Dependencies

- **python-telegram-bot v20.8**: Telegram bot framework
- **aiosqlite v0.19.0**: Async SQLite database
- **langdetect v1.0.9**: Language detection

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the bot admin via Telegram

## Acknowledgments

- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Thumbnails sourced from YouTube's image CDN

---

Made with ❤️ for the Telegram community
