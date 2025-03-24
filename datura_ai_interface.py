from datura_py import Datura
import os
from config import DATURA_API_KEY
import datetime
import logging

# Initialize Datura client with API key from config
datura = Datura(api_key=DATURA_API_KEY)

# Set up logging to capture important events, especially errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_tweets(count: int, days: int):
    """
    Fetches a list of tweet texts based on specific filters from Datura API.
    
    Args:
        count (int): The number of tweets to fetch.
        days (int): The number of past days to consider when fetching tweets.
    
    Returns:
        list: A list of tweet texts.
        
    Raises:
        ValueError: If the `count` or `days` arguments are invalid.
        Exception: If there are issues with the Datura API request.
    """
    # Validate count and days parameters
    if not isinstance(count, int) or count <= 0:
        raise ValueError("`count` must be a positive integer.")
    if not isinstance(days, int) or days <= 0:
        raise ValueError("`days` must be a positive integer.")
    
    try:
        # Get current date and compute the start date
        current_date = datetime.datetime.now()
        start_date = (current_date - datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        end_date = current_date.strftime("%Y-%m-%d")
        
        # Make the API call to fetch tweets with the given parameters
        results = datura.basic_twitter_search(
            query="Whats going on with Bittensor",  # The search query for tweets
            sort="Top",  # Sort by 'Top' tweets
            user="elonmusk",  # Tweets from user "elonmusk"
            start_date=start_date,  # Filter tweets from the start date
            end_date=end_date,  # Filter tweets up to the current date
            lang="en",  # Only tweets in English
            verified=True,  # Only verified accounts
            blue_verified=True,  # Blue verified accounts
            is_quote=True,  # Include tweets that are quotes
            is_video=True,  # Include tweets that have video
            is_image=True,  # Include tweets that have images
            min_retweets=1,  # Minimum retweets required
            min_replies=1,  # Minimum replies required
            min_likes=1,  # Minimum likes required
            count=count  # Number of tweets to retrieve
        )
        
        # Check if results are empty and log if necessary
        if not results:
            logger.warning(f"No tweets found for query. Count: {count}, Days: {days}.")
            return []

        # Extract tweet texts from the results
        tweet_texts = [tweet['text'] for tweet in results]
        
        # Log how many tweets were retrieved
        logger.info(f"Fetched {len(tweet_texts)} tweets.")
        return tweet_texts
        
    except Exception as e:
        # Log any errors that occur during the API request or data extraction
        logger.error(f"Error while fetching tweets: {e}")
        raise Exception(f"Failed to fetch tweets: {str(e)}") from e
