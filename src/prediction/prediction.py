import joblib
import numpy as np

def load_model(model_path):
    return joblib.load(model_path)

def make_prediction(model, features):
    probabilities = model.predict_proba(features)
    return np.argmax(probabilities, axis=1), probabilities