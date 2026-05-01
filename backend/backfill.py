import json
import os
from datetime import datetime, timedelta, timezone

import requests

# --- CONFIGURATION ---
MIN_TRADE_USD = int(os.getenv("POLYPULSE_MIN_TRADE_USD", "100"))
DAYS_TO_BACKFILL = int(os.getenv("POLYPULSE_ARCHIVE_DAYS", "30"))
MAX_TRADES = int(os.getenv("POLYPULSE_MAX_TRADES", "2000"))
GRAPH_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/polymarket/prod/gn"

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
DATA_PATH = os.path.join(ROOT_DIR, "data", "whales.json")


def utc_now():
    return datetime.now(timezone.utc)


def normalize_trade(trade):
    return {
        "id": trade["id"],
        "timestamp": int(trade["creationTimestamp"]),
        "user": trade.get("creator") or {"id": "0x00"},
        "market": {"question": trade.get("title") or "Unknown Market"},
        "outcomeIndex": trade.get("outcomeIndex"),
        "amountUSD": trade.get("amountUSD") or "0",
        "type": trade.get("type"),
    }


def fetch_history():
    start_time = int((utc_now() - timedelta(days=DAYS_TO_BACKFILL)).timestamp())
    print("Connecting to Polymarket subgraph...")

    query = f"""
    {{
      fpmmTrades(
        first: 1000,
        orderBy: creationTimestamp,
        orderDirection: desc,
        where: {{ creationTimestamp_gt: {start_time}, amountUSD_gt: {MIN_TRADE_USD} }}
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

    response = requests.post(GRAPH_URL, json={"query": query}, timeout=30)
    response.raise_for_status()

    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])

    trades = payload.get("data", {}).get("fpmmTrades", [])
    print(f"Found {len(trades)} trades.")
    return [normalize_trade(trade) for trade in trades]


def save_trades(trades, status="ok", error=None):
    trades.sort(key=lambda trade: int(trade.get("timestamp", 0)), reverse=True)
    trades = trades[:MAX_TRADES]
    checked_at = utc_now().isoformat().replace("+00:00", "Z")

    payload = {
        "meta": {
            "status": status,
            "last_checked_at": checked_at,
            "lookback_hours": DAYS_TO_BACKFILL * 24,
            "archive_days": DAYS_TO_BACKFILL,
            "min_trade_usd": MIN_TRADE_USD,
            "fetched_count": len(trades),
            "stored_count": len(trades),
            "source": "Goldsky Polymarket subgraph",
        },
        "trades": trades,
    }

    if error:
        payload["meta"]["error"] = str(error)[:500]

    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    print(f"Saved {len(trades)} trades to {DATA_PATH}")


if __name__ == "__main__":
    try:
        history = fetch_history()
        save_trades(history)
    except Exception as exc:
        print(f"Backfill error: {exc}")
        save_trades([], status="error", error=exc)
