import os
import logging
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import cross_val_score

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define model paths
MODEL_PATHS = {
    'logistic_regression': 'models/logistic_regression_model.pkl',
    'random_forest': 'models/random_forest_model.pkl',
    'voting_classifier': 'models/voting_classifier_model.pkl',
    'gradient_boosting': 'models/gradient_boosting_model.pkl',
}

def preprocess_data(csv_file_path, add_target=False):
    """
    Preprocess the input CSV file for training.
    - Handles missing values.
    - Adds calculated fields.
    - Encodes categorical variables.
    - Scales numeric features.
    
    Parameters:
        csv_file_path (str): Path to the input CSV file.
        add_target (bool): If True, separates features and target for supervised learning.
    
    Returns:
        If add_target=True:
            X_train_scaled, X_test_scaled, y_train_encoded, y_test_encoded
        If add_target=False:
            features (DataFrame)
    """
    # Load data
    df = pd.read_csv(csv_file_path)
    logging.info(f"Loaded data with shape: {df.shape} and columns: {df.columns.tolist()}")

    # Handle missing values
    # Fill missing values in specific columns
    if 'market_name' in df.columns:
        df['market_name'].fillna('Unknown', inplace=True)
    else:
        logging.warning("'market_name' column is missing in the dataset.")

    if 'outcome_name' in df.columns:
        df['outcome_name'].fillna('Unknown', inplace=True)
    else:
        logging.warning("'outcome_name' column is missing in the dataset.")
    
    # Replace URLs with 'NaN'
    df.replace(to_replace=r'http[s]?://\S+', value='NaN', regex=True, inplace=True)

    # Add calculated fields
    if 'best_price' in df.columns:
        df['implied_probability'] = 1 / df['best_price']
        df['adjusted_odds'] = df['best_price'] * (1 - df['implied_probability'])
    else:
        logging.warning("'best_price' column is missing. Skipping calculated fields.")

    # One-hot encode categorical columns
    categorical_columns = ['market_name', 'odds_type']
    available_categorical_columns = [col for col in categorical_columns if col in df.columns]
    if available_categorical_columns:
        df = pd.get_dummies(df, columns=available_categorical_columns, drop_first=True)
    else:
        logging.warning("No categorical columns found for encoding.")

    # Separate features and target
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    if add_target:
        if 'outcome_name' in df.columns:
            target = df['outcome_name']
            numeric_columns = [col for col in numeric_columns if col != 'outcome_name']
        else:
            logging.error("'outcome_name' column is missing. Cannot separate features and target.")
            return None
        
        # Ensure encoded_outcome is present or create it
        if 'encoded_outcome' not in df.columns:
            logging.info("Creating 'encoded_outcome' from 'outcome_name' column.")
            encoder = LabelEncoder()
            df['encoded_outcome'] = encoder.fit_transform(df['outcome_name'])
        
        target = df['encoded_outcome']
        numeric_columns.remove('encoded_outcome')  # Exclude target from features

    features = df[numeric_columns]

    # Split and scale data if add_target is True
    if add_target:
        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
        
        # Scale numeric features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Encode target variable
        encoder = LabelEncoder()
        y_train_encoded = encoder.fit_transform(y_train)
        y_test_encoded = encoder.transform(y_test)
        
        return X_train_scaled, X_test_scaled, y_train_encoded, y_test_encoded

    return features




def save_model(model, model_name, save_path=None):
    """
    Save the trained model to disk.
    """
    save_path = save_path or MODEL_PATHS.get(model_name, f'models/{model_name}_model.pkl')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(model, save_path)
    logging.info(f"Model '{model_name}' saved to {save_path}")

def train_and_save_model(model_type, csv_file_path):
    """
    Train and save the specified model type.
    """
    if model_type not in MODEL_PATHS.keys():
        raise ValueError(f"Unsupported model type: {model_type}")

    logging.info(f"Training {model_type} model...")
    X_train_scaled, X_test_scaled, y_train_encoded, y_test_encoded = preprocess_data(csv_file_path, add_target=True)

    # Initialize model
    if model_type == 'logistic_regression':
        model = LogisticRegression(random_state=42, solver='liblinear')
    elif model_type == 'random_forest':
        model = RandomForestClassifier(random_state=42)
    elif model_type == 'voting_classifier':
        log_reg = LogisticRegression(random_state=42, solver='liblinear')
        rf = RandomForestClassifier(random_state=42)
        model = VotingClassifier(estimators=[('logreg', log_reg), ('rf', rf)], voting='soft')
    elif model_type == 'gradient_boosting':
        model = GradientBoostingClassifier(random_state=42)

    # Train model
    model.fit(X_train_scaled, y_train_encoded)
    y_pred = model.predict(X_test_scaled)

    # Evaluate model
    accuracy = accuracy_score(y_test_encoded, y_pred)
    f1 = f1_score(y_test_encoded, y_pred, average='weighted')
    roc_auc = roc_auc_score(y_test_encoded, model.predict_proba(X_test_scaled), multi_class='ovr', average='weighted')
    logging.info(f"{model_type} - Accuracy: {accuracy:.4f}, F1: {f1:.4f}, ROC-AUC: {roc_auc:.4f}")
    logging.info(f"Confusion Matrix:\n{confusion_matrix(y_test_encoded, y_pred)}")
    logging.info(f"Classification Report:\n{classification_report(y_test_encoded, y_pred)}")

    # Save model
    save_model(model, model_type)

# List of required columns for model training
REQUIRED_COLUMNS = ['market_name', 'outcome_name', 'encoded_outcome']

def check_required_columns(df):
    """Check if all required columns are present in the dataframe."""
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        logging.error(f"Missing required columns: {', '.join(missing_columns)}")
        return False
    return True

if __name__ == "__main__":
    csv_file_path = "../../data/raw/processed_combined_data.csv"
    
    try:
        # Load the data first
        df = pd.read_csv(csv_file_path)
        
        # Check if all required columns are present
        if check_required_columns(df):
            # Proceed with model training if columns are valid
            for model_name in MODEL_PATHS.keys():
                try:
                    train_and_save_model(model_name, csv_file_path)
                except Exception as e:
                    logging.error(f"Failed to train {model_name}: {e}")
        else:
            logging.error("Missing required columns, training aborted.")
    
    except FileNotFoundError:
        logging.error(f"The file {csv_file_path} was not found.")
    except Exception as e:
        logging.error(f"An error occurred while loading the CSV: {e}")
