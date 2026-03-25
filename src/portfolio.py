from data_fetcher import fetch_stock_data
from indicators import add_moving_average
import pandas as pd

def compare_stocks(tickers):
    combined_df = pd.DataFrame()

    for ticker in tickers:
        df = fetch_stock_data(ticker)
        df = add_moving_average(df)

        df['Ticker'] = ticker
        combined_df = pd.concat([combined_df, df])

    return combined_df

def normalize_prices(df):
    df['Normalized'] = df.groupby('Ticker')['Close'].transform(lambda x: x / x.iloc[0] * 100)
    return df

def calculate_portfolio_return(df, weights):
    portfolio_return = 0
    for ticker, weight in weights.items():
        stock_df = df[df['Ticker'] == ticker].sort_values('Date')
        if not stock_df.empty:
            start_price = stock_df['Close'].iloc[0]
            end_price = stock_df['Close'].iloc[-1]
            stock_return = (end_price - start_price) / start_price * 100
            portfolio_return += stock_return * weight
    return portfolio_return