import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler
import os
import logging

# Set up logging for better debugging
logging.basicConfig(level=logging.DEBUG)

def load_model(model_path):
    """
    Loads a pre-trained machine learning model.
    
    Args:
        model_path (str): Path to the saved model file.
        
    Returns:
        model: The loaded model.
    """
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    
    logging.debug(f"Loading model from {model_path}")
    return joblib.load(model_path)

def preprocess_data(odds):
    """
    Preprocesses the gambling odds data before feeding it into the prediction model.
    
    Args:
        odds (list of dict): List of gambling odds data in dictionary format.
        
    Returns:
        tuple: Scaled feature matrix and the target variable (event_name as a placeholder).
    """
    if not isinstance(odds, list) or not all(isinstance(item, dict) for item in odds):
        raise ValueError("Odds must be a list of dictionaries.")
    
    logging.debug("Converting odds data to DataFrame for preprocessing.")
    
    # Convert odds data to DataFrame for easier manipulation
    df = pd.DataFrame(odds)
    
    # Handle missing values
    df.fillna(0, inplace=True)

    # Validate required columns exist (you may want to add more columns depending on your training data)
    required_columns = ['bet_coef1', 'bet_coef2', 'event_name', 'bookmaker1', 'bet_name1', 'bookmaker2', 'bet_name2']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    logging.debug(f"Features available: {df.columns}")
    
    # One-hot encode categorical features (if needed, adjust based on your model training)
    df = pd.get_dummies(df, columns=['bookmaker1', 'bet_name1', 'bookmaker2', 'bet_name2'], drop_first=True)
    
    # Feature scaling (only 'bet_coef1' and 'bet_coef2')
    scaler = StandardScaler()
    features = scaler.fit_transform(df[['bet_coef1', 'bet_coef2']])

    # Return the features and target (event_name as a placeholder)
    return features, df['event_name']

def predict_bet(odds, model_name, max_odds, desired_profit):
    """
    Predicts which bets to place based on the provided model and odds.
    
    Args:
        odds (list of dict): List of gambling odds data.
        model_name (str): The name of the model to use for predictions.
        max_odds (float): The maximum odds allowed for the bet.
        desired_profit (float): The desired profit from the bet.
        
    Returns:
        tuple: (Predictions, Processed Data)
    """
    # Dynamically build model path
    models_dir = os.path.join(os.getcwd(), 'src', 'prediction', 'models')
    model_path = os.path.join(models_dir, f"{model_name}")
    if not os.path.exists(model_path):
        raise ValueError(f"Model '{model_name}' not found at {model_path}")

    # Preprocess the data
    logging.debug("Preprocessing odds data.")
    processed_data, match_outcomes = preprocess_data(odds)

    # Load the prediction model
    prediction_model = load_model(model_path)

    # Make predictions (binary classification using `predict_proba`)
    logging.debug("Making predictions.")
    predicted_probabilities = prediction_model.predict_proba(processed_data)[:, 1]

    # Calculate expected value (EV) for each bet
    bet_predictions = []
    for i, probability in enumerate(predicted_probabilities):
        bet_odd = odds[i].get('bet_coef1', 0)
        ev = (probability * bet_odd) - (1 - probability)
        
        # Append the bet if EV is positive and odds meet criteria
        if ev > 0 and bet_odd <= max_odds:
            bet_predictions.append({
                "event_name": odds[i].get("event_name", "Unknown"),
                "bookmaker": odds[i].get("bookmaker1", "Unknown"),
                "bet_name": odds[i].get("bet_name1", "Unknown"),
                "bet_coef": bet_odd,
                "ev": ev
            })
    
    logging.debug(f"Predicted {len(bet_predictions)} potential bets with positive EV.")

    return bet_predictions, processed_data

def preprocess_match_data(match_data):
    """
    Preprocess match data (e.g., scaling, encoding).
    
    Args:
        match_data (list): List of match data to preprocess.
        
    Returns:
        list: Preprocessed match data.
    """
    if not isinstance(match_data, list):
        raise ValueError("Match data must be a list.")
    
    # Additional preprocessing steps can be added here if necessary
    return match_data
