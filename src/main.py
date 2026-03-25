from data_fetcher import fetch_stock_data
from indicators import add_moving_average, calculate_rsi, calculate_macd
from visualizer import plot_price, plot_rsi
from model import train_model
from utils import save_to_csv
from config.config import TICKER, DATA_PATH

def run():
    print("Fetching stock data...")
    df = fetch_stock_data(TICKER)

    print("Processing indicators...")
    df = add_moving_average(df)
    df = calculate_rsi(df)
    df = calculate_macd(df)

    print("Saving data...")
    save_to_csv(df, DATA_PATH)

    print("Visualizing...")
    plot_price(df, TICKER)
    plot_rsi(df)

    print("Training model...")
    train_model(df)

if __name__ == "__main__":
    run()