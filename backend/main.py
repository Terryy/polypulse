import requests
import json
import os
import time

# --- CONFIGURATION ---
# We use the Goldsky Subgraph (Official Polymarket Data Source)
# This does NOT require an API Key.
GRAPH_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/activity-subgraph/0.0.4/gn"
OUTPUT_FILE = "data/whales.json"
MIN_USD_THRESHOLD = 1000  # Show trades > $1k

def fetch_whales():
    print("--- 🐳 PolyPulse: Connecting to Subgraph ---")
    
    # GraphQL Query to get recent trades
    query = """
    {
      trades(first: 30, orderBy: timestamp, orderDirection: desc) {
        timestamp
        price
        size
        side
        market {
          question
          slug
        }
        maker {
          id
        }
        outcomeIndex
      }
    }
    """

    try:
        response = requests.post(
            GRAPH_URL, 
            json={'query': query},
            headers={"User-Agent": "PolyPulse/1.0"}
        )
        
        if response.status_code != 200:
            print(f"Error: API returned {response.status_code}")
            print(response.text)
            return

        data = response.json()
        trades = data.get('data', {}).get('trades', [])
        
        whale_sightings = []
        
        for trade in trades:
            # Calculate USD Size
            size_shares = float(trade.get('size', 0))
            price = float(trade.get('price', 0))
            usd_value = size_shares * price
            
            # Filter
            if usd_value >= MIN_USD_THRESHOLD:
                # Format Data for Frontend
                market = trade.get('market', {})
                maker = trade.get('maker', {})
                
                sighting = {
                    "time": int(trade.get('timestamp')),
                    "question": market.get('question', "Unknown Market"),
                    "outcome": int(trade.get('outcomeIndex', 0)),
                    "side": trade.get('side').upper(),
                    "size_usd": round(usd_value, 2),
                    "price": price,
                    "maker_address": maker.get('id', '0x...'),
                    "icon": "🐳" if usd_value > 10000 else "🐟"
                }
                whale_sightings.append(sighting)

        print(f"✅ Found {len(whale_sightings)} whale trades.")
        
        # Save to File
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, "w") as f:
            json.dump(whale_sightings, f, indent=2)

    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    fetch_whales()
