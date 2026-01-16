# 🐋 PolyPulse | Whale Watcher

**Real-time detection of high-conviction trades on Polymarket.**

PolyPulse is an automated market surveillance tool that monitors the Polymarket ecosystem 24/7. It detects sudden capital inflows ("Whales") and visualizes them in a live dashboard, helping traders spot smart money movements and potential insider activity before the wider market reacts.

**[🔴 Live Dashboard Link](https://terryy.github.io/polypulse/)**

---

## ⚡ Features

* **Real-Time Surveillance:** Scans the Polymarket Activity Subgraph every 5 minutes.
* **Whale Classification:** Automatically tags trades based on size (Minnow to Leviathan).
* **Sentiment Analysis:** Intelligently colors trades as **BULLISH** (Green) or **BEARISH** (Red) based on whether the user is buying "Yes" or selling "No".
* **30-Day Archive:** Maintains a rolling history log of abnormal movements to track trends over time.
* **Zero-Maintenance:** Runs entirely on **GitHub Actions** (Backend) and **GitHub Pages** (Frontend). No expensive servers required.

---

## 📊 Whale Tier Definitions

PolyPulse categorizes trades into four tiers to filter noise from signal:

| Badge | Tier Name | Trade Size (USD) | Description |
| :--- | :--- | :--- | :--- |
| 🦖 | **LEVIATHAN** | **> $50,000** | Market Makers or High-Conviction Insiders. Often moves the price immediately. |
| 🐋 | **WHALE** | **$10,000 - $50k** | Serious capital. Notable conviction that warrants attention. |
| 🦈 | **SHARK** | **$1,000 - $10k** | Aggressive traders. Common but significant in lower-liquidity markets. |
| 🐟 | **MINNOW** | **< $1,000** | Retail activity. Used for "debug mode" or tracking retail sentiment. |

---

## 🛠️ Tech Stack

This project uses a "Flat Data" architecture to remain 100% free and open-source.

* **Frontend:** Vanilla HTML5 + Tailwind CSS (via CDN). No build step required.
* **Backend:** Python 3.9 (Requests, JSON handling).
* **Data Source:** [Goldsky Subgraph](https://goldsky.com/) (Polymarket Official Data).
* **Automation:** GitHub Actions (Cron job runs every 5 minutes).
* **Database:** A simple JSON file (`data/whales.json`) that acts as a flat database.

---

## 🚀 Local Setup (For Developers)

If you want to run this on your own machine:

1.  **Clone the repo**
    ```bash
    git clone [https://github.com/Terryy/polypulse.git](https://github.com/Terryy/polypulse.git)
    cd polypulse
    ```

2.  **Install Python Dependencies**
    ```bash
    pip install -r backend/requirements.txt
    ```

3.  **Run the Scanner Manually**
    ```bash
    python backend/main.py
    ```
    *This will generate a `data/whales.json` file locally.*

4.  **Open the Dashboard**
    Simply double-click `index.html` to open it in your browser.

---

## ⚠️ Disclaimer

**This tool is for informational purposes only.**
The data provided by PolyPulse does not constitute financial advice. Cryptocurrency and prediction markets involve high risk. "Whale" movements can be misleading, manipulative, or simply wrong. Always do your own research (DYOR).

---

© 2026 PolyPulse Project. Open Source.
