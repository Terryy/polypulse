import json
import os
from datetime import datetime, timedelta

import requests

# --- CONFIGURATION ---
WHALE_THRESHOLD = 1000       
DAYS_TO_BACKFILL = 30        

# ✅ CORRECT URL (The "Main" Subgraph, not the Activity one)
GRAPH_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/polymarket/prod/gn"

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
DATA_PATH = os.path.join(ROOT_DIR, "data", "whales.json")

def fetch_history():
    start_time = int((datetime.now() - timedelta(days=DAYS_TO_BACKFILL)).timestamp())
    print(f"⏳ Connecting to Main Polymarket Database...")
    
    # We query 'fpmmTrades' which is the standard table for Buy/Sell actions
    query = f"""
    {{
      fpmmTrades(
        first: 1000,
        orderBy: creationTimestamp,
        orderDirection: desc,
        where: {{ creationTimestamp_gt: {start_time}, amountUSD_gt: {WHALE_THRESHOLD} }}
      ) {{
        id
        creationTimestamp
        title
        outcomeIndex
        amountUSD
        type
        creator {{ id }}
      }}
    }}
    """
    
    try:
        response = requests.post(GRAPH_URL, json={'query': query}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            trades = data.get('data', {}).get('fpmmTrades', [])
            
            if trades:
                print(f"✅ SUCCESS: Found {len(trades)} trades!")
                
                # Normalize the data format for your frontend
                clean_trades = []
                for t in trades:
                    clean_trades.append({
                        "id": t['id'],
                        "timestamp": int(t['creationTimestamp']),
                        "user": t.get('creator', {'id': '0x00'}),
                        "market": {"question": t.get('title', 'Unknown Market')},
                        "outcomeIndex": t.get('outcomeIndex'),
                        "amountUSD": t.get('amountUSD')
                    })
                return clean_trades
            else:
                print("⚠️ Connected, but found 0 trades. (Maybe threshold is too high?)")
                return []
        else:
            print(f"❌ API Error: {response.status_code}")
            return []

    except Exception as e:
        print(f"❌ Critical Error: {e}")
        return []

def save_trades(trades):
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        
    trades.sort(key=lambda x: int(x['timestamp']), reverse=True)
    
    with open(DATA_PATH, 'w') as f:
        json.dump(trades, f, indent=2)
    print(f"💾 Saved {len(trades)} trades to {DATA_PATH}")

if __name__ == "__main__":
    history = fetch_history()
    save_trades(history)
