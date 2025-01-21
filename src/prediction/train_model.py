import os
import joblib
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split, cross_val_score

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Define model paths
MODEL_PATHS = {
    'logistic_regression': 'models/logistic_regression_model.pkl',
    'random_forest': 'models/random_forest_model.pkl',
}

def save_model(model, model_name):
    """Save a model to a specified filepath based on the model name."""
    if model_name not in MODEL_PATHS:
        raise ValueError(f"Model name '{model_name}' is not valid.")
    
    filepath = MODEL_PATHS[model_name]
    
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(model, filepath)
        logging.info(f"Model '{model_name}' successfully saved at {filepath}")
    except Exception as e:
        logging.error(f"Error saving model '{model_name}': {e}")
        raise  # Re-raise to propagate the error

def train_and_save_model(model_type='logistic_regression', model_filepath=None):
    """
    Train and save a model. Supports multiple model types.
    
    Args:
        model_type (str): Type of model to train ('logistic_regression' or 'random_forest').
        model_filepath (str): The path to save the model.
    """
    if model_filepath is None:
        model_filepath = MODEL_PATHS.get(model_type, 'models/model.pkl')
    
    # Generate synthetic classification dataset (you can replace this with real-world data)
    X, y = make_classification(n_samples=1000, n_features=2, random_state=42)
    
    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Select model based on model_type
    if model_type == 'logistic_regression':
        model = LogisticRegression(random_state=42)
    elif model_type == 'random_forest':
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    
    try:
        # Train the model
        model.fit(X_train, y_train)

        # Evaluate the model with cross-validation (use train/test split for final evaluation)
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        logging.info(f"Model trained successfully with cross-validation scores: {cv_scores}")
        logging.info(f"Mean CV Accuracy: {cv_scores.mean():.4f}")
        
        # Final evaluation on the test set
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logging.info(f"Model accuracy on test set: {accuracy:.4f}")

        # Save the trained model using the save_model utility function
        save_model(model, model_type)
        logging.info(f"Model successfully saved at {model_filepath}")

    except Exception as e:
        logging.error(f"Error during model training or saving: {e}")
        raise  # Re-raise the error to be caught higher up if needed

if __name__ == "__main__":
    # Ensure the 'models/' directory exists
    os.makedirs('models', exist_ok=True)

    # Train and save logistic regression model
    train_and_save_model(model_type='logistic_regression')
    
    # Train and save random forest model
    train_and_save_model(model_type='random_forest')
