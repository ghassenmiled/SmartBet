import joblib

def save_model(model, filepath):
    joblib.dump(model, filepath)
    print(f"Model saved at {filepath}")

def load_model(filepath):
    return joblib.load(filepath)
