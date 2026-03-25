import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# MUST be first streamlit command
st.set_page_config(page_title="Stock Analyzer Pro", page_icon="📈", layout="wide", initial_sidebar_state="collapsed")

from data_fetcher import fetch_stock_data, get_all_tickers
all_tickers = get_all_tickers()
from indicators import add_moving_average, calculate_rsi, calculate_macd, calculate_bollinger_bands
from signals import generate_signals
from backtester import run_backtest
from portfolio import compare_stocks, normalize_prices, calculate_portfolio_return

# UI Styling overrides
st.markdown("""             
    <style>
    .main {background-color: #0E1117;}
    h1 {color: #FF4B4B;}
    </style>
""", unsafe_allow_html=True)

st.title("📈 Market Intelligence Dashboard")
st.markdown("Professional-grade technical tracking & portfolio analysis.")

# Layout Tabs
tab1, tab2 = st.tabs(["🔍 Single Stock Intelligence", "📊 Portfolio Comparator"])

with tab1:
    col1, col2 = st.columns([1, 4])
    with col1:
        default_idx = all_tickers.index("AAPL") if "AAPL" in all_tickers else 0
        ticker_select = st.selectbox("Select Target Stock", all_tickers, index=default_idx)
        custom_ticker = st.text_input("Or Enter Custom Ticker (e.g. RELIANCE.NS)", "")
        ticker = custom_ticker.strip().upper() if custom_ticker.strip() else ticker_select
        analyze_btn = st.button("Generate Dashboard", use_container_width=True)

    if analyze_btn:
        with st.spinner(f"Aggregating data for {ticker}..."):
            try:
                df = fetch_stock_data(ticker)
                df = add_moving_average(df)
                df = calculate_rsi(df)
                df = calculate_macd(df)
                df = calculate_bollinger_bands(df)
                df = generate_signals(df)
                
                # Execute Backtest
                bt_results = run_backtest(df, ticker, initial_capital=10000.0)
                if bt_results and 'df' in bt_results:
                    df = bt_results['df']

                # Key Metrics Area
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                
                prices_col1, prices_col2, prices_col3, prices_col4 = st.columns(4)
                with prices_col1:
                    price_change = latest['Close'] - prev['Close']
                    pct_change = (price_change / prev['Close']) * 100
                    st.metric("Latest Close", f"${latest['Close']:.2f}", f"${price_change:.2f} ({pct_change:.2f}%)")
                with prices_col2:
                    st.metric("RSI (14)", f"{latest['RSI']:.1f}", "Overbought" if latest['RSI']>70 else "Oversold" if latest['RSI']<30 else "Neutral", delta_color="off")
                with prices_col3:
                    st.metric("MACD", f"{latest['MACD']:.2f}")
                with prices_col4:
                    signal = latest['Signal']
                    color = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪"
                    st.metric("Algorithm Signal", f"{color} {signal}", delta_color="off")

                # Main Candlestick Chart
                st.markdown("---")
                st.subheader("Interactive Price & Trend Evolution")
                
                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Market Price'))
                if 'SMA_20' in df.columns:
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_20'], mode='lines', line=dict(color='#FFA500', width=2), name='SMA 20'))
                if 'SMA_50' in df.columns:
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA_50'], mode='lines', line=dict(color='#00FFFF', width=2), name='SMA 50'))
                if 'BB_upper' in df.columns and 'BB_lower' in df.columns:
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['BB_upper'], mode='lines', line=dict(color='rgba(255, 255, 255, 0.2)', width=1, dash='dash'), name='BB Upper'))
                    fig.add_trace(go.Scatter(x=df['Date'], y=df['BB_lower'], mode='lines', line=dict(color='rgba(255, 255, 255, 0.2)', width=1, dash='dash'), fill='tonexty', fillcolor='rgba(255, 255, 255, 0.05)', name='BB Lower'))
                fig.update_layout(template="plotly_dark", margin=dict(l=0, r=0, t=30, b=0), height=550, xaxis_rangeslider_visible=True)
                st.plotly_chart(fig, use_container_width=True)

                # RSI Chart below
                st.subheader("Relative Strength Index (RSI)")
                fig_rsi = px.line(df, x="Date", y="RSI", template="plotly_dark")
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought 70")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold 30")
                fig_rsi.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=250)
                st.plotly_chart(fig_rsi, use_container_width=True)

                # Simulation Backtester Performance
                if bt_results:
                    st.markdown("---")
                    st.subheader(f"Strategy Simulation Output (SMA Crossover)")
                    
                    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
                    b_col1.metric("Final Capital (Net)", f"${bt_results['final_capital']:.2f}", f"{bt_results['return_pct']:.2f}% Yield")
                    b_col2.metric("Sharpe Ratio", f"{bt_results['sharpe_ratio']:.3f}", delta_color="off")
                    b_col3.metric("Max Drawdown", f"{bt_results['max_drawdown']:.2f}%", delta_color="inverse")
                    b_col4.metric("Starting Capital", f"${bt_results['initial_capital']:.2f}", delta_color="off")
                    
                    fig_eq = px.line(df, x="Date", y="Equity", title="Simulated Portfolio Equity Curve (Includes 0.1% transaction slips)", template="plotly_dark")
                    fig_eq.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=350)
                    st.plotly_chart(fig_eq, use_container_width=True)

                # Expandable Raw Data
                with st.expander("Show Raw Structured Dataset"):
                    st.dataframe(df.tail(60).style.highlight_max(axis=0), use_container_width=True)

            except Exception as e:
                st.error(f"Error generating dashboard: {e}")

