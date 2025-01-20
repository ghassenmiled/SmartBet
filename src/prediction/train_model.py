from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification
import joblib

def train_and_save_model():
    # Generate sample data
    X, y = make_classification(n_samples=100, n_features=4, random_state=42)

    # Train logistic regression model
    model = LogisticRegression()
    model.fit(X, y)

    # Save the model
    joblib.dump(model, 'models/logistic_regression_model.pkl')
    print("Model saved!")

if __name__ == "__main__":
    train_and_save_model()
