import requests
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

API_KEY = os.getenv("FINNHUB_API_KEY")

import streamlit as st

@st.cache_data(ttl=86400) # Cache for 24 hours
def get_all_tickers():
    # Load 1000 Indian NSE tickers from local cache
    global_stocks = []
    try:
        if os.path.exists("data/indian_tickers.csv"):
            with open("data/indian_tickers.csv", "r", encoding="utf-8") as f:
                content = f.read()
                # Slicing at 1000 explicitly just in case
                global_stocks = [s.strip() for s in content.split(",") if s.strip()][:1000]
    except Exception as e:
        print(f"Could not load large Indian dataset: {e}")

    # Fallback list if the file didn't exist
    if not global_stocks:
        global_stocks = [
            "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", 
            "HINDUNILVR.NS", "SBIN.NS", "BHARTIARTL.NS", "ITC.NS", "KOTAKBANK.NS",
            "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS"
        ]

    url = "https://finnhub.io/api/v1/stock/symbol"
    params = {"exchange": "US", "token": API_KEY}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            # Extract common stock tickers
            symbols = [item['symbol'] for item in data if item.get('type') == 'Common Stock']
            if symbols:
                global_stocks.extend(symbols)
                return sorted(list(set(global_stocks)))
    except Exception as e:
        print(f"Error fetching symbols: {e}")
        
    # Standard emergency fallback list
    fallback = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX", "AMD", "SPY"]
    
    global_stocks.extend(fallback)
    return sorted(list(set(global_stocks)))

def fetch_stock_data(symbol="AAPL"):
    file_path = f"data/{symbol}.csv"

    # ✅ Load from cache if exists
    if os.path.exists(file_path):
        try:
            df_cached = pd.read_csv(file_path, parse_dates=["Date"])
            if not df_cached.empty:
                print(f"Loading cached data for {symbol}")
                return df_cached
            else:
                os.remove(file_path)
        except Exception:
            os.remove(file_path)

    print(f"Fetching data from yfinance for {symbol}")
    import yfinance as yf
    
    try:
        ticker = yf.Ticker(symbol)
        df_yf = ticker.history(period="1y")
    except Exception as e:
        raise Exception(f"Failed to fetch data from yfinance for {symbol}: {e}")
        
    if df_yf.empty:
        raise Exception(f"No historical price data found for ticker '{symbol}'. It may be delisted or simply invalid on Yahoo Finance.")
        
    df_yf.reset_index(inplace=True)
    if 'Date' in df_yf.columns:
        df_yf['Date'] = pd.to_datetime(df_yf['Date']).dt.tz_localize(None)
    
    df = pd.DataFrame({
        "Date": df_yf["Date"],
        "Open": df_yf["Open"],
        "High": df_yf["High"],
        "Low": df_yf["Low"],
        "Close": df_yf["Close"],
        "Volume": df_yf["Volume"]
    })

    df.sort_values("Date", inplace=True)

    # ✅ Save cache
    os.makedirs("data", exist_ok=True)
    df.to_csv(file_path, index=False)

    return df