import os
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.metrics import accuracy_score
from src.utils.model_utils import save_model  # Import save_model function for saving the model

def train_and_save_model(model_type='logistic_regression', model_filepath='models/model.pkl'):
    """
    Train and save a model. Supports multiple model types.
    
    Args:
        model_type (str): Type of model to train ('logistic_regression' or 'random_forest').
        model_filepath (str): The path to save the model.
    """
    # Generate synthetic classification dataset
    X, y = make_classification(n_samples=100, n_features=4, random_state=42)
    
    # Select model based on model_type
    if model_type == 'logistic_regression':
        model = LogisticRegression(random_state=42)
    elif model_type == 'random_forest':
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    
    try:
        # Train the model
        model.fit(X, y)

        # Evaluate the model
        y_pred = model.predict(X)
        accuracy = accuracy_score(y, y_pred)
        print(f"Model trained successfully with accuracy: {accuracy:.4f}")

        # Save the trained model using the save_model utility function
        save_model(model, model_filepath)
        print(f"Model successfully saved at {model_filepath}")

    except Exception as e:
        print(f"Error during model training or saving: {e}")
        raise  # Re-raise the error to be caught higher up if needed

if __name__ == "__main__":
    # Ensure the 'models/' directory exists
    if not os.path.exists('models'):
        os.makedirs('models')
    
    # Train and save logistic regression model
    train_and_save_model(model_type='logistic_regression', model_filepath='models/logistic_regression_model.pkl')
    
    # Train and save random forest model
    train_and_save_model(model_type='random_forest', model_filepath='models/random_forest_model.pkl')
