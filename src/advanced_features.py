import yfinance as yf
import pandas as pd
import numpy as np
from datetime import timedelta

def get_fundamentals(ticker: str):
    """
    Returns fundamental data for the given ticker.
    """
    try:
        t = yf.Ticker(ticker)
        info = t.info
        return {
            "marketCap": info.get("marketCap"),
            "peRatio": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "dividendYield": info.get("dividendYield"),
            "revenueGrowth": info.get("revenueGrowth"),
            "profitMargins": info.get("profitMargins"),
            "freeCashflow": info.get("freeCashflow"),
            "debtToEquity": info.get("debtToEquity"),
            "returnOnEquity": info.get("returnOnEquity")
        }
    except Exception as e:
        return {"error": str(e)}


def get_news_sentiment(ticker: str):
    """
    Fetches latest news and applies a basic NLP sentiment analysis heuristic to gauge bullish/bearish momentum.
    """
    try:
        t = yf.Ticker(ticker)
        news = t.news[:5]  # Top 5 news
        
        bullish_keywords = ['surge', 'gain', 'jump', 'up', 'upgrade', 'beat', 'positive', 'acquire', 'growth', 'bullish', 'high']
        bearish_keywords = ['drop', 'fall', 'down', 'downgrade', 'miss', 'negative', 'sell', 'loss', 'bearish', 'low', 'plunge']
        
        analyzed_news = []
        overall_score = 0
        
        for article in news:
            title = article.get("title", "").lower()
            score = 0
            for w in bullish_keywords:
                if w in title: score += 1
            for w in bearish_keywords:
                if w in title: score -= 1
                
            overall_score += score
            analyzed_news.append({
                "title": article.get("title"),
                "publisher": article.get("publisher"),
                "link": article.get("link"),
                "sentiment_score": score
            })
            
        return {
            "overall_sentiment": "Bullish 📈" if overall_score > 0 else "Bearish 📉" if overall_score < 0 else "Neutral ⚖️",
            "articles": analyzed_news
        }
    except Exception as e:
        return {"error": str(e)}


def generate_ai_forecast(df: pd.DataFrame, days: int = 7):
    """
    Applies a Polyfit Linear Regression to historical close prices to project future price movement.
    """
    if df.empty or len(df) < 14:
        return []
        
    df = df.copy().tail(60) # Train on the last 60 days of momentum
    y = df['Close'].values
    x = np.arange(len(y))
    
    # Fit a 1st degree polynomial (linear regression)
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    
    last_date = pd.to_datetime(df['Date'].iloc[-1])
    
    predictions = []
    for i in range(1, days + 1):
        future_x = len(y) - 1 + i
        predicted_price = p(future_x)
        future_date = last_date + timedelta(days=i)
        
        # Don't predict weekends if possible, but keep it simple for now
        if future_date.weekday() >= 5: # 5=Sat, 6=Sun
            future_date += timedelta(days=2) # Push to Monday/Tuesday implicitly
            
        predictions.append({
            "DateStr": future_date.strftime("%Y-%m-%d"),
            "ForecastPrice": float(predicted_price)
        })
        
    return predictions
