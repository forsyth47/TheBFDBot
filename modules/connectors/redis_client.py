import redis
import os
import sys
import secrets

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config

class RedisClient:
    def __init__(self):
        self.redis_enabled = config.redis_enabled
        self.client = None

        if self.redis_enabled:
            try:
                self.host = getattr(config, "redis_host", "localhost")
                self.port = int(getattr(config, "redis_port", 6379))
                self.db = int(getattr(config, "redis_db", 0))

                self.client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    decode_responses=True
                )
                # Test connection
                self.client.ping()
                print("✅ Redis connection established.")
            except Exception as e:
                print(f"⚠️ Redis connection failed: {e}")
                self.client = None
                self.redis_enabled = False

    def get(self, key):
        if self.client:
            return self.client.get(key)
        return None

    def set(self, key, value, ex=None):
        if self.client:
            return self.client.set(key, value, ex=ex)
        return None

    def delete(self, key):
        if self.client:
            return self.client.delete(key)
        return None

    @staticmethod
    def gen_token():
        return secrets.token_urlsafe(5)

# Create a singleton instance
r = RedisClient()
