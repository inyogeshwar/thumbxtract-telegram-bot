# Deployment Guide

## Local Development

1. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure the bot**
   ```bash
   cp config.ini.example config.ini
   # Edit config.ini with your settings
   ```

3. **Run the bot**
   ```bash
   python bot.py
   ```

## Production Deployment

### Using systemd (Linux)

1. **Create a systemd service file**
   ```bash
   sudo nano /etc/systemd/system/thumbxtract-bot.service
   ```

2. **Add the following content**
   ```ini
   [Unit]
   Description=YouTube Thumbnail Extractor Telegram Bot
   After=network.target

   [Service]
   Type=simple
   User=YOUR_USER
   WorkingDirectory=/path/to/thumbxtract-telegram-bot
   ExecStart=/path/to/venv/bin/python bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start the service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable thumbxtract-bot
   sudo systemctl start thumbxtract-bot
   sudo systemctl status thumbxtract-bot
   ```

4. **View logs**
   ```bash
   sudo journalctl -u thumbxtract-bot -f
   ```

### Using Docker

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.11-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   CMD ["python", "bot.py"]
   ```

2. **Create docker-compose.yml**
   ```yaml
   version: '3.8'
   
   services:
     bot:
       build: .
       container_name: thumbxtract-bot
       restart: unless-stopped
       volumes:
         - ./config.ini:/app/config.ini
         - ./bot_data.db:/app/bot_data.db
       environment:
         - TZ=UTC
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Using Heroku

1. **Create Procfile**
   ```
   worker: python bot.py
   ```

2. **Deploy to Heroku**
   ```bash
   heroku create your-bot-name
   git push heroku main
   heroku ps:scale worker=1
   ```

3. **Set config vars**
   ```bash
   heroku config:set BOT_TOKEN=your_token_here
   ```

### Using Railway

1. **Create railway.json**
   ```json
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "python bot.py",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

2. **Connect your GitHub repo to Railway**
3. **Add environment variables in Railway dashboard**

## Environment Variables (Alternative to config.ini)

You can use environment variables instead of config.ini:

```python
import os

token = os.getenv('BOT_TOKEN', self.config.get('bot', 'token'))
```

## Security Best Practices

1. **Never commit config.ini** - It contains sensitive tokens
2. **Use environment variables** for production
3. **Restrict admin IDs** to trusted users only
4. **Enable firewall** rules on your server
5. **Keep dependencies updated** regularly
6. **Monitor logs** for suspicious activity
7. **Backup database** regularly

## Monitoring

### Basic Health Check
```bash
# Check if bot is running
ps aux | grep bot.py

# Check logs
tail -f /var/log/thumbxtract-bot.log
```

### Advanced Monitoring
- Use tools like Prometheus + Grafana
- Set up alerts for downtime
- Monitor database size
- Track API rate limits

## Database Backup

```bash
# Backup SQLite database
cp bot_data.db bot_data.db.backup.$(date +%Y%m%d)

# Automated backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp bot_data.db backups/bot_data.db.$DATE
find backups/ -name "bot_data.db.*" -mtime +7 -delete
```

## Troubleshooting

### Bot not responding
- Check if the bot process is running
- Verify network connectivity
- Check bot token validity
- Review error logs

### Database locked errors
- Ensure only one instance is running
- Check file permissions
- Consider connection pooling

### Rate limit errors
- Implement request queuing
- Add delays between messages
- Upgrade to Bot API server if needed

## Scaling

For high-traffic scenarios:
1. Use connection pooling
2. Implement caching
3. Use asynchronous operations (already implemented)
4. Consider sharding database
5. Load balance across multiple instances
