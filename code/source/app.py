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
    # Retrieve form data
    website = request.form.get('website')  # Gambling website
    model = request.form.get('model')  # Chosen model for prediction
    max_odds = float(request.form.get('max_odds', 2.0))  # Default to 2.0 if not provided
    bet_amount = float(request.form.get('bet_amount', 10.0))  # Default to 10 if not provided
    desired_profit = float(request.form.get('desired_profit', 100.0))  # Default to 100 if not provided
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
    
    # Predict betting outcomes based on selected model
    predictions = predict_bet_outcome(real_world_data, model)  # Removed num_models
    
    # Save the user's bet (even though user_id is unique, you can adjust if a persistent session is needed)
    save_user_bet(user_id, website, model, bet_amount, predictions)
    
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
