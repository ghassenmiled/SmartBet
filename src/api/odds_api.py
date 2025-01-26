import http.client
import json
import logging
from typing import List, Dict, Optional

# Set up logging for better debugging
logging.basicConfig(level=logging.DEBUG)

def get_gambling_odds() -> Optional[List[Dict[str, str]]]:
    """
    Fetches gambling odds from the RapidAPI endpoint for soccer events, using the new data format.
    
    Returns:
        List of odds data or None if an error occurs.
    """
    conn = http.client.HTTPSConnection("odds-api1.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "33a834c215msha6e80ead5dea978p1a94d9jsn2668968f7801",
        'x-rapidapi-host': "odds-api1.p.rapidapi.com"
    }

    # Request for soccer event odds
    request_url = "/odds?eventId=id1000001750850429&bookmakers=bet365%2Cpinnacle%2Cdraftkings%2Cbetsson%2Cladbrokes&oddsFormat=decimal&raw=false"
    logging.debug(f"Requesting odds data from: {request_url}")
    conn.request("GET", request_url, headers=headers)

    try:
        res = conn.getresponse()
        data = res.read()

        # Decode the response data
        data = json.loads(data.decode("utf-8"))
        logging.debug(f"Response data received: {data}")

        if isinstance(data, dict):
            odds_list = []

            # Extract necessary information from the nested structure
            event_info = {
                "event_id": data.get("eventId", "N/A"),
                "event_date": data.get("date", "N/A"),
                "event_status": data.get("eventStatus", "N/A"),
            }

            # Extracting market data
            for market_id, market_data in data.get("markets", {}).items():
                market_info = {
                    "market_name": market_data.get("marketName", "N/A"),
                    "market_short_name": market_data.get("marketNameShort", "N/A"),
                    "odds_type": market_data.get("oddsType", "N/A"),
                }

                # Extract outcomes and bookmaker odds
                outcomes = market_data.get("outcomes", {})
                for outcome_id, outcome_data in outcomes.items():
                    odds_info = {
                        "outcome_name": outcome_data.get("outcomeName", "N/A"),
                        "best_price": outcome_data.get("bookmakers", {}).get("bestPrice", {}).get("price", "N/A"),
                    }

                    # Extract bookmaker odds and links
                    for bookmaker, bookmaker_data in outcome_data.get("bookmakers", {}).items():
                        bookmaker_info = {
                            "bookmaker_name": bookmaker,
                            "bookmaker_price": bookmaker_data.get("price", "N/A"),
                            "bookmaker_link": bookmaker_data.get("eventPath", "N/A")
                        }
                        odds_info["bookmaker_details"] = bookmaker_info

                    odds_list.append({**event_info, **market_info, **odds_info})

            logging.debug(f"Extracted {len(odds_list)} odds entries.")
            return odds_list
        else:
            logging.error("Invalid or empty data structure received from the API.")
            return None
    except Exception as e:
        logging.error(f"Error fetching gambling odds: {e}")
        return None
    finally:
        conn.close()

# Testing the function
if __name__ == "__main__":
    odds_data = get_gambling_odds()
    if odds_data:
        for odds in odds_data:
            print(odds)
    else:
        logging.error("No odds data available.")
