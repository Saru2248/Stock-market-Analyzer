from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import math

# Guarantee the local src directory is loaded accurately for custom module routing
sys.path.append(os.path.dirname(__file__))

from data_fetcher import fetch_stock_data
from indicators import add_moving_average, calculate_rsi, calculate_macd, calculate_bollinger_bands
from signals import generate_signals
from backtester import run_backtest
from db_loader import load_and_upsert_candles

# ── Load ticker database once at startup ─────────────────────────────────────
import json as _json
_TICKER_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "tickers.json")
try:
    with open(_TICKER_DB_PATH, encoding="utf-8") as f:
        _TICKER_DB = _json.load(f)
except Exception:
    _TICKER_DB = []

app = FastAPI(title="Stock Analyzer Core API", description="Microservice serving technical pipelines.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/tickers")
def get_tickers(q: str = ""):
    """Returns the static ticker database, optionally filtered by a query string (matches ticker or name)."""
    if not q:
        return {"status": "success", "data": _TICKER_DB}
    
    q_lower = q.lower()
    results = [t for t in _TICKER_DB if q_lower in t["ticker"].lower() or q_lower in t["name"].lower()]
    return {"status": "success", "data": results}

class RefreshRequest(BaseModel):
    ticker: str
    period: str = "2y"

@app.post("/refresh")
def refresh_data(req: RefreshRequest):
    """
    Executes an explicit downstream SQLite db_loader upsertion protocol bridging yfinance directly.
    Ideal for external cron triggers mapping nightly dataset synchronization.
    """
    try:
        count = load_and_upsert_candles(req.ticker, req.period, "1d")
        return {"status": "success", "ticker": req.ticker, "candles_upserted": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chart")
def get_chart_data(ticker: str):
    """
    Exposes raw cached technical dataset outputs directly dynamically computing SMAs, MAs, and RSI structures for arbitrary ticker targets instantly.
    """
    try:
        df = fetch_stock_data(ticker)
        df = add_moving_average(df)
        df = calculate_rsi(df)
        df = calculate_macd(df)
        df = calculate_bollinger_bands(df)
        
        # Data integrity mapping explicit NaNs uniformly resolving JSON errors 
        df = df.fillna(0)
        
        return {
            "status": "success",
            "ticker": ticker,
            "data": df.tail(252).to_dict(orient="records")  # Return last 252 days (1 trading year)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed compiling Chart Engine: {str(e)}")

@app.get("/backtest")
def get_backtest_stats(ticker: str, capital: float = 10000.0):
    """
    Triggers our robust SMA Cross Quant Engine pushing parameters, checking historical bounds natively computing yielding equity parameters perfectly recorded automatically into SQLite.
    """
    try:
        df = fetch_stock_data(ticker)
        df = add_moving_average(df)
        df = calculate_rsi(df)
        df = calculate_macd(df)
        df = calculate_bollinger_bands(df)
        df = generate_signals(df)
        
        bt_results = run_backtest(df, ticker, initial_capital=capital)
        if not bt_results:
            raise HTTPException(status_code=400, detail="Backtest failed: Check target asset liquidity or valid history limits.")
            
        # Clean mathematically void properties efficiently to resolve API type checks
        sharpe = 0.0 if math.isnan(bt_results["sharpe_ratio"]) else float(bt_results["sharpe_ratio"])
        
        return {
            "status": "success",
            "ticker": ticker,
            "starting_capital": bt_results["initial_capital"],
            "final_capital": bt_results["final_capital"],
            "return_pct": bt_results["return_pct"],
            "max_drawdown": bt_results["max_drawdown"],
            "sharpe_ratio": sharpe
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed Backtest Run: {str(e)}")

# ─── ADVANCED INTELLIGENCE FEATURES ─────────────────────────────────────────

from advanced_features import get_fundamentals, get_news_sentiment, generate_ai_forecast

@app.get("/intelligence/fundamentals")
def fetch_fundamentals(ticker: str):
    """Returns absolute truth core financial metrics."""
    return {"status": "success", "ticker": ticker, "data": get_fundamentals(ticker)}

@app.get("/intelligence/news")
def fetch_news_sentiment(ticker: str):
    """Returns top headlines alongside basic NLP sentiment scoring."""
    return {"status": "success", "ticker": ticker, "data": get_news_sentiment(ticker)}

@app.get("/intelligence/forecast")
def fetch_ai_forecast(ticker: str):
    """Generates an embedded Polynomial Regression ML forecast plotting future prices."""
    try:
        df = fetch_stock_data(ticker)
        forecast_pts = generate_ai_forecast(df, days=7)
        return {"status": "success", "ticker": ticker, "data": forecast_pts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── MOCK ALERTS ────────────────────────────────────────────────────────────

@app.post("/alerts/toggle")
def toggle_alerts(req: dict):
    """Mocks toggling the background alerter thread."""
    return {"status": "success", "message": f"Alerts for {req.get('ticker')} toggled {req.get('state')}."}


# manual reload


