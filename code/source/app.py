from flask import Flask, render_template, request
import uuid  # for generating unique user IDs
import requests  # to fetch odds from the API

app = Flask(__name__)

# Function to fetch gambling odds from an API (e.g., OddsAPI)
def get_gambling_odds(website):
    api_key = 'your_api_key'  # Replace with your actual API key
    url = f'https://api.oddsapi.io/v1/odds?apiKey={api_key}&sport=soccer'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if request was successful
        data = response.json()
        
        # Example logic for selecting odds based on gambling site
        if website == 'Site A':
            return data['data']['Site A']  # Modify based on actual response structure
        elif website == 'Site B':
            return data['data']['Site B']
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching gambling odds: {e}")
        return None

@app.route('/bet', methods=['POST'])
def bet():
    # Dynamically import modules to avoid circular import issues
    from models.data_preprocessing import get_real_world_data
    from models.betting_model import predict_bet_outcome
    from user_behavior.user_tracking import get_user_preferences, save_user_bet
    from utils.odds_calculator import calculate_odds

    # Retrieve form data
    website = request.form.get('website')  # Gambling website
    models = request.form.getlist('model')  # List of selected models
    max_odds = request.form.get('max_odds', type=float)  # Default to None if not provided
    bet_amount = request.form.get('bet_amount', type=float)  # Default to None if not provided
    desired_profit = request.form.get('desired_profit', type=float)  # Default to None if not provided

    # Validate input
    if not website or not models or not bet_amount or not max_odds or not desired_profit:
        return render_template('error.html', message="All fields are required.")

    if bet_amount <= 0:
        return render_template('error.html', message="Bet Amount must be positive and in euros.")
    
    if max_odds <= 0:
        return render_template('error.html', message="Max Odds must be a positive value.")
    
    if not (1 <= desired_profit <= 1000):
        return render_template('error.html', message="Desired Profit should be between 1% and 1000%.")
