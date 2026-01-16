import requests
import json
import os
import time
from datetime import datetime, timedelta

# --- CONFIGURATION ---
GRAPH_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/activity-subgraph/0.0.4/gn"
OUTPUT_FILE = "data/whales.json"
MIN_USD_THRESHOLD = 1000       # Min size to record
RETENTION_DAYS = 30            # Keep history for 30 days

def get_whale_level(usd_value):
    if usd_value >= 50000: return "LEVIATHAN", "🦖"
    elif usd_value >= 10000: return "WHALE", "🐋"
    else: return "SHARK", "🦈"

def fetch_and_update():
    print("--- 🐳 PolyPulse: Updating History Log ---")
    
    # 1. Load Existing History
    history = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                history = json.load(f)
            print(f"Loaded {len(history)} existing records.")
        except Exception as e:
            print(f"Warning: Could not load existing history: {e}")
            history = []

    # 2. Fetch NEW Trades (Grab last 100 to ensure we don't miss gaps)
    query = """
    {
      trades(first: 100, orderBy: timestamp, orderDirection: desc) {
        id
        timestamp
        price
        size
        side
        outcomeIndex
        market { question, slug }
        maker { id }
      }
    }
    """
    
    new_sightings = []
    try:
        response = requests.post(
            GRAPH_URL, 
            json={'query': query}, 
            headers={"User-Agent": "PolyPulse/3.0"}
        )
        data = response.json()
        trades = data.get('data', {}).get('trades', [])
        
        for trade in trades:
            usd = float(trade['size']) * float(trade['price'])
            
            if usd >= MIN_USD_THRESHOLD:
                level_name, level_icon = get_whale_level(usd)
                
                new_sightings.append({
                    "id": trade['id'], # Unique ID from blockchain
                    "time": int(trade['timestamp']),
                    "question": trade['market']['question'],
                    "outcome": int(trade['outcomeIndex']),
                    "side": trade['side'].upper(),
                    "size_usd": round(usd, 2),
                    "price": float(trade['price']),
                    "maker_address": trade['maker']['id'],
                    "level": level_name,
                    "icon": level_icon
                })
    except Exception as e:
        print(f"❌ API Error: {e}")
        return # Stop if API fails to prevent overwriting with empty data

    # 3. Merge & Deduplicate
    # We use a dictionary keyed by ID to ensure no duplicates
    combined_db = {item['id']: item for item in history}
    
    # Add new items (this will update existing ones or add new ones)
    for sighting in new_sightings:
        combined_db[sighting['id']] = sighting
    
    # Convert back to list
    final_list = list(combined_db.values())
    
    # 4. Prune Old Records (> 30 Days)
    cutoff_time = time.time() - (RETENTION_DAYS * 24 * 60 * 60)
    final_list = [x for x in final_list if x['time'] > cutoff_time]
    
    # 5. Sort (Newest First)
    final_list.sort(key=lambda x: x['time'], reverse=True)

    # 6. Save
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(final_list, f, indent=2)
        
    print(f"✅ Database Updated: {len(final_list)} total records (30-day retention).")

if __name__ == "__main__":
    fetch_and_update()
