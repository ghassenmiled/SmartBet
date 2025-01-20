import random
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score
import joblib  # for saving the model

# Example training data (for demonstration purposes, this would be your preprocessed data)
def train_model():
    # Assuming you have preprocessed historical data
    data = {
        'team_a_goals': [3, 2, 1, 4],
        'team_b_goals': [1, 3, 2, 2],
        'team_a_shots': [10, 8, 5, 12],
        'team_b_shots': [5, 9, 6, 7],
        'match_result': [1, 0, 1, 1]  # 1=win, 0=loss
    }

    df = pd.DataFrame(data)

    # Features: Remove 'match_result' column and use the rest as features
    X = df.drop('match_result', axis=1)
    y = df['match_result']

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    # Initialize the Random Forest model
    model = RandomForestClassifier()

    # Cross-validation for better model evaluation
    cross_val_score(model, X_train, y_train, cv=5)

    # Train the model on the training set
    model.fit(X_train, y_train)

    # Test accuracy
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Model accuracy: {accuracy * 100:.2f}%')

    # Save the trained model to a file for future use
    joblib.dump(model, 'betting_model.pkl')
    print('Model saved as betting_model.pkl')

    return model

def predict_bet_outcome(real_world_data, num_models):
    # Load the pre-trained model (only once when needed)
    model = joblib.load('betting_model.pkl')

    predictions = []
    
    for _ in range(num_models):
        # Extract features from real-world data for prediction
        features = [
            real_world_data['team_a']['goals'],
            real_world_data['team_b']['goals'],
            real_world_data['team_a']['shots'],
            real_world_data['team_b']['shots']
        ]
        
        # Make the prediction using the trained model
        prediction = model.predict([features])

        # Calculate dynamic odds based on model output
        if prediction[0] == 1:
            odds = random.uniform(1.5, 2.5)  # Odds for a win prediction
        else:
            odds = random.uniform(2.5, 3.5)  # Odds for a loss prediction
        
        # Append prediction to the result list
        predictions.append({
            'odds': odds,
            'prediction': 'Win' if prediction[0] == 1 else 'Lose'
        })
    
    return predictions
