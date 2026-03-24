# ============================================================
# SNIPPET 12: Volatility Filter
# ============================================================
# Formula: Vol = std(returns) over 6 periods
#
# If current volatility is BELOW the 12-period median,
# the market is calmer than usual = safer to invest.
# If volatility is spiking, the model stays in cash.
# ============================================================

# Current volatility over last 6 periods
volatility = returns.rolling(6).std()

# Historical median volatility over last 12 periods
median_vol = volatility.rolling(12).median()

# Is the market calmer than usual?
vol_ok = volatility < median_vol

# Example:
# Current 6-month volatility = 12%
# 12-month median volatility = 15%
# 12% < 15%, so vol_ok = True (market is calm, safe to buy)
#
# Current 6-month volatility = 25%
# 12-month median volatility = 15%
# 25% > 15%, so vol_ok = False (market is shaky, stay in cash)
