# app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from data_fetch import fetch_historical
from strategies import generate_signals_sma, generate_signals_rsi
from backtest import backtest, DB_PATH
import os
import time

st.set_page_config(page_title="Algo Trading Prototype - JarNox", layout="wide")

st.title("Algo Trading Prototype — JarNox Intern Assignment")
st.markdown("Built: SMA Crossover + RSI | Backtest + Paper Simulation | SQLite trade log")

# Sidebar controls
with st.sidebar:
    symbol = st.text_input("Symbol (Yahoo Finance)", value="AAPL")
    period = st.selectbox("Historical period", ["6mo", "1y", "2y", "5y"], index=1)
    interval = st.selectbox("Interval", ["1d", "1h"], index=0)
    short = st.number_input("SMA short window", min_value=5, max_value=200, value=50)
    long = st.number_input("SMA long window", min_value=10, max_value=500, value=200)
    rsi_period = st.number_input("RSI period", min_value=5, max_value=50, value=14)
    rsi_buy = st.slider("RSI buy threshold", 1, 50, 30)
    rsi_sell = st.slider("RSI sell threshold", 50, 99, 70)
    start_cash = st.number_input("Start cash (USD)", min_value=1000, max_value=1000000, value=10000)
    run_button = st.button("Fetch & Backtest")
    st.markdown("---")
    st.write("Database trade log path:")
    st.code(DB_PATH)

# Main
if run_button:
    try:
        data = fetch_historical(symbol, period=period, interval=interval)
    except Exception as e:
        st.error(f"Failed to fetch data: {e}")
        st.stop()

    # Add signals
    df_sma = generate_signals_sma(data, short=short, long=long)
    df_all = generate_signals_rsi(df_sma, period=rsi_period, rsi_buy=rsi_buy, rsi_sell=rsi_sell)

    # show preview
    st.subheader("Data preview")
    st.dataframe(df_all.tail(10))

    # Backtest using both signal columns
    res = backtest(df_all, symbol=symbol, start_cash=float(start_cash),
                   strategy_signals=["signal_sma", "signal_rsi"], db_log=True)
    equity = res["equity_curve"]
    trades = res["trades"]

    # Charts
    st.subheader("Price chart with signals")
    fig = go.Figure()
    fig.add_trace(go.Candlestick(x=df_all.index,
                                 open=df_all['Open'], high=df_all['High'],
                                 low=df_all['Low'], close=df_all['Close'],
                                 name='Price'))
    fig.add_trace(go.Scatter(x=df_all.index, y=df_all[f"SMA_{short}"], mode="lines", name=f"SMA {short}"))
    fig.add_trace(go.Scatter(x=df_all.index, y=df_all[f"SMA_{long}"], mode="lines", name=f"SMA {long}"))
    # Buy/Sell markers from trades recorded
    if not trades.empty:
        buys = trades[trades["action"] == "BUY"]
        sells = trades[trades["action"] == "SELL"]
        if not buys.empty:
            fig.add_trace(go.Scatter(x=buys["timestamp"], y=buys["price"], mode="markers", marker_symbol="triangle-up", marker_size=12, name="Buys"))
        if not sells.empty:
            fig.add_trace(go.Scatter(x=sells["timestamp"], y=sells["price"], mode="markers", marker_symbol="triangle-down", marker_size=12, name="Sells"))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Equity curve (portfolio value over time)")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=equity["timestamp"], y=equity["portfolio_value"], mode="lines+markers", name="Portfolio Value"))
    fig2.add_trace(go.Scatter(x=equity["timestamp"], y=equity["cash"], mode="lines", name="Cash"))
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Trades (executed during backtest)")
    st.dataframe(trades)

    # Summary metrics
    final_value = float(equity["portfolio_value"].iloc[-1])
    pnl = final_value - float(start_cash)
    roi = pnl / float(start_cash) * 100
    st.metric("Final Portfolio Value (USD)", f"{final_value:,.2f}")
    st.metric("P&L (USD)", f"{pnl:,.2f}")
    st.metric("ROI (%)", f"{roi:.2f}%")

    st.success("Backtest complete. Trades logged to local SQLite database.")
    st.markdown("### Notes")
    st.write("""
    - This prototype uses combined signals from SMA crossover and RSI.  
    - BUY = signal positive and there is cash to buy; strategy buys integer shares with all available cash.  
    - SELL = any negative signal will liquidate position.  
    - Trade log is saved to `trades.sqlite`.
    - This is a simple approach for demonstration; production systems include partial fills, slippage, fees, and risk limits.
    """)
    st.balloons()

# Pseudo-streaming / step-through simulation demo
st.sidebar.markdown("---")
st.sidebar.subheader("Pseudo-live demo")
if st.sidebar.button("Load demo (AAPL, 1y daily)"):
    data_demo = fetch_historical("AAPL", period="1y", interval="1d")
    demo_df = generate_signals_sma(data_demo, short=20, long=50)
    demo_df = generate_signals_rsi(demo_df, period=14)
    st.session_state["demo_df"] = demo_df
    st.success("Demo loaded. Use 'Step' to move day by day (simulates streaming).")

if "demo_df" in st.session_state:
    demo_df = st.session_state["demo_df"]
    if "step_index" not in st.session_state:
        st.session_state["step_index"] = 0
    step_col1, step_col2 = st.columns([1,4])
    with step_col1:
        if st.button("Step (next day)"):
            st.session_state["step_index"] = min(st.session_state["step_index"] + 1, len(demo_df) - 1)
    with step_col2:
        st.write(f"Demo index: {st.session_state['step_index']} / {len(demo_df)-1}")
    idx = st.session_state["step_index"]
    current_row = demo_df.iloc[:idx+1]
    # show price up to idx
    fig_demo = go.Figure()
    fig_demo.add_trace(go.Scatter(x=current_row.index, y=current_row["Close"], mode="lines+markers", name="Close"))
    if "signal_sma" in current_row.columns:
        buys = current_row[current_row["signal_sma"]==1]
        sells = current_row[current_row["signal_sma"]==-1]
        if not buys.empty:
            fig_demo.add_trace(go.Scatter(x=buys.index, y=buys["Close"], mode="markers", marker_symbol="triangle-up", marker_size=10, name="SMA Buys"))
        if not sells.empty:
            fig_demo.add_trace(go.Scatter(x=sells.index, y=sells["Close"], mode="markers", marker_symbol="triangle-down", marker_size=10, name="SMA Sells"))
    st.plotly_chart(fig_demo, use_container_width=True)
