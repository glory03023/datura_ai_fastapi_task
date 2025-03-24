import motor.motor_asyncio
from pydantic import BaseModel, ValidationError
from fastapi import FastAPI, HTTPException
from datetime import datetime
from models import User, TradingLog
from typing import Dict, Optional
from utils import get_hashed_password  # Import from utils
import logging
from config import DATABASE_URL
# MongoDB client setup (motor)
client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)
db = client.datura_ai_db  # Database
users_collection = db.users  # Users collection
trading_logs_collection = db.trading_logs  # Trading logs collection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to store a user in MongoDB
async def store_user(user_data: Dict[str, str]) -> Optional[dict]:
    """
    Store a user in the MongoDB database. If a user with the same username already exists, return an error.
    
    Args:
        user_data (Dict[str, str]): The user information including username, full_name, email, and password.
    
    Returns:
        Optional[dict]: A result message or error description.
    """
    try:
        # Check if the user already exists
        existing_user = await users_collection.find_one({"username": user_data["username"]})
        if existing_user:
            logger.warning(f"User with username {user_data['username']} already exists.")
            return {"error": "User with this username already exists."}

        # Hash password and remove the original password field
        user_data["hashed_password"] = get_hashed_password(user_data["password"])
        user_data.pop("password", None)

        # Create and validate User object
        user = User(**user_data)

        # Insert user into MongoDB collection
        result = await users_collection.insert_one(user.dict())
        logger.info(f"User {user.username} created successfully with ID: {result.inserted_id}")
        return {"message": f"User created successfully with ID: {result.inserted_id}"}

    except ValidationError as e:
        logger.error(f"Validation error: {e.errors()}")
        return {"error": f"Validation error: {e.errors()}"}
    
    except Exception as e:
        logger.error(f"Error occurred while storing the user: {str(e)}")
        return {"error": f"An error occurred while storing the user: {str(e)}"}

# Function to get a user by username
async def get_user_by_username(username: str) -> Optional[User]:
    """
    Retrieve a user from the database by their username.

    Args:
        username (str): The username of the user to be fetched.

    Returns:
        Optional[User]: The user object if found, or None if not.
    """
    try:
        user_data = await users_collection.find_one({"username": username})
        if user_data:
            # Return the user as a validated Pydantic model
            return User(**user_data)
        logger.warning(f"User {username} not found.")
        return None

    except Exception as e:
        logger.error(f"Error occurred while fetching user {username}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error occurred while fetching user.")

# Function to log a trading action in MongoDB
async def log_trading_action(user_id: str, action_type: str, netuid: int, hotkey: str, amount: float, transaction_id: str = None):
    """
    Log a trading action into the trading logs collection.

    Args:
        user_id (str): The ID of the user performing the action.
        action_type (str): The type of action ("stake" or "unstake").
        netuid (int): The netuid related to the action.
        hotkey (str): The hotkey related to the action.
        amount (float): The amount involved in the action.
        transaction_id (str, optional): The transaction ID associated with the action, default is None.
    """
    try:
        timestamp = datetime.utcnow()  # Store the current UTC time as timestamp
        trading_log = TradingLog(
            user_id=user_id,
            action_type=action_type,
            netuid=netuid,
            hotkey=hotkey,
            amount=amount,
            timestamp=timestamp,
            transaction_id=transaction_id
        )

        # Insert the trading log into MongoDB
        result = await trading_logs_collection.insert_one(trading_log.dict())
        logger.info(f"Trading action logged successfully. Log inserted with ID: {result.inserted_id}")
    except Exception as e:
        logger.error(f"Error occurred while logging trading action: {str(e)}")
        raise HTTPException(status_code=500, detail="Error occurred while logging trading action.")
