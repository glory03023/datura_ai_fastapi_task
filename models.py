from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class User(BaseModel):
    """
    Represents a user in the system.
    
    Attributes:
        username (str): The unique username of the user.
        full_name (str): The full name of the user.
        email (EmailStr): The email of the user, validated to be in the correct email format.
        hashed_password (str): The hashed password of the user.
    """
    username: str
    full_name: str
    email: EmailStr  # Email field with automatic validation for valid email format.
    hashed_password: str


class TradingLog(BaseModel):
    """
    Represents a trading action log in the system.
    
    Attributes:
        user_id (str): The unique identifier of the user performing the action.
        action_type (str): The action being performed ('stake' or 'unstake').
        netuid (int): The network unique ID where the action occurs.
        hotkey (str): The hotkey associated with the wallet performing the action.
        amount (float): The amount staked or unstaked.
        timestamp (datetime): The timestamp when the action was performed.
        transaction_id (str, optional): The ID of the transaction associated with the action (default is None).
    """
    user_id: str
    action_type: str  # 'stake' or 'unstake'
    netuid: int
    hotkey: str
    amount: float
    timestamp: datetime
    transaction_id: Optional[str] = None  # Transaction ID is optional (default is None)


