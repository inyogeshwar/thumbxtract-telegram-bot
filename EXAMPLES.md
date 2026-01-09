# Usage Examples

## Quick Start

### Basic Usage

1. **Send a YouTube link**
   ```
   User: https://www.youtube.com/watch?v=dQw4w9WgXcQ
   Bot: ⏳ Processing your request...
   Bot: ✅ Found 8 thumbnails for video: dQw4w9WgXcQ
   Bot: [Sends 8 thumbnail images with quality labels]
   ```

2. **Send just the video ID**
   ```
   User: dQw4w9WgXcQ
   Bot: [Processes and sends thumbnails]
   ```

3. **Send a YouTube Shorts link**
   ```
   User: https://www.youtube.com/shorts/abc123xyz
   Bot: [Processes and sends thumbnails]
   ```

## Supported URL Formats

All these formats work:
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- `https://www.youtube.com/live/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `VIDEO_ID` (just the 11-character ID)

## Command Examples

### Getting Started
```
/start
```
Registers you and shows welcome message with instructions.

### Getting Help
```
/help
```
Shows detailed usage instructions and available commands.

### Checking Your Stats
```
/stats
```
Example response:
```
📊 Your Statistics:

Daily requests used: 3/10
Total referrals: 2
Premium status: No ❌
Member since: 2026-01-09 01:57:38
```

### Getting Your Referral Link
```
/referral
```
Example response:
```
🎁 Referral Program:

Share your link and earn bonuses!
Each referral gives you 5 extra requests.
Get 10 referrals for free premium! 💎

Your referral link:
https://t.me/YourBotName?start=ref_123456789

Total referrals: 2
```

### Checking Premium Info
```
/premium
```
Example response:
```
💎 Premium Benefits:

✅ 1000 requests per day
✅ Priority processing
✅ No ads
✅ Early access to new features

🎁 Get premium FREE by referring 10 users!
Use /referral to get your link.

Current referrals: 2/10
```

### Changing Language
```
/language
```
Shows a menu with available languages:
- English 🇬🇧
- Español 🇪🇸
- हिंदी 🇮🇳

## Referral System

### How to Refer Friends

1. Get your referral link:
   ```
   /referral
   ```

2. Share your link:
   ```
   https://t.me/YourBotName?start=ref_YOUR_USER_ID
   ```

3. When someone starts the bot using your link:
   - They get registered as your referral
   - You both get bonus requests
   - Your referral count increases

4. Earn premium:
   - Get 10 successful referrals
   - Automatically receive premium status
   - Enjoy unlimited daily requests!

## Premium Benefits

### Free vs Premium

| Feature | Free | Premium |
|---------|------|---------|
| Daily Requests | 10 | 1000 |
| Flood Control | Yes | Yes |
| All Thumbnails | Yes | Yes |
| Priority Support | No | Yes |
| No Ads | No | Yes |

### How to Get Premium

1. **Refer friends** (recommended)
   - Refer 10 users = Free premium forever
   - Use `/referral` to get your link

2. **Future payment options** (planned)
   - Monthly subscription
   - One-time purchase

## Multi-Language Support

### Automatic Detection

The bot automatically detects your language from:
1. Your manual selection (highest priority)
2. Your Telegram language setting
3. The language of your messages
4. Falls back to English if unsure

### Supported Languages

- **English** - Full support
- **Español** - Full support
- **हिंदी** - Full support

### Changing Language

1. Use `/language` command
2. Select your preferred language from the menu
3. All messages will now be in your chosen language

## Rate Limits & Flood Control

### Daily Limits
- **Free users**: 10 requests per day
- **Premium users**: 1000 requests per day
- Limits reset at midnight UTC

### Flood Control
- Maximum 5 requests per 60 seconds
- Prevents spam and abuse
- Automatic cooldown period

Example warning:
```
⚠️ Please slow down! Wait 45 seconds before trying again.
```

### When You Hit the Limit
```
⚠️ Daily limit reached (10 requests).
Upgrade to premium for 1000 requests per day!
Or refer friends to get bonus requests: /referral
```

## Error Handling

### Invalid Link
```
User: not_a_youtube_link
Bot: ❌ Invalid YouTube link or video ID. Please try again.
```

### General Error
```
❌ An error occurred. Please try again later.
```

If you continue to experience errors:
1. Check if the YouTube video exists
2. Try sending just the video ID
3. Wait a few minutes and try again
4. Contact the bot admin if issues persist

## Advanced Usage

### Batch Processing
Want to get thumbnails for multiple videos?
- Send them one at a time
- Wait for each to complete
- Don't spam (flood control applies)

### Best Practices
1. **Copy full URLs** - More reliable than partial links
2. **Check video ID** - Ensure it's exactly 11 characters
3. **Respect limits** - Don't spam the bot
4. **Report issues** - Help improve the bot

### API Integration
For developers wanting to integrate:
- Currently not available via API
- Use the Telegram bot interface
- Future API planned

## Troubleshooting

### Bot Not Responding
1. Check if you're rate limited
2. Ensure the URL is valid
3. Try using `/start` to re-register
4. Check your internet connection

### Wrong Language
1. Use `/language` to change manually
2. Update your Telegram language settings
3. The bot will remember your preference

### Thumbnails Not Loading
1. YouTube may not have all qualities
2. Some thumbnails might be missing
3. Try a different video
4. Report persistent issues

### Can't Get Premium
1. Check referral count with `/referral`
2. Ensure your referrals actually started the bot
3. Self-referrals don't count
4. Need exactly 10 referrals

## Tips & Tricks

1. **Save bandwidth** - Download only the quality you need
2. **Share wisely** - Your referral link is your key to premium
3. **Check stats regularly** - Monitor your usage
4. **Use shortcuts** - Just paste the video ID for faster results
5. **Report bugs** - Help make the bot better

## Privacy & Security

- **No data selling** - Your data stays private
- **Minimal storage** - Only essential info stored
- **Secure database** - SQLite with proper permissions
- **No video downloading** - Only thumbnail URLs
- **No spam** - Flood control protects everyone

## Support

Need help?
- Use `/help` for quick guidance
- Check this documentation
- Report issues to bot admin
- Join the community (if available)

## Future Features (Planned)

- [ ] Video metadata extraction
- [ ] Custom quality selection
- [ ] Batch processing
- [ ] Download links
- [ ] More languages
- [ ] API access
- [ ] Payment integration
- [ ] Statistics dashboard
