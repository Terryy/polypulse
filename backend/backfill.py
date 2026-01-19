import requests
import json
import os
import time
from datetime import datetime, timedelta

# --- CONFIGURATION ---
WHALE_THRESHOLD = 1000       
DAYS_TO_BACKFILL = 30        
# New API Endpoint
GRAPH_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/polymarket/prod/gn"

def fetch_history():
    start_time = int((datetime.now() - timedelta(days=DAYS_TO_BACKFILL)).timestamp())
    current_time = int(time.time())
    
    print(f"⏳ Connecting to Goldsky API...")
    all_trades = []
    
    try:
        query = f"""
        {{
          globalDeals(
            first: 1000,
            orderBy: timestamp,
            orderDirection: desc,
            where: {{ timestamp_gt: {start_time}, amountUSD_gt: {WHALE_THRESHOLD} }}
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
        response = requests.post(GRAPH_URL, json={'query': query}, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            trades = data.get('data', {}).get('globalDeals', [])
            if trades:
                print(f"✅ SUCCESS: Found {len(trades)} real trades.")
                return trades
            else:
                print("⚠️ API returned 0 trades (Clean result).")
                return []
        else:
             print(f"❌ API Error: {response.status_code}")
             return []

    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return []

def save_trades(trades):
    if not os.path.exists('data'):
        os.makedirs('data')
        
    trades.sort(key=lambda x: int(x['timestamp']), reverse=True)
    
    with open('data/whales.json', 'w') as f:
        json.dump(trades, f, indent=2)
    
    if len(trades) == 0:
        print("💾 Saved EMPTY file (No trades found).")
    else:
        print(f"💾 Saved {len(trades)} trades to data/whales.json")

if __name__ == "__main__":
    history = fetch_history()
    save_trades(history)
