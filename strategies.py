# strategies.py
import pandas as pd
from ta.momentum import RSIIndicator

def add_sma(df: pd.DataFrame, short: int = 50, long: int = 200) -> pd.DataFrame:
    df = df.copy()
    df[f"SMA_{short}"] = df["Close"].rolling(window=short, min_periods=1).mean()
    df[f"SMA_{long}"] = df["Close"].rolling(window=long, min_periods=1).mean()
    return df

def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    df = df.copy()
    # Ensure Close is a Series (1D)
    close_series = df["Close"]
    if isinstance(close_series, pd.DataFrame):  # flatten if needed
        close_series = close_series.iloc[:, 0]

    df["RSI"] = RSIIndicator(close_series, window=period).rsi()
    return df


def generate_signals_sma(df: pd.DataFrame, short: int = 50, long: int = 200) -> pd.DataFrame:
    df = add_sma(df, short, long)
    df = df.copy()
    df["signal_sma"] = 0
    # when short crosses above long -> 1, when below -> -1
    df["prev_short"] = df[f"SMA_{short}"].shift(1)
    df["prev_long"] = df[f"SMA_{long}"].shift(1)
    buy_mask = (df[f"SMA_{short}"] > df[f"SMA_{long}"]) & (df["prev_short"] <= df["prev_long"])
    sell_mask = (df[f"SMA_{short}"] < df[f"SMA_{long}"]) & (df["prev_short"] >= df["prev_long"])
    df.loc[buy_mask, "signal_sma"] = 1
    df.loc[sell_mask, "signal_sma"] = -1
    df = df.drop(columns=["prev_short", "prev_long"])
    return df

def generate_signals_rsi(df: pd.DataFrame, period: int = 14, rsi_buy: float = 30, rsi_sell: float = 70) -> pd.DataFrame:
    df = add_rsi(df, period)
    df = df.copy()
    df["signal_rsi"] = 0
    df.loc[df["RSI"] < rsi_buy, "signal_rsi"] = 1
    df.loc[df["RSI"] > rsi_sell, "signal_rsi"] = -1
    return df
