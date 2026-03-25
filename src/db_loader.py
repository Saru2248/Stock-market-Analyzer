import sqlite3
import yfinance as yf
import pandas as pd
import os
from datetime import datetime

# Set Database Path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "stock_analyzer.db")

def get_db_connection():
    """Establish and return a connection to the SQLite database."""
    if not os.path.exists(DB_PATH):
        raise Exception(f"Database not found at {DB_PATH}. Please run database.py first.")
    return sqlite3.connect(DB_PATH)

def get_or_create_symbol(conn, ticker, name="Unknown", exchange="Unknown"):
    """Inserts a symbol if it doesn't exist and returns its primary key ID."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO symbols (ticker, name, exchange)
        VALUES (?, ?, ?)
    ''', (ticker, name, exchange))
    conn.commit()
    
    # Retrieve the id for the symbol
    cursor.execute('SELECT id FROM symbols WHERE ticker = ?', (ticker,))
    return cursor.fetchone()[0]

def load_and_upsert_candles(ticker, period="2y", interval="1d"):
    """
    Downloads candlestick data via yfinance and heavily upserts into the SQLite database.
    Prevents duplicates and updates live unclosed daily candles safely using ON CONFLICT.
    """
    print(f"Fetching {period} of {interval} data for {ticker} via yfinance...")
    stock = yf.Ticker(ticker)
    
    # Fetch historical data
    df = stock.history(period=period, interval=interval)
    
    if df.empty:
        print(f"⚠️ No historical data found for {ticker}.")
        return 0

    conn = get_db_connection()
    
    # Attempt to grab some light metadata via fast-info (fallback safely if Yahoo rate limits)
    try:
        # Avoid heavy stock.info to prevent slowdowns on massive lists
        name = stock.info.get('shortName', ticker)
        exchange = stock.info.get('exchange', 'Unknown')
    except Exception:
        name = ticker
        exchange = 'Unknown'

    # Map the textual Ticker to its Database ID
    symbol_id = get_or_create_symbol(conn, ticker, name, exchange)
    
    # Standardize DataFrame
    df.reset_index(inplace=True)
    date_col = 'Date' if 'Date' in df.columns else 'Datetime'
    
    records_upserted = 0
    cursor = conn.cursor()
    
    for _, row in df.iterrows():
        # Standardize SQLite datetime format
        dt_str = row[date_col].strftime('%Y-%m-%d 00:00:00') if interval == '1d' else row[date_col].strftime('%Y-%m-%d %H:%M:%S')
        
        # SQLite Upsert Architecture
        # This inserts the row. If the exact date for this symbol already exists, it forcefully updates the close/high/low/etc!
        cursor.execute('''
            INSERT INTO candles (symbol_id, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(symbol_id, date) DO UPDATE SET
                open=excluded.open,
                high=excluded.high,
                low=excluded.low,
                close=excluded.close,
                volume=excluded.volume
        ''', (
            symbol_id,
            dt_str,
            float(row['Open']),
            float(row['High']),
            float(row['Low']),
            float(row['Close']),
            int(row['Volume'])
        ))
        records_upserted += 1
        
    conn.commit()
    conn.close()
    
    print(f"✅ Successfully upserted {records_upserted} candles for {ticker} into the local database.")
    return records_upserted

if __name__ == "__main__":
    # Test execution: Load up 3 distinctive globally traded test stocks dynamically
    print("Initiating Pipeline Batch Job...\n" + "-"*35)
    test_symbols = ["AAPL", "NVDA", "RELIANCE.NS", "TSLA"]
    for sym in test_symbols:
        load_and_upsert_candles(sym, period="2y")
    print("-" * 35 + "\nPipeline Engine Complete!")
