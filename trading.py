from sentiment_task import get_sentiment_score
from bittensor_wallet_interface import add_stake, unstake
from database import log_trading_action
import logging

# Set up logging for debugging and monitoring
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def trading_process(netuid, hotkey, user):
    """
    This function performs a trading action (staking or unstaking) based on the sentiment score.
    
    The sentiment score is fetched from the `get_sentiment_score()` function. Based on the sign of the score:
    - If the score is positive, the function stakes a calculated amount.
    - If the score is negative, the function unstakes a calculated amount.
    
    The action is logged in the database with the user's trading action (stake or unstake).

    Parameters:
        - netuid (int): The unique identifier for the network where the action is to take place.
        - hotkey (str): The hotkey associated with the wallet for staking/unstaking.
        - user (dict): The authenticated user performing the action, required to log the action.

    Returns:
        - bool: Returns `True` if a trading action (stake or unstake) was performed, `False` otherwise.
    """
    
    # Fetch the current sentiment score (this could be positive or negative)
    score = get_sentiment_score()

    # Calculate the amount to stake/unstake. The absolute value of the score is used,
    # and a percentage (0.01) of that value is used for the trading action.
    amount = abs(score) * 0.01  # 1% of the absolute sentiment score

    # If sentiment score is positive, perform staking action
    if score > 0:
        try:
            # Perform the staking action
            add_stake(netuid, hotkey, amount)
            
            # Log the trading action in the database
            await log_trading_action(user.username, "stake", netuid, hotkey, amount)
            return True
        
        except Exception as e:
            # Log any error encountered during the staking process
            logger.error(f"Error during staking process: {e}")
            return False

    # If sentiment score is negative, perform unstaking action
    elif score < 0:
        try:
            # Perform the unstaking action
            unstake(netuid, hotkey, amount)
            
            # Log the trading action in the database
            await log_trading_action(user.username, "unstake", netuid, hotkey, amount)
            return True
        
        except Exception as e:
            # Log any error encountered during the unstaking process
            logger.error(f"Error during unstaking process: {e}")
            return False

    # If the sentiment score is zero, no action is taken
    return False
