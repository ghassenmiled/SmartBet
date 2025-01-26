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
import glob

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

def replace_urls_with_nan(val):
    """Helper function to replace URLs with NaN only for string columns."""
    if isinstance(val, str) and bool(re.match(r'http[s]?://', val)):
        return np.nan
    return val

def clean_and_enrich_csv(input_csv_path, output_csv_path):
    """
    Cleans, enriches, and enhances the input CSV data, then exports it as a new CSV file.
    """
    # Load the CSV file
    try:
        df = pd.read_csv(input_csv_path)
        logging.info(f"Loaded data with columns: {df.columns.tolist()}")
    except Exception as e:
        logging.error(f"Error loading CSV file: {e}")
        return None

    # Clean Text Columns
    if 'market_name' in df.columns:
        df['market_name'] = df['market_name'].astype(str).str.strip().str.lower()

    if 'outcome_name' in df.columns:
        df['outcome_name'] = df['outcome_name'].astype(str).str.strip().str.lower()

    # Handle missing 'encoded_outcome' and other essential columns
    if 'outcome_name' in df.columns:
        df['encoded_outcome'] = LabelEncoder().fit_transform(df['outcome_name'])
        df['outcome_name'].fillna('Unknown', inplace=True)

    essential_columns = ['best_price', 'handicap', 'odds_type']
    for col in essential_columns:
        if col not in df.columns:
            logging.warning(f"'{col}' is missing. Adding it with default value 0.")
            df[col] = 0
        else:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df[col].fillna(df[col].mean(), inplace=True)

    # Feature Engineering: Implied Probability, Handicap Sign, and Market Category
    if 'best_price' in df.columns:
        df['implied_probability'] = df['best_price'].apply(lambda x: 1 / x if x > 0 else np.nan)
        df['implied_probability'] = df['implied_probability'].clip(upper=1.0)

    if 'handicap' in df.columns:
        df['handicap_sign'] = df['handicap'].apply(lambda x: 'positive' if x > 0 else 'negative' if x < 0 else 'zero')

    if 'market_name' in df.columns:
        df['market_category'] = df['market_name'].apply(
            lambda x: 'totals' if 'over' in x or 'under' in x else 'both teams to score' if 'score' in x else 'other'
        )

    # Clean URLs and One-Hot Encoding
    df = df.applymap(replace_urls_with_nan)

    if 'market_name' in df.columns:
        df = pd.get_dummies(df, columns=['market_name'], drop_first=True)

    # Add missing columns before saving
    df = add_missing_columns(df)

    # Log final data shape
    logging.info(f"Final enhanced data shape: {df.shape}")

    # Export Enhanced Dataset
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


###########################


# Load and combine CSV files
data_dir = '../../data/raw/'
csv_files = glob.glob(os.path.join(data_dir, '*.csv'))

# Initialize an empty list to store DataFrames
data_frames = [pd.read_csv(file) for file in csv_files]

# Concatenate all the DataFrames into one
combined_df = pd.concat(data_frames, ignore_index=True)

# Apply URL cleaning and handle missing values
combined_df = combined_df.apply(lambda x: x.apply(replace_urls_with_nan) if x.dtype == 'object' else x)

# Ensure 'market_name' and 'outcome_name' are treated as strings before applying .str methods
for col in ['market_name', 'outcome_name']:
    if col in combined_df.columns:
        combined_df[col] = combined_df[col].astype(str).str.strip().str.lower()

# Check for the 'best_price' column and handle it accordingly
if 'best_price' in combined_df.columns:
    combined_df['best_price'].fillna(0, inplace=True)
else:
    logging.warning("'best_price' column is missing, skipping filling missing values.")

# Check for the 'handicap' column and fill missing values if it exists
if 'handicap' in combined_df.columns:
    combined_df['handicap'].fillna(0, inplace=True)
else:
    logging.warning("'handicap' column is missing, skipping filling missing values.")

# Check for the 'odds_type' column and fill missing values if it exists
if 'odds_type' in combined_df.columns:
    combined_df['odds_type'].fillna(0, inplace=True)
else:
    logging.warning("'odds_type' column is missing, skipping filling missing values.")

# Add missing columns if needed
if 'market_name' not in combined_df.columns:
    combined_df['market_name'] = ''
if 'outcome_name' not in combined_df.columns:
    combined_df['outcome_name'] = ''

# Handle 'price' column cleaning (if it exists, replace commas or unwanted characters)
if 'price' in combined_df.columns:
    combined_df['price'] = combined_df['price'].astype(str).str.replace(',', '').astype(float)

# Save the preprocessed data
processed_file_path = os.path.join('../../data/raw/', 'processed_combined_data.csv')
combined_df.to_csv(processed_file_path, index=False)

# Log final shape
logging.info(f"Processed data shape: {combined_df.shape}")

####################################

if __name__ == "__main__":
    input_csv = processed_file_path  # Now points to the new processed file
    output_csv = os.path.join('../../data/raw/', 'processed_data_final.csv')  # Save the final processed file in the same folder

    # Run the cleaning and enrichment process
    df_enriched = clean_and_enrich_csv(input_csv, output_csv)

    # Check if 'encoded_outcome' exists before dropping it
    if 'encoded_outcome' in df_enriched.columns:
        X = df_enriched.drop(['encoded_outcome'], axis=1)
        y = df_enriched['encoded_outcome']
    else:
        logging.warning("No 'encoded_outcome' column found, cannot proceed with model training.")
