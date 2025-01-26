import pandas as pd
import numpy as np
import logging
import re
import os
import glob
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.neighbors import KNeighborsClassifier

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define constants and file paths
data_dir = '../../data/raw/'
csv_files = glob.glob(os.path.join(data_dir, '*.csv'))
PROCESSED_FILE_PATH = os.path.join(data_dir, 'processed_combined_data.csv')
FINAL_OUTPUT_PATH = os.path.join(data_dir, 'processed_data_final.csv')
REQUIRED_COLUMNS = ["outcomeName"]

def replace_urls_with_nan(val):
    """Helper function to replace URLs with NaN only for string columns."""
    if isinstance(val, str) and bool(re.match(r'http[s]?://', val)):
        return np.nan
    return val

def clean_and_enrich_csv(input_csv_path, output_csv_path):
    """
    Cleans, enriches, and enhances the input CSV data, then exports it as a new CSV file.
    """
    try:
        df = pd.read_csv(input_csv_path)
        logging.info(f"Loaded data with columns: {df.columns.tolist()}")
    except Exception as e:
        logging.error(f"Error loading CSV file: {e}")
        return None

    if 'market_name' in df.columns:
        df['market_name'] = df['market_name'].astype(str).str.strip().str.lower()
    else:
        logging.warning("'market_name' column is missing.")
    if 'market_name' not in df.columns:
        df['market_name'] = 'unknown'  # or some other default value
        logging.warning("'market_name' column was missing and has been filled with 'unknown'.")
    if 'outcome_name' in df.columns:
        df['outcome_name'] = df['outcome_name'].astype(str).str.strip().str.lower()
    if 'outcome_name' not in df.columns:
        df['outcome_name'] = 'unknown'  # or some other default value
        logging.warning("'outcome_name' column was missing and has been filled with 'unknown'.")
    else:
        logging.warning("'outcome_name' column is missing.")


    # Clean Text Columns
    df['market_name'] = df['market_name'].astype(str).str.strip().str.lower() 
    df['outcome_name'] = df['outcome_name'].astype(str).str.strip().str.lower() 

    # Handle missing 'outcome_name' column
    if 'outcome_name' in df.columns:
        df['encoded_outcome'] = LabelEncoder().fit_transform(df['outcome_name'])
        df['outcome_name'].fillna('Unknown', inplace=True)

    # Feature Engineering: Implied Probability, Handicap Sign, and Market Category
    if 'best_price' in df.columns:
        df['implied_probability'] = df['best_price'].apply(lambda x: 1 / x if x > 0 else np.nan)
        df['implied_probability'] = df['implied_probability'].clip(upper=1.0)

    if 'handicap' in df.columns:
        df['handicap_sign'] = df['handicap'].apply(lambda x: 'positive' if x > 0 else 'negative' if x < 0 else 'zero')

    if 'market_name' in df.columns:
        df['market_category'] = df['market_name'].apply(lambda x: categorize_market(x))

    # Clean URLs and One-Hot Encoding
    df = df.applymap(replace_urls_with_nan)

    # Log final data shape
    logging.info(f"Final enhanced data shape: {df.shape}")

    # Export Enhanced Dataset
    try:
        df.to_csv(output_csv_path, index=False)
        logging.info(f"Enhanced CSV saved to {output_csv_path}")
    except Exception as e:
        logging.error(f"Error saving enhanced CSV: {e}")

    return df

def categorize_market(market_name):
    """
    Categorizes market name based on odds type.
    """
    if 'over' in market_name or 'under' in market_name:
        return 'over/under'
    elif 'score' in market_name:
        return 'both teams to score'
    elif 'asian' in market_name or '2way' in market_name:
        return '2way/asian handicap'
    elif '3way' in market_name or 'european' in market_name:
        return '3way/european handicap'
    else:
        return 'other'

def model_evaluation_metrics(y_true, y_pred):
    """
    Evaluate the model using multiple metrics.
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

def preprocess_data(csv_files):
    """
    Load and combine multiple CSV files into one dataframe and preprocess.
    """
    # Load CSVs and combine
    data_frames = [pd.read_csv(file) for file in csv_files]
    combined_df = pd.concat(data_frames, ignore_index=True)

    # Apply URL cleaning and handle missing values
    combined_df = combined_df.apply(lambda x: x.apply(replace_urls_with_nan) if x.dtype == 'object' else x)


    # Ensure consistency for text columns
    for col in ['market_name', 'outcome_name']:
        if col in combined_df.columns:
            combined_df[col] = combined_df[col].astype(str).str.strip().str.lower()

    # Handle missing 'best_price' column
    if 'best_price' in combined_df.columns:
        combined_df['best_price'].fillna(0, inplace=True)
    else:
        logging.warning("'best_price' column is missing, skipping filling missing values.")

    # Handle missing 'odds_type' column
    if 'odds_type' in combined_df.columns:
        combined_df['odds_type'].fillna('Unknown', inplace=True)
    else:
        logging.warning("'odds_type' column is missing, skipping filling missing values.")

    return combined_df

def save_processed_data(df):
    """Saves the processed data to a CSV file."""
    df.to_csv(PROCESSED_FILE_PATH, index=False)
    logging.info(f"Processed data saved to {PROCESSED_FILE_PATH}")

if __name__ == "__main__":
    # Preprocess and clean the data
    combined_df = preprocess_data(csv_files)

    # Save preprocessed data
    save_processed_data(combined_df)

    # Enrich the data and save final output
    enriched_df = clean_and_enrich_csv(PROCESSED_FILE_PATH, FINAL_OUTPUT_PATH)

    # Prepare for modeling if the data is enriched
    if enriched_df is not None:
        if 'encoded_outcome' in enriched_df.columns:
            X = enriched_df.drop(['encoded_outcome'], axis=1)
            y = enriched_df['encoded_outcome']
        else:
            logging.warning("No 'encoded_outcome' column found, cannot proceed with model training.")
    else:
        logging.error("The data frame could not be processed correctly. Exiting the script.")
