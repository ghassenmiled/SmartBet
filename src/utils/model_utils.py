import joblib
import os

# Model path mapping for easy lookup
MODEL_PATHS = {
    "model_1": "models/model_1.pkl",  # Example model file path
    # Add other models here
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
        print(f"Model '{model_name}' successfully saved at {filepath}")
    except Exception as e:
        print(f"Error saving model '{model_name}': {e}")

def load_model(model_name):
    """Load a model from a specified model name."""
    if model_name not in MODEL_PATHS:
        raise ValueError(f"Model '{model_name}' not found in the model path mapping.")
    
    filepath = MODEL_PATHS[model_name]
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Model file '{filepath}' not found.")
    
    try:
        model = joblib.load(filepath)
        print(f"Model '{model_name}' successfully loaded from {filepath}")
        return model
    except Exception as e:
        print(f"Error loading model '{model_name}': {e}")
        raise
