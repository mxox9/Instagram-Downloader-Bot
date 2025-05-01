import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram API
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    
    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    
    # Instagram (optional)
    INSTA_USERNAME = os.getenv("INSTA_USERNAME", None)
    INSTA_PASSWORD = os.getenv("INSTA_PASSWORD", None)
    
    @property
    def has_insta_creds(self):
        return bool(self.INSTA_USERNAME and self.INSTA_PASSWORD)
