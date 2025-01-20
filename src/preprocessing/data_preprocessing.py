import pandas as pd
from sklearn.preprocessing import StandardScaler

def preprocess_data(filepath):
    data = pd.read_csv(filepath)
    data.fillna(0, inplace=True)  # Handle missing values
    scaler = StandardScaler()
    features = scaler.fit_transform(data[['team_strength', 'recent_form', 'odds']])
    return features, data['match_outcome']