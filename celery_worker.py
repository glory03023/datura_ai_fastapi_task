from celery import Celery
import asyncio
import logging
from sentiment_task import start_sentiment_analysis_periodically

# Create a Celery instance. Redis is used as both the message broker and result backend.
app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.task
def perform_sentiment_analysis():
    """
    This Celery task is responsible for running the sentiment analysis in a periodic manner.
    It invokes the `start_sentiment_analysis_periodically()` function that fetches and analyzes tweets.
    
    We wrap the async call to `start_sentiment_analysis_periodically()` using `asyncio.run()`.
    """
    try:
        # Run the async task with asyncio.run, which handles the event loop properly
        logger.info("Starting sentiment analysis task.")
        asyncio.run(start_sentiment_analysis_periodically())  # Run the async task synchronously
        logger.info("Sentiment analysis task completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred during sentiment analysis: {e}")
