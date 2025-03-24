from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_user_by_username
from utils import verify_password  # Import from utils
# Password hashing setup using bcrypt for secure password storage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2PasswordBearer is used to extract the token from the request header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Function to authenticate the user by verifying username and password
async def authenticate_user(username: str, password: str):
    """
    Authenticate the user by comparing the plain password with the stored hashed password.
    
    Args:
        username (str): The username entered by the user.
        password (str): The plain password entered by the user.
    
    Returns:
        dict or None: The user data if authenticated, None otherwise.
    """
    # Fetch the user from the database using the provided username
    user = await get_user_by_username(username)
    
    # Check if the user exists and if the password matches
    try:
        verified = verify_password(password, user.hashed_password)
    except Exception as e:
        print(e)
    
    if not user or not verified:
        return None
    
    return user

# Function to create a JWT access token
def create_access_token(data: dict) -> str:
    """
    Create a JWT token that includes the user data and expiration time.
    
    Args:
        data (dict): The data to include in the token (typically user info).
    
    Returns:
        str: The encoded JWT token.
    """
    # Copy the data and add an expiration time
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})  # Set the expiration claim
        # Encode the token with the secret key and algorithm
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception as e:
        print(e)
        return None
    return token

# Dependency to retrieve the current user from the token
def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current user from the JWT token by decoding it and verifying the user exists in the database.
    
    Args:
        token (str): The JWT token sent by the client in the Authorization header.
    
    Returns:
        dict: The authenticated user.
    
    Raises:
        HTTPException: If the token is invalid or the user doesn't exist in the database.
    """
    try:
        # Decode the JWT token to extract user data
        print("---------------")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")  # Extract the subject (username) from the payload
        
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Fetch user data from the database
        user = get_user_by_username(username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found in the database")
        
        return user  # Return the user data if everything is valid

    except JWTError:
        # If there's an issue decoding the JWT token, raise an HTTPException
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

