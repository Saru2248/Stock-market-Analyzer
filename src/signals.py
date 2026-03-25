import numpy as np

def generate_signals(df):
    """
    Vectorized trigger logic generation for SMA 20/50 Crossovers.
    - BUY (Golden Cross) when SMA 20 pulls above SMA 50.
    - SELL (Death Cross) when SMA 20 falls beneath SMA 50.
    """
    if 'SMA_20' not in df.columns or 'SMA_50' not in df.columns:
        df['Signal'] = "HOLD"
        return df

    # Create basic conditionals arrays mapping whether short > long term.
    buy_cond = df['SMA_20'] > df['SMA_50']
    sell_cond = df['SMA_20'] < df['SMA_50']

    # Detect active crossing points to only trigger a state change exactly when pulling over
    cross_up = buy_cond & ~buy_cond.shift(1).fillna(False)
    cross_down = sell_cond & ~sell_cond.shift(1).fillna(False)

    # Convert triggers to textual markers in sequence
    # Pandas 2.0+ compliant logic
    df['Signal'] = "HOLD"
    
    # Using np.where / loc directly
    df.loc[cross_up, 'Signal'] = "BUY"
    df.loc[cross_down, 'Signal'] = "SELL"
    
    return df