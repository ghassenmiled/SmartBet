from flask import Flask, render_template, request
import uuid
import random
import requests
import logging
import os

# Set up logging for verbose debugging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Function to fetch sports data from Sports Game Odds API
def get_sports_data():
    api_key = os.getenv('SPORTS_API_KEY')
    url = f'https://api.sportsgameodds.com/v1/odds?apiKey={api_key}&sport=nfl'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data['odds']
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching sports data: {e}")
        return None

# Function to fetch gambling odds from a new API
def get_gambling_odds(website):
    api_key = os.getenv('GAMBLING_API_KEY')
    url = 'https://api.sportsgamesodds.com/v1/odds?oddsAvailable=true'
    headers = { 'X-Api-Key': api_key }
    
    logging.debug(f"Fetching gambling odds from: {url} for website: {website}")

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Log the full response for debugging
        logging.debug(f"Response from API: {response.text}")

        # Check if the expected odds data exists in the response
        data = response.json()
        if 'data' not in data or not data['data']:
            logging.error(f"No odds data found in the response for website: {website}")
            return None

        # Check if the website's odds are available in the response
        if website == 'Site A' and 'Site A' in data['data']:
            logging.debug(f"Odds for Site A: {data['data']['Site A']}")
            return data['data']['Site A']
        elif website == 'Site B' and 'Site B' in data['data']:
            logging.debug(f"Odds for Site B: {data['data']['Site B']}")
            return data['data']['Site B']

        logging.warning(f"No odds found for website: {website}")
        return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching gambling odds: {e}")
        return None

@app.route('/')
def index():
    gambling_sites = ['Sportsbook1', 'Sportsbook2', 'Sportsbook3']  # List of gambling sites
    return render_template('index.html', gambling_sites=gambling_sites)

@app.route('/bet', methods=['POST'])
def bet():
    from models.data_preprocessing import get_real_world_data
    from models.betting_model import predict_bet_outcome
    from user_behavior.user_tracking import get_user_preferences, save_user_bet
    from utils.odds_calculator import calculate_odds

    website = request.form.get('website')
    models = request.form.getlist('model')
    max_odds = request.form.get('max_odds', type=float)
    bet_amount = request.form.get('bet_amount', type=float)
    desired_profit = request.form.get('desired_profit', type=float)

    logging.debug(f"Received form data: Website={website}, Models={models}, Max Odds={max_odds}, Bet Amount={bet_amount}, Desired Profit={desired_profit}")
    
    if not website or not models or not bet_amount or not max_odds or not desired_profit:
        logging.error("One or more required fields are missing")
        return render_template('error.html', message="All fields are required.")

    if bet_amount <= 0:
        logging.error("Invalid bet amount")
        return render_template('error.html', message="Bet Amount must be positive and in euros.")
    
    if max_odds <= 0:
        logging.error("Invalid max odds value")
        return render_template('error.html', message="Max Odds must be a positive value.")
    
    if not (1 <= desired_profit <= 1000):
        logging.error("Invalid desired profit value")
        return render_template('error.html', message="Desired Profit should be between 1% and 1000%.")
    
    odds = get_gambling_odds(website)
    if odds is None:
        logging.error(f"Failed to fetch odds for website: {website}")
        return render_template('error.html', message="Failed to fetch odds for the selected website.")
    
    logging.debug(f"Fetched odds: {odds}")

    predicted_outcome = "Win" if random.choice([True, False]) else "Lose"
    logging.debug(f"Predicted outcome: {predicted_outcome}")

    user_id = str(uuid.uuid4())
    save_user_bet(user_id, models, bet_amount, predicted_outcome)

    dynamic_odds = calculate_odds(odds, models)
    logging.debug(f"Calculated dynamic odds: {dynamic_odds}")

    return render_template('result.html', prediction=predicted_outcome, odds=dynamic_odds, bet_amount=bet_amount)

if __name__ == '__main__':
    app.run(debug=True)
