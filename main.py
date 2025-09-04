from pyrogram import Client
from config import Config
import handler  # noqa: F401  (to register handler)

app = Client(
    "insta-bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

if __name__ == "__main__":
    print("🚀 Bot started...")
    app.run()
