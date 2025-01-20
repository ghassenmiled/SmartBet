import joblib
import os

def save_model(model, filepath):
    """Save a model to a specified filepath."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(model, filepath)
        print(f"Model successfully saved at {filepath}")
    except Exception as e:
        print(f"Error saving model: {e}")

def load_model(filepath):
    """Load a model from a specified filepath."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Model file '{filepath}' not found.")
    
    try:
        model = joblib.load(filepath)
        print(f"Model successfully loaded from {filepath}")
        return model
    except Exception as e:
        print(f"Error loading model: {e}")
        raise
