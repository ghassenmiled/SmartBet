import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

def preprocess_data(filepath):
    # Load the dataset
    data = pd.read_csv(filepath)

    # Handle missing values more intelligently
    imputer = SimpleImputer(strategy='mean')  # Using mean imputation for numerical columns
    data[['team_strength', 'recent_form', 'odds']] = imputer.fit_transform(data[['team_strength', 'recent_form', 'odds']])

    # Feature scaling: Scale numerical features
    scaler = StandardScaler()
    features = scaler.fit_transform(data[['team_strength', 'recent_form', 'odds']])

    # Optionally, you can add more feature engineering here (e.g., ratio between team strength and odds)
    
    # Return the scaled features and the target variable
    return features, data['match_outcome']

