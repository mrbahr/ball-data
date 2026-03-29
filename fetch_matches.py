import requests
import json
import os
from datetime import datetime

today = datetime.today().strftime('%Y-%m-%d')
print(f"Fetching matches for: {today}...\n")

url = "https://v3.football.api-sports.io/fixtures"
querystring = {"date": today}


api_key = os.environ.get("FOOTBALL_API_KEY")

headers = {
    "x-apisports-key": api_key, 
}

try:
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    if response.status_code == 200 and "response" in data:
        matches = data['response']
        
       
        with open('today_matches.json', 'w', encoding='utf-8') as f:
            json.dump(matches, f, ensure_ascii=False, indent=4)
            
        print(f"Success! {len(matches)} matches saved.")
    else:
        print("API Error:")
        print(data)
        
except Exception as e:
    print(f"Error: {e}")