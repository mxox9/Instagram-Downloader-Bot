# Instagram Downloader Telegram Bot 🚀

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Contributors](https://img.shields.io/badge/contributors-1-lightgrey)

A feature-rich Telegram bot that lets users download Instagram posts, reels, and profile pictures directly through Telegram. Built with Python and powered by Instaloader + Telethon.

## Features ✨
- 📥 Download Instagram posts/reels (videos & images)
- 👤 Get Instagram profile pictures with bio
- 📊 Admin dashboard with user statistics
- 📢 Broadcast messages to all users
- 📄 Logging system for error tracking
- ⚡ Redis database integration

## Installation 🛠️

1. Clone the repository:
```bash
git clone https://github.com/Harshit-shrivastav/Instagram-Downloader-Bot.git
cd instagram-downloader-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration ⚙️

Create `.env` file with following variables:
```ini
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
BOT_TOKEN=your_bot_token
AUTH_USER_ID=admin_user_ids
REDIS_HOST=your_redis_host
REDIS_PORT=your_redis_port
REDIS_PASSWORD=your_redis_password
```

## Usage 📲
1. Start the bot:
```bash
python3 -m main
```

2. Send Instagram links to the bot:
   - Post URL: `https://www.instagram.com/reel/Cxyz...`
   - Post URL: `https://www.instagram.com/p/Cxyz...`
   - Profile URL: `https://www.instagram.com/username/`

## Commands 🎮
| Command | Description | Access |
|---------|-------------|--------|
| `/start` | Initialize the bot | All users |
| `/users` | Get total user count | Admin |
| `/bcast` | Broadcast message | Admin |
| `/logs` | Get error logs | Admin |

## Database Setup 🗃️
1. Create a Redis database using:
   - Redis Cloud (https://redis.com)
   - Upstash (https://upstash.com)
2. Add your Redis credentials to `.env`

## Environment Variables 🌐
| Variable | Description | Example |
|----------|-------------|---------|
| `API_ID` | Telegram API ID | 123456 |
| `API_HASH` | Telegram API Hash | abcdef12345 |
| `BOT_TOKEN` | Telegram bot token | 123456:ABC-DEF1234 |
| `AUTH_USER_ID` | Admin user IDs (space separated) | 12345 67890 |
| `REDIS_HOST` | Redis host address | your-redis-host.redislabs.com |
| `REDIS_PORT` | Redis port | 12345 |
| `REDIS_PASSWORD` | Redis password | your_strong_password |

## Requirements 📦
```python
telethon
instaloader
requests
redis
python-dotenv
```

## Logging 📝
All activities are logged in `log.txt`. Admins can retrieve logs using `/logs` command.

## Support ❤️
Found a bug? Open an issue!  
Like this project? Leave a ⭐!
