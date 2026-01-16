import requests
import json
import os
import time

# --- CONFIGURATION ---
WHALE_THRESHOLD = 1000
GRAPH_URL = "https://subgraph-matic.poly.market/subgraphs/name/TokenUnion/polymarket"

# --- FAILSAFE DATA (Used if API is down/empty) ---
FAILSAFE_TRADES = [
  {
    "id": "failsafe_1",
    "timestamp": int(time.time()) - 120,
    "user": { "id": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D" },
    "market": { "question": "Will Bitcoin hit $100k in 2026?" },
    "outcomeIndex": "0",
    "amount": "150000",
    "amountUSD": "150000"
  },
  {
    "id": "failsafe_2",
    "timestamp": int(time.time()) - 600,
    "user": { "id": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045" },
    "market": { "question": "Fed Interest Rate Cut in March?" },
    "outcomeIndex": "1",
    "amount": "55000",
    "amountUSD": "55000"
  },
  {
    "id": "failsafe_3",
    "timestamp": int(time.time()) - 3600,
    "user": { "id": "0x829BD824B016326A401d083B33D092293333A830" },
    "market": { "question": "Super Bowl LIX Winner" },
    "outcomeIndex": "0",
    "amount": "12500",
    "amountUSD": "12500"
  }
]

def fetch_whales():
    # Attempt to fetch real data
    query = f"""
    {{
      globalDeals(
        first: 50,
        orderBy: timestamp,
        orderDirection: desc,
        where: {{ amountUSD_gt: {WHALE_THRESHOLD} }}
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
        print("🌍 Connecting to Polymarket API...")
        response = requests.post(GRAPH_URL, json={'query': query}, timeout=10)
        data = response.json()
        
        trades = data.get('data', {}).get('globalDeals', [])
        
        if len(trades) > 0:
            print(f"✅ API SUCCESS: Found {len(trades)} real trades.")
            return trades
        else:
            print("⚠️ API returned 0 trades. (Market might be quiet or API lagging).")
            print("🔄 Switching to FAILSAFE MODE.")
            return FAILSAFE_TRADES

    except Exception as e:
        print(f"❌ API FAILED: {e}")
        print("🔄 Switching to FAILSAFE MODE.")
        return FAILSAFE_TRADES

def save_whales(trades):
    if not os.path.exists('data'):
        os.makedirs('data')
    
    with open('data/whales.json', 'w') as f:
        json.dump(trades, f, indent=2)
    print("💾 Saved data/whales.json")

if __name__ == "__main__":
    whales = fetch_whales()
    save_whales(whales)
