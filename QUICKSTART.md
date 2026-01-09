# 🚀 Quick Start Guide

Get your YouTube Thumbnail Bot running in 5 minutes!

## ⚡ Quick Setup (5 Steps)

### 1. Clone & Install

```bash
git clone https://github.com/inyogeshwar/thumbxtract-telegram-bot.git
cd thumbxtract-telegram-bot
pip install -r requirements.txt
```

### 2. Get Bot Token

1. Open Telegram
2. Search for [@BotFather](https://t.me/BotFather)
3. Send `/newbot`
4. Follow instructions
5. Copy your bot token

### 3. Get Your User ID

1. Search for [@userinfobot](https://t.me/userinfobot) on Telegram
2. Start the bot
3. Copy your user ID

### 4. Configure

```bash
cp config.ini.example config.ini
nano config.ini
```

**Minimal Required Config:**
```ini
[bot]
token = YOUR_BOT_TOKEN_HERE
admin_ids = YOUR_USER_ID

[payment]
upi_id = your-upi@bank

[admin_panel]
username = admin
password = ChangeMe123!
```

Save and exit (Ctrl+X, Y, Enter)

### 5. Run!

```bash
# Terminal 1 - Run the bot
python bot.py

# Terminal 2 - Run admin panel (optional but recommended)
python admin_panel.py
```

**Done! 🎉**

Your bot is now running! 
- Open Telegram and search for your bot
- Send `/start`
- Admin panel: http://localhost:5000

## 📱 First Steps After Setup

### Initialize Data (Recommended)

```bash
# First, start the bot once to create database
python bot.py
# Press Ctrl+C after it says "Bot started successfully"

# Then initialize FAQ and default data
python initialize_data.py
```

### Add Yourself as Agent (Optional)

Open Python and run:
```python
import asyncio
from database import Database

async def add_me():
    db = Database('bot_data.db')
    await db.initialize()
    await db.add_agent(YOUR_USER_ID, 'owner')
    print("✅ Added as agent!")

asyncio.run(add_me())
```

Replace `YOUR_USER_ID` with your actual Telegram user ID.

### Test Your Bot

1. Open Telegram
2. Search for your bot (use the username you set with BotFather)
3. Send `/start`
4. You should see the main menu with buttons!
5. Try `📹 Get Thumbnail` and send a YouTube link

### Access Admin Panel

1. Open browser
2. Go to http://localhost:5000
3. Login with username and password from config.ini
4. Explore the dashboard!

## 🎯 Quick Commands

### User Commands
- `/start` - Start the bot
- `/help` - Show help
- `/stats` - Your statistics
- `/referral` - Get referral link
- `/premium` - Premium info

### Admin Commands (Bot)
- Use `👑 Admin Panel` button
- No commands needed!

### Admin Panel Features
- Dashboard: http://localhost:5000
- Users: http://localhost:5000/users
- Tickets: http://localhost:5000/tickets
- Agents: http://localhost:5000/agents
- Settings: http://localhost:5000/settings

## ⚙️ Common Configurations

### Change Daily Limits

Edit `config.ini`:
```ini
[limits]
free_daily_limit = 20      # Change free user limit
premium_daily_limit = 2000 # Change premium limit
```

Restart bot to apply changes.

### Enable Force Join Channel

1. Create a Telegram channel
2. Add your bot as admin
3. Go to admin panel → Settings
4. Toggle "Force Join Channel"
5. Enter channel username (e.g., @mychannel)
6. Save

### Enable Maintenance Mode

**Via Admin Panel:**
1. Go to Settings
2. Toggle "Maintenance Mode"
3. Save

**Via Database:**
```python
import asyncio
from database import Database

async def maintenance():
    db = Database('bot_data.db')
    await db.initialize()
    await db.set_setting('maintenance_mode', '1')  # Enable
    # await db.set_setting('maintenance_mode', '0')  # Disable
    print("✅ Updated!")

asyncio.run(maintenance())
```

## 🐛 Troubleshooting

### Bot Not Starting

**Error: "No module named 'telegram'"**
```bash
pip install -r requirements.txt
```

**Error: "Config file not found"**
```bash
cp config.ini.example config.ini
nano config.ini
# Add your bot token
```

**Error: "Unauthorized"**
```bash
# Check your bot token in config.ini
# Make sure it's correct from BotFather
```

### Bot Starts but Doesn't Respond

**Check bot is running:**
```bash
ps aux | grep bot.py
```

**Check logs:**
```bash
python bot.py
# Look for errors in the output
```

**Test bot token:**
```bash
curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
```

### Admin Panel Not Loading

**Port already in use:**
```bash
# Kill existing process
sudo lsof -ti:5000 | xargs kill -9

# Or change port in admin_panel.py:
# app.run(host='0.0.0.0', port=5001, debug=False)
```

**Can't access from outside:**
```bash
# Check firewall
sudo ufw allow 5000

# Or use SSH tunnel
ssh -L 5000:localhost:5000 user@your-vps
# Then access http://localhost:5000 on your local machine
```

### Database Errors

**Error: "database is locked"**
```bash
# Stop all instances of bot/admin panel
pkill -f bot.py
pkill -f admin_panel.py

# Restart one at a time
```

**Reset database (WARNING: Deletes all data):**
```bash
rm bot_data.db
python bot.py
# Bot will create new database
python initialize_data.py
```

## 📊 Usage Examples

### Test Thumbnail Download

1. Click `📹 Get Thumbnail`
2. Send: `https://youtube.com/watch?v=dQw4w9WgXcQ`
3. Choose `⚡ All Qualities`
4. Receive thumbnails!

### Test Support System

1. Click `💬 Support`
2. Click `🎫 Create Ticket`
3. Enter subject: "Test Ticket"
4. Enter message: "This is a test"
5. Optionally add attachment (photo/document)
6. Click `✅ Submit Ticket`
7. Check ticket in admin panel!

### Test Referral System

1. Click `🎁 Referrals`
2. Copy your link
3. Open in incognito/another browser
4. Join as new user
5. Check referral count increased!

### Test Agent System

1. Add yourself as agent (see above)
2. Restart bot
3. You'll see `🎫 Agent Panel` button
4. Create a ticket as regular user
5. Click `📋 Open Tickets` in agent panel
6. See the ticket!

## 🚀 Production Deployment

### Using systemd (Recommended)

Create `/etc/systemd/system/thumbxtract-bot.service`:
```ini
[Unit]
Description=YouTube Thumbnail Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/thumbxtract-telegram-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/thumbxtract-admin.service`:
```ini
[Unit]
Description=YouTube Thumbnail Bot Admin Panel
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/thumbxtract-telegram-bot
ExecStart=/usr/bin/python3 admin_panel.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable thumbxtract-bot thumbxtract-admin
sudo systemctl start thumbxtract-bot thumbxtract-admin

# Check status
sudo systemctl status thumbxtract-bot
sudo systemctl status thumbxtract-admin

# View logs
sudo journalctl -u thumbxtract-bot -f
sudo journalctl -u thumbxtract-admin -f
```

### Using PM2 (Alternative)

```bash
# Install PM2
npm install -g pm2

# Start bot
pm2 start bot.py --name thumbxtract-bot --interpreter python3
pm2 start admin_panel.py --name thumbxtract-admin --interpreter python3

# Save configuration
pm2 save
pm2 startup

# View logs
pm2 logs thumbxtract-bot
pm2 logs thumbxtract-admin

# Restart
pm2 restart all

# Stop
pm2 stop all
```

### Using Docker (Coming Soon)

Stay tuned for Docker deployment!

## 📚 Next Steps

Once your bot is running:

1. **Customize Settings**
   - Change limits in config.ini
   - Set up force join channel
   - Add FAQ entries

2. **Add Agents**
   - Add support team members
   - Train them on ticket system

3. **Configure Payment**
   - Set up UPI ID
   - Test payment flow

4. **Monitor Analytics**
   - Check admin panel daily
   - Monitor user growth
   - Track request patterns

5. **Promote Your Bot**
   - Share on social media
   - Create promotional content
   - Engage with users

## 🆘 Need Help?

- **Documentation**: See README.md
- **Issues**: [GitHub Issues](https://github.com/inyogeshwar/thumbxtract-telegram-bot/issues)
- **Questions**: Open a discussion on GitHub

## 🎉 You're All Set!

Your YouTube Thumbnail Bot is now running with:
- ✅ ReplyKeyboard UI
- ✅ Support ticket system
- ✅ Multi-agent operations
- ✅ Premium & referral system
- ✅ Web admin panel with analytics
- ✅ Force join & maintenance mode
- ✅ Multi-language support

**Happy bot running! 🚀**
