import json
import os
from datetime import datetime, timedelta, timezone

import requests

# --- CONFIGURATION ---
# Keep the feed active enough to prove the scanner is working, while the UI still
# highlights larger trades with whale tiers.
MIN_TRADE_USD = int(os.getenv("POLYPULSE_MIN_TRADE_USD", "100"))
LOOKBACK_HOURS = int(os.getenv("POLYPULSE_LOOKBACK_HOURS", "24"))
ARCHIVE_DAYS = int(os.getenv("POLYPULSE_ARCHIVE_DAYS", "365"))
MAX_TRADES = int(os.getenv("POLYPULSE_MAX_TRADES", "10000"))
DATA_API_URL = "https://data-api.polymarket.com/trades"

BASE_DIR = os.path.dirname(__file__)
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
DATA_PATH = os.path.join(ROOT_DIR, "data", "whales.json")


def utc_now():
    return datetime.now(timezone.utc)


def load_existing_trades():
    if not os.path.exists(DATA_PATH):
        return []

    try:
        with open(DATA_PATH, "r") as f:
            payload = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict) and isinstance(payload.get("trades"), list):
        return payload["trades"]

    return []


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


def fetch_new_trades():
    start_time = int((utc_now() - timedelta(hours=LOOKBACK_HOURS)).timestamp())
    params = {
        "limit": 1000,
        "offset": 0,
        "takerOnly": "true",
        "filterType": "CASH",
        "filterAmount": MIN_TRADE_USD,
        "after": start_time,
    }

    response = requests.get(DATA_API_URL, params=params, timeout=20)
    response.raise_for_status()

    payload = response.json()
    if not isinstance(payload, list):
        raise RuntimeError(f"Unexpected Data API payload: {payload}")

    trades = [normalize_trade(trade) for trade in payload]
    return [trade for trade in trades if trade["timestamp"] >= start_time and float(trade["amountUSD"]) >= MIN_TRADE_USD]


def prune_archive(trades):
    cutoff = int((utc_now() - timedelta(days=ARCHIVE_DAYS)).timestamp())
    recent_trades = [trade for trade in trades if int(trade.get("timestamp", 0)) >= cutoff]
    recent_trades.sort(key=lambda trade: int(trade.get("timestamp", 0)), reverse=True)
    return recent_trades[:MAX_TRADES]


def atomic_write_json(path, payload):
    tmp_path = f"{path}.tmp"
    with open(tmp_path, "w") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    os.replace(tmp_path, path)


def write_database(trades, status, error=None, fetched_count=0):
    checked_at = utc_now().isoformat().replace("+00:00", "Z")
    payload = {
        "meta": {
            "status": status,
            "last_checked_at": checked_at,
            "lookback_hours": LOOKBACK_HOURS,
            "archive_days": ARCHIVE_DAYS,
            "min_trade_usd": MIN_TRADE_USD,
            "fetched_count": fetched_count,
            "stored_count": len(trades),
            "source": "Polymarket Data API /trades",
        },
        "trades": trades,
    }

    if error:
        payload["meta"]["error"] = str(error)[:500]

    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    atomic_write_json(DATA_PATH, payload)

    print(f"Database wrote {len(trades)} trades. Status: {status}. Checked: {checked_at}")


def update_database():
    existing_trades = load_existing_trades()

    try:
        new_trades = fetch_new_trades()
    except Exception as exc:
        print(f"API error: {exc}")
        write_database(prune_archive(existing_trades), status="error", error=exc, fetched_count=0)
        return

    trade_map = {trade["id"]: trade for trade in existing_trades if trade.get("id")}
    for trade in new_trades:
        trade_map[trade["id"]] = trade

    all_trades = prune_archive(list(trade_map.values()))
    status = "ok" if new_trades else "ok_no_new_trades"
    write_database(all_trades, status=status, fetched_count=len(new_trades))


if __name__ == "__main__":
    update_database()
