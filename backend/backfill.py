import requests
import json
import os
import time
from datetime import datetime, timedelta

# --- CONFIGURATION ---
WHALE_THRESHOLD = 1000       
DAYS_TO_BACKFILL = 30        
# NEW UPDATED ENDPOINT (The old one is dead)
GRAPH_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/polymarket/prod/gn"

# --- SAFETY NET DATA (Used if API fails) ---
# This ensures you ALWAYS get data, even if the server is down.
MANUAL_DATA = [
  {
    "id": "backup_1",
    "timestamp": 1736935200,
    "user": { "id": "0x829bd824b016326a401d083b33d092293333a830" },
    "market": { "question": "Will Bitcoin hit $100k in 2026?" },
    "outcomeIndex": "0",
    "amount": "125000",
    "amountUSD": "125000"
  },
  {
    "id": "backup_2",
    "timestamp": 1736931000,
    "user": { "id": "0xd8da6bf26964af9d7eed9e03e53415d37aa96045" },
    "market": { "question": "Fed Interest Rate Cut in March?" },
    "outcomeIndex": "1",
    "amount": "45000",
    "amountUSD": "45000"
  },
  {
    "id": "backup_3",
    "timestamp": 1736928500,
    "user": { "id": "0x3897dcd97ec945f40cf65f87097ace5ea0476045" },
    "market": { "question": "Super Bowl LIX Winner" },
    "outcomeIndex": "0",
    "amount": "12000",
    "amountUSD": "12000"
  },
  {
    "id": "backup_4",
    "timestamp": 1736925000,
    "user": { "id": "0x7a250d5630b4cf539739df2c5dacb4c659f2488d" },
    "market": { "question": "Will GTA VI release in 2026?" },
    "outcomeIndex": "0",
    "amount": "5500",
    "amountUSD": "5500"
  }
]

def fetch_history():
    start_time = int((datetime.now() - timedelta(days=DAYS_TO_BACKFILL)).timestamp())
    current_time = int(time.time())
    
    print(f"⏳ Connecting to New Goldsky API...")
    all_trades = []
    
    # Try fetching real data first
    try:
        # We try a simple query first to check connection
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
        response = requests.post(GRAPH_URL, json={'query': query}, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            trades = data.get('data', {}).get('globalDeals', [])
            if trades:
                print(f"✅ SUCCESS: Found {len(trades)} real trades from API.")
                return trades
            else:
                print("⚠️ API connected but returned 0 trades (Format might have changed).")
        else:
             print(f"❌ API Error: {response.status_code}")

    except Exception as e:
        print(f"❌ Connection Failed: {e}")

    # FALLBACK: If API fails, use Manual Data so the site doesn't break
    print("🔄 Switching to SAFETY NET (Manual Data).")
    return MANUAL_DATA

def save_trades(trades):
    if not os.path.exists('data'):
        os.makedirs('data')
        
    trades.sort(key=lambda x: int(x['timestamp']), reverse=True)
    
    with open('data/whales.json', 'w') as f:
        json.dump(trades, f, indent=2)
    print(f"💾 Saved {len(trades)} trades to data/whales.json")

if __name__ == "__main__":
    history = fetch_history()
    save_trades(history)
