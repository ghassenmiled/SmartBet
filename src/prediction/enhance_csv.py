import pandas as pd
import numpy as np
import logging
import re
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, LeaveOneOut
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import GridSearchCV
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Required columns
REQUIRED_COLUMNS = ['market_name', 'outcome_name', 'encoded_outcome']

def add_missing_columns(df):
    """Add missing columns to the dataframe with default values."""
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            logging.warning(f"'{col}' column is missing. Adding it with default value.")
            if col == 'encoded_outcome':
                df[col] = 0  # Default value for encoded_outcome
            else:
                df[col] = 'Unknown'  # Default value for market_name and outcome_name
    return df

def clean_and_enrich_csv(input_csv_path, output_csv_path):
    """
    Cleans, enriches, and enhances the input CSV data, then exports it as a new CSV file.

    Args:
        input_csv_path (str): Path to the input CSV file.
        output_csv_path (str): Path to save the enhanced CSV file.

    Returns:
        pd.DataFrame: The enhanced DataFrame.
    """
    # Load the CSV file
    try:
        df = pd.read_csv(input_csv_path)
        logging.info(f"Loaded data with columns: {df.columns.tolist()}")
    except Exception as e:
        logging.error(f"Error loading CSV file: {e}")
        return None

    # 1. Clean Text Columns
    if 'market_name' in df.columns:
        df['market_name'] = df['market_name'].str.strip().str.lower()

    if 'outcome_name' in df.columns:
        df['outcome_name'] = df['outcome_name'].str.strip().str.lower()

    if 'outcome_name' in df.columns:
        # Fill missing values for the target column
        df['encoded_outcome'] = LabelEncoder().fit_transform(df['outcome_name']) 
        df['outcome_name'].fillna('Unknown', inplace=True)

    # 2. Handle Missing Values
    essential_columns = ['best_price', 'handicap', 'odds_type']
    for col in essential_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col] = df[col].fillna(df[col].mean())
        else:
            logging.warning(f"'{col}' is missing. Adding it with default value 0.")
            df[col] = 0

    # 3. Feature Engineering

    # Implied Probability
    if 'best_price' in df.columns:
        df['implied_probability'] = df['best_price'].apply(lambda x: 1 / x if x > 0 else np.nan)
        df['implied_probability'] = df['implied_probability'].clip(upper=1.0)

    else:
        logging.warning("'best_price' column is missing, skipping implied probability calculation.")

    # Handicap Sign Indicator
    if 'handicap' in df.columns:
        df['handicap_sign'] = df['handicap'].apply(lambda x: 'positive' if x > 0 else 'negative' if x < 0 else 'zero')

    # Market Grouping
    if 'market_name' in df.columns:
        df['market_category'] = df['market_name'].apply(
            lambda x: 'totals' if 'over' in x or 'under' in x else 'both teams to score' if 'score' in x else 'other'
        )

    # Odds Spread (if there are multiple odds per outcome)
    if 'market_id' in df.columns and 'best_price' in df.columns:
        df['odds_spread'] = df.groupby('market_id')['best_price'].transform(lambda x: x.max() - x.min())

    # Profit Margin
    if 'implied_probability' in df.columns:
        df['profit_margin'] = 1 - df['implied_probability']

    # 4. Remove URLs or invalid entries
    def replace_urls_with_nan(val):
        if isinstance(val, str) and bool(re.match(r'http[s]?://', val)):
            return np.nan
        return val

    df = df.applymap(replace_urls_with_nan)

    # 5. One-Hot Encoding for Categorical Features
    if 'market_name' in df.columns:
        df = pd.get_dummies(df, columns=['market_name'], drop_first=True)

    # 6. Add Missing Columns Before Saving
    df = add_missing_columns(df)

    # Log final data shape
    logging.info(f"Final enhanced data shape: {df.shape}")

    # 7. Export Enhanced Dataset
    try:
        df.to_csv(output_csv_path, index=False)
        logging.info(f"Enhanced CSV saved to {output_csv_path}")
    except Exception as e:
        logging.error(f"Error saving enhanced CSV: {e}")

    return df


