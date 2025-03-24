import logging
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from bittensor_interface import get_tao_dividend_from_netuid_address, get_tao_dividends_for_subnet, get_tao_dividends_for_address
from authenticator import authenticate_user, create_access_token, get_current_user
from database import store_user
from trading import trading_process
from sentiment_task import analyze_sentiment

# Initialize FastAPI app and APScheduler
app = FastAPI()

# Set up logging for debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Root endpoint to guide users to the Swagger documentation
@app.get("/")
def read_root():
    """
    Root endpoint to guide users to the Swagger documentation.
    """
    return {"message": "Please refer to the Swagger doc at /docs"}

# Register endpoint to create a new user
@app.post("/api/v1/register")
async def register(
    username: str,
    full_name: str,
    email: str,
    password: str
):
    """
    Register a new user in the system. This stores the user's information in the database.
    
    Parameters:
        - username: The username of the new user.
        - full_name: Full name of the user.
        - email: Email address of the user.
        - password: User's password.

    Returns:
        - result: The result of storing the user in the database.
    """
    new_user = {
        "username": username,
        "full_name": full_name,
        "email": email,
        "password": password
    }
    # Store the user data in the database
    result = await store_user(new_user)
    return {"result": result}

# Login endpoint to authenticate a user and return a JWT token
@app.post("/api/v1/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate a user and return a JWT access token.

    Parameters:
        - form_data: The OAuth2 password request form containing the username and password.

    Returns:
        - access_token: The JWT token for the authenticated user.
        - token_type: The type of the token, which is 'bearer'.
    """
    # Authenticate the user with the provided username and password
    
    user = await authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    # Generate an access token for the authenticated user
    access_token = create_access_token(data={"sub": user.username})
    print(access_token)
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/tao_dividends")
async def get_tao_dividends(
    netuid: Optional[int] = Query(None, description="Filter by netuid"),
    hotkey: Optional[str] = Query(None, description="Filter by hotkey"),
    trade: bool = Query(False, description="Include trade data in the response"),
    user: dict = Depends(get_current_user)  # Ensure the user is authenticated
):
    """
    Fetch TAO dividends based on optional netuid and hotkey filters.
    The function also triggers trade actions if the trade parameter is set to True.
    
    Parameters:
        - netuid: Optional filter by netuid (integer).
        - hotkey: Optional filter by hotkey (string).
        - trade: Boolean flag indicating if trade data should be included in the response.
        - user: Current authenticated user (automatically passed by Depends).
    
    Returns:
        - A JSON response with the relevant dividend data and additional metadata.
    """
    stake_tx_triggered = False  # Flag to track if a trade action is triggered
    
    # If 'trade' is true, attempt to trigger a trade action with netuid and hotkey
    if trade:
        if netuid is not None and hotkey is not None:
            stake_tx_triggered = await trading_process(netuid, hotkey, user)
    
    # Handle different cases based on the presence of netuid and hotkey
    if netuid is None and hotkey is None:
        return {"message": "No netuid or hotkey provided"}
    
    elif netuid is not None and hotkey is not None:
        # Fetch dividends based on both netuid and hotkey
        value = await get_tao_dividend_from_netuid_address(netuid=netuid, address=hotkey)
        return {
            "netuid": netuid,
            "hotkey": hotkey,
            "dividend": value,
            "cached": True,
            "stake_tx_triggered": stake_tx_triggered
        }
    
    elif netuid is not None:
        # Fetch dividends for the entire subnet associated with netuid
        values = await get_tao_dividends_for_subnet(netuid)
        return {
            "netuid": netuid,
            "hotkey": hotkey,
            "dividend": values,
            "cached": True,
            "stake_tx_triggered": stake_tx_triggered
        }
    
    else:
        # Fetch dividends for a specific hotkey
        values = await get_tao_dividends_for_address(hotkey)
        return {
            "netuid": netuid,
            "hotkey": hotkey,
            "dividend": values,
            "cached": True,
            "stake_tx_triggered": stake_tx_triggered
        }
