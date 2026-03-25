import sqlite3
import os

# Define the local database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "stock_analyzer.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Symbols Table (Lookup base)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS symbols (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT UNIQUE NOT NULL,
        name TEXT,
        exchange TEXT
    )
    ''')

    # 2. Candles Table (OHLCV Time-Series Price Data)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS candles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol_id INTEGER NOT NULL,
        date DATETIME NOT NULL,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        FOREIGN KEY (symbol_id) REFERENCES symbols (id),
        UNIQUE(symbol_id, date) 
    )
    ''')
    
    # 3. Indicators Table (Pre-calculated/Stored AI metrics & technicals)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS indicators (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candle_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        value REAL,
        FOREIGN KEY (candle_id) REFERENCES candles (id)
    )
    ''')

    # 4. Backtests Table (Simulated Trading Logs)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS backtests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        strategy_name TEXT NOT NULL,
        symbol_id INTEGER NOT NULL,
        start_date DATETIME,
        end_date DATETIME,
        initial_capital REAL,
        final_capital REAL,
        return_pct REAL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (symbol_id) REFERENCES symbols (id)
    )
    ''')

    # 5. Portfolio Transactions Table (User Trading execution log)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS portfolio_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol_id INTEGER NOT NULL,
        transaction_type TEXT NOT NULL CHECK(transaction_type IN ('BUY', 'SELL')),
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        transaction_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (symbol_id) REFERENCES symbols (id)
    )
    ''')

    # 6. Alerts Table (Monitoring configurations)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol_id INTEGER NOT NULL,
        target_price REAL,
        indicator_name TEXT,
        condition TEXT NOT NULL CHECK(condition IN ('ABOVE', 'BELOW', 'CROSSES')),
        status TEXT DEFAULT 'ACTIVE' CHECK(status IN ('ACTIVE', 'TRIGGERED', 'CANCELLED')),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (symbol_id) REFERENCES symbols (id)
    )
    ''')

    # Create Indexes for massively faster lookup times on heavy tables
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_candles_symbol ON candles(symbol_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_candles_date ON candles(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_indicators_candle ON indicators(candle_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_transactions_symbol ON portfolio_transactions(symbol_id)')

    conn.commit()
    conn.close()
    print(f"Database successfully structured and initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
