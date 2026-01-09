# YouTube Thumbnail Extractor Telegram Bot

A feature-rich, production-ready Telegram bot that extracts YouTube video IDs from any link format and sends all available thumbnails. Built with python-telegram-bot v20 and featuring a complete monetization system, payment processing, and admin panel.

## 🚀 Core Features

### 🎥 Video Support
- ✅ **Any YouTube Link Format**
  - `youtube.com/watch?v=VIDEO_ID`
  - `youtu.be/VIDEO_ID`
  - `youtube.com/shorts/VIDEO_ID`
  - `youtube.com/live/VIDEO_ID`
  - Direct video IDs (11 characters)
- ✅ **Auto Video ID Extraction**
- ✅ **Smart Thumbnail Detection** - Only sends thumbnails that exist (HEAD request validation)
- ✅ **Fast Response** - No API keys, no login required

### 🖼️ Media Features
- ✅ **All Available Thumbnails**
  - Maximum Resolution (1920x1080)
  - Standard Definition (640x480)
  - High Quality (480x360)
  - Medium Quality (320x180)
  - Default and numbered thumbnails
- ✅ **Clean Captions** - Quality labels without clutter
- ✅ **No Watermark** - Direct YouTube CDN links
- ✅ **No Quality Loss** - Original resolution thumbnails

### 🧠 Smart UI Features
- ✅ **Inline Keyboard Buttons** - Context-aware action buttons
- ✅ **Smart Navigation**
  - "New Video" button after results
  - "Main Menu" fallback
  - Quick action buttons in help
- ✅ **One-Click Actions** - Premium upgrade, referrals, stats
- ✅ **Clean Premium UI** - Professional button layout

### 🌍 Language Features
- ✅ **Auto Language Detection** - Smart text analysis
- ✅ **Multi-language Support**
  - 🇬🇧 English
  - 🇪🇸 Spanish (Español)
  - 🇮🇳 Hindi (हिंदी)
- ✅ **Manual Language Selection** via `/language` command
- ✅ **Easy to Extend** - Add new languages easily

### 🎁 Referral System
- ✅ **Unique Referral Links** - Per user tracking
- ✅ **Auto Tracking** - Automatic referral counting
- ✅ **Bonus Rewards** - Extra requests per referral
- ✅ **Premium Unlock** - Free premium after N referrals
- ✅ **Growth Focused** - Viral growth mechanics

### 💰 Monetization System
- ✅ **Free + Premium Tiers**
- ✅ **Daily Usage Limits** (Free: 10, Premium: 1000)
- ✅ **Upgrade CTAs** - Strategic premium promotion
- ✅ **Payment Integration**

### 💳 Payment System
- ✅ **UPI Payment Support** (India)
  - Manual payment flow
  - Screenshot upload
  - Admin verification
- ✅ **Telegram Stars** (Coming Soon placeholder)
- ✅ **Premium Validity** - Days-based expiry tracking
- ✅ **Payment Proof Storage** - Secure file tracking
- ✅ **Admin Approval Workflow** - Inline approve/reject buttons

### 📦 Premium Features
- ✅ **Unlimited Daily Requests** (1000/day vs 10/day)
- ✅ **Priority Processing**
- ✅ **No Ads**
- ✅ **MaxRes Guaranteed**
- ✅ **Early Feature Access**

### 🛡️ Security & Anti-Spam
- ✅ **Flood Control** - Time-based rate limiting
- ✅ **Request Rate Limiting**
- ✅ **User Ban System** - Admin-controlled bans
- ✅ **Abuse Prevention**
- ✅ **Safe Bot Usage**

### 📊 Admin Features (Bot)
- ✅ **Broadcast Messages** - `/broadcast` to all users
- ✅ **User Management** - `/ban` and `/unban` commands
- ✅ **Payment Approval** - Inline approve/reject buttons
- ✅ **Admin Statistics** - `/adminstats` command

### 🌐 Web Admin Panel
- ✅ **Secure Login** - Username/password authentication
- ✅ **User Management Dashboard**
  - View all users
  - Toggle premium status
  - Ban/unban users
- ✅ **Real-time Analytics**
  - Total users
  - Premium users
  - Banned users
  - Today's requests
  - Pending payments
- ✅ **Lightweight Flask Panel** - Minimal dependencies
- ✅ **Responsive Design** - Clean, modern UI

### 🗂️ Database Features
- ✅ **SQLite Database** - No external DB required
- ✅ **User Tracking** - Complete user profiles
- ✅ **Referral Tracking** - Full referral tree
- ✅ **Premium Status** - With expiry dates
- ✅ **Daily Usage Counting**
- ✅ **Ban Flags**
- ✅ **Payment Proof Storage**

