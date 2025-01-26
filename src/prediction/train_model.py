import os
import logging
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, VotingClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Define model paths
MODEL_PATHS = {
    'random_forest': 'models/random_forest_model.pkl',
    'logistic_regression': 'models/logistic_regression_model.pkl',
    'voting_classifier': 'models/voting_classifier_model.pkl',
    'gradient_boosting': 'models/gradient_boosting_model.pkl',
}

def preprocess_data(csv_file_path, add_target=False):
    """
    Preprocess the input CSV file for training.
    Handles missing values, adds calculated fields, encodes categorical variables,
    and scales numeric features.
    
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

    # Check if 'outcome_name' column exists
    if 'outcome_name' not in df.columns:
        logging.error("'outcome_name' column is missing. Cannot encode target.")
        return None

    # Replace URLs with 'NaN' for any textual fields
    df.replace(to_replace=r'http[s]?://\S+', value='NaN', regex=True, inplace=True)

    # Add calculated fields for 'best_price'
    if 'best_price' in df.columns:
        df['implied_probability'] = 1 / df['best_price']
        df['adjusted_odds'] = df['best_price'] * (1 - df['implied_probability'])

    # One-hot encode categorical columns
    categorical_columns = ['market_name', 'odds_type']
    available_categorical_columns = [col for col in categorical_columns if col in df.columns]
    if available_categorical_columns:
        df = pd.get_dummies(df, columns=available_categorical_columns, drop_first=True)

    # Encode target variable ('outcome_name') based on 'odds_type'
    if 'outcome_name' in df.columns:
        logging.info("'outcome_name' column found, proceeding with encoding.")
        
        # Skip rows where outcome_name is missing or invalid
        df = df.dropna(subset=['outcome_name'])
        df = df[df['outcome_name'].isin(['Yes', 'No', '1', '2', 'X', 'Over', 'Under'])]

        if df.empty:
            logging.warning("No valid 'outcome_name' values after filtering.")
            return None

        df['encoded_outcome'] = df.apply(
            lambda row: encode_outcome_based_on_odds_type(row), axis=1
        )
    else:
        logging.error("'outcome_name' column is missing. Cannot encode target.")
        return None

    # Handle missing values for numeric columns
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()

    # Drop columns with all missing values
    df = df.dropna(axis=1, how='all')

    # Use SimpleImputer to fill missing values in numeric columns
    imputer = SimpleImputer(strategy='mean')  # You can also use 'median' or 'most_frequent'
    df[numeric_columns] = imputer.fit_transform(df[numeric_columns])

    # Verify if there are any NaN values left
    if df.isnull().any().any():
        logging.warning("There are still missing values in the data after imputation.")

    # Separate features and target
    if add_target:
        target = df['encoded_outcome']
        numeric_columns.remove('encoded_outcome')  # Exclude target from features

    features = df[numeric_columns]

    # Log columns before splitting and training
    logging.info(f"Columns before splitting and training: {features.columns.tolist()}")

    # Split and scale data if add_target is True
    if add_target:
        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

        # Log columns of X_train before training
        logging.info(f"X_train columns: {X_train.columns.tolist()}")

        # Scale numeric features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Return scaled data and encoded target
        return X_train_scaled, X_test_scaled, y_train, y_test

    return features



def encode_outcome_based_on_odds_type(row):
    """
    Encode the outcome based on the odds_type and outcome_name.
    """
    odds_type = row['odds_type']
    outcome_name = row['outcome_name']

    # Logic based on odds_type
    if odds_type in ['Totals', 'Score']:
        if outcome_name == 'Yes':
            return 'Yes'
        elif outcome_name == 'No':
            return 'No'
    elif odds_type in ['2Way', 'Asian Handicap']:
        if outcome_name == '1':
            return '1'
        elif outcome_name == '2':
            return '2'
    elif odds_type in ['3Way', 'European Handicap']:
        if outcome_name == '1':
            return '1'
        elif outcome_name == '2':
            return '2'
        elif outcome_name == 'X':
            return 'X'
    elif odds_type == 'Over/Under':
        if outcome_name == 'Over':
            return 'Over'
        elif outcome_name == 'Under':
            return 'Under'
    else:
        logging.error(f"Unexpected odds_type or outcome_name: {odds_type}, {outcome_name}")
        return None


def save_model(model, model_name, save_path=None):
    """
    Save the trained model to disk.
    """
    save_path = save_path or MODEL_PATHS.get(model_name, f'models/{model_name}_model.pkl')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    joblib.dump(model, save_path)
    logging.info(f"Model '{model_name}' saved to {save_path}")

def initialize_model(model_type):
    """Initialize a model based on type."""
    if model_type == 'logistic_regression':
        return LogisticRegression(random_state=42, solver='liblinear')
    elif model_type == 'random_forest':
        return RandomForestClassifier(random_state=42)
    elif model_type == 'voting_classifier':
        log_reg = LogisticRegression(random_state=42, solver='liblinear')
        rf = RandomForestClassifier(random_state=42)
        return VotingClassifier(estimators=[('logreg', log_reg), ('rf', rf)], voting='soft')
    elif model_type == 'gradient_boosting':
        return GradientBoostingClassifier(random_state=42)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")

def evaluate_model_performance(y_test_encoded, y_pred, X_test_scaled, model):
    """Evaluate model performance using multiple metrics."""
    accuracy = accuracy_score(y_test_encoded, y_pred)
    f1 = f1_score(y_test_encoded, y_pred, average='weighted')
    roc_auc = roc_auc_score(y_test_encoded, model.predict_proba(X_test_scaled), multi_class='ovr', average='weighted')
    logging.info(f"Accuracy: {accuracy:.4f}, F1: {f1:.4f}, ROC-AUC: {roc_auc:.4f}")
    logging.info(f"Confusion Matrix:\n{confusion_matrix(y_test_encoded, y_pred)}")
    logging.info(f"Classification Report:\n{classification_report(y_test_encoded, y_pred)}")

def train_and_save_model_with_cv(model_type, csv_file_path):
    """ Train model with cross-validation and save the model """
    if model_type not in MODEL_PATHS.keys():
        raise ValueError(f"Unsupported model type: {model_type}")

    logging.info(f"Training {model_type} model with cross-validation...")

    X_train_scaled, X_test_scaled, y_train_encoded, y_test_encoded = preprocess_data(csv_file_path, add_target=True)

    # Initialize model
    model = initialize_model(model_type)

    # Perform cross-validation
    cross_val_scores = cross_val_score(model, X_train_scaled, y_train_encoded, cv=5, scoring='accuracy')
    logging.info(f"Cross-validation scores: {cross_val_scores}")
    logging.info(f"Mean cross-validation score: {cross_val_scores.mean():.4f}")

    # Train final model on the full dataset
    model.fit(X_train_scaled, y_train_encoded)
    y_pred = model.predict(X_test_scaled)

    # Evaluate and log performance
    evaluate_model_performance(y_test_encoded, y_pred, X_test_scaled, model)

    # Save the trained model
    save_model(model, model_type)

if __name__ == "__main__":
    csv_file_path = "../../data/raw/processed_combined_data.csv"
    
    try:
        # Load the data first
        df = pd.read_csv(csv_file_path)

        # Get columns dynamically
        # Ensure all columns are present
        df = preprocess_data(csv_file_path, add_target=False)

        # Proceed with model training
        model_type = 'logistic_regression'  # Choose any model type
        train_and_save_model_with_cv(model_type, csv_file_path)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
