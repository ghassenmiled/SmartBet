from flask import Flask, render_template, request
import uuid
import random
import requests
import logging
import os
import http.client
import json

# Set up logging for verbose debugging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Function to fetch gambling odds from Website 
def get_gambling_odds(website):
    api_key = os.getenv('API_KEY')  
    conn = http.client.HTTPSConnection("bet365-api-inplay.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "bet365-api-inplay.p.rapidapi.com"
    }

    try:
        conn.request("GET", "/bet365/get_betfair_forks", headers=headers)

        res = conn.getresponse()
        data = res.read()

        # Decode and load JSON data
        data = json.loads(data.decode("utf-8"))

        # Check for valid data
        if 'data' in data:
            return data['data']
        else:
            logging.error(f"No odds data found for website: {website}")
            return None

    except Exception as e:
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