### ⚙️ Technical Features
- ✅ **Python-based** - Modern async/await
- ✅ **Scalable Structure** - Modular design
- ✅ **VPS/Local Deploy** - Works anywhere
- ✅ **Environment Config** - Easy configuration
- ✅ **Easy Maintenance** - Clean codebase

## 📋 Installation

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
   
   Edit `config.ini` and configure your settings:
   ```ini
   [bot]
   token = YOUR_BOT_TOKEN_HERE
   admin_ids = YOUR_TELEGRAM_USER_ID
   
   [payment]
   upi_id = your-upi-id@bank
   premium_days = 30
   
   [admin_panel]
   username = admin
   password = CHANGE_THIS_PASSWORD
   ```

4. **Run the bot**
   ```bash
   python bot.py
   ```

5. **Run the admin panel** (optional, in a separate terminal)
   ```bash
   python admin_panel.py
   ```
   Access at: http://localhost:5000

## 📖 Configuration

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

### Payment Settings
- `upi_id`: Your UPI ID for receiving payments
- `premium_days`: Premium validity in days (default: 30)

### Admin Panel
- `username`: Admin panel username (default: admin)
- `password`: Admin panel password (CHANGE THIS!)

### Languages
- `default`: Default language code (default: en)

## 🎮 Usage

### User Commands

- `/start` - Start the bot and register
- `/help` - Show help message with usage instructions
- `/stats` - View your usage statistics
- `/referral` - Get your referral link and see referral count
- `/premium` - View premium benefits and upgrade options
- `/language` - Change bot language

### Admin Commands

- `/adminstats` - View bot-wide statistics (admin only)
- `/broadcast <message>` - Send message to all users (admin only)
- `/ban <user_id>` - Ban a user (admin only)
- `/unban <user_id>` - Unban a user (admin only)

### Getting Thumbnails

Simply send any YouTube link or video ID to the bot:

**Examples:**
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/dQw4w9WgXcQ
https://youtube.com/shorts/dQw4w9WgXcQ
dQw4w9WgXcQ
```

The bot will:
1. Extract the video ID
2. Check which thumbnails exist
3. Send all available thumbnails
4. Show action buttons (New Video, Main Menu)

## 🏗️ Project Structure

```
thumbxtract-telegram-bot/
├── bot.py              # Main bot application
├── database.py         # SQLite database operations
├── youtube_utils.py    # YouTube video ID extraction and thumbnail generation
├── i18n.py            # Internationalization and language support
├── admin_panel.py      # Flask-based web admin panel
├── config.ini.example  # Example configuration file
├── requirements.txt    # Python dependencies
├── test_bot.py        # Test suite
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

## 🗄️ Database Schema

### users table
- `user_id` (PRIMARY KEY): Telegram user ID
- `username`: Telegram username
- `first_name`: User's first name
- `language_code`: User's language preference
- `is_premium`: Premium status (0/1)
- `premium_expiry`: Premium expiration date
- `referred_by`: User ID of referrer
- `referral_count`: Number of successful referrals
- `is_banned`: Ban status (0/1)
- `created_at`: Registration timestamp
- `last_active`: Last activity timestamp

### usage table
- `id` (PRIMARY KEY): Auto-increment ID
- `user_id`: Foreign key to users
- `date`: Date of usage
- `count`: Number of requests on that date

### referrals table
- `id` (PRIMARY KEY): Auto-increment ID
- `referrer_id`: User who referred
- `referred_id`: User who was referred
- `created_at`: Referral timestamp

### flood_control table
- `user_id` (PRIMARY KEY): Telegram user ID
- `request_count`: Request count in current window
- `window_start`: Window start timestamp

### payment_proofs table
- `id` (PRIMARY KEY): Auto-increment ID
- `user_id`: Foreign key to users
- `file_id`: Telegram file ID
- `file_unique_id`: Unique file identifier
- `status`: Payment status (pending/approved/rejected)
- `created_at`: Upload timestamp

## 💡 Feature Details

### Referral System
1. Users get a unique referral link: `https://t.me/YOUR_BOT?start=ref_USER_ID`
2. When someone joins via the link:
   - Both users get bonus requests
   - Referrer's count increments
3. After N referrals (default: 10):
   - Referrer gets free premium automatically
   - Notification sent to referrer

### Premium System

**How to Get Premium:**
1. **Via Referrals**: Refer 10 users (free)
2. **Via Payment**: UPI payment with admin approval

**Premium Benefits:**
- 1000 requests/day (vs 10 for free)
- Priority processing
- No ads
- Early access to features
- Premium badge

