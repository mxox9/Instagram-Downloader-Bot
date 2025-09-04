import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram API
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")

    # Instagram (optional)
    INSTA_USERNAME = os.getenv("INSTA_USERNAME", None)
    INSTA_PASSWORD = os.getenv("INSTA_PASSWORD", None)

    @property
    def has_insta_creds(self):
        return bool(self.INSTA_USERNAME and self.INSTA_PASSWORD)
