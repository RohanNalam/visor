# ============================================================
# SNIPPET 23: Computing All 5 Performance Metrics
# ============================================================
# For every strategy, compute these 5 numbers:
#   1. Cumulative return  = total growth (higher is better)
#   2. Annualized return  = average yearly growth (higher is better)
#   3. Volatility         = risk level (lower is safer)
#   4. Sharpe ratio       = return per unit of risk (higher is better)
#   5. Max drawdown       = worst crash (closer to 0 is safer)
# ============================================================

def performance_metrics(returns, risk_free_annual, frequency):
    periods_per_year = {"D": 252, "W": 52, "M": 12}.get(frequency, 52)
    rf_period = (1 + risk_free_annual) ** (1 / periods_per_year) - 1
    excess = returns - rf_period

    # 1. Total growth
    cumulative = (1 + returns).prod() - 1

    # 2. Average yearly growth
    annualized = (1 + cumulative) ** (periods_per_year / len(returns)) - 1

    # 3. How much returns bounce around
    volatility = returns.std() * np.sqrt(periods_per_year)

    # 4. Return per unit of risk
    sharpe = excess.mean() / returns.std() * np.sqrt(periods_per_year)

    # 5. Worst peak-to-bottom drop
    max_dd = max_drawdown((1 + returns).cumprod())

    return {
        "cumulative_return": cumulative,
        "annualized_return": annualized,
        "volatility": volatility,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
    }

# Example output for one strategy:
# {
#     "cumulative_return": 1.14,    -> grew 114% total
#     "annualized_return": 0.136,   -> 13.6% per year
#     "volatility": 0.171,          -> 17.1% annual risk
#     "sharpe": 0.715,              -> decent risk-adjusted return
#     "max_drawdown": -0.248,       -> worst crash was -24.8%
# }
