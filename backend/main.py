import requests
import json
import os
import time

# --- CONFIGURATION ---
GRAPH_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/activity-subgraph/0.0.4/gn"
OUTPUT_FILE = "data/whales.json"
MIN_USD_THRESHOLD = 10         # <--- CHANGED TO $10 (Catch everything)
RETENTION_DAYS = 30

def get_whale_level(usd_value):
    if usd_value >= 50000: return "LEVIATHAN", "🦖"
    elif usd_value >= 5000: return "WHALE", "🐋"
    elif usd_value >= 1000: return "SHARK", "🦈"
    else: return "MINNOW", "🐟"  # <--- NEW TIER for small trades

def fetch_and_update():
    print("--- 🐳 PolyPulse: Debug Scan (Threshold: $10) ---")
    
    # 1. Load Existing History
    history = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                history = json.load(f)
        except:
            history = []

    # 2. Fetch NEW Trades
    # We fetch 1000 trades to ensure we find *something*
    query = """
    {
      trades(first: 1000, orderBy: timestamp, orderDirection: desc) {
        id, timestamp, price, size, side, outcomeIndex
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
            headers={"User-Agent": "PolyPulse/Debug"}
        )
        data = response.json()
        trades = data.get('data', {}).get('trades', [])
        
        print(f"🔍 API returned {len(trades)} raw trades from the blockchain.")

        if len(trades) == 0:
            print("⚠️ WARNING: API returned 0 trades. The Graph might be syncing.")

        for trade in trades:
            try:
                usd = float(trade['size']) * float(trade['price'])
                
                # Debug Print for the first 5 trades found
                if len(new_sightings) < 5:
                    print(f"   Found trade: ${usd:.2f} on '{trade['market']['question'][:30]}...'")

                if usd >= MIN_USD_THRESHOLD:
                    level_name, level_icon = get_whale_level(usd)
                    
                    new_sightings.append({
                        "id": trade['id'],
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
                continue

    except Exception as e:
        print(f"❌ API Error: {e}")
        return

    # 3. Merge & Deduplicate
    combined_db = {item['id']: item for item in history}
    count_before = len(combined_db)
    
    for sighting in new_sightings:
        combined_db[sighting['id']] = sighting
    
    print(f"➕ Added {len(combined_db) - count_before} new trades to database.")
    
    final_list = list(combined_db.values())
    
    # 4. Prune (> 30 Days)
    cutoff_time = time.time() - (RETENTION_DAYS * 86400)
    final_list = [x for x in final_list if x['time'] > cutoff_time]
    final_list.sort(key=lambda x: x['time'], reverse=True)

    # 5. Save
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(final_list, f, indent=2)
        
    print(f"✅ Database Saved: {len(final_list)} total records.")

if __name__ == "__main__":
    fetch_and_update()
