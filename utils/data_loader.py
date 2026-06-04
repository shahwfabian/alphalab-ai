"""
AlphaLab AI — Data Loader
Handles market data retrieval via yfinance and CSV upload processing.
"""

import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta


DEFAULT_START = (datetime.today() - timedelta(days=5 * 365)).strftime("%Y-%m-%d")
DEFAULT_END = datetime.today().strftime("%Y-%m-%d")


@st.cache_data(ttl=3600)
def fetch_prices(tickers: list[str], start: str = DEFAULT_START, end: str = DEFAULT_END) -> pd.DataFrame:
    """Download adjusted closing prices for a list of tickers."""
    if not tickers:
        return pd.DataFrame()
    try:
        raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            prices = raw["Close"]
        else:
            prices = raw[["Close"]]
            prices.columns = tickers
        prices.dropna(how="all", inplace=True)
        return prices
    except Exception as e:
        st.error(f"Data fetch error: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600)
def fetch_returns(tickers: list[str], start: str = DEFAULT_START, end: str = DEFAULT_END) -> pd.DataFrame:
    """Return daily log returns for a list of tickers."""
    prices = fetch_prices(tickers, start, end)
    if prices.empty:
        return pd.DataFrame()
    returns = np.log(prices / prices.shift(1)).dropna()
    return returns


@st.cache_data(ttl=3600)
def fetch_simple_returns(tickers: list[str], start: str = DEFAULT_START, end: str = DEFAULT_END) -> pd.DataFrame:
    """Return daily simple (arithmetic) returns for a list of tickers."""
    prices = fetch_prices(tickers, start, end)
    if prices.empty:
        return pd.DataFrame()
    returns = prices.pct_change().dropna()
    return returns


def parse_uploaded_csv(uploaded_file) -> pd.DataFrame:
    """
    Parse a user-uploaded CSV file. Attempts to detect a date column
    and set it as the index.
    """
    try:
        df = pd.read_csv(uploaded_file)
        date_cols = [c for c in df.columns if any(k in c.lower() for k in ["date", "time", "datetime"])]
        if date_cols:
            df[date_cols[0]] = pd.to_datetime(df[date_cols[0]], infer_datetime_format=True, errors="coerce")
            df.set_index(date_cols[0], inplace=True)
            df.sort_index(inplace=True)
        return df
    except Exception as e:
        st.error(f"CSV parse error: {e}")
        return pd.DataFrame()


def get_ticker_info(ticker: str) -> dict:
    """Fetch basic metadata for a ticker symbol."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        return {
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "currency": info.get("currency", "USD"),
            "country": info.get("country", "N/A"),
        }
    except Exception:
        return {"name": ticker}


def annualized_return(returns: pd.Series, periods_per_year: int = 252) -> float:
    """Compute CAGR-style annualized return from a daily returns series."""
    total = (1 + returns).prod()
    n_years = len(returns) / periods_per_year
    if n_years <= 0:
        return 0.0
    return float(total ** (1 / n_years) - 1)


def annualized_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    """Annualized standard deviation of daily returns."""
    return float(returns.std() * np.sqrt(periods_per_year))


def describe_dataframe(df: pd.DataFrame) -> dict:
    """Generate a summary dictionary for a DataFrame."""
    summary = {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "missing_counts": df.isnull().sum().to_dict(),
        "missing_pct": (df.isnull().mean() * 100).round(2).to_dict(),
        "numeric_summary": df.describe().to_dict(),
    }
    return summary
