from typing import Optional

import pandas as pd


def _rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    delta = prices.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))


def _trend_momentum_rsi_vol(returns: pd.Series) -> pd.Series:
    prices = (1 + returns).cumprod()
    momentum = prices / prices.shift(3) - 1
    trend = prices.rolling(6).mean() / prices.rolling(12).mean() - 1
    volatility = returns.rolling(6).std()
    rsi = _rsi(prices, window=14)

    trend_up = trend > 0
    momentum_up = momentum > 0
    vol_ok = volatility < volatility.rolling(12).median()
    rsi_ok = rsi < 70

    signal = trend_up & momentum_up & vol_ok & rsi_ok
    return signal.astype(float).fillna(0.0)


def _sma_crossover(returns: pd.Series) -> pd.Series:
    prices = (1 + returns).cumprod()
    short_ma = prices.rolling(6).mean()
    long_ma = prices.rolling(12).mean()
    signal = short_ma > long_ma
    return signal.astype(float).fillna(0.0)


def _vol_adjusted_momentum(returns: pd.Series) -> pd.Series:
    prices = (1 + returns).cumprod()
    momentum = prices / prices.shift(6) - 1
    volatility = returns.rolling(6).std()
    trend = prices.rolling(6).mean() / prices.rolling(12).mean() - 1
    score = momentum / (volatility + 1e-8)
    signal = (score > 0) & (trend > 0)
    return signal.astype(float).fillna(0.0)


QUANT_MODELS = {
    "trend_momentum_rsi_vol": _trend_momentum_rsi_vol,
    "sma_crossover": _sma_crossover,
    "vol_adjusted_momentum": _vol_adjusted_momentum,
}


def quant_model_name(model_key: str) -> str:
    names = {
        "trend_momentum_rsi_vol": "Trend + Momentum + RSI + Vol Filter",
        "sma_crossover": "SMA Crossover (6/12)",
        "vol_adjusted_momentum": "Vol-Adjusted Momentum",
    }
    return names.get(model_key, model_key)


def quant_model_signals(returns: pd.Series, model: str) -> pd.Series:
    if model not in QUANT_MODELS:
        raise ValueError(f"Unknown quant model: {model}")
    return QUANT_MODELS[model](returns)


def compute_strategy_series(
    returns: pd.Series, signal: Optional[pd.Series]
) -> pd.Series:
    if signal is None:
        strat_returns = returns
    else:
        strat_returns = returns * signal
    return (1 + strat_returns).cumprod()
