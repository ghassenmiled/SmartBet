import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler

def load_model(model_path):
    """Load a pre-trained machine learning model."""
    return joblib.load(model_path)

def preprocess_data(odds):
    """
    Preprocesses the gambling odds data before feeding it into the prediction model.
    
    Args:
        odds (list): List of gambling odds data (dictionary format).
        
    Returns:
        tuple: Scaled feature matrix and the target variable (match outcome).
    """
    # Convert odds data to DataFrame for easier manipulation
    df = pd.DataFrame(odds)
    
    # Handle missing values
    df.fillna(0, inplace=True)

    # Feature scaling (example, scale numerical columns)
    scaler = StandardScaler()
    features = scaler.fit_transform(df[['bet_coef1', 'bet_coef2']])
    
    # Return scaled features and match outcomes
    return features, df['event_name']  # Assuming 'event_name' is the target outcome (adjust if necessary)

def predict_bet(odds, model, max_odds, desired_profit):
    """
    Predicts which bets to place based on the provided model and odds.
    
    Args:
        odds (list): List of gambling odds data.
        model (str): The model to use for predictions.
        max_odds (float): The maximum odds allowed for the bet.
        desired_profit (float): The desired profit from the bet.
        
    Returns:
        tuple: (Predictions, Processed Data)
    """
    # Preprocess the data
    processed_data, match_outcomes = preprocess_data(odds)

    # Load the prediction model
    prediction_model = load_model(model)

    # Make predictions based on the model
    predicted_probabilities = prediction_model.predict_proba(processed_data)[:, 1]  # Assuming binary classification

    # Calculate expected value (EV) for each bet
    bet_predictions = []
    for i, probability in enumerate(predicted_probabilities):
        bet_odd = odds[i]['bet_coef1']  # Example, update if needed
        ev = (probability * bet_odd) - (1 - probability)
        
        # Append the bet with the EV calculation
        if ev > 0 and bet_odd <= max_odds:
            bet_predictions.append({
                "event_name": odds[i]["event_name"],
                "bookmaker": odds[i]["bookmaker1"],
                "bet_name": odds[i]["bet_name1"],
                "bet_coef": bet_odd,
                "ev": ev
            })

    return bet_predictions, processed_data

def preprocess_match_data(match_data):
    """Preprocess match data (e.g., scaling, encoding)."""
    # You can add any other preprocessing steps here like feature encoding
    return match_data
