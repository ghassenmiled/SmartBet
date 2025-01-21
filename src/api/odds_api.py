import os
import http.client
import json
import logging
from typing import List, Dict, Optional

# Constants
API_HOSTS = {
    "bet365": "bet365-api-inplay.p.rapidapi.com",
    "other_website": "other-website-api.com"
}

API_ENDPOINTS = {
    "bet365": "/bet365/get_betfair_forks",
    "other_website": "/other_website/get_odds"
}

def get_gambling_odds(website: str) -> Optional[List[Dict[str, str]]]:
    """
    Fetch gambling odds from the specified website's API.

    Args:
        website (str): The website name for which to fetch odds.

    Returns:
        list: A list of dictionaries containing odds information, or None if an error occurs.
    """
    api_key = os.getenv('API_KEY')
    
    if not api_key:
        logging.error("API key is missing. Please set the 'API_KEY' environment variable.")
        return None

    # Check if the website is supported
    if website not in API_HOSTS:
        logging.error(f"Unsupported website: {website}")
        return None

    # Configure connection and headers based on the website
    conn = http.client.HTTPSConnection(API_HOSTS[website])
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': API_HOSTS[website]
    }
    endpoint = API_ENDPOINTS[website]

    try:
        # Make the API request
        conn.request("GET", endpoint, headers=headers)
        res = conn.getresponse()
        data = res.read()

        # Decode and parse JSON data
        data = json.loads(data.decode("utf-8"))

        if isinstance(data, list) and data:
            # Process and extract relevant odds data
            odds_list = [
                {
                    "event_name": event.get('bK1_EventName', 'N/A'),
                    "bookmaker1": event.get('bookmaker1', 'N/A'),
                    "bet_name1": event.get('bK1_BetName', 'N/A'),
                    "bet_coef1": event.get('bK1_BetCoef', 'N/A'),
                    "bookmaker2": event.get('bookmaker2', 'N/A'),
                    "bet_name2": event.get('bK2_BetName', 'N/A'),
                    "bet_coef2": event.get('bK2_BetCoef', 'N/A'),
                }
                for event in data
            ]
            return odds_list
        else:
            logging.error("Invalid or empty data structure received from the API.")
            return None

    except json.JSONDecodeError as json_err:
        logging.error(f"JSON decoding error: {json_err}")
        return None
    except http.client.HTTPException as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error fetching gambling odds: {e}")
        return None
    finally:
        conn.close()
