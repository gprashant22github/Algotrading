# data_fetch.py
import yfinance as yf
import pandas as pd

def fetch_historical(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical OHLCV data using yfinance.
    period examples: "6mo", "1y", "2y"
    interval examples: "1d", "1h", "1m" (minute intervals may be limited)
    """
    df = yf.download(symbol, period=period, interval=interval, progress=False)
    if df.empty:
        raise ValueError(f"No data returned for {symbol} with {period} {interval}")
    df = df.dropna()
    df.index = pd.to_datetime(df.index)
    return df
