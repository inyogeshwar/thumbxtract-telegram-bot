#!/usr/bin/env python3
"""Quick verification script to check if the bot can be run."""

import sys
import os

def check_requirements():
    """Check if all requirements are met."""
    print("🔍 Checking installation...\n")
    
    errors = []
    warnings = []
    
    # Check Python version
    if sys.version_info < (3, 8):
        errors.append("Python 3.8 or higher required")
    else:
        print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Check for required modules
    required_modules = ['telegram', 'aiosqlite', 'langdetect']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ Module '{module}' installed")
        except ImportError:
            errors.append(f"Module '{module}' not installed")
    
    # Check for required files
    required_files = [
        'bot.py',
        'database.py',
        'youtube_utils.py',
        'i18n.py',
        'requirements.txt',
        'config.ini.example'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ File '{file}' exists")
        else:
            errors.append(f"File '{file}' missing")
    
    # Check for config.ini
    if os.path.exists('config.ini'):
        print("✅ config.ini exists")
    else:
        warnings.append("config.ini not found (copy from config.ini.example)")
    
    print()
    
    # Report results
    if errors:
        print("❌ Errors found:")
        for error in errors:
            print(f"  - {error}")
        print()
        print("Please fix the errors above before running the bot.")
        return False
    
    if warnings:
        print("⚠️  Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
        print()
    
    print("✅ Installation verified!")
    print("\nNext steps:")
    if warnings:
        print("1. Copy config.ini.example to config.ini")
        print("2. Edit config.ini and add your bot token")
        print("3. Run: python bot.py")
    else:
        print("1. Make sure config.ini has your bot token")
        print("2. Run: python bot.py")
    
    return True

if __name__ == '__main__':
    success = check_requirements()
    sys.exit(0 if success else 1)
