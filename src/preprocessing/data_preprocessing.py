import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

def preprocess_data(data):
    """
    Preprocesses the input JSON data, handles missing values, scales features, and returns the processed data.

    Args:
        data (list of dict): The input data in JSON format.

    Returns:
        tuple: Scaled features and the target variable (bet coefficients).
    """
    try:
        logging.debug("Data loaded successfully.")
    except Exception as e:
        logging.error("Error loading data: %s", e)
        raise

    # Convert the JSON data to a DataFrame
    df = pd.DataFrame(data)
    logging.debug("Converted JSON to DataFrame.")

    # Extract necessary columns and handle missing values
    df['team_strength'] = df['bK1_BetCoef']  # Example: Assuming bK1_BetCoef is the team strength
    df['recent_form'] = df['winrate']  # Example: Assuming winrate as recent form
    df['odds'] = df['bK1_BetCoef']  # Assuming the odds are associated with bK1_BetCoef
    df['match_outcome'] = df['winrate']  # For example, use winrate as match outcome
    
    required_columns = ['team_strength', 'recent_form', 'odds', 'match_outcome']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logging.error(f"Missing required columns: {', '.join(missing_columns)}")
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    # Handle missing values more intelligently
    imputer = SimpleImputer(strategy='mean')  # Mean imputation for numerical columns
    df[['team_strength', 'recent_form', 'odds']] = imputer.fit_transform(df[['team_strength', 'recent_form', 'odds']])
    
    logging.debug("Missing values handled successfully.")

    # Feature engineering: Add ratio between team_strength and odds (optional, but may improve predictions)
    df['team_odds_ratio'] = df['team_strength'] / df['odds']
    logging.debug("Feature engineering applied: Added 'team_odds_ratio'.")

    # Feature scaling: Scale numerical features
    features = df[['team_strength', 'recent_form', 'odds', 'team_odds_ratio']]  # Include the engineered feature
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)

    logging.debug("Feature scaling applied to numerical columns.")

    # Returning scaled features and the target variable (match_outcome)
    return scaled_features, df['match_outcome']
