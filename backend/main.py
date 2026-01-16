import requests
import json
import os
import time
from datetime import datetime, timedelta

# --- CONFIGURATION (UPDATED) ---
# $1,000 is a much better baseline for "significant" activity
WHALE_THRESHOLD = 1000  
# Look back 24 hours to fill the board immediately
HOURS_TO_LOOK_BACK = 24 
GRAPH_URL = "https://subgraph-matic.poly.market/subgraphs/name/TokenUnion/polymarket"

def fetch_whales():
    # Calculate timestamp for X hours ago
    start_time = int((datetime.now() - timedelta(hours=HOURS_TO_LOOK_BACK)).timestamp())
    
    print(f"⏳ Scanning trades > ${WHALE_THRESHOLD} from the last {HOURS_TO_LOOK_BACK} hours...")

    # Query: Get the top 100 trades by size
    query = f"""
    {{
      globalDeals(
        where: {{ timestamp_gt: {start_time}, amountUSD_gt: {WHALE_THRESHOLD} }}
        orderBy: amountUSD
        orderDirection: desc
        first: 100
      ) {{
        id
        timestamp
        user {{ id }}
        market {{ question }}
        outcomeIndex
        amount
        amountUSD
      }}
    }}
    """
    
    try:
        response = requests.post(GRAPH_URL, json={'query': query})
        
        if response.status_code != 200:
            print(f"❌ API Error: {response.status_code}")
            return []

        data = response.json()
        trades = data.get('data', {}).get('globalDeals', [])
        
        print(f"✅ Success! Found {len(trades)} trades.")
        return trades

    except Exception as e:
        print(f"❌ Critical Error: {e}")
        return []

def save_whales(trades):
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Sort by time (newest first)
    trades.sort(key=lambda x: int(x['timestamp']), reverse=True)

    with open('data/whales.json', 'w') as f:
        json.dump(trades, f, indent=2)
    print(f"💾 Saved {len(trades)} trades to data/whales.json")

if __name__ == "__main__":
    whales = fetch_whales()
    if whales:
        save_whales(whales)
    else:
        # Create an empty list if nothing found, so the file exists
        save_whales([])
        print("⚠️ No trades found. Try lowering WHALE_THRESHOLD even more.")
