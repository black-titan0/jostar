import redis

from Jostar import settings


class RedisProxy:
    @staticmethod
    def cache_with_ttl(key, value, ttl=settings.REDIS_CACHE_TIMEOUT):
        redis_client.setex(key, ttl, value)

    @staticmethod
    def get_cached_value(key):
        value = redis_client.get(key)
        if value is not None:
            return value.decode('utf-8')  # Decode bytes to string
        return None


redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)
