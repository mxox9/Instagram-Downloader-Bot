import os
from dotenv import load_dotenv

load_dotenv()

class Telegram:
    API_ID = int(os.environ.get('API_ID'))
    API_HASH = os.environ.get('API_HASH')
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    AUTH_USER_ID = list(map(int, filter(None, os.environ.get("AUTH_USER_ID", "").split())))
    SESSION_ID = os.environ.get('SESSION_ID', None)
    
class Database:
    REDIS_HOST = os.environ.get('REDIS_HOST') # Example: ec2.redns.redis-cloud.com, local-elephant-58690.upstash.io
    REDIS_PORT = int(os.environ.get('REDIS_PORT')) #Example 8080, 47384
    REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD')
