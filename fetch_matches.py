import requests
import json
import os
from datetime import datetime
import pytz

tz = pytz.timezone('Africa/Cairo')
today = datetime.now(tz).strftime('%Y-%m-%d')

print(f"Fetching matches for: {today} from football-data.org...\n")

url = "https://api.football-data.org/v4/matches"
querystring = {"dateFrom": today, "dateTo": today}

api_key = os.environ.get("FOOTBALL_API_KEY")

headers = {
    "X-Auth-Token": api_key, 
}

try:
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    if response.status_code == 200 and "matches" in data:
        formatted_matches = []
        
        for match in data["matches"]:
            status_map = {
                "SCHEDULED": "NS",
                "TIMED": "NS",
                "IN_PLAY": "LIVE",
                "PAUSED": "HT",
                "FINISHED": "FT",
                "SUSPENDED": "SUSP",
                "POSTPONED": "PST",
                "CANCELLED": "CANC",
                "AWARDED": "AWD"
            }
            raw_status = match.get("status", "NS")
            short_status = status_map.get(raw_status, "NS")
            
            score_data = match.get("score", {})
            full_time = score_data.get("fullTime") or {}
            
            home_goals = full_time.get("home")
            away_goals = full_time.get("away")

            formatted_match = {
                "fixture": {
                    "id": match["id"],
                    "date": match["utcDate"],
                    "status": {
                        "short": short_status
                    }
                },
                "league": {
                    "name": match["competition"]["name"],
                    "country": match["area"]["name"],
                    "logo": match["competition"].get("emblem", "")
                },
                "teams": {
                    "home": {
                        "name": match["homeTeam"]["name"],
                        "logo": match["homeTeam"].get("crest", "")
                    },
                    "away": {
                        "name": match["awayTeam"]["name"],
                        "logo": match["awayTeam"].get("crest", "")
                    }
                },
                "goals": {
                    "home": home_goals,
                    "away": away_goals
                }
            }
            
            formatted_matches.append(formatted_match)
            
        with open('today_matches.json', 'w', encoding='utf-8') as f:
            json.dump(formatted_matches, f, ensure_ascii=False, indent=4)
            
        print(f"Success! {len(formatted_matches)} matches saved and translated.")
    else:
        print(f"API Error: {response.status_code}")
        print(data)
        
except Exception as e:
    print(f"Error: {e}")
