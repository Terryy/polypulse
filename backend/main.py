import requests
import json
import os
import time
from datetime import datetime, timedelta

# --- CONFIGURATION ---
GRAPH_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/activity-subgraph/0.0.4/gn"
OUTPUT_FILE = "data/whales.json"
MIN_USD_THRESHOLD = 1000       # Define "Abnormal" as > $1,000
RETENTION_DAYS = 30            # Keep records for 30 days

def get_whale_level(usd_value):
    if usd_value >= 50000: return "LEVIATHAN", "🦖"
    elif usd_value >= 10000: return "WHALE", "🐋"
    else: return "SHARK", "🦈"

def fetch_and_update():
    print("--- 🐳 PolyPulse: 30-Day Archive Scan ---")
    
    # 1. Load Existing History (The Database)
    history = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                history = json.load(f)
            print(f"📂 Loaded {len(history)} existing records.")
        except Exception as e:
            print(f"Warning: Could not load existing history: {e}")
            history = []

    # 2. Fetch Deep History (Last 1000 trades to find past whales)
    query = """
    {
      trades(first: 1000, orderBy: timestamp, orderDirection: desc) {
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
            headers={"User-Agent": "PolyPulse/Archive"}
        )
        data = response.json()
        trades = data.get('data', {}).get('trades', [])
        print(f"🔍 Scanned {len(trades)} raw trades from the blockchain...")
        
        for trade in trades:
            # Calculate Value
            try:
                usd = float(trade['size']) * float(trade['price'])
            except:
                continue
            
            # FILTER: What counts as "Abnormal"?
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
        return # Stop if API fails to protect existing data

    # 3. Merge & Deduplicate (The "Append" Step)
    # We use a dictionary keyed by ID to ensure we never add the same trade twice
    combined_db = {item['id']: item for item in history}
    
    count_before = len(combined_db)
    for sighting in new_sightings:
        combined_db[sighting['id']] = sighting
    
    print(f"➕ Added {len(combined_db) - count_before} new whales found in this scan.")
    
    # Convert back to list
    final_list = list(combined_db.values())
    
    # 4. Prune Old Records (The "30-Day" Step)
    cutoff_time = time.time() - (RETENTION_DAYS * 24 * 60 * 60)
    original_count = len(final_list)
    final_list = [x for x in final_list if x['time'] > cutoff_time]
    
    if len(final_list) < original_count:
        print(f"✂️ Pruned {original_count - len(final_list)} records older than 30 days.")
    
    # 5. Sort (Newest First)
    final_list.sort(key=lambda x: x['time'], reverse=True)

    # 6. Save
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(final_list, f, indent=2)
        
    print(f"✅ Database Saved: {len(final_list)} total active records.")

if __name__ == "__main__":
    fetch_and_update()
