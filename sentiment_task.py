import logging
import asyncio
from datetime import datetime
from datura_ai_interface import get_tweets
from chutes_ai_interface import analyze_tweet

# Global variable to store the fetched sentiment score
sentiment_score = 0

# Set up logging configuration
logging.basicConfig(level=logging.INFO)  # Set log level to INFO for application logs
logger = logging.getLogger(__name__)

# Function to fetch and analyze sentiment from tweets
async def analyze_sentiment():
    """
    Fetch tweets from Datura API, analyze their sentiment, and update the global sentiment score.

    This function simulates fetching tweets for sentiment analysis, aggregates the results,
    and calculates the average sentiment score from the tweets. It runs asynchronously.

    It also handles errors gracefully by logging any exceptions that occur during the process.
    """
    global sentiment_score  # Use the global variable to store the sentiment score
    
    try:
        # Log the start of the data fetching process
        logger.info("Fetching new data from Datura API...")
        
        # Fetch the most recent 10 tweets from the past 7 days
        tweets = await get_tweets(count=10, days=7)
        
        # If no tweets are fetched, log a warning and skip analysis
        if not tweets:
            logger.warning("No tweets fetched. Skipping sentiment analysis.")
            return
        
        # Initialize variable to accumulate sentiment scores
        score_sum = 0
        
        # Loop through the fetched tweets and analyze each one
        for tweet in tweets:
            # Analyze the sentiment of the tweet using the Chutes API
            sub_score = await analyze_tweet(tweet)
            score_sum += sub_score  # Accumulate the sentiment scores
        
        # Calculate the average sentiment score
        sentiment_score = score_sum / len(tweets)
        
        # Log the sentiment analysis result
        logger.info(f"Sentiment analysis complete. Average sentiment score: {sentiment_score:.2f}")

    except Exception as e:
        # Log any error that occurs during sentiment analysis
        logger.error(f"Error occurred while analyzing sentiment: {e}")
        

def get_sentiment_score():
    """
    Get the current sentiment score.

    This function returns the latest sentiment score calculated by `analyze_sentiment`.
    The score represents the average sentiment of the fetched tweets.

    Returns:
        float: The current sentiment score (average sentiment of fetched tweets).
    """
    global sentiment_score  # Access the global sentiment score
    return sentiment_score

# Optional: Function to start the sentiment analysis periodically
async def start_sentiment_analysis_periodically():
    """
    Starts the sentiment analysis periodically every 2 hours.
    This function uses an asyncio loop to schedule the periodic execution of `analyze_sentiment`.
    """
    while True:
        # Call the sentiment analysis function
        await analyze_sentiment()
        # Wait for 2 hours (7200 seconds) before the next run
        await asyncio.sleep(7200)

# Optional: Run the periodic task if needed (example usage)
# asyncio.run(start_sentiment_analysis_periodically())  # Uncomment to run periodically in an event loop
