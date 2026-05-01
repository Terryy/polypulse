import json
import os
from datetime import datetime, timedelta, timezone

import requests

# --- CONFIGURATION ---
MIN_TRADE_USD = int(os.getenv("POLYPULSE_MIN_TRADE_USD", "100"))
DAYS_TO_BACKFILL = int(os.getenv("POLYPULSE_ARCHIVE_DAYS", "365"))
MAX_TRADES = int(os.getenv("POLYPULSE_MAX_TRADES", "10000"))
DATA_API_URL = "https://data-api.polymarket.com/trades"

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
DATA_PATH = os.path.join(ROOT_DIR, "data", "whales.json")


def utc_now():
    return datetime.now(timezone.utc)


def get_trade_amount_usd(trade):
    if trade.get("amountUSD") is not None:
        return float(trade.get("amountUSD") or 0)

    size = float(trade.get("size") or 0)
    price = float(trade.get("price") or 0)
    return abs(size * price)


def get_trade_id(trade):
    parts = [
        trade.get("transactionHash"),
        trade.get("asset"),
        str(trade.get("timestamp", "")),
        trade.get("side"),
    ]
    return ":".join(str(part) for part in parts if part) or str(trade.get("id"))


def normalize_trade(trade):
    return {
        "id": get_trade_id(trade),
        "timestamp": int(trade.get("timestamp") or 0),
        "user": {"id": trade.get("proxyWallet") or "0x00"},
        "market": {"question": trade.get("title") or "Unknown Market"},
        "outcomeIndex": trade.get("outcomeIndex"),
        "outcome": trade.get("outcome"),
        "amountUSD": f"{get_trade_amount_usd(trade):.2f}",
        "size": trade.get("size"),
        "price": trade.get("price"),
        "type": trade.get("side"),
        "slug": trade.get("slug"),
        "eventSlug": trade.get("eventSlug"),
        "transactionHash": trade.get("transactionHash"),
    }


def fetch_history():
    start_time = int((utc_now() - timedelta(days=DAYS_TO_BACKFILL)).timestamp())
    print("Connecting to Polymarket Data API...")

    params = {
        "limit": min(MAX_TRADES, 10000),
        "offset": 0,
        "takerOnly": "true",
        "filterType": "CASH",
        "filterAmount": MIN_TRADE_USD,
        "after": start_time,
    }
    response = requests.get(DATA_API_URL, params=params, timeout=30)
    response.raise_for_status()

    payload = response.json()
    if not isinstance(payload, list):
        raise RuntimeError(f"Unexpected Data API payload: {payload}")

    trades = [normalize_trade(trade) for trade in payload]
    filtered_trades = [
        trade for trade in trades
        if trade["timestamp"] >= start_time and float(trade["amountUSD"]) >= MIN_TRADE_USD
    ]
    print(f"Found {len(filtered_trades)} trades.")
    return filtered_trades


def atomic_write_json(path, payload):
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    os.replace(tmp_path, path)


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
            "source": "Polymarket Data API /trades",
        },
        "trades": trades,
    }

    if error:
        payload["meta"]["error"] = str(error)[:500]

    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    atomic_write_json(DATA_PATH, payload)
    print(f"Saved {len(trades)} trades to {DATA_PATH}")


if __name__ == "__main__":
    try:
        history = fetch_history()
        save_trades(history)
    except Exception as exc:
        print(f"Backfill error: {exc}")
        save_trades([], status="error", error=exc)
