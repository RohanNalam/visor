# ============================================================
# SNIPPET 1: Daily Return Formula
# ============================================================
# Formula: rt = (Pt - Pt-1) / Pt-1
#
# This converts raw stock prices into percent changes.
# If the S&P 500 was $4000 yesterday and $4040 today,
# the return is (4040 - 4000) / 4000 = +1%.
# ============================================================

def to_period_returns(prices, frequency):
    period_prices = prices.resample(frequency).last()
    returns = period_prices.pct_change().dropna(how="all")
    return returns

# Example:
# Input prices:  [4000, 4040, 3990, 4100]
# Output returns: [+1.0%, -1.2%, +2.8%]
