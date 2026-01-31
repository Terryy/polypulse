import json
import os
from datetime import datetime, timedelta

import requests

# --- CONFIGURATION ---
WHALE_THRESHOLD = 1000
GRAPH_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/polymarket/prod/gn"

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
DATA_PATH = os.path.join(ROOT_DIR, "data", "whales.json")

def fetch_new_whales():
    # Look back 1 hour
    start_time = int((datetime.now() - timedelta(hours=1)).timestamp())
    
    query = f"""
    {{
      fpmmTrades(
        first: 100,
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
        response = requests.post(GRAPH_URL, json={'query': query}, timeout=10)
        data = response.json()
        trades = data.get('data', {}).get('fpmmTrades', [])
        
        # Normalize
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

    except Exception as e:
        print(f"❌ API Error: {e}")
        return []

def update_database(new_trades):
    existing_trades = []

    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, 'r') as f:
                existing_trades = json.load(f)
        except:
            existing_trades = []

    if not new_trades:
        print("No new trades found.")
        return

    # Merge
    trade_map = {t['id']: t for t in existing_trades}
    for t in new_trades:
        trade_map[t['id']] = t
    
    all_trades = list(trade_map.values())
    all_trades.sort(key=lambda x: int(x['timestamp']), reverse=True)
    all_trades = all_trades[:2000] 

    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w') as f:
        json.dump(all_trades, f, indent=2)
    print(f"💾 Database updated. Total: {len(all_trades)}")

if __name__ == "__main__":
    new_data = fetch_new_whales()
    update_database(new_data)
