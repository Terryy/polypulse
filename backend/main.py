import requests
import json
import os
import time
from datetime import datetime, timedelta

# --- CONFIGURATION ---
WHALE_THRESHOLD = 1000
GRAPH_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/polymarket/prod/gn"

def fetch_new_whales():
    # Look back 1 hour
    start_time = int((datetime.now() - timedelta(hours=1)).timestamp())
    
    query = f"""
    {{
      globalDeals(
        first: 100,
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
    try:
        response = requests.post(GRAPH_URL, json={'query': query}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', {}).get('globalDeals', [])
        return []
    except Exception as e:
        print(f"❌ API Error: {e}")
        return []

def update_database(new_trades):
    file_path = 'data/whales.json'
    existing_trades = []

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                existing_trades = json.load(f)
        except:
            existing_trades = []

    if not new_trades and not existing_trades:
        print("No data available at all.")
        return

    # Merge Logic
    trade_map = {t['id']: t for t in existing_trades}
    for t in new_trades:
        trade_map[t['id']] = t
    
    all_trades = list(trade_map.values())
    all_trades.sort(key=lambda x: int(x['timestamp']), reverse=True)
    all_trades = all_trades[:2000] # Limit file size

    with open(file_path, 'w') as f:
        json.dump(all_trades, f, indent=2)
    print(f"💾 Database updated. Count: {len(all_trades)}")

if __name__ == "__main__":
    new_data = fetch_new_whales()
    update_database(new_data)