with tab2:
    st.subheader("Advanced Portfolio Modeling")
    
    col_port1, col_port2 = st.columns([1, 4])
    with col_port1:
        default_portfolio = [t for t in ["AAPL", "MSFT", "GOOGL", "NVDA"] if t in all_tickers]
        tickers = st.multiselect("Select Basket for Analysis", all_tickers, default=default_portfolio)
        custom_tickers_input = st.text_input("Or Enter Custom Tickers (Comma separated)", "")
        compare_btn = st.button("Run Comparison", use_container_width=True)
    
    if compare_btn:
        custom_tickers = [t.strip().upper() for t in custom_tickers_input.split(",") if t.strip()]
        tickers = list(set(tickers + custom_tickers))
        if len(tickers) > 0:
            with st.spinner("Fetching portfolio sector data..."):
                try:
                    df_port = compare_stocks(tickers)
                    df_norm = normalize_prices(df_port)
    
                    st.markdown("#### Cumulative Normalized Returns (Base 100)")
                    fig_comp = px.line(df_norm, x="Date", y="Normalized", color="Ticker", template="plotly_dark")
                    fig_comp.update_layout(margin=dict(l=0, r=0, t=30, b=0), height=500, yaxis_title="Comparative Growth Indexed to 100", xaxis_title="Timeline")
                    st.plotly_chart(fig_comp, use_container_width=True)
                except Exception as e:
                    st.error(f"Error during baseline comparison: {e}")

    st.markdown("---")
    res_col1, res_col2 = st.columns([1, 2])
    with res_col1:
        st.markdown("#### Custom Weight Allocation")
        st.caption("Distribute investment allocation manually across the basket")
        weights = {}
        for t in tickers:
            weights[t] = st.slider(f"{t} Exposure", 0.0, 1.0, 1.0/len(tickers) if len(tickers)>0 else 1.0)
            
        if st.button("Calculate Aggregated Returns", use_container_width=True):
            try:
                total_w = sum(weights.values())
                if total_w == 0:
                    st.error("Total allocated weight cannot be empty (0.0)")
                else:
                    norm_weights = {k: v / total_w for k, v in weights.items()}
                    df_port = compare_stocks(tickers)
                    port_return = calculate_portfolio_return(df_port, norm_weights)
                    st.success(f"Estimated Portfolio Yield: **{port_return:.2f}%**")
                    with res_col2:
                         fig_pie = px.pie(values=list(norm_weights.values()), names=list(norm_weights.keys()), hole=0.4, title="Portfolio Distribution Allocation", template="plotly_dark")
                         st.plotly_chart(fig_pie, use_container_width=True)
            except Exception as e:
                st.error(f"Engine Calculation Error: {e}")