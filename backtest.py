# backtest.py
import pandas as pd
from typing import List, Dict
import sqlite3
import os
import math

DB_PATH = "trades.sqlite"

def init_db(db_path: str = DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            symbol TEXT,
            action TEXT,
            price REAL,
            qty INTEGER,
            cash REAL,
            position INTEGER,
            portfolio_value REAL
        )
    """)
    conn.commit()
    conn.close()

def log_trade(db_path: str, row: dict):
    # Convert any Series to scalar
    row = {k: (v.item() if isinstance(v, pd.Series) else v) for k, v in row.items()}

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        INSERT INTO trades (timestamp, symbol, action, price, qty, cash, position, portfolio_value)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["timestamp"], row["symbol"], row["action"], row["price"], 
        row["qty"], row["cash"], row["position"], row["portfolio_value"]
    ))
    conn.commit()
    conn.close()


def backtest(df: pd.DataFrame, symbol: str = "AAPL", start_cash: float = 10000.0,
             strategy_signals: list = None,
             db_log: bool = True) -> dict:
    """
    df must include:
      - 'Close'
      - one or more signal columns (values: 1 for buy, -1 for sell, 0 for nothing)
    strategy_signals: list of column names with signals. If multiple, signals are combined (sum).
    """
    if strategy_signals is None:
        raise ValueError("Pass at least one signal column name")

    if db_log:
        init_db(DB_PATH)

    data = df.copy()

    # Ensure datetime index
    if not isinstance(data.index, pd.DatetimeIndex):
        data.index = pd.to_datetime(data.index)

    # Create timestamp column
    data["timestamp"] = data.index.strftime("%Y-%m-%d %H:%M:%S")

    # Reset numeric index for iteration
    data = data.reset_index(drop=True)

    # Combine signals if multiple
    data["combined_signal"] = data[strategy_signals].sum(axis=1).clip(-1, 1)

    cash = start_cash
    position = 0
    portfolio_values = []
    trades = []

    for i, row in data.iterrows():
        price = float(row["Close"])
        sig = int(row["combined_signal"])
        ts = row["timestamp"]

        # BUY signal
        if sig == 1 and cash >= price:
            qty = math.floor(cash / price)
            if qty > 0:
                cost = qty * price
                cash -= cost
                position += qty
                action = "BUY"
                pv = cash + position * price
                trades.append({
                    "timestamp": ts, "symbol": symbol, "action": action,
                    "price": price, "qty": qty, "cash": cash,
                    "position": position, "portfolio_value": pv
                })
                if db_log:
                    log_trade(DB_PATH, trades[-1])

        # SELL signal
        elif sig == -1 and position > 0:
            qty = position
            proceeds = qty * price
            cash += proceeds
            position = 0
            action = "SELL"
            pv = cash + position * price
            trades.append({
                "timestamp": ts, "symbol": symbol, "action": action,
                "price": price, "qty": qty, "cash": cash,
                "position": position, "portfolio_value": pv
            })
            if db_log:
                log_trade(DB_PATH, trades[-1])

        # record portfolio value
        pv = cash + position * price
        portfolio_values.append({
            "timestamp": ts, "cash": cash, "position": position,
            "price": price, "portfolio_value": pv
        })

    equity_df = pd.DataFrame(portfolio_values)
    trades_df = pd.DataFrame(trades)
    if trades_df.empty:
        trades_df = pd.DataFrame(columns=[
            "timestamp", "symbol", "action", "price",
            "qty", "cash", "position", "portfolio_value"
        ])

    return {"equity_curve": equity_df, "trades": trades_df}
