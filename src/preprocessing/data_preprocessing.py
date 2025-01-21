import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

def preprocess_data(filepath):
    """
    Preprocesses the input dataset, handles missing values, scales features, and returns the processed data.

    Args:
        filepath (str): The file path to the CSV dataset.

    Returns:
        tuple: Scaled features and the target variable (match_outcome).
    """
    # Load the dataset
    try:
        data = pd.read_csv(filepath)
        logging.debug("Data loaded successfully from %s", filepath)
    except Exception as e:
        logging.error("Error loading data: %s", e)
        raise

    # Check if required columns exist
    required_columns = ['team_strength', 'recent_form', 'odds', 'match_outcome']
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        logging.error(f"Missing required columns: {', '.join(missing_columns)}")
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    # Handle missing values more intelligently
    imputer = SimpleImputer(strategy='mean')  # Mean imputation for numerical columns
    data[['team_strength', 'recent_form', 'odds']] = imputer.fit_transform(data[['team_strength', 'recent_form', 'odds']])
    
    logging.debug("Missing values handled successfully.")

    # Feature engineering: Add ratio between team_strength and odds (optional, but may improve predictions)
    data['team_odds_ratio'] = data['team_strength'] / data['odds']
    logging.debug("Feature engineering applied: Added 'team_odds_ratio'.")

    # Feature scaling: Scale numerical features
    features = data[['team_strength', 'recent_form', 'odds', 'team_odds_ratio']]  # Include the engineered feature
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    logging.debug("Feature scaling applied to numerical columns.")

    # Returning scaled features and the target variable (match_outcome)
    return scaled_features, data['match_outcome']

