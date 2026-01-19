import requests
import json
import os
import time
from datetime import datetime, timedelta

# --- CONFIGURATION ---
WHALE_THRESHOLD = 1000       # Trades > $1,000
DAYS_TO_BACKFILL = 30        # Look back 30 days
GRAPH_URL = "https://subgraph-matic.poly.market/subgraphs/name/TokenUnion/polymarket"

def fetch_history():
    start_time = int((datetime.now() - timedelta(days=DAYS_TO_BACKFILL)).timestamp())
    current_time = int(time.time())
    
    print(f"⏳ Backfilling {DAYS_TO_BACKFILL} days of whale data...")
    all_trades = []
    
    while current_time > start_time:
        query = f"""
        {{
          globalDeals(
            first: 1000,
            orderBy: timestamp,
            orderDirection: desc,
            where: {{ timestamp_lt: {current_time}, timestamp_gt: {start_time}, amountUSD_gt: {WHALE_THRESHOLD} }}
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
            response = requests.post(GRAPH_URL, json={'query': query}, timeout=30)
            data = response.json()
            trades = data.get('data', {}).get('globalDeals', [])
            
            if not trades:
                break
                
            all_trades.extend(trades)
            print(f"   Collected {len(trades)} trades (Total: {len(all_trades)})...")
            
            # Update cursor
            current_time = int(trades[-1]['timestamp'])
            time.sleep(0.5) # Be nice to the API
            
        except Exception as e:
            print(f"❌ Error: {e}")
            break
            
    return all_trades

def save_trades(trades):
    if not os.path.exists('data'):
        os.makedirs('data')
        
    # Sort by time (newest first)
    trades.sort(key=lambda x: int(x['timestamp']), reverse=True)
    
    with open('data/whales.json', 'w') as f:
        json.dump(trades, f, indent=2)
    print(f"💾 Saved {len(trades)} historical trades to data/whales.json")

if __name__ == "__main__":
    history = fetch_history()
    if history:
        save_trades(history)
