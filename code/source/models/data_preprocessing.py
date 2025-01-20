import pandas as pd
from sklearn.preprocessing import StandardScaler
import logging

logging.basicConfig(level=logging.INFO)

def preprocess_data(file_path, file_type='csv', fill_missing=False):
    """
    Preprocess the betting data.
    - Handles missing values
    - Normalizes numerical columns
    - One-hot encodes categorical columns

    :param file_path: Path to the data file (CSV or others)
    :param file_type: Type of the file ('csv', 'excel', etc.)
    :param fill_missing: Whether to fill missing values or drop them
    :return: Processed DataFrame
    """

    # Step 1: Load the data file
    try:
        if file_type == 'csv':
            df = pd.read_csv(file_path)
        elif file_type == 'excel':
            df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file type. Please use 'csv' or 'excel'.")
    except Exception as e:
        logging.error(f"Error loading file {file_path}: {e}")
        raise

    logging.info(f"Loaded {len(df)} rows from {file_path}")

    # Step 2: Handle missing values
    if fill_missing:
        # Fill missing numerical values with mean and categorical with 'missing'
        for column in df.select_dtypes(include=['object']).columns:
            df[column] = df[column].fillna('missing')
        
        for column in df.select_dtypes(include=['float64', 'int64']).columns:
            df[column] = df[column].fillna(df[column].mean())
        
        logging.info("Missing values filled")
    else:
        df = df.dropna()  # Drop rows with missing values
        logging.info("Missing values dropped")

    # Step 3: Normalize numerical columns (e.g., betting odds, bet amounts)
    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
    if numerical_cols.size > 0:
        scaler = StandardScaler()
        df[numerical_cols] = scaler.fit_transform(df[numerical_cols])  # Normalize numeric data
        logging.info(f"Normalized numerical columns: {', '.join(numerical_cols)}")
    else:
        logging.info("No numerical columns to normalize.")

    # Step 4: Encode categorical columns if any (e.g., team names, betting markets)
    categorical_cols = df.select_dtypes(include=['object']).columns
    if categorical_cols.size > 0:
        df = pd.get_dummies(df, columns=categorical_cols, drop_first=True)  # One-hot encode categorical columns
        logging.info(f"One-hot encoded categorical columns: {', '.join(categorical_cols)}")
    else:
        logging.info("No categorical columns to encode.")

    logging.info("Preprocessing completed")
    return df
