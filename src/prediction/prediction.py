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

    # Validate required columns exist
    required_columns = ['best_price', 'event_id', 'market_name', 'bookmaker_details']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    logging.debug(f"Features available: {df.columns}")
    
    # One-hot encode market_name and outcome_name (if needed, adjust based on your model training)
    df = pd.get_dummies(df, columns=['market_name', 'outcome_name'], drop_first=True)
    
    # Feature scaling (only 'best_price')
    scaler = StandardScaler()
    features = scaler.fit_transform(df[['best_price']])

    # Return the features and target (event_id as a placeholder)
    return features, df['event_id']

def extract_outcome_data(odds):
    """
    Extract the relevant odds and bookmaker data from the new nested structure.

    Args:
        odds (dict): The odds data containing the bookmakers and outcomes.

    Returns:
        list: Processed list of extracted data for predictions.
    """
    processed_data = []

    for event in odds:
        event_data = {
            "event_id": event.get("event_id", "Unknown"),
            "event_date": event.get("event_date", "Unknown"),
            "market_name": event.get("market_name", "Unknown"),
            "outcome_name": event.get("outcome_name", "Unknown"),
            "best_price": event.get("best_price", 0)
        }
        
        # Extract bookmaker details (if available)
        bookmaker = event.get("bookmaker_details", {})
        event_data["bookmaker_name"] = bookmaker.get("bookmaker_name", "Unknown")
        event_data["bookmaker_price"] = bookmaker.get("bookmaker_price", 0)
        event_data["bookmaker_link"] = bookmaker.get("bookmaker_link", "N/A")
        
        processed_data.append(event_data)
    
    return processed_data

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
    model_path = os.path.join(models_dir, f"{model_name}.pkl")
    if not os.path.exists(model_path):
        raise ValueError(f"Model '{model_name}' not found at {model_path}")

    # Extract and preprocess the data
    logging.debug("Extracting and preprocessing odds data.")
    processed_data = extract_outcome_data(odds)

    # Convert to DataFrame for further processing if needed
    processed_df = pd.DataFrame(processed_data)
    
    # Preprocess for prediction (feature scaling)
    features, match_outcomes = preprocess_data(processed_df.to_dict(orient='records'))

    # Load the prediction model
    prediction_model = load_model(model_path)

    # Make predictions (binary classification using `predict_proba`)
    logging.debug("Making predictions.")
    predicted_probabilities = prediction_model.predict_proba(features)[:, 1]

    # Calculate expected value (EV) for each bet
    bet_predictions = []
    for i, probability in enumerate(predicted_probabilities):
        bet_odd = processed_data[i].get("bookmaker_price", 0)
        ev = (probability * bet_odd) - (1 - probability)
        
        # Check if expected value is positive and meets the criteria
        if ev > 0 and bet_odd <= max_odds:
            bet_predictions.append({
                "event_id": processed_data[i].get("event_id", "Unknown"),
                "market_name": processed_data[i].get("market_name", "Unknown"),
                "outcome_name": processed_data[i].get("outcome_name", "Unknown"),
                "bookmaker": processed_data[i].get("bookmaker_name", "Unknown"),
                "bookmaker_link": processed_data[i].get("bookmaker_link", "Unknown"),
                "bet_coef": bet_odd,
                "ev": ev,
                "predicted_probability": probability,
                "expected_profit": ev * bet_odd * desired_profit  # New calculation for expected profit
            })
    
    logging.debug(f"Predicted {len(bet_predictions)} potential bets with positive EV.")

    # Sort bets by expected profit (in descending order)
    bet_predictions.sort(key=lambda x: x['expected_profit'], reverse=True)

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
    return match_data  # As we already know all data will contain the required columns
