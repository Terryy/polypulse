import json
import os
from datetime import datetime, timedelta, timezone

import requests

# --- CONFIGURATION ---
# Keep the feed active enough to prove the scanner is working, while the UI still
# highlights larger trades with whale tiers.
MIN_TRADE_USD = int(os.getenv("POLYPULSE_MIN_TRADE_USD", "100"))
LOOKBACK_HOURS = int(os.getenv("POLYPULSE_LOOKBACK_HOURS", "24"))
ARCHIVE_DAYS = int(os.getenv("POLYPULSE_ARCHIVE_DAYS", "30"))
MAX_TRADES = int(os.getenv("POLYPULSE_MAX_TRADES", "2000"))
GRAPH_URL = "https://api.goldsky.com/api/public/project_cl6mb8i9h0003e201j6li0diw/subgraphs/polymarket/prod/gn"

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


def fetch_new_trades():
    start_time = int((utc_now() - timedelta(hours=LOOKBACK_HOURS)).timestamp())

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

    response = requests.post(GRAPH_URL, json={"query": query}, timeout=20)
    response.raise_for_status()

    payload = response.json()
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])

    trades = payload.get("data", {}).get("fpmmTrades", [])
    return [normalize_trade(trade) for trade in trades]


def prune_archive(trades):
    cutoff = int((utc_now() - timedelta(days=ARCHIVE_DAYS)).timestamp())
    recent_trades = [trade for trade in trades if int(trade.get("timestamp", 0)) >= cutoff]
    recent_trades.sort(key=lambda trade: int(trade.get("timestamp", 0)), reverse=True)
    return recent_trades[:MAX_TRADES]


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
