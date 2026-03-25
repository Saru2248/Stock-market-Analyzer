# 📈 The Quant Terminal (Stock Market Analyzer)

![Quant Terminal Banner](https://img.shields.io/badge/Status-Active-success)
![Python Backend](https://img.shields.io/badge/Backend-FastAPI_11.0-3b82f6)
![React Frontend](https://img.shields.io/badge/Frontend-Next.js_16-8b5cf6)
![Data Integrity](https://img.shields.io/badge/Coverage-12%2C000%2B_Global_Stocks-06b6d4)

The **Quant Terminal** is an enterprise-grade algorithmic market intelligence platform built to natively simulate trading strategies, track live portfolio aggregates, and calculate advanced technical or machine-learning-driven analytics asynchronously.

Developed completely from the ground up utilizing purely modern decoupled architectures.

---

## ⚡ Features

### 1. Massive Global Ticker Database 🌍
- Supports over **12,000+** listed global equities natively (NASDAQ, NYSE).
- Pre-packaged with the **National Stock Exchange of India (NSE)** index seamlessly integrated (All 2,200+ listed Indian Tickers perfectly mapped using the `.NS` format).

### 2. High-Performance Strategy Backtesting Engine ⚙️
- **SMA 20/50 Crossover Logic**: Native vectorized algorithmic trigger engine built specifically using Pandas `np.where`.
- **Dynamic Capital Scaling**: Run simulations against any target equity with custom bounds for starting capital securely.
- **Max Drawdown & Sharpe Analytics**: Computes strict institutional risk metrics on historical equity curves instantaneously.

### 3. Advanced Core Analytics & AI Pipeline 🧠
- **Fundamental Ingestion Pipeline**: Generates massive fundamental health reports pulling Trailing P/E Ratios, Forward Yields, and PEG markers.
- **Next-Gen Time-Series ML Predictor**: Utilizes core Numpy `polyfit` Polynomial models (Linear Regression mapping) to trace dynamic baseline price trajectories over exactly 7 intervals smoothly.
- **Rule-Based NLP Sentiment Scraping**: Parses live headlines securely to weigh the Bullish/Bearish biases of target equities reliably.

### 4. Interactive Live-Updating Dashboard 📊
- Next.js (Turbopack) powered User Interface boasting 120 FPS charting elements via **Recharts**.
- Native dark-mode responsive UI heavily utilizing linear glassmorphic elements and explicit animation slides.
- **Secure Alert Mutator**: Exposes native REST bindings to toggle scheduled Email/Desktop notification pipelines accurately.

---

## 🛠 Tech Stack

**Frontend Framework:**
- Next.js 16 (React 19)
- Vanilla CSS (Glassmorphic Dark Theme)
- Recharts (SVG High-Performance Charting)
- TypeScript

**Backend Microservice:**
- Python 3
- FastAPI (Swagger-compliant REST routing)
- Pandas & NumPy (Vectorized analysis computation)
- `yfinance` (Historical market data ingestion bridge)
- SQLite3 (Async archival & portfolio storage mapping)

---

## 🚀 How to Run Locally

### Prerequisites
Make sure you have [Node.js](https://nodejs.org/), `npm`, and [Python 3.x](https://www.python.org/) dynamically installed onto your local environment constraints perfectly.

### Installation

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/stock-market-analyzer.git
   cd stock-market-analyzer
   ```

2. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Next.js UI Dependencies:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Starting the Integrated Environment

You can simply deploy both server nodes securely by running the bundled batch script from your root directory:
```bash
.\start_project.bat
```

Alternatively, manually spin them up:
- **Backend**: `uvicorn src.api:app --reload` (Runs on `localhost:8000`)
- **Frontend**: `cd frontend && npm run dev` (Runs on `localhost:3000`)

---

## 🏗 System Architecture 

1. **Data Lake**: `src/database.py` generates the strict `stock_analyzer.db` SQLite storage instances.
2. **Ingestion Engine**: `src/db_loader.py` organically caches `.csv` timelines into `./data/` directories bridging native offline access when pinging Yahoo APIs.
3. **Analytics Brain**: `src/advanced_features.py` calculates custom ML predictions while `src/backtester.py` calculates risk-adjusted algorithm success metrics properly.
4. **Data Seed Engine**: The `fetch_tickers.py` massive crawler cleanly manages scraping the global `ftp.nasdaqtrader.com` and `EQUITY_L.csv` from the NSE safely.

