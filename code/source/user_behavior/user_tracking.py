import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Use a JSON file as a mock persistent storage
USER_DATA_FILE = "user_data.json"

# Load existing user data from the file
def load_user_data():
    try:
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return empty dictionary if file is not found or corrupted
        return {}

# Save user data to the file
def save_user_data():
    try:
        with open(USER_DATA_FILE, "w") as file:
            json.dump(user_data, file, indent=4)
        logging.info("User data saved successfully.")
    except Exception as e:
        logging.error(f"Error saving user data: {e}")

# Global dictionary to store user data
user_data = load_user_data()

def save_user_bet(user_id, model, bet_amount, prediction, odds):
    """Track user bets and outcomes."""
    if user_id not in user_data:
        user_data[user_id] = {
            'bets': [],
            'preferences': {'risk_tolerance': 'medium'}  # Default risk tolerance
        }
    
    # Append the bet information, including the odds for the bet
    user_data[user_id]['bets'].append({
        'model': model,
        'bet_amount': bet_amount,
        'prediction': prediction,
        'odds': odds
    })
    
    # Persist the updated user data to the file
    save_user_data()

def get_user_preferences(user_id):
    """Get user preferences based on their betting behavior."""
    return user_data.get(user_id, {}).get('preferences', {'risk_tolerance': 'medium'})

def update_user_preferences(user_id, risk_tolerance):
    """Allow users to update their preferences, such as risk tolerance."""
    if user_id not in user_data:
        user_data[user_id] = {'bets': [], 'preferences': {}}
    
    user_data[user_id]['preferences']['risk_tolerance'] = risk_tolerance
    save_user_data()

