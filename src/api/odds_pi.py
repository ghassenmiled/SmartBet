def get_gambling_odds(website):
    """
    Fetch gambling odds from the Bet365 API or other websites based on the 'website' parameter.

    Args:
        website (str): The website name for which to fetch odds.

    Returns:
        list: A list of dictionaries containing odds information, or None if an error occurs.
    """
    # You could modify this logic to handle different websites based on the `website` argument.
    # For now, this example keeps using the Bet365 API for demonstration purposes.
    api_key = os.getenv('API_KEY')
    if not api_key:
        logging.error("API key is missing. Please set the 'API_KEY' environment variable.")
        return None

    # Configure the HTTPS connection
    conn = http.client.HTTPSConnection("bet365-api-inplay.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "bet365-api-inplay.p.rapidapi.com"
    }

    try:
        # Make the API request (you can customize this based on the `website`)
        conn.request("GET", "/bet365/get_betfair_forks", headers=headers)
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
    except Exception as e:
        logging.error(f"Error fetching gambling odds: {e}")
        return None
    finally:
        conn.close()
