import requests
import json
import os
import time
from datetime import datetime, timedelta

# --- CONFIGURATION ---
WHALE_THRESHOLD = 1000
GRAPH_URL = "https://subgraph-matic.poly.market/subgraphs/name/TokenUnion/polymarket"

def fetch_new_whales():
    # Only look back 1 hour for new updates
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
        data = response.json()
        return data.get('data', {}).get('globalDeals', [])
    except Exception as e:
        print(f"❌ API Error: {e}")
        return []

def update_database(new_trades):
    if not new_trades:
        print("No new trades found.")
        return

    file_path = 'data/whales.json'
    existing_trades = []

    # 1. Load existing history
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                existing_trades = json.load(f)
        except:
            existing_trades = []

    # 2. Merge (Avoid duplicates using ID)
    trade_map = {t['id']: t for t in existing_trades}
    for t in new_trades:
        trade_map[t['id']] = t
    
    # 3. Sort & Save
    all_trades = list(trade_map.values())
    all_trades.sort(key=lambda x: int(x['timestamp']), reverse=True)

    # Optional: Keep file size manageable (Limit to last 2000 trades)
    all_trades = all_trades[:2000]

    with open(file_path, 'w') as f:
        json.dump(all_trades, f, indent=2)
    print(f"💾 Database updated. Now contains {len(all_trades)} trades.")

if __name__ == "__main__":
    print("🐳 Checking for new whales...")
    new_data = fetch_new_whales()
    update_database(new_data)
