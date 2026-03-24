# ============================================================
# SNIPPET 6: Sharpe Ratio Formula
# ============================================================
# Formula: S = (Rannual - Rf) / sigma_annual
#
# Measures return PER UNIT OF RISK. Higher = better.
# Rf = risk-free rate (2%, what a savings account earns)
# Only returns ABOVE the risk-free rate count.
#
# Sharpe of 1.0 = you got 1% extra for every 1% of risk
# Sharpe of 0.5 = you only got 0.5% extra per 1% of risk
# ============================================================

# Convert annual risk-free rate to per-period rate
rf_period = (1 + risk_free_annual) ** (1 / periods_per_year) - 1

# Subtract the risk-free rate from each return
excess = returns - rf_period

# Sharpe = average excess return / volatility
sharpe = excess.mean() / returns.std() * np.sqrt(periods_per_year)

# Example:
# Annual return = 14%, Risk-free = 2%, Volatility = 17%
# Sharpe = (14% - 2%) / 17% = 0.71
