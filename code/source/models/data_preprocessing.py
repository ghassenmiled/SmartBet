import pandas as pd
from sklearn.preprocessing import StandardScaler
import logging

logging.basicConfig(level=logging.INFO)

def get_real_world_data(file_path, file_type='csv', fill_missing=False, missing_value_strategy='mean'):
    """
    Retrieve and preprocess real-world betting data.
    This method is used to load and preprocess the data for predictions.

    :param file_path: Path to the data file (CSV or Excel)
    :param file_type: Type of the file ('csv', 'excel', etc.)
    :param fill_missing: Whether to fill missing values or drop them
    :param missing_value_strategy: Strategy to fill missing values ('mean', 'median', 'mode', 'zero')
    :return: Processed DataFrame
    """
    df = preprocess_data(file_path, file_type, fill_missing, missing_value_strategy)
    return df

def preprocess_data(file_path, file_type='csv', fill_missing=False, missing_value_strategy='mean'):
    """
    Preprocess the betting data.
    - Handles missing values
    - Normalizes numerical columns
    - One-hot encodes categorical columns

    :param file_path: Path to the data file (CSV or others)
    :param file_type: Type of the file ('csv', 'excel', etc.)
    :param fill_missing: Whether to fill missing values or drop them
    :param missing_value_strategy: Strategy to fill missing values ('mean', 'median', 'mode', 'zero')
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

    logging.info(f"Loaded {len(df)} rows and {df.shape[1]} columns from {file_path}")

    # Step 2: Handle missing values
    if fill_missing:
        if missing_value_strategy == 'mean':
            # Fill missing numerical values with mean
            for column in df.select_dtypes(include=['float64', 'int64']).columns:
                df[column] = df[column].fillna(df[column].mean())
            logging.info("Missing numerical values filled with mean")

        elif missing_value_strategy == 'median':
            # Fill missing numerical values with median
            for column in df.select_dtypes(include=['float64', 'int64']).columns:
                df[column] = df[column].fillna(df[column].median())
            logging.info("Missing numerical values filled with median")

        elif missing_value_strategy == 'mode':
            # Fill missing categorical values with mode
            for column in df.select_dtypes(include=['object']).columns:
                df[column] = df[column].fillna(df[column].mode()[0])
            logging.info("Missing categorical values filled with mode")

        elif missing_value_strategy == 'zero':
            # Fill all missing values with zero
            df = df.fillna(0)
            logging.info("Missing values filled with zero")
        else:
            raise ValueError("Unsupported missing value strategy. Please use 'mean', 'median', 'mode', or 'zero'.")

    else:
        df = df.dropna()  # Drop rows with missing values
        logging.info("Dropped rows with missing values")

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

    logging.info(f"Preprocessing completed. Final shape: {df.shape}")
    return df
