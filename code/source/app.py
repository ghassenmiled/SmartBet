from flask import Flask, render_template, request
import uuid  # for generating unique user IDs
import random
import requests  # to fetch odds from the API
import logging

# Set up logging for verbose debugging
logging.basicConfig(level=logging.DEBUG)  # Change to INFO or ERROR in production

app = Flask(__name__)

# Function to fetch soccer match data from TheSportsDB API
def get_sports_data():
    api_key = 'your_api_key'  # Replace with your API key
    url = f'https://www.thesportsdb.com/api/v1/json/{api_key}/eventsnextleague.php?id=4328'  # Example: Premier League data
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure the request was successful
        data = response.json()
        return data['events']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sports data: {e}")
        return None

# Function to fetch gambling odds from a new API (replace with actual URL)
def get_gambling_odds(website):
    api_key = 'your_api_key'  # Replace with your actual API key
    url = f'https://api.gamblingapi.com/v1/odds?apiKey={api_key}&sport=soccer'

    logging.debug(f"Fetching gambling odds from: {url} for website: {website}")

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if request was successful
        data = response.json()

        # Example logic for selecting odds based on gambling site
        if website == 'Site A':
            logging.debug(f"Odds for Site A: {data['data']['Site A']}")
            return data['data']['Site A']  # Modify based on actual response structure
        elif website == 'Site B':
            logging.debug(f"Odds for Site B: {data['data']['Site B']}")
            return data['data']['Site B']

        logging.warning(f"No odds found for website: {website}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching gambling odds: {e}")
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

    logging.debug(f"Received form data: Website={website}, Models={models}, Max Odds={max_odds}, Bet Amount={bet_amount}, Desired Profit={desired_profit}")
    
    # Validate input
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
    
    # Fetch gambling odds from the API
    odds = get_gambling_odds(website)
    if odds is None:
        logging.error(f"Failed to fetch odds for website: {website}")
        return render_template('error.html', message="Failed to fetch odds for the selected website.")
    
    logging.debug(f"Fetched odds: {odds}")

    # Use the odds, user preferences, and models to make a bet prediction
    predicted_outcome = "Win" if random.choice([True, False]) else "Lose"
    
    logging.debug(f"Predicted outcome: {predicted_outcome}")

    # Save the bet data
    user_id = str(uuid.uuid4())  # For demonstration purposes
    save_user_bet(user_id, models, bet_amount, predicted_outcome)

    # Calculate the dynamic odds (example placeholder)
    dynamic_odds = calculate_odds(odds, models)  # Adjust according to your logic
    
    logging.debug(f"Calculated dynamic odds: {dynamic_odds}")

    # Render the result page with the prediction and odds
    return render_template('result.html', prediction=predicted_outcome, odds=dynamic_odds, bet_amount=bet_amount)

# Run the Flask app (only needed if you're running the app locally)
if __name__ == '__main__':
    app.run(debug=True)
