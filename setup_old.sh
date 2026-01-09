#!/bin/bash
# Quick setup script for the YouTube Thumbnail Extractor Bot

set -e

echo "=================================="
echo "YouTube Thumbnail Extractor Bot"
echo "Quick Setup Script"
echo "=================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

echo "✅ pip3 found"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "❌ Could not find virtual environment activation script"
    exit 1
fi

echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo "✅ Dependencies installed"
echo ""

# Create config file if it doesn't exist
if [ ! -f "config.ini" ]; then
    echo "📝 Creating config.ini from template..."
    cp config.ini.example config.ini
    echo "✅ config.ini created"
    echo ""
    echo "⚠️  IMPORTANT: Edit config.ini and add your bot token!"
    echo "   Get your token from @BotFather on Telegram"
    echo ""
else
    echo "✅ config.ini already exists"
    echo ""
fi

# Run tests
echo "🧪 Running tests to verify installation..."
python test_bot.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ Setup Complete!"
    echo "=================================="
    echo ""
    echo "Next steps:"
    echo "1. Edit config.ini and add your bot token"
    echo "2. Run the bot with: python bot.py"
    echo ""
    echo "For more information, see README.md"
else
    echo ""
    echo "❌ Tests failed. Please check the error messages above."
    exit 1
fi
