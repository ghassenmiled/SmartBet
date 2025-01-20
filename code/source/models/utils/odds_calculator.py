import random
import math

def calculate_odds(team_a_stats, team_b_stats, home_advantage=True):
    """
    Calculate the odds for a betting outcome based on team statistics.
    
    :param team_a_stats: A dictionary with statistics for team A
    :param team_b_stats: A dictionary with statistics for team B
    :param home_advantage: Boolean to indicate if Team A is playing at home
    :return: A tuple with the odds for both teams
    """
    
    # Normalize goal difference for a more realistic range
    team_a_goal_diff = team_a_stats['goals'] - team_b_stats['goals']
    team_b_goal_diff = team_b_stats['goals'] - team_a_stats['goals']
    
    # Factor in the shot accuracy ratio (more weight to shots on target)
    team_a_accuracy = team_a_stats['shots'] / max(team_a_stats['pass_accuracy'], 1)  # Prevent division by zero
    team_b_accuracy = team_b_stats['shots'] / max(team_b_stats['pass_accuracy'], 1)
    
    # Normalize shooting and passing accuracy (bounded between 0 and 1)
    team_a_accuracy = min(team_a_accuracy / 10, 1)  # Limiting to a maximum of 1
    team_b_accuracy = min(team_b_accuracy / 10, 1)
    
    # Adjust odds based on goal difference, accuracy, and home advantage
    team_a_odds = 1 + (team_a_goal_diff * 0.1) + (team_a_accuracy * 0.2)
    team_b_odds = 1 + (team_b_goal_diff * 0.1) + (team_b_accuracy * 0.2)
    
    # Apply home advantage if applicable
    if home_advantage:
        team_a_odds -= 0.05  # Home team has a slight advantage (adjust as needed)
        team_b_odds += 0.05  # Away team suffers a slight disadvantage
    
    # Apply additional randomness to simulate betting market fluctuations
    random_factor_a = random.uniform(0.05, 0.15)  # Simulate fluctuations
    random_factor_b = random.uniform(0.05, 0.15)
    
    team_a_odds += random_factor_a
    team_b_odds += random_factor_b

    # Ensure odds are within a reasonable range
    team_a_odds = max(1.5, min(team_a_odds, 5.0))  # Minimum odds of 1.5, max of 5.0
    team_b_odds = max(1.5, min(team_b_odds, 5.0))

    return round(team_a_odds, 2), round(team_b_odds, 2)

# Example usage
team_a_stats = {
    'goals': 3,
    'shots': 12,
    'pass_accuracy': 75
}

team_b_stats = {
    'goals': 1,
    'shots': 9,
    'pass_accuracy': 65
}

# Assume team A is playing at home
team_a_odds, team_b_odds = calculate_odds(team_a_stats, team_b_stats, home_advantage=True)
print(f"Odds for Team A: {team_a_odds}")
print(f"Odds for Team B: {team_b_odds}")
