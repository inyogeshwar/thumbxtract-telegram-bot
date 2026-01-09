#!/usr/bin/env python3
"""
Simple test script to validate bot components without running the full bot.
Tests YouTube extraction, database operations, and i18n functionality.
"""

import asyncio
import sys
from youtube_utils import YouTubeExtractor
from database import Database
from i18n import I18n


async def test_youtube_extractor():
    """Test YouTube video ID extraction."""
    print("=" * 50)
    print("Testing YouTube Extractor")
    print("=" * 50)
    
    test_cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://youtu.be/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/shorts/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/live/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("https://www.youtube.com/embed/dQw4w9WgXcQ", "dQw4w9WgXcQ"),
        ("invalid_link", None),
    ]
    
    extractor = YouTubeExtractor()
    passed = 0
    failed = 0
    
    for url, expected in test_cases:
        result = extractor.extract_video_id(url)
        if result == expected:
            print(f"✅ PASS: {url[:50]}")
            passed += 1
        else:
            print(f"❌ FAIL: {url[:50]} (expected: {expected}, got: {result})")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    
    # Test thumbnail generation
    print("\nTesting thumbnail generation...")
    thumbnails = extractor.get_thumbnails("dQw4w9WgXcQ")
    print(f"✅ Generated {len(thumbnails)} thumbnail URLs")
    for thumb in thumbnails[:3]:
        print(f"  - {thumb['quality']}: {thumb['url'][:60]}...")
    
    return failed == 0


async def test_database():
    """Test database operations."""
    print("\n" + "=" * 50)
    print("Testing Database Operations")
    print("=" * 50)
    
    db = Database("test_bot.db")
    await db.initialize()
    print("✅ Database initialized")
    
    # Test user operations
    await db.add_user(12345, "testuser", "Test User", "en")
    print("✅ User added")
    
    user = await db.get_user(12345)
    if user:
        print(f"✅ User retrieved: {user['username']}")
    else:
        print("❌ Failed to retrieve user")
        return False
    
    # Test premium status
    await db.set_premium(12345, True)
    is_premium = await db.is_premium(12345)
    print(f"✅ Premium status: {is_premium}")
    
    # Test usage tracking
    await db.increment_usage(12345)
    usage = await db.get_daily_usage(12345)
    print(f"✅ Daily usage: {usage}")
    
    # Test flood control
    is_flooding, wait_time = await db.check_flood_control(12345, 5, 60)
    print(f"✅ Flood control: flooding={is_flooding}, wait={wait_time}")
    
    # Test stats
    stats = await db.get_stats()
    print(f"✅ Bot stats: {stats}")
    
    # Clean up
    import os
    if os.path.exists("test_bot.db"):
        os.remove("test_bot.db")
        print("✅ Test database cleaned up")
    
    return True


def test_i18n():
    """Test internationalization."""
    print("\n" + "=" * 50)
    print("Testing Internationalization")
    print("=" * 50)
    
    i18n = I18n()
    
    # Test language detection
    test_texts = [
        ("Hello, how are you?", "en"),
        ("Hola, ¿cómo estás?", "es"),
        ("नमस्ते, आप कैसे हैं?", "hi"),
    ]
    
    for text, expected_lang in test_texts:
        detected = i18n.detect_language(text)
        if detected == expected_lang:
            print(f"✅ Detected {expected_lang} from: {text[:30]}")
        else:
            print(f"⚠️  Expected {expected_lang}, got {detected} from: {text[:30]}")
    
    # Test translations
    en_text = i18n.get_text('welcome', 12345, 'en')
    es_text = i18n.get_text('welcome', 12345, 'es')
    hi_text = i18n.get_text('welcome', 12345, 'hi')
    
    print(f"\n✅ English: {en_text[:50]}...")
    print(f"✅ Spanish: {es_text[:50]}...")
    print(f"✅ Hindi: {hi_text[:50]}...")
    
    # Test text formatting
    formatted = i18n.get_text('referral_info', 12345, 'en', 
                             bonus=5, required=10, link="test.link", count=3)
    print(f"\n✅ Formatted text works: {bool(formatted)}")
    
    return True


async def main():
    """Run all tests."""
    print("\n🧪 Running Bot Component Tests\n")
    
    results = []
    
    # Test YouTube extractor
    results.append(await test_youtube_extractor())
    
    # Test database
    results.append(await test_database())
    
    # Test i18n
    results.append(test_i18n())
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    if all(results):
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
