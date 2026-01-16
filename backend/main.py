import requests
import json
import os

GRAPH_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/activity-subgraph/0.0.4/gn"
OUTPUT_FILE = "data/whales.json"
MIN_USD_THRESHOLD = 1000 

def get_whale_level(usd_value):
    if usd_value >= 50000: return "LEVIATHAN", "🦖"
    elif usd_value >= 10000: return "WHALE", "🐋"
    else: return "SHARK", "🦈"

def fetch_whales():
    print("--- 🐳 PolyPulse V2: Scanning ---")
    
    query = """
    {
      trades(first: 60, orderBy: timestamp, orderDirection: desc) {
        timestamp, price, size, side, outcomeIndex
        market { question, slug }
        maker { id }
      }
    }
    """
    
    try:
        response = requests.post(GRAPH_URL, json={'query': query}, headers={"User-Agent": "PolyPulse/2.0"})
        data = response.json()
        trades = data.get('data', {}).get('trades', [])
        
        sightings = []
        for trade in trades:
            usd = float(trade['size']) * float(trade['price'])
            
            if usd >= MIN_USD_THRESHOLD:
                level_name, level_icon = get_whale_level(usd)
                
                sightings.append({
                    "time": int(trade['timestamp']),
                    "question": trade['market']['question'],
                    "outcome": int(trade['outcomeIndex']),
                    "side": trade['side'].upper(),
                    "size_usd": round(usd, 2),
                    "price": float(trade['price']),
                    "maker_address": trade['maker']['id'],
                    "level": level_name,   # Needed for new badges
                    "icon": level_icon
                })

        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, "w") as f:
            json.dump(sightings, f, indent=2)
        print(f"✅ Saved {len(sightings)} trades.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_whales()
