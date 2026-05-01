# 🐋 PolyPulse | Whale Watcher

Real-time detection of notable Polymarket trades.

PolyPulse is an automated market surveillance dashboard that scans Polymarket trade activity, classifies larger trades by size, and publishes a static GitHub Pages feed. It is designed to show whether the scanner is alive even when no trades match the current listing rules.

[Live Dashboard](https://terryy.github.io/polypulse/)

## Features

- Trade surveillance via the public Polymarket Data API.
- Scheduled scanner runs on GitHub Actions every 5 minutes.
- Feed metadata shows the last scan time, scan status, lookback window, and listing threshold.
- Signal listing starts at $100 so the dashboard can show smaller activity when no larger trades are present.
- Larger trades are classified from Pulse through Blue Whale.
- Dashboard filters for tier and period: last day, last 7 days, last month, last year, or all stored trades.
- Lazy-loaded trade cards render 50 at a time.
- Static hosting on GitHub Pages with no server to maintain.

## Listing Rules

| Badge | Tier Name | Trade Size (USD) | Description |
| --- | --- | --- | --- |
| 🐋 | **BLUE WHALE** | **> $50,000** | Very large position. |
| 🐳 | **WHALE** | **$10,000 - $50,000** | Large high-conviction trade. |
| 🦈 | **SHARK** | **$5,000 - $10,000** | Significant active trader size. |
| 🐬 | **DOLPHIN** | **$1,000 - $5,000** | Larger than typical retail size. |
| • | **PULSE** | **$100 - $1,000** | Smaller signal shown so the feed does not look broken during quiet periods. |

The backend default listing threshold is controlled by `POLYPULSE_MIN_TRADE_USD` and currently defaults to `$100`.

## Tech Stack

- Frontend: HTML5 + Tailwind CSS via CDN.
- Backend: Python 3.9 with `requests`.
- Data Source: Polymarket Data API `/trades`.
- Automation: GitHub Actions cron.
- Data Store: Static JSON file at `data/whales.json`.

## Local Setup

```bash
git clone https://github.com/Terryy/polypulse.git
cd polypulse
pip install -r backend/requirements.txt
python backend/main.py
```

Then open `index.html` in your browser.

## Backfill

To rebuild the archive from the last year:

```bash
python backend/backfill.py
```

## Configuration

The scanner supports these environment variables:

| Variable | Default | Purpose |
| --- | ---: | --- |
| `POLYPULSE_MIN_TRADE_USD` | `100` | Minimum trade value to list. |
| `POLYPULSE_LOOKBACK_HOURS` | `24` | How far each scheduled scan looks back. |
| `POLYPULSE_ARCHIVE_DAYS` | `365` | How long to keep stored trades. |
| `POLYPULSE_MAX_TRADES` | `10000` | Maximum records stored in the JSON feed. |

## Release & Publish

PolyPulse releases are tagged and published automatically via GitHub Actions.

```bash
git tag vYYYY.MM.DD
git push origin vYYYY.MM.DD
```

Pushing a `v*` tag creates a GitHub Release and deploys the current site to GitHub Pages. Pushes to `main` also deploy the site.

## Disclaimer

This tool is for informational purposes only. The data provided by PolyPulse does not constitute financial advice. Cryptocurrency and prediction markets involve high risk. Always do your own research.

© 2026 PolyPulse Project. Open Source.
