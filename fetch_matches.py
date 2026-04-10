import requests
import json
import os
from datetime import datetime, timedelta
import pytz

# 1. ضبط توقيت مصر
tz = pytz.timezone('Africa/Cairo')
now_cairo = datetime.now(tz)
today_str = now_cairo.strftime('%Y-%m-%d')

# 2. حيلة الشبكة الواسعة: هنجيب ماتشات من إمبارح لبكرة عشان نتفادى أخطاء سيرفر الموقع
yesterday_str = (now_cairo - timedelta(days=1)).strftime('%Y-%m-%d')
tomorrow_str = (now_cairo + timedelta(days=1)).strftime('%Y-%m-%d')

print(f"Fetching matches from {yesterday_str} to {tomorrow_str}...")

url = "https://api.football-data.org/v4/matches"
querystring = {
    "dateFrom": yesterday_str, 
    "dateTo": tomorrow_str
}

api_key = os.environ.get("FOOTBALL_API_KEY")
headers = {"X-Auth-Token": api_key}

try:
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    if response.status_code == 200 and "matches" in data:
        formatted_matches = []
        
        for match in data["matches"]:
            # 3. الفلتر الذكي: تحويل وقت المباراة لتوقيت مصر
            original_date = match["utcDate"]
            match_utc = datetime.strptime(original_date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=pytz.utc)
            match_cairo = match_utc.astimezone(tz)
            
            # هل المباراة تلعب اليوم بتوقيت مصر؟ (لو لا، تجاهلها تماماً)
            if match_cairo.strftime('%Y-%m-%d') != today_str:
                continue

            # لو المباراة اليوم، قم بتجهيزها للأندرويد
            status_map = {
                "SCHEDULED": "NS", "TIMED": "NS", "IN_PLAY": "LIVE",
                "PAUSED": "HT", "FINISHED": "FT", "SUSPENDED": "SUSP",
                "POSTPONED": "PST", "CANCELLED": "CANC", "AWARDED": "AWD"
            }
            raw_status = match.get("status", "NS")
            short_status = status_map.get(raw_status, "NS")
            
            android_friendly_date = original_date.replace("Z", "+00:00")
            
            league_name = match["competition"]["name"]
            if league_name == "Primera Division":
                league_name = "La Liga"
            elif league_name == "European Championship":
                league_name = "Euro"
                
            score_data = match.get("score", {})
            full_time = score_data.get("fullTime") or {}
            
            formatted_match = {
                "fixture": {
                    "id": match["id"],
                    "date": android_friendly_date,
                    "status": {"short": short_status}
                },
                "league": {
                    "name": league_name,
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
                    "home": full_time.get("home"),
                    "away": full_time.get("away")
                }
            }
            formatted_matches.append(formatted_match)
            
        with open('today_matches.json', 'w', encoding='utf-8') as f:
            json.dump(formatted_matches, f, ensure_ascii=False, indent=4)
            
        print(f"Success! {len(formatted_matches)} matches saved EXACTLY for today in Egypt.")
    else:
        print(f"API Error: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
