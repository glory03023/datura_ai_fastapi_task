import os
from dotenv import load_dotenv
import logging
from distutils.util import strtobool

# Configure logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Determine which environment file to load
env = os.getenv("ENV", "development")  # Default to 'development' if ENV is not set

# Load the correct .env file
if env == "production":
    load_dotenv(".env.prod")
    logger.info("Loaded .env.prod for production environment")
else:
    load_dotenv(".env.dev")
    logger.info("Loaded .env.dev for development environment")

# Access environment variables with error handling for missing variables
DEBUG = strtobool(os.getenv("DEBUG", "False"))  # Convert the string to a boolean
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
DATURA_API_KEY = os.getenv("DATURA_API_KEY")
CHUTES_API_KEY = os.getenv("CHUTES_API_KEY")
TESTNET_WALLET_MNE = os.getenv("TESTNET_WALLET_MNE")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")  # Default to 60 minutes

# Ensure critical environment variables are set
required_env_vars = [DATABASE_URL, REDIS_URL, SECRET_KEY, ALGORITHM, DATURA_API_KEY, CHUTES_API_KEY]
missing_vars = [var for var in required_env_vars if var is None]

if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Convert ACCESS_TOKEN_EXPIRE_MINUTES to an integer
ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)

# Log success of loading environment variables
logger.info("Environment variables loaded successfully.")
