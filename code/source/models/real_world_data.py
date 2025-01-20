import requests
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)

def get_real_world_data(season, api_key, retry_attempts=3, delay=2):
    """
    Fetch real-world match data from a sports API with retries and logging.
    Replace the API endpoint and the headers as per your requirements.

    :param season: The season of the matches to retrieve (e.g., '2025')
    :param api_key: Your API key for authentication
    :param retry_attempts: Number of retry attempts in case of failure
    :param delay: Delay between retry attempts in seconds
    :return: A dictionary with match stats or None if an error occurred
    """

    # Example API URL (replace with your actual API endpoint)
    url = f"https://api.sportsdata.io/v3/soccer/scores/json/GamesBySeason/{season}"

    headers = {
        'Authorization': f'Bearer {api_key}'  # Use the provided API key
    }

    # Retry mechanism for handling transient errors
    for attempt in range(retry_attempts):
        try:
            # Send a GET request to the API
            response = requests.get(url, headers=headers)

            # Check if the response is successful
            if response.status_code == 200:
                data = response.json()
                
                # Validate if the expected data structure is present
                if not data:
                    logging.error("No data found for the requested season.")
                    return None

                match_stats = {}
                for game in data:
                    # Ensure necessary keys exist in the response
                    if 'GameKey' in game and 'HomeTeamScore' in game and 'AwayTeamScore' in game:
                        match_stats[game['GameKey']] = {
                            'team_a': {
                                'goals': game['HomeTeamScore'],
                                'shots': game.get('HomeTeamShots', 0),  # Default to 0 if missing
                                'pass_accuracy': game.get('HomeTeamPassAccuracy', 0)  # Default to 0 if missing
                            },
                            'team_b': {
                                'goals': game['AwayTeamScore'],
                                'shots': game.get('AwayTeamShots', 0),
                                'pass_accuracy': game.get('AwayTeamPassAccuracy', 0)
                            }
                        }
                    else:
                        logging.warning(f"Missing expected keys in game data: {game}")

                logging.info(f"Successfully fetched {len(match_stats)} games for season {season}")
                return match_stats

            else:
                logging.error(f"Error fetching data from API. Status code: {response.status_code}")
                return None

        except requests.exceptions.RequestException as e:
            logging.error(f"An error occurred: {e}")
            if attempt < retry_attempts - 1:
                logging.info(f"Retrying... ({attempt + 1}/{retry_attempts})")
                time.sleep(delay)  # Wait before retrying
            else:
                logging.error(f"All {retry_attempts} attempts failed.")
                return None
