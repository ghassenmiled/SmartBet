import random
from .odds_calculator import calculate_odds

def calculate_odds(team_a_stats, team_b_stats):
    """
    Calculate the odds for a betting outcome based on team statistics.
    
    :param team_a_stats: A dictionary with statistics for team A
    :param team_b_stats: A dictionary with statistics for team B
    :return: A tuple with the odds for both teams
    """

    # Example: Calculate the goal difference between the teams
    team_a_goal_diff = team_a_stats['goals'] - team_b_stats['goals']
    
    # Example: Calculate the shot accuracy ratio
    team_a_accuracy = team_a_stats['shots'] / team_a_stats['pass_accuracy']
    team_b_accuracy = team_b_stats['shots'] / team_b_stats['pass_accuracy']
    
    # Base odds are calculated from stats (e.g., goal difference and shot accuracy)
    team_a_odds = 1 + (team_a_goal_diff * 0.1) + (team_a_accuracy * 0.05)
    team_b_odds = 1 + (-team_a_goal_diff * 0.1) + (team_b_accuracy * 0.05)

    # Adjusting odds slightly with random noise (simulate real-world fluctuations)
    team_a_odds += random.uniform(0.1, 0.3)
    team_b_odds += random.uniform(0.1, 0.3)

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

team_a_odds, team_b_odds = calculate_odds(team_a_stats, team_b_stats)
print(f"Odds for Team A: {team_a_odds}")
print(f"Odds for Team B: {team_b_odds}")
