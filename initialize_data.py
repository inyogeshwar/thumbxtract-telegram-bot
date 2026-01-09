"""
Initialize database with default FAQ entries and settings.
Run this script after first bot startup to populate initial data.
"""

import asyncio
import aiosqlite
import sys

DB_PATH = 'bot_data.db'

async def initialize_faq():
    """Add default FAQ entries."""
    async with aiosqlite.connect(DB_PATH) as db:
        faqs = [
            # English FAQs
            {
                'keywords': 'how get thumbnail download extract',
                'answer': (
                    "📹 How to Get Thumbnails:\n\n"
                    "1. Click '📹 Get Thumbnail' button\n"
                    "2. Send any YouTube link or video ID\n"
                    "3. Choose quality (MaxRes, HD, Medium, or All)\n"
                    "4. Receive thumbnails instantly!\n\n"
                    "It's that simple! 🎉"
                ),
                'language': 'en'
            },
            {
                'keywords': 'premium how get unlock upgrade',
                'answer': (
                    "💎 How to Get Premium:\n\n"
                    "1. Refer 10 friends (FREE!)\n"
                    "   - Use /referral to get your link\n\n"
                    "2. Pay via UPI\n"
                    "   - Use /premium for payment info\n\n"
                    "Premium Benefits:\n"
                    "✅ 1000 requests/day\n"
                    "✅ Priority processing\n"
                    "✅ No ads\n"
                    "✅ ZIP downloads"
                ),
                'language': 'en'
            },
            {
                'keywords': 'limit daily request quota',
                'answer': (
                    "📊 Daily Limits:\n\n"
                    "Free Users: 10 requests/day\n"
                    "Premium Users: 1000 requests/day\n\n"
                    "Limits reset at midnight UTC.\n\n"
                    "Want more? Get premium! Use /premium"
                ),
                'language': 'en'
            },
            {
                'keywords': 'support help ticket problem issue',
                'answer': (
                    "💬 Need Help?\n\n"
                    "1. Click '💬 Support' button\n"
                    "2. Click '🎫 Create Ticket'\n"
                    "3. Describe your issue\n"
                    "4. Attach screenshots if needed\n"
                    "5. Submit ticket\n\n"
                    "Our support team will respond soon!"
                ),
                'language': 'en'
            },
            {
                'keywords': 'referral invite friend bonus',
                'answer': (
                    "🎁 Referral Program:\n\n"
                    "1. Click '🎁 Referrals'\n"
                    "2. Copy your unique link\n"
                    "3. Share with friends\n"
                    "4. Both get bonus requests!\n"
                    "5. Get FREE premium after 10 referrals!\n\n"
                    "Start sharing today! 🚀"
                ),
                'language': 'en'
            },
            {
                'keywords': 'quality maxres hd sd resolution size',
                'answer': (
                    "🎨 Thumbnail Qualities:\n\n"
                    "MaxRes: 1920x1080 (Best quality)\n"
                    "HD: 640x480 (High quality)\n"
                    "Medium: 320x180 (Mobile friendly)\n"
                    "All: Get all available sizes\n\n"
                    "Choose based on your needs!"
                ),
                'language': 'en'
            },
            # Hindi FAQs
            {
                'keywords': 'कैसे प्राप्त डाउनलोड thumbnail',
                'answer': (
                    "📹 थंबनेल कैसे प्राप्त करें:\n\n"
                    "1. '📹 Get Thumbnail' बटन क्लिक करें\n"
                    "2. कोई YouTube लिंक भेजें\n"
                    "3. क्वालिटी चुनें (MaxRes, HD, Medium, या All)\n"
                    "4. थंबनेल तुरंत प्राप्त करें!\n\n"
                    "बहुत आसान है! 🎉"
                ),
                'language': 'hi'
            },
            {
                'keywords': 'premium कैसे अपग्रेड',
                'answer': (
                    "💎 Premium कैसे प्राप्त करें:\n\n"
                    "1. 10 दोस्तों को रेफर करें (मुफ्त!)\n"
                    "   - /referral से अपना लिंक प्राप्त करें\n\n"
                    "2. UPI से भुगतान करें\n"
                    "   - /premium से भुगतान जानकारी प्राप्त करें\n\n"
                    "Premium लाभ:\n"
                    "✅ 1000 requests/day\n"
                    "✅ Priority processing\n"
                    "✅ कोई विज्ञापन नहीं"
                ),
                'language': 'hi'
            },
        ]
        
        for faq in faqs:
            try:
                await db.execute('''
                    INSERT INTO faq (keywords, answer, language, is_active)
                    VALUES (?, ?, ?, 1)
                ''', (faq['keywords'], faq['answer'], faq['language']))
                print(f"✅ Added FAQ: {faq['keywords'][:30]}...")
            except Exception as e:
                print(f"❌ Error adding FAQ: {e}")
        
        await db.commit()
        print(f"\n✅ Added {len(faqs)} FAQ entries!")


async def check_tables():
    """Check if all tables exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        tables = [
            'users', 'usage', 'referrals', 'flood_control', 'payment_proofs',
            'support_tickets', 'support_messages', 'support_attachments',
            'agents', 'faq', 'bot_settings'
        ]
        
        for table in tables:
            async with db.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
            ) as cursor:
                result = await cursor.fetchone()
                if result:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' does NOT exist")


async def main():
    """Main initialization function."""
    print("🚀 Initializing database with default data...\n")
    
    print("📋 Checking database tables...")
    await check_tables()
    
    print("\n📝 Adding FAQ entries...")
    await initialize_faq()
    
    print("\n✅ Initialization complete!")
    print("\n💡 You can now start the bot with: python bot.py")
    print("💡 And the admin panel with: python admin_panel.py")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
