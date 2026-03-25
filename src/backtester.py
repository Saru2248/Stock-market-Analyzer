import pandas as pd
import numpy as np
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "stock_analyzer.db")

def calculate_max_drawdown(equity_curve):
    """Calculate maximum peak-to-trough decline as a percentage."""
    rolling_max = equity_curve.cummax()
    drawdown = equity_curve / rolling_max - 1.0
    return drawdown.min()

def calculate_sharpe_ratio(returns, risk_free_rate=0.0):
    """Calculate annualized Sharpe Ratio based on daily returns."""
    if returns.std() == 0:
        return 0.0
    return (returns.mean() - risk_free_rate) / returns.std() * np.sqrt(252)

def store_backtest_results(ticker, strategy_name, start_date, end_date, initial_cap, final_cap, return_pct):
    """Stores the execution log parameters natively into the SQLite backtests table."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM symbols WHERE ticker=?", (ticker,))
        row = cursor.fetchone()
        
        if not row:
            # If the specific queried symbol was not pre-populated in SQL, just ignore database logging.
            return
            
        symbol_id = row[0]
        
        cursor.execute('''
            INSERT INTO backtests (strategy_name, symbol_id, start_date, end_date, initial_capital, final_capital, return_pct)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (strategy_name, symbol_id, start_date, end_date, initial_cap, final_cap, return_pct))
        
        conn.commit()
    except Exception as e:
        print(f"Error persisting backtest results to local database: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

def run_backtest(df, ticker, initial_capital=10000.0, commission_pct=0.001):
    """
    Simulates trading the pre-computed signals traversing the timeline constraints.
    Applies compounding transaction fees explicitly yielding an equivalent Equity Curve.
    """
    if 'Signal' not in df.columns:
        return None
        
    cash = initial_capital
    position = 0.0
    equity_curve = []
    
    for idx, row in df.iterrows():
        signal = row['Signal']
        price = row['Close']
        
        # Golden Cross -> BUY ALL constraint
        if signal == "BUY" and cash > 0:
            cost = cash * commission_pct
            investable = cash - cost
            position = investable / price
            cash = 0.0
            
        # Death Cross -> SELL ALL constraint
        elif signal == "SELL" and position > 0:
            revenue = position * price
            cost = revenue * commission_pct
            cash = revenue - cost
            position = 0.0
            
        # Mark to market equity per tick
        current_equity = cash + (position * price)
        equity_curve.append(current_equity)

    df['Equity'] = equity_curve
    df['Daily_Return'] = df['Equity'].pct_change().fillna(0)
    
    # Extract Analytics
    final_capital = df['Equity'].iloc[-1]
    return_pct = ((final_capital - initial_capital) / initial_capital) * 100
    max_dd = calculate_max_drawdown(df['Equity']) * 100
    sharpe = calculate_sharpe_ratio(df['Daily_Return'])
    
    start_str = df['Date'].iloc[0].strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(df['Date'].iloc[0]) else None
    end_str = df['Date'].iloc[-1].strftime('%Y-%m-%d %H:%M:%S') if pd.notnull(df['Date'].iloc[-1]) else None
    
    # Store Database Archival log
    store_backtest_results(ticker, "SMA_20_50_Cross", start_str, end_str, initial_capital, final_capital, return_pct)
    
    return {
        "initial_capital": initial_capital,
        "final_capital": final_capital,
        "return_pct": return_pct,
        "max_drawdown": max_dd,
        "sharpe_ratio": sharpe,
        "df": df
    }
