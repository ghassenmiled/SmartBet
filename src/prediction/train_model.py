from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def train_and_save_model(model_type='logistic_regression', model_filepath='models/model.pkl'):
    """
    Train and save a model. Supports multiple model types.
    
    Args:
        model_type (str): Type of model to train ('logistic_regression' or 'random_forest').
        model_filepath (str): The path to save the model.
    """
    # Generate sample data
    X, y = make_classification(n_samples=100, n_features=4, random_state=42)
    
    # Select model based on model_type
    if model_type == 'logistic_regression':
        model = LogisticRegression()
    elif model_type == 'random_forest':
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    else:
        raise ValueError(f"Unsupported model type: {model_type}")
    
    # Train the model
    model.fit(X, y)
    
    # Save the trained model using the save_model utility function
    save_model(model, model_filepath)

if __name__ == "__main__":
    # Train and save logistic regression model
    train_and_save_model(model_type='logistic_regression', model_filepath='models/logistic_regression_model.pkl')
    
    # Train and save random forest model
    train_and_save_model(model_type='random_forest', model_filepath='models/random_forest_model.pkl')
