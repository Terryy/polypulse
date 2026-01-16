import requests
import json
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
WHALE_THRESHOLD = 10000  # Whales must be > $10,000
DAYS_TO_LOOK_BACK = 30   # Scan the last 30 days
GRAPH_URL = "https://subgraph-matic.poly.market/subgraphs/name/TokenUnion/polymarket"

def fetch_historical_whales():
    # Calculate timestamp for 30 days ago
    start_time = int((datetime.now() - timedelta(days=DAYS_TO_LOOK_BACK)).timestamp())
    
    print(f"⏳ Scanning last {DAYS_TO_LOOK_BACK} days (since timestamp {start_time})...")

    # Query: Get the largest 100 trades from the last 30 days
    # We sort by amountUSD to ensure we get the REAL whales, not just recent small trades.
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
        data = response.json()
        
        trades = data.get('data', {}).get('globalDeals', [])
        print(f"✅ Found {len(trades)} historical whale trades.")
        return trades
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return []

def save_whales(trades):
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Sort by time (newest first) so the dashboard displays them correctly
    trades.sort(key=lambda x: int(x['timestamp']), reverse=True)

    with open('data/whales.json', 'w') as f:
        json.dump(trades, f, indent=2)
    print("💾 Saved to data/whales.json")

if __name__ == "__main__":
    print("🦕 Starting 30-Day Historical Backfill...")
    whales = fetch_historical_whales()
    if whales:
        save_whales(whales)
    else:
        print("⚠️ No whales found. Check the threshold or API status.")
