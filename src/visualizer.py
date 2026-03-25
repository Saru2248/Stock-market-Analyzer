from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression


def train_model(df):
    df = df.dropna()

    X = df[['Open', 'High', 'Low', 'Volume']]
    y = df['Close']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = LinearRegression()
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print(f"Model Accuracy: {accuracy:.2f}")

    return model


import matplotlib.pyplot as plt

def plot_price(df, ticker):
    plt.figure(figsize=(12,6))
    plt.plot(df['Date'], df['Close'], label='Close Price')
    plt.plot(df['Date'], df['MA'], label='Moving Avg')
    plt.title(f"{ticker} Price Trend")
    plt.legend()
    plt.show()

def plot_rsi(df):
    plt.figure(figsize=(10,4))
    plt.plot(df['RSI'], label='RSI')
    plt.axhline(70, linestyle='--')
    plt.axhline(30, linestyle='--')
    plt.title("RSI Indicator")
    plt.legend()
    plt.show()