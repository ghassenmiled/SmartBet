import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler
import os

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
    
    return joblib.load(model_path)

def preprocess_data(odds):
    """
    Preprocesses the gambling odds data before feeding it into the prediction model.
    
    Args:
        odds (list): List of gambling odds data (dictionary format).
        
    Returns:
        tuple: Scaled feature matrix and the target variable (event_name as a placeholder).
    """
    # Convert odds data to DataFrame for easier manipulation
    df = pd.DataFrame(odds)
    
    # Handle missing values
    df.fillna(0, inplace=True)

    # Feature scaling (example: scale numerical columns)
    scaler = StandardScaler()
    features = scaler.fit_transform(df[['bet_coef1', 'bet_coef2']])
    
    # Assuming 'event_name' is just a placeholder for actual target
    return features, df['event_name']  # Adjust target if necessary

def predict_bet(odds, model_name, max_odds, desired_profit):
    """
    Predicts which bets to place based on the provided model and odds.
    
    Args:
        odds (list): List of gambling odds data.
        model_name (str): The name of the model to use for predictions.
        max_odds (float): The maximum odds allowed for the bet.
        desired_profit (float): The desired profit from the bet.
        
    Returns:
        tuple: (Predictions, Processed Data)
    """
    # Mapping model names to file paths
    model_paths = {
        'logistic_regression': 'models/logistic_regression_model.pkl',
        'random_forest': 'models/random_forest_model.pkl',
        # Add more models as necessary
    }

    # Get the model path based on the model_name
    model_path = model_paths.get(model_name)
    if not model_path:
        raise ValueError(f"Model '{model_name}' not found in the model path mapping.")

    # Preprocess the data
    processed_data, match_outcomes = preprocess_data(odds)

    # Load the prediction model
    prediction_model = load_model(model_path)

    # Make predictions based on the model (assumes binary classification with `predict_proba`)
    predicted_probabilities = prediction_model.predict_proba(processed_data)[:, 1]  # Binary classification

    # Calculate expected value (EV) for each bet
    bet_predictions = []
    for i, probability in enumerate(predicted_probabilities):
        bet_odd = odds[i]['bet_coef1']  # Example, update if needed
        ev = (probability * bet_odd) - (1 - probability)
        
        # Append the bet with the EV calculation if it meets criteria
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
    """
    Preprocess match data (e.g., scaling, encoding).
    
    Args:
        match_data (list): List of match data to preprocess.
        
    Returns:
        list: Preprocessed match data.
    """
    # You can add additional preprocessing steps here if necessary
    # For now, we're just returning the match_data as is
    return match_data
