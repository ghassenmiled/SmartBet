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

    # Extract necessary columns from nested structures
    df['team_strength'] = df['markets'].apply(lambda x: x.get('101', {}).get('outcomes', {}).get('101', {}).get('bookmakers', {}).get('bestPrice', {}).get('price', None))  # Example: Assuming 101 is the desired market
    df['recent_form'] = df['markets'].apply(lambda x: x.get('104', {}).get('outcomes', {}).get('104', {}).get('bookmakers', {}).get('bestPrice', {}).get('price', None))  # Another market as example
    df['odds'] = df['markets'].apply(lambda x: x.get('101', {}).get('outcomes', {}).get('101', {}).get('bookmakers', {}).get('bestPrice', {}).get('price', None))  # Assuming '101' is used for odds
    df['match_outcome'] = df['markets'].apply(lambda x: x.get('101', {}).get('outcomes', {}).get('101', {}).get('outcomeName', None))  # Outcome name (1, X, 2)

    # Handle missing values
    required_columns = ['team_strength', 'recent_form', 'odds']
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
    return scaled_features, df['match_outcome'], df  # Returning the full DataFrame for better traceability
