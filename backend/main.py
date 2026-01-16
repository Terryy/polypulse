import requests
import json
import os
from datetime import datetime

# --- CONFIGURATION ---
MIN_USD_THRESHOLD = 5000  # Only save trades larger than $5,000 #old value
MIN_USD_THRESHOLD = 10    # New value (for testing)
OUTPUT_FILE = "data/whales.json"

# Polymarket APIs
CLOB_URL = "https://data-api.polymarket.com/trades"
GAMMA_URL = "https://gamma-api.polymarket.com/markets"

def get_market_details(token_id):
    """Fetches human-readable title for a given token ID"""
    try:
        # We query Gamma to find the market that matches this token
        # Note: This is a simplified lookup. 
        resp = requests.get(f"{GAMMA_URL}?clob_token_id={token_id}")
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0:
                return {
                    "question": data[0].get("question", "Unknown Market"),
                    "slug": data[0].get("slug", ""),
                    "icon": data[0].get("icon", "")
                }
    except Exception as e:
        print(f"Warning: Could not fetch details for {token_id}: {e}")
    
    return {"question": "Unknown Market", "slug": "", "icon": ""}

def fetch_and_filter():
    print("--- PolyPulse: Scanning the Ocean ---")
    
    # 1. Fetch recent trades (last 50)
    params = {"limit": 50, "taker_only": "true"}
    try:
        r = requests.get(CLOB_URL, params=params)
        trades = r.json()
    except Exception as e:
        print(f"Critical Error fetching trades: {e}")
        return

    whale_sightings = []

    for trade in trades:
        size = float(trade.get('size', 0))
        price = float(trade.get('price', 0))
        usd_value = size * price

        # 2. Filter: Is it a Whale?
        if usd_value >= MIN_USD_THRESHOLD:
            print(f"🐳 Whale found: ${usd_value:,.2f}")
            
            # 3. Enrich: Get the real question name
            details = get_market_details(trade.get('asset_id'))
            
            sighting = {
                "id": trade.get('match_id'),
                "time": trade.get('timestamp'),
                "question": details['question'],
                "outcome": trade.get('outcome_index'), # 0 usually YES, 1 usually NO
                "side": trade.get('side'),             # BUY or SELL
                "size_usd": round(usd_value, 2),
                "price": price,
                "maker_address": trade.get('maker_address'),
                "icon": details['icon']
            }
            whale_sightings.append(sighting)

    # 4. Save to JSON
    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(whale_sightings, f, indent=2)
    print(f"--- Saved {len(whale_sightings)} whales to {OUTPUT_FILE} ---")

if __name__ == "__main__":
    fetch_and_filter()
