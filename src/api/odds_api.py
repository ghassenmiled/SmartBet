import os
import http.client
import json
import logging
from typing import List, Dict, Optional

def get_gambling_odds() :

    # Configure connection and headers based on the website
    conn = http.client.HTTPSConnection("bet365-api-inplay.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': "33a834c215msha6e80ead5dea978p1a94d9jsn2668968f7801",
        'x-rapidapi-host': "bet365-api-inplay.p.rapidapi.com"
    }
    endpoint = "/bet365/get_betfair_forks"

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
