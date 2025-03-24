import redis.asyncio as aioredis
from config import REDIS_URL
import logging

# Set up logger for connection issues or general use
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

async def get_redis_connection():
    """
    Establish an asynchronous connection to Redis using the provided URL from the config.
    
    This function uses the `aioredis` library to asynchronously connect to the Redis server.
    
    Returns:
        aioredis.Redis: A Redis connection object for interacting with the Redis server.
    
    Raises:
        ConnectionError: If unable to connect to Redis.
    """
    try:
        # Attempt to establish a Redis connection
        redis_conn = await aioredis.from_url(REDIS_URL, decode_responses=True)
        logger.info("Successfully connected to Redis.")
        return redis_conn
    except Exception as e:
        # Log the exception and raise a ConnectionError with details
        logger.error(f"Failed to connect to Redis: {e}")
        raise ConnectionError(f"Could not connect to Redis at {REDIS_URL}.") from e
