import requests
import json
import os
import logging
import re
from config import CHUTES_API_KEY

# Set API endpoint and token
def analyze_tweet(tweet):
    url = "https://llm.chutes.ai/v1/chat/completions"
    
    # Define headers
    headers = {
        "Authorization": f"Bearer {CHUTES_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Define payload
    data = {
        "model": "unsloth/Llama-3.2-3B-Instruct",
        "messages": [
            {
                "role": "user", 
                "content": f"Evaluate positive or negative score within a range of -100 to 100 for Bittensor trading from following text: {tweet}"
            }
        ],
        "stream": False,
        "max_tokens": 1024,
        "temperature": 0.7
    }
    
    try:
        # Make the POST request
        response = requests.post(url, headers=headers, json=data, stream=True)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            result = response.json()
            # Extract useful data
            text = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # If there's no content in the response, log and return default score
            if not text:
                logging.warning(f"No content returned from Chutes API for tweet: {tweet}")
                return 0
            
            # Use regex to extract numbers from the response text
            pattern = r'-?\b\d+(\.\d+)?\b'
            numbers = re.findall(pattern, text)
            filtered_numbers = [float(num) for num in numbers if -100 <= float(num) <= 100]
            
            # Return the first valid number or 0 if no valid number found
            if filtered_numbers:
                return filtered_numbers[0]
            else:
                logging.warning(f"No valid sentiment score found in response: {text}")
                return 0
        else:
            # If the request fails, log the error and return default score
            logging.error(f"Error: Received status code {response.status_code} from Chutes API for tweet: {tweet}")
            return 0
    except requests.exceptions.RequestException as e:
        # Handle network-related errors
        logging.error(f"RequestException occurred: {e} while processing tweet: {tweet}")
        return 0
