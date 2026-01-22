from typing import List

import numpy as np
import pandas as pd

try:
    import yfinance as yf
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "yfinance is required. Install with: pip install yfinance pandas numpy matplotlib"
    ) from exc


def download_prices(tickers: List[str], start: str, end: str) -> pd.DataFrame:
    data = yf.download(
        tickers=tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
    )
    if data.empty:
        raise ValueError("No price data returned. Check tickers or date range.")
    if isinstance(data.columns, pd.MultiIndex):
        data = data["Close"]
    else:
        data = data.rename(columns={"Close": tickers[0]})
    return data.dropna(how="all")


def load_prices_csv(
    path: str,
    date_column: str,
    tickers: List[str],
    start: str,
    end: str,
) -> pd.DataFrame:
    df = pd.read_csv(path)
    if date_column not in df.columns:
        raise ValueError(f"{path} missing required column: {date_column}")
    df[date_column] = pd.to_datetime(df[date_column])
    df = df.set_index(date_column).sort_index()
    df = df[(df.index >= pd.to_datetime(start)) & (df.index <= pd.to_datetime(end))]

    missing = [ticker for ticker in tickers if ticker not in df.columns]
    if missing:
        raise ValueError(f"{path} missing ticker columns: {missing}")
    return df[tickers].dropna(how="all")


def generate_synthetic_prices(
    tickers: List[str], start: str, end: str
) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    dates = pd.date_range(start=start, end=end, freq="B")
    prices = {}
    for ticker in tickers:
        drift = 0.0003 if ticker == "SPY" else 0.0002
        noise = rng.normal(0, 0.01, size=len(dates))
        returns = drift + noise
        prices[ticker] = 100 * (1 + pd.Series(returns, index=dates)).cumprod()
    return pd.DataFrame(prices)


def to_period_returns(prices: pd.DataFrame, frequency: str) -> pd.DataFrame:
    period_prices = prices.resample(frequency).last()
    returns = period_prices.pct_change().dropna(how="all")
    return returns


def load_advisor_returns(
    path: str, frequency: str, start: str, end: str
) -> pd.Series:
    df = pd.read_csv(path)
    if "date" not in df.columns:
        raise ValueError(f"{path} missing required column: date")
    if "return" not in df.columns and "value" not in df.columns:
        raise ValueError(f"{path} must include column: return or value")

    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    df = df[(df["date"] >= pd.to_datetime(start)) & (df["date"] <= pd.to_datetime(end))]

    if "return" in df.columns:
        returns = pd.Series(df["return"].astype(float).values, index=df["date"])
        period_returns = (
            (1 + returns)
            .resample(frequency)
            .prod()
            .sub(1)
            .dropna()
        )
        return period_returns

    values = pd.Series(df["value"].astype(float).values, index=df["date"])
    period_values = values.resample(frequency).last().dropna()
    return period_values.pct_change().dropna()
