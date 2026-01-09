#!/bin/bash

# YouTube Thumbnail Bot - Enhanced Setup Script 2026
# This script automates the complete setup process

set -e

echo "🚀 YouTube Thumbnail Bot - Enhanced Setup"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python 3 is installed
echo "📋 Checking requirements..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 is not installed. Please install pip3.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ pip3 found${NC}"

echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt --quiet

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

echo ""
echo "⚙️  Setting up configuration..."

# Check if config.ini exists
if [ -f "config.ini" ]; then
    echo -e "${YELLOW}⚠️  config.ini already exists.${NC}"
    read -p "Do you want to reconfigure? (y/N): " RECONFIGURE
    if [[ ! $RECONFIGURE =~ ^[Yy]$ ]]; then
        echo "Skipping configuration."
        SKIP_CONFIG=1
    fi
fi

if [ -z "$SKIP_CONFIG" ]; then
    cp config.ini.example config.ini
    echo -e "${GREEN}✅ Created config.ini from example${NC}"
    
    echo ""
    echo -e "${BLUE}📝 Bot Configuration${NC}"
    echo "----------------------"
    
    # Get bot token
    echo ""
    echo -e "${YELLOW}1️⃣  Bot Token${NC}"
    echo "   Get your token from @BotFather on Telegram"
    echo "   Steps:"
    echo "   1. Open Telegram and search for @BotFather"
    echo "   2. Send /newbot"
    echo "   3. Follow instructions"
    echo "   4. Copy the token"
    echo ""
    read -p "Enter your bot token: " BOT_TOKEN
    
    # Get admin user ID
    echo ""
    echo -e "${YELLOW}2️⃣  Admin User ID${NC}"
    echo "   Get your user ID from @userinfobot on Telegram"
    echo "   Steps:"
    echo "   1. Open Telegram and search for @userinfobot"
    echo "   2. Start the bot"
    echo "   3. Copy your user ID"
    echo ""
    read -p "Enter your Telegram user ID: " ADMIN_ID
    
    # Get UPI ID (optional)
    echo ""
    echo -e "${YELLOW}3️⃣  UPI ID for Payments (Optional)${NC}"
    echo "   Enter your UPI ID to receive payments"
    echo ""
    read -p "Enter UPI ID (or press Enter to skip): " UPI_ID
    
    # Get admin panel password
    echo ""
    echo -e "${YELLOW}4️⃣  Admin Panel Password${NC}"
    echo "   Set a strong password for the web admin panel"
    echo ""
    while true; do
        read -sp "Enter admin panel password: " ADMIN_PASSWORD
        echo ""
        read -sp "Confirm password: " ADMIN_PASSWORD_CONFIRM
        echo ""
        
        if [ "$ADMIN_PASSWORD" == "$ADMIN_PASSWORD_CONFIRM" ]; then
            if [ ${#ADMIN_PASSWORD} -lt 8 ]; then
                echo -e "${RED}❌ Password too short. Use at least 8 characters.${NC}"
            else
                break
            fi
        else
            echo -e "${RED}❌ Passwords don't match. Try again.${NC}"
        fi
    done
    
    # Update config.ini
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/token = YOUR_BOT_TOKEN_HERE/token = $BOT_TOKEN/" config.ini
        sed -i '' "s/admin_ids = 123456789/admin_ids = $ADMIN_ID/" config.ini
        
        if [ ! -z "$UPI_ID" ]; then
            sed -i '' "s/upi_id = your-upi-id@bank/upi_id = $UPI_ID/" config.ini
        fi
        
        if [ ! -z "$ADMIN_PASSWORD" ]; then
            sed -i '' "s/password = admin123/password = $ADMIN_PASSWORD/" config.ini
        fi
    else
        # Linux
        sed -i "s/token = YOUR_BOT_TOKEN_HERE/token = $BOT_TOKEN/" config.ini
        sed -i "s/admin_ids = 123456789/admin_ids = $ADMIN_ID/" config.ini
        
        if [ ! -z "$UPI_ID" ]; then
            sed -i "s/upi_id = your-upi-id@bank/upi_id = $UPI_ID/" config.ini
        fi
        
        if [ ! -z "$ADMIN_PASSWORD" ]; then
            sed -i "s/password = admin123/password = $ADMIN_PASSWORD/" config.ini
        fi
    fi
    
    echo -e "${GREEN}✅ Configuration saved${NC}"
fi

echo ""
echo "🗄️  Initializing database..."

# Check if database exists
if [ -f "bot_data.db" ]; then
    echo -e "${YELLOW}⚠️  Database already exists.${NC}"
    read -p "Do you want to reinitialize (THIS WILL DELETE ALL DATA)? (y/N): " REINIT_DB
    if [[ $REINIT_DB =~ ^[Yy]$ ]]; then
        rm -f bot_data.db
        echo "Database removed. Will create fresh database."
    else
        echo "Keeping existing database."
        SKIP_DB_INIT=1
    fi
fi

if [ -z "$SKIP_DB_INIT" ]; then
    # Create database by running bot briefly
    echo "Creating database structure..."
    timeout 5 python3 bot.py > /dev/null 2>&1 || true
    
    if [ -f "bot_data.db" ]; then
        echo -e "${GREEN}✅ Database created${NC}"
        
        # Initialize FAQ and default data
        echo "Adding default FAQ entries..."
        python3 initialize_data.py
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Database initialized with default data${NC}"
        else
            echo -e "${YELLOW}⚠️  Could not initialize FAQ data${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Database will be created on first bot run${NC}"
    fi
fi

echo ""
echo "🧪 Verifying installation..."

# Test Python imports
python3 -c "import telegram; import aiosqlite; import flask; print('✅ All required packages installed')" 2>/dev/null

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Some packages are missing. Try reinstalling requirements.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Installation verified${NC}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✨ Setup Complete!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}🤖 To start the bot:${NC}"
echo "   python3 bot.py"
echo ""
echo -e "${BLUE}🌐 To start the admin panel:${NC}"
echo "   python3 admin_panel.py"
echo "   Then visit: http://localhost:5000"
echo ""
echo -e "${BLUE}🔑 Admin Panel Login:${NC}"
echo "   Username: admin"
echo "   Password: (the one you just set)"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "   README.md       - Complete documentation"
echo "   QUICKSTART.md   - Quick start guide"
echo ""
echo -e "${BLUE}✅ Features Ready:${NC}"
echo "   • ReplyKeyboard UI"
echo "   • YouTube thumbnail download"
echo "   • Support ticket system"
echo "   • Multi-agent operations"
echo "   • Premium & referral system"
echo "   • Web admin panel with analytics"
echo "   • Multi-language support (en, hi, es)"
echo "   • Force join channel"
echo "   • Maintenance mode"
echo ""
echo "🎉 Happy bot running!"
echo ""
