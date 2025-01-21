from flask import Flask, render_template, request
import os
import logging
from api.odds_api import get_gambling_odds
from src.prediction.prediction import predict_bet, load_model
from src.preprocessing.data_preprocessing import preprocess_data

# Set up logging for verbose debugging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route('/')
def home():
    # Get the list of models in the models directory
    models_dir = os.path.join(os.getcwd(), 'src', 'prediction', 'models')
    models = [f for f in os.listdir(models_dir) if f.endswith('.pkl')]

    # Render the HTML template with the list of models
    return render_template('index.html', models=models)


@app.route('/bet', methods=['POST'])
def bet():
    website = request.form.get('website')
    model = request.form.get('model')
    max_odds = request.form.get('max_odds', type=float)
    desired_profit = request.form.get('desired_profit', type=float)

    logging.debug(f"Received form data: Website={website}, Model={model}, Max Odds={max_odds}, Desired Profit={desired_profit}")

    # Input validation
    if not website:
        logging.error("Website is missing")
        return render_template('error.html', message="Website is required.")

    if not max_odds or max_odds <= 0:
        logging.error("Invalid or missing Max Odds")
        return render_template('error.html', message="Max Odds should be a positive number.")

    if not desired_profit or desired_profit <= 0:
        logging.error("Invalid or missing Desired Profit")
        return render_template('error.html', message="Desired Profit should be a positive number.")

    # Fetch gambling odds from the website
    odds = get_gambling_odds("bet365")
    if odds is None:
        logging.error(f"Failed to fetch odds for website: {website}")
        return render_template('error.html', message="Failed to fetch odds for the selected website.")
    
    # Logging fetched odds for debugging purposes
    logging.debug("Gambling odds fetched successfully!")
    for odd in odds:
        logging.debug(odd)

    # Predict the bet outcome using the predict_bet function
    try:
        bet_prediction, processed_data = predict_bet(odds, model, max_odds, desired_profit)
        logging.debug(f"Bet Prediction: {bet_prediction}")
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return render_template('error.html', message="An error occurred during prediction.")

    # Return the result to the user
    return render_template('result.html', website=website, model=model, max_odds=max_odds, 
                           desired_profit=desired_profit, odds=odds, bet_prediction=bet_prediction)

if __name__ == '__main__':
    app.run(debug=True)
