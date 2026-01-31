Here is the raw text for your README file, split into two parts. You can copy each part and paste them into your file one after another.

**Part 1: Features and Tech Stack**

# 🐋 PolyPulse | Whale Watcher

**Real-time detection of high-conviction trades on Polymarket.**

PolyPulse is an automated market surveillance tool that detects and visualizes large trades ("Whales") on Polymarket in real-time. It runs 24/7 to help traders spot smart money movements before the wider market reacts.

**[🔴 Live Dashboard Link](https://terryy.github.io/polypulse/)**

---

## ⚡ Features

* **Real-Time Surveillance:** Scans the **Polymarket Main Subgraph** (`fpmmTrades`) every 5 minutes.
* **Whale Classification:** Tags trades based on size (Dolphin to Blue Whale).
* **Smart Sentiment:** Tags trades as **BET YES** (Green) or **BET NO** (Red).
* **30-Day Archive:** Maintains a history log of significant movements.
* **Zero-Maintenance:** Runs on **GitHub Actions** and **GitHub Pages**. No servers required.

---

## 📊 Whale Tier Definitions

PolyPulse categorizes trades into four tiers:

| Badge | Tier Name | Trade Size (USD) | Description |
| --- | --- | --- | --- |
| 🐋 | **BLUE WHALE** | **> $50,000** | Market Makers or High-Conviction Insiders. |
| 🐳 | **WHALE** | **$10,000 - $50k** | Serious capital. Notable conviction. |
| 🦈 | **SHARK** | **$5,000 - $10k** | Aggressive traders. Significant size. |
| 🐬 | **DOLPHIN** | **$1,000 - $5,000** | Active traders. Larger than retail size. |

*(Trades under $1,000 are filtered out as noise.)*

---

## 🛠️ Tech Stack

* **Frontend:** HTML5 + Tailwind CSS (via CDN).
* **Backend:** Python 3.9 (Requests, JSON).
* **Data Source:** [Goldsky Subgraph](https://goldsky.com/) (Polymarket Mainnet).
* **Automation:** GitHub Actions (Cron every 5 mins).
* **Database:** Flat JSON file (`data/whales.json`).

---

**Part 2: Setup and Disclaimer (Paste this right after Part 1)**

---

## 🚀 Local Setup (For Developers)

If you want to run this on your own machine:

### 1. Clone the repo

```bash
git clone https://github.com/Terryy/polypulse.git
cd polypulse

```

### 2. Install Python Dependencies

```bash
pip install -r backend/requirements.txt

```

### 3. Run the Scanner Manually

This connects to the API and generates `data/whales.json`.

```bash
python backend/main.py

```

### 4. Open the Dashboard

Double-click `index.html` to open it in your browser.

---

## 📦 Release & Publish

PolyPulse releases are tagged and published automatically via GitHub Actions.

### 1. Tag a Release

```bash
git tag vYYYY.MM.DD
git push origin vYYYY.MM.DD
```

### 2. Automated Publish

Pushing a `v*` tag creates a GitHub Release and deploys the latest site to GitHub Pages.

---

## ⚠️ Disclaimer

**This tool is for informational purposes only.**
The data provided by PolyPulse does not constitute financial advice. Cryptocurrency and prediction markets involve high risk. Always do your own research (DYOR).

---

© 2026 PolyPulse Project. Open Source.
