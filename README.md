# 🐋 PolyPulse | Whale Watcher

**Real-time detection of high-conviction trades on Polymarket.**

PolyPulse is an automated market surveillance tool that monitors the Polymarket ecosystem 24/7. It detects sudden capital inflows ("Whales") and visualizes them in a live dashboard, helping traders spot smart money movements and potential insider activity before the wider market reacts.

**[🔴 Live Dashboard Link](https://terryy.github.io/polypulse/)** *(Replace with your actual link)*

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
| 🐟 | **MINNOW** | **< $1,0
