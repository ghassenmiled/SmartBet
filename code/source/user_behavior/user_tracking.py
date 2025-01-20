user_data = {}

def save_user_bet(user_id, model, bet_amount, prediction):
    # Track user bets and outcomes
    if user_id not in user_data:
        user_data[user_id] = {
            'bets': [],
            'preferences': {'risk_tolerance': 'medium'}  # Default risk tolerance
        }
    
    user_data[user_id]['bets'].append({
        'model': model,
        'bet_amount': bet_amount,
        'prediction': prediction
    })

def get_user_preferences(user_id):
    # Example: Get user preferences based on their betting behavior
    return user_data.get(user_id, {}).get('preferences', {'risk_tolerance': 'medium'})
