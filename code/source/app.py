from flask import Flask, render_template, request
import uuid
import random
import requests
import logging
import os
import http.client
import json

# Set up logging for verbose debugging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Function to fetch gambling odds from Website 
def get_gambling_odds(website):
    api_key = os.getenv('API_KEY')
    conn = http.client.HTTPSConnection("bet365-api-inplay.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': api_key,
        'x-rapidapi-host': "bet365-api-inplay.p.rapidapi.com"
    }

    try:
        conn.request("GET", "/bet365/get_betfair_forks", headers=headers)
        res = conn.getresponse()
        data = res.read()

        # Decode and load JSON data
        data = json.loads(data.decode("utf-8"))

        if isinstance(data, list) and len(data) > 0:
            # Extract odds data from response
            odds_list = []
            for event in data:
                odds_info = {
                    "event_name": event.get('bK1_EventName'),
                    "bookmaker1": event.get('bookmaker1'),
                    "bet_name1": event.get('bK1_BetName'),
                    "bet_coef1": event.get('bK1_BetCoef'),
                    "bookmaker2": event.get('bookmaker2'),
                    "bet_name2": event.get('bK2_BetName'),
                    "bet_coef2": event.get('bK2_BetCoef'),
                }
                odds_list.append(odds_info)
            return odds_list
        else:
            logging.error("Invalid data structure received")
            return None

    except Exception as e:
        logging.error(f"Error fetching gambling odds: {e}")
        return None

@app.route('/')
def index():
    gambling_sites = ['Sportsbook1', 'Sportsbook2', 'Sportsbook3']  # List of gambling sites
    return render_template('index.html', gambling_sites=gambling_sites)

@app.route('/bet', methods=['POST'])
def bet():
    website = request.form.get('website')
    model = request.form.get('model')
    max_odds = request.form.get('max_odds', type=float)
    desired_profit = request.form.get('desired_profit', type=float)

    logging.debug(f"Received form data: Website={website}, Model={model}, Max Odds={max_odds}, Desired Profit={desired_profit}")

    if not website:
        logging.error("Website is missing")
        return render_template('error.html', message="Website is required.")
    
    odds = get_gambling_odds(website)
    if odds is None:
        logging.error(f"Failed to fetch odds for website: {website}")
        return render_template('error.html', message="Failed to fetch odds for the selected website.")
    
    logging.debug(f"Fetched odds: {odds}")

    return render_template('result.html', website=website, model=model, max_odds=max_odds, desired_profit=desired_profit, odds=odds)


    return render_template('result.html', odds=odds)

if __name__ == '__main__':
    app.run(debug=True)
