from flask import Flask, render_template, request
import uuid  # for generating unique user IDs

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

@app.route('/')
def home():
    # List of gambling websites
    gambling_sites = ["Site A", "Site B", "Site C"]
    return render_template('index.html', gambling_sites=gambling_sites)

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
        return render_template('error.html', message="Bet Amount must be in euros.")
    
    if max_odds <= 0:
        return render_template('error.html', message="Max Odds must be a value.")
    
    if not (1 <= desired_profit <= 1000):
        return render_template('error.html', message="Desired Profit should be between 1% and 1000%.")

    season = request.form.get('season', '2025')  # Default to 2025 if not provided

    # Generate or retrieve the user ID (UUID for uniqueness)
    user_id = str(uuid.uuid4())
    
    # Fetch real-world data (e.g., match statistics) based on the season
    real_world_data = get_real_world_data(season)
    
    # Ensure real-world data was fetched successfully
    if real_world_data is None:
        return render_template('error.html', message="Failed to fetch real-world data")

    # Get team stats and calculate odds
    team_a_stats = real_world_data['team_a']
    team_b_stats = real_world_data['team_b']
    team_a_odds, team_b_odds = calculate_odds(team_a_stats, team_b_stats)
    
    # Predict betting outcomes based on selected models
    predictions = {}
    for model in models:
        predictions[model] = predict_bet_outcome(real_world_data, model, 1)  # Assuming num_models=1 for simplicity
    
    # Save the user's bet (even though user_id is unique, you can adjust if a persistent session is needed)
    save_user_bet(user_id, website, models, bet_amount, predictions)
    
    # Retrieve user preferences
    user_preferences = get_user_preferences(user_id)
    
    # Return the results to the user
    return render_template(
        'result.html', 
        models=predictions, 
        preferences=user_preferences, 
        website=website, 
        team_a_odds=team_a_odds, 
        team_b_odds=team_b_odds,
        bet_amount=bet_amount,
        desired_profit=desired_profit
    )

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
