import requests
import json
import os
import time
from datetime import datetime, timedelta

# --- CONFIGURATION ---
WHALE_THRESHOLD = 1000       # Trades must be > $1,000 USD
DAYS_TO_BACKFILL = 30        # Look back 30 days
GRAPH_URL = "https://subgraph-matic.poly.market/subgraphs/name/TokenUnion/polymarket"

def fetch_all_history():
    # Calculate cutoff time (30 days ago)
    end_time = int(time.time())
    start_time = int((datetime.now() - timedelta(days=DAYS_TO_BACKFILL)).timestamp())
    
    print(f"⏳ Starting Backfill: {DAYS_TO_BACKFILL} days ({datetime.fromtimestamp(start_time)} to Now)")
    
    all_trades = []
    current_time = end_time
    
    # Loop to fetch data in chunks (Graph API limit is usually 100-1000 items)
    while current_time > start_time:
        query = f"""
        {{
          globalDeals(
            first: 1000,
            orderBy: timestamp,
            orderDirection: desc,
            where: {{ 
              timestamp_lt: {current_time}, 
              timestamp_gt: {start_time},
              amountUSD_gt: {WHALE_THRESHOLD}
            }}
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
            print(f"   Scanning before timestamp {current_time}...")
            response = requests.post(GRAPH_URL, json={'query': query}, timeout=15)
            
            if response.status_code != 200:
                print(f"❌ API Error: {response.status_code}")
                break
                
            data = response.json()
            trades = data.get('data', {}).get('globalDeals', [])
            
            if not trades:
                print("   ✅ No more trades found in this time range.")
                break
                
            all_trades.extend(trades)
            print(f"   Found {len(trades)} trades... (Total: {len(all_trades)})")
            
            # Update cursor to the oldest timestamp found to get the next batch
            last_timestamp = int(trades[-1]['timestamp'])
            current_time = last_timestamp
            
            # Safety sleep to avoid rate limits
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Critical Error: {e}")
            break
            
    return all_trades

def save_to_file(trades):
    if not os.path.exists('data'):
        os.makedirs('data')
        
    # Final sort just in case
    trades.sort(key=lambda x: int(x['timestamp']), reverse=True)
    
    file_path = 'data/whales.json'
    with open(file_path, 'w') as f:
        json.dump(trades, f, indent=2)
    
    print(f"\n🎉 SUCCESS! Saved {len(trades)} historical whale trades to {file_path}")

if __name__ == "__main__":
    history = fetch_all_history()
    if history:
        save_to_file(history)
    else:
        print("⚠️ No data found. The API might be down or parameters are too strict.")
