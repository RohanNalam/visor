from typing import Dict

import numpy as np
import pandas as pd


def max_drawdown(series: pd.Series) -> float:
    peak = series.cummax()
    drawdown = (series / peak) - 1
    return float(drawdown.min())


def performance_metrics(
    returns: pd.Series, risk_free_annual: float, frequency: str
) -> Dict[str, float]:
    periods_per_year = {"D": 252, "W": 52, "M": 12}.get(frequency, 52)
    rf_period = (1 + risk_free_annual) ** (1 / periods_per_year) - 1
    excess = returns - rf_period
    cumulative = (1 + returns).prod() - 1
    if len(returns) == 0:
        return {
            "cumulative_return": float("nan"),
            "annualized_return": float("nan"),
            "volatility": float("nan"),
            "sharpe": float("nan"),
            "max_drawdown": float("nan"),
        }

    annualized = (1 + cumulative) ** (periods_per_year / len(returns)) - 1
    volatility = returns.std() * np.sqrt(periods_per_year)
    sharpe = (
        excess.mean() / returns.std() * np.sqrt(periods_per_year)
        if returns.std() != 0
        else float("nan")
    )
    max_dd = max_drawdown((1 + returns).cumprod())

    return {
        "cumulative_return": float(cumulative),
        "annualized_return": float(annualized),
        "volatility": float(volatility),
        "sharpe": float(sharpe),
        "max_drawdown": float(max_dd),
    }
