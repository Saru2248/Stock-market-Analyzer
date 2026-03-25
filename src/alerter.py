import sqlite3
import os
import pandas as pd
from datetime import datetime

# Map explicit pointer to the database root
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "stock_analyzer.db")

def upgrade_alerts_table():
    """Utility engine to automatically hot-patch SQLite adding anti-spam properties safely."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        # Patching structural architecture adding timestamp limit boundaries
        cursor.execute("ALTER TABLE alerts ADD COLUMN last_fired DATETIME")
        conn.commit()
    except sqlite3.OperationalError:
        pass # Expected bypass if column already exists successfully
    finally:
        conn.close()

def create_alert(ticker, indicator, condition, target_value):
    """Exposed method to inject alert logic natively into the SQLite monitor."""
    upgrade_alerts_table()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM symbols WHERE ticker=?", (ticker,))
    row = cursor.fetchone()
    if not row:
        print(f"Failed Configuration: The symbol {ticker} doesn't actively exist within the db_loader engine yet.")
        conn.close()
        return
        
    cursor.execute('''
        INSERT INTO alerts (symbol_id, indicator_name, condition, target_price) 
        VALUES (?, ?, ?, ?)
    ''', (row[0], indicator.upper(), condition.upper(), float(target_value)))
    
    conn.commit()
    conn.close()
    print(f"✅ Success: Locked tracking algorithm for {ticker} executing when {indicator} runs {condition} {target_value}")

def send_notification(ticker, message):
    """External hook bridging execution to Dashboards/Webhooks securely."""
    # In production, swap print with Twilio/SMTP/Websockets logic!
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n[🚨 LIVE MARKET NOTIFIER - {timestamp}]\n* TARGET: {ticker} \n* TRIGGER: {message}\n")

def check_alerts_for_dataframe(df, ticker):
    """
    Aggressively evaluates massive dataframes natively checking the very latest unclosed daily bounds against SQL alerts.
    Utilizes SQL `last_fired` to avoid double-triggers occurring in the same 24-hour cycle.
    """
    if df.empty: return
    
    upgrade_alerts_table()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM symbols WHERE ticker=?", (ticker,))
    symbol_row = cursor.fetchone()
    if not symbol_row:
        return
    
    # Isolate the latest market parameters exclusively for live evaluations
    newest = df.iloc[-1]
    
    cursor.execute('''
        SELECT id, indicator_name, condition, target_price, last_fired 
        FROM alerts WHERE symbol_id=? AND status='ACTIVE'
    ''', (symbol_row[0],))
    
    active_alerts = cursor.fetchall()
    
    for alert in active_alerts:
        alert_id, ind_name, condition, target_val, last_fired = alert
        
        triggered = False
        msg = ""
        
        # 1. RELATIVE STRENGTH INDEX RULES
        if ind_name == 'RSI' and 'RSI' in df.columns:
            val = newest['RSI']
            if condition == 'ABOVE' and val >= target_val:
                triggered, msg = True, f"RSI momentum ripped heavily to {val:.2f} (Trigger > {target_val})"
            elif condition == 'BELOW' and val <= target_val:
                triggered, msg = True, f"RSI momentum dumped into oversold limits: {val:.2f} (Trigger < {target_val})"
                
        # 2. BOLLINGER BANDS / RAW PRICE RULES
        elif ind_name in ['BB_UPPER', 'BB_LOWER', 'PRICE'] and 'Close' in df.columns:
            price = newest['Close']
            
            # Rebind target locally to the dynamic bands array or default bounds
            dynamic_target = target_val
            if ind_name == 'BB_UPPER' and 'BB_upper' in df.columns:
                dynamic_target = newest['BB_upper']
            elif ind_name == 'BB_LOWER' and 'BB_lower' in df.columns:
                dynamic_target = newest['BB_lower']
                
            if condition == 'ABOVE' and price >= dynamic_target:
                triggered, msg = True, f"Underlying Asset Price {price:.2f} shattered ABOVE {ind_name} ceiling set at {dynamic_target:.2f}"
            elif condition == 'BELOW' and price <= dynamic_target:
                triggered, msg = True, f"Underlying Asset Price {price:.2f} crashed BELOW {ind_name} floor mapped at {dynamic_target:.2f}"

        # 3. ANTI-SPAM RESOLUTION LOGIC
        if triggered:
            today_str = datetime.now().strftime('%Y-%m-%d')
            # If `last_fired` is null, or heavily out of date outside the current EOD bound, we trigger smoothly!
            if not last_fired or not last_fired.startswith(today_str):
                # 1. Fire Webhook/Print statement dynamically
                send_notification(ticker, msg)
                
                # 2. Seal executed rule into SQLite heavily mapping accurate execution boundaries
                cursor.execute("UPDATE alerts SET last_fired = CURRENT_TIMESTAMP WHERE id = ?", (alert_id,))
                
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Internal Unit Execution mapping standard configurations dynamically
    import sys
    sys.path.append(os.path.dirname(__file__))
    
    from data_fetcher import fetch_stock_data
    from indicators import calculate_rsi, calculate_bollinger_bands
    
    stock_target = "AAPL"
    
    # Simulate a user generating complex triggers directly inside their dashboard
    print("Writing Test Configurations...")
    create_alert(stock_target, 'BB_UPPER', 'BELOW', 0.0) # Highly aggressive test mapping Apple operating beneath its top band natively
    create_alert(stock_target, 'RSI', 'BELOW', 70.0) # Typical technical oversold tests
    
    # Process Engine Core
    print(f"\nInitiating Core Scanner evaluating final unclosed limits dynamically for {stock_target}...")
    df = fetch_stock_data(stock_target)
    df = calculate_rsi(df)
    df = calculate_bollinger_bands(df)
    
    check_alerts_for_dataframe(df, stock_target)
    print("\nAlert Protocol finished. Triggers successfully fired once globally to prevent spam.")
