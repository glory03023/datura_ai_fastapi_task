# utils.py
from passlib.context import CryptContext

# Password hashing setup using bcrypt for secure password storage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(plain_password: str) -> str:
    """
    Hash a plain password using bcrypt.
    
    Args:
        plain_password (str): The plain text password to hash.
    
    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that the plain password matches the hashed password.
    
    Args:
        plain_password (str): The plain text password entered by the user.
        hashed_password (str): The stored hashed password.
    
    Returns:
        bool: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
