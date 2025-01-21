import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
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
    # We use SimpleImputer to fill in missing values for numerical columns
    imputer = SimpleImputer(strategy='mean')  # Mean imputation for numerical columns
    data[['team_strength', 'recent_form', 'odds']] = imputer.fit_transform(data[['team_strength', 'recent_form', 'odds']])
    
    logging.debug("Missing values handled successfully.")

    # Feature scaling: Scale numerical features
    scaler = StandardScaler()
    features = scaler.fit_transform(data[['team_strength', 'recent_form', 'odds']])
    
    logging.debug("Feature scaling applied to numerical columns.")

    # Feature Engineering: Add ratio between team_strength and odds (optional, but may improve predictions)
    data['team_odds_ratio'] = data['team_strength'] / data['odds']
    features = pd.DataFrame(features, columns=['team_strength', 'recent_form', 'odds'])
    features['team_odds_ratio'] = data['team_odds_ratio']
    logging.debug("Feature engineering applied: Added 'team_odds_ratio'.")

    # Optionally handle categorical features (for example: if you want to encode 'team' or 'location' columns)
    # You can use OneHotEncoder if needed in the future. For now, we're assuming no categorical features in this dataset.

    # Returning features and the target variable (match_outcome)
    return features, data['match_outcome']
