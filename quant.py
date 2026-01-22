from typing import Optional

import pandas as pd


def quant_model_signals(returns: pd.Series) -> pd.Series:
    prices = (1 + returns).cumprod()
    momentum = prices / prices.shift(3) - 1
    volatility = returns.rolling(6).std()
    trend = prices.rolling(6).mean() / prices.rolling(12).mean() - 1
    mean_reversion = -returns.rolling(3).mean()

    score = (
        0.35 * momentum
        + 0.25 * trend
        + 0.2 * mean_reversion
        - 0.2 * volatility
    )

    vol_filter = volatility < volatility.rolling(12).median()
    signal = (score > 0) & vol_filter
    return signal.astype(float).fillna(0.0)


def compute_strategy_series(
    returns: pd.Series, signal: Optional[pd.Series]
) -> pd.Series:
    if signal is None:
        strat_returns = returns
    else:
        strat_returns = returns * signal
    return (1 + strat_returns).cumprod()