**Payment Flow:**
1. User clicks "Buy Premium"
2. Chooses payment method (UPI/Stars)
3. Makes payment to UPI ID
4. Uploads screenshot
5. Admin approves/rejects
6. Premium activated with expiry date

### Flood Control
- Tracks requests per user in a time window
- Default: 5 requests per 60 seconds
- Temporarily blocks excessive requesters
- Auto-resets after window expires
- Prevents bot abuse

### Multi-language Support
The bot detects language from:
1. User's manual selection (`/language`)
2. Telegram's language setting
3. Default fallback (English)

Supported languages:
- English (en) 🇬🇧
- Spanish (es) 🇪🇸
- Hindi (hi) 🇮🇳

**Adding New Languages:**
1. Add translations to `i18n.py` TRANSLATIONS dict
2. Add language name to LANGUAGE_NAMES dict
3. Done!

### Admin Panel Features

Access the web panel at `http://localhost:5000` (or your VPS IP)

**Features:**
- 📊 Real-time statistics dashboard
- 👥 User list with filters
- ⚡ Quick actions (premium toggle, ban/unban)
- 💳 Payment tracking
- 🔒 Secure authentication
- 📱 Responsive design

**Security:**
- Change default password in `config.ini`
- Use strong passwords
- Consider adding HTTPS for production
- Restrict access by IP if possible

## 🧪 Testing

Run the test suite:
```bash
python test_bot.py
```

Tests cover:
- YouTube video ID extraction
- Thumbnail URL generation
- Database operations
- Language detection
- User management
- Referral system

## 🚀 Deployment

### Local Deployment
```bash
python bot.py
```

### VPS Deployment

1. **Upload files to VPS**
   ```bash
   scp -r . user@your-vps:/path/to/bot/
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure bot**
   ```bash
   nano config.ini
   # Set your bot token and settings
   ```

4. **Run with screen/tmux**
   ```bash
   screen -S bot
   python bot.py
   # Ctrl+A, D to detach
   ```

5. **Optional: Run admin panel**
   ```bash
   screen -S admin
   python admin_panel.py
   # Ctrl+A, D to detach
   ```

### Systemd Service (Recommended)

Create `/etc/systemd/system/thumbxtract-bot.service`:
```ini
[Unit]
Description=YouTube Thumbnail Extractor Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/bot
ExecStart=/usr/bin/python3 /path/to/bot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable thumbxtract-bot
sudo systemctl start thumbxtract-bot
```

## 🔧 Development

### Adding New Features

1. **Update database schema** in `database.py` if needed
2. **Implement feature logic**
3. **Add command handlers** in `bot.py`
4. **Add translations** in `i18n.py`
5. **Update documentation**
6. **Add tests** in `test_bot.py`

### Code Style
- Follow PEP 8
- Use async/await for I/O operations
- Add docstrings to functions
- Keep functions focused and small

## 📦 Dependencies

- **python-telegram-bot v20.8**: Telegram bot framework
- **aiosqlite v0.19.0**: Async SQLite database
- **langdetect v1.0.9**: Language detection
- **aiohttp v3.9.1**: Async HTTP client (for thumbnail checking)
- **flask v3.0.0**: Web framework (for admin panel)

## 🚀 Future Enhancements

- [ ] ZIP download of all thumbnails
- [ ] AI-powered title/SEO suggestions
- [ ] Advanced analytics dashboard
- [ ] Docker deployment
- [ ] Multi-bot scaling
- [ ] Telegram Stars payment integration
- [ ] Auto-posting to channels
- [ ] Custom thumbnail editing

## 🐛 Troubleshooting

### Bot doesn't respond
- Check bot token in `config.ini`
- Verify internet connection
- Check bot is running: `ps aux | grep bot.py`
- Check logs for errors

### Database errors
- Ensure `bot_data.db` has write permissions
- Check disk space
- Verify SQLite is installed

### Thumbnails not sending
- Some videos don't have all thumbnail sizes
- Bot only sends thumbnails that exist (by design)
- Check video ID is correct

### Admin panel not accessible
- Check Flask is running: `ps aux | grep admin_panel.py`
- Verify port 5000 is not blocked
- Check firewall settings
- Try: `http://localhost:5000` or `http://YOUR_VPS_IP:5000`

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 💬 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: [Your Contact Information]

## 🙏 Acknowledgments

- Built with [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- Thumbnails sourced from YouTube's image CDN
- Inspired by the Telegram community

---

**Made with ❤️ for the Telegram community**

⭐ Star this repo if you find it useful!
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
