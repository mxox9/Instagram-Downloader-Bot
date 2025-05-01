import redis
from config import Config

class Database:
    def __init__(self):
        self.redis = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            password=Config.REDIS_PASSWORD,
            db=Config.REDIS_DB,
            decode_responses=False
        )
    
    def set_user_credentials(self, user_id: int, username: str, password: str):
        self.redis.hset(
            f"user:{user_id}",
            mapping={
                "username": username,
                "password": password
            }
        )
    
    def delete_user_credentials(self, user_id: int):
        return self.redis.delete(f"user:{user_id}")
    
    def get_user_credentials(self, user_id: int):
        creds = self.redis.hgetall(f"user:{user_id}")
        if creds:
            return (
                creds.get(b"username", b"").decode(),
                creds.get(b"password", b"").decode()
            )
        return None, None

db = Database()
