# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Get Your Bot Token
1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` and follow the instructions
3. Copy your bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
4. Get your Telegram user ID from [@userinfobot](https://t.me/userinfobot)

### Step 2: Install the Bot
```bash
# Clone the repository
git clone https://github.com/inyogeshwar/thumbxtract-telegram-bot.git
cd thumbxtract-telegram-bot

# Install dependencies
pip3 install -r requirements.txt

# Create configuration
cp config.ini.example config.ini
```

### Step 3: Configure
Edit `config.ini`:
```ini
[bot]
token = YOUR_BOT_TOKEN_HERE  # Paste your token from BotFather
admin_ids = YOUR_USER_ID      # Your user ID from userinfobot

[payment]
upi_id = your-upi-id@bank     # Your UPI ID for payments

[admin_panel]
username = admin
password = CHANGE_THIS_NOW    # Pick a strong password!
```

### Step 4: Run
```bash
# Start the bot
python3 bot.py

# In another terminal (optional): Start admin panel
python3 admin_panel.py
```

### Step 5: Test
1. Open Telegram
2. Search for your bot (the username you chose)
3. Send `/start`
4. Send any YouTube link: `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
5. Enjoy your thumbnails! 🎉

## 📋 Common Commands

### User Commands
- `/start` - Register and see welcome message
- `/help` - Get help and quick actions
- `/stats` - View your usage statistics
- `/referral` - Get your referral link
- `/premium` - See premium benefits and upgrade
- `/language` - Change language

### Admin Commands
- `/adminstats` - Bot statistics
- `/broadcast <message>` - Message all users
- `/ban <user_id>` - Ban a user
- `/unban <user_id>` - Unban a user

## 🎮 How to Use

### Extract Thumbnails
Just send any of these formats:
- Full link: `https://www.youtube.com/watch?v=VIDEO_ID`
- Short link: `https://youtu.be/VIDEO_ID`
- Shorts: `https://youtube.com/shorts/VIDEO_ID`
- Just ID: `VIDEO_ID`

### Get Premium
**Option 1: Free via Referrals**
1. Send `/referral` to get your link
2. Share it with friends
3. Get 10 referrals = Free Premium! 🎁

**Option 2: Purchase**
1. Send `/premium`
2. Click "Buy Premium"
3. Choose UPI Payment
4. Send payment to the UPI ID
5. Upload screenshot
6. Wait for admin approval

## 🌐 Admin Panel

Access at: `http://localhost:5000` (or your VPS IP)

**Default Login:**
- Username: `admin`
- Password: `admin123` (⚠️ CHANGE THIS!)

**Features:**
- View all users
- Toggle premium status
- Ban/unban users
- Approve payments
- See statistics

## 🐛 Troubleshooting

### Bot not responding?
```bash
# Check if running
ps aux | grep bot.py

# View logs
tail -f bot.log  # if you set up logging

# Restart
pkill -f bot.py
python3 bot.py
```

### Can't access admin panel?
```bash
# Check if running
ps aux | grep admin_panel.py

# Try direct access
curl http://localhost:5000

# Check firewall
sudo ufw allow 5000
```

### Database locked?
```bash
# Stop bot
pkill -f bot.py

# Backup database
cp bot_data.db bot_data.db.backup

# Start bot again
python3 bot.py
```

## 💡 Pro Tips

### 1. Run in Background
```bash
# Using screen
screen -S bot
python3 bot.py
# Press Ctrl+A, then D to detach

# Reattach later
screen -r bot
```

### 2. Auto-Restart on Crash
Create systemd service (see README for details)

### 3. Monitor Logs
```python
# Add to bot.py for file logging:
logging.basicConfig(
    filename='bot.log',
    level=logging.INFO
)
```

### 4. Backup Database
```bash
# Daily backup cronjob
0 2 * * * cp /path/to/bot_data.db /path/to/backups/bot_data_$(date +\%Y\%m\%d).db
```

### 5. Security Checklist
- ✅ Change admin panel password
- ✅ Keep bot token secret
- ✅ Use strong passwords
- ✅ Regular database backups
- ✅ Keep dependencies updated
- ✅ Monitor for suspicious activity

## 🎯 Next Steps

1. **Customize Messages**
   - Edit `i18n.py` to change bot messages
   - Add your own language translations

2. **Adjust Limits**
   - Modify `config.ini` for different limits
   - Balance free vs premium features

3. **Add Your Branding**
   - Update welcome messages
   - Add your contact info
   - Customize button text

4. **Monitor Growth**
   - Check admin panel regularly
   - Review user statistics
   - Track referral performance

5. **Scale Up**
   - Deploy to VPS for 24/7 uptime
   - Set up systemd service
   - Configure automatic backups

## 📞 Need Help?

- 📖 Full docs: See README.md
- 🐛 Found a bug: Open an issue on GitHub
- 💬 Questions: Check GitHub discussions
- ⭐ Like it? Star the repo!

---

**Happy Bot Running! 🤖**