def model_evaluation_metrics(y_true, y_pred):
    """
    Evaluate the model using multiple metrics.

    Args:
        y_true (array): True labels.
        y_pred (array): Predicted labels.

    Returns:
        dict: Dictionary with various evaluation metrics.
    """
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, average='weighted'),
        "recall": recall_score(y_true, y_pred, average='weighted'),
        "f1_score": f1_score(y_true, y_pred, average='weighted')
    }
    return metrics


def hyperparameter_tuning(model, X_train, y_train):
    """
    Perform hyperparameter tuning using GridSearchCV.

    Args:
        model (sklearn model): The model to tune.
        X_train (pd.DataFrame): The training features.
        y_train (pd.Series): The training labels.

    Returns:
        sklearn model: The best tuned model.
    """
    param_grid = {
        'n_neighbors': [3, 5, 7, 9],
        'weights': ['uniform', 'distance'],
        'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute']
    }

    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=2, scoring='accuracy')
    grid_search.fit(X_train, y_train)

    logging.info(f"Best Hyperparameters: {grid_search.best_params_}")
    return grid_search.best_estimator_


# Load and combine CSV files
csv_files = [f for f in os.listdir('../../data/raw/') if f.endswith('.csv')]

# Initialize an empty list to store DataFrames
data_frames = []

# Loop through each CSV file and read it
for file in csv_files:
    file_path = os.path.join('../../data/raw/', file)
    df = pd.read_csv(file_path)
    data_frames.append(df)

# Concatenate all the DataFrames into one
combined_df = pd.concat(data_frames, ignore_index=True)

# Apply URL cleaning and handle missing values
combined_df = combined_df.applymap(replace_urls_with_nan)
combined_df['best_price'].fillna(0, inplace=True)
combined_df['handicap'].fillna(0, inplace=True)
combined_df['odds_type'].fillna(0, inplace=True)

# Add missing columns if needed
if 'market_name' not in combined_df.columns:
    combined_df['market_name'] = ''
if 'outcome_name' not in combined_df.columns:
    combined_df['outcome_name'] = ''

# Save the preprocessed data
combined_df.to_csv('../../data/processed_combined_data.csv', index=False)

# Log final shape
logging.info(f"Processed data shape: {combined_df.shape}")

# Example Usage
if __name__ == "__main__":
    output_csv = "../../data/processed_data.csv"

    # Run the cleaning and enrichment process
    df_enriched = clean_and_enrich_csv(input_csv, output_csv)

    # Check if 'encoded_outcome' exists before dropping it
    if 'encoded_outcome' in df_enriched.columns:
        X = df_enriched.drop(columns=['encoded_outcome'])
        y = df_enriched['encoded_outcome']
    else:
        logging.warning("'encoded_outcome' column not found, skipping drop.")
        X = df_enriched.copy()  # If not found, just use the dataframe as is
        y = None  # In this case, y would be None, handle accordingly in the model training process.

    if df_enriched is not None and len(df_enriched) > 1:
        if y is not None:
            # Perform train-test split if there is sufficient data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        else:
            logging.warning("Insufficient data for target column 'encoded_outcome'. Skipping model training.")
            X_train, X_test, y_train, y_test = X, X, y, y  # Skip splitting if there's no target column or insufficient data
    else:
        logging.warning("Insufficient data for train-test split.")
        # If only one sample exists, skip splitting and skip tuning
        X_train, X_test, y_train, y_test = X, X, y, y  # Use the full dataset directly

    # Only proceed with training if there is more than 1 sample
    if len(X_train) > 1:
        # Example model (e.g., KNeighborsClassifier)
        model = KNeighborsClassifier()

        # Hyperparameter tuning
        best_model = hyperparameter_tuning(model, X_train, y_train)

        # Evaluate the best model
        y_pred = best_model.predict(X_test)
        metrics = model_evaluation_metrics(y_test, y_pred)

        logging.info(f"Model Evaluation Metrics: {metrics}")
    else:
        logging.warning("Not enough data for model training and evaluation. Skipping.")
