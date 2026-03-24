# ============================================================
# SNIPPET 3: Growth of $1 (The Line on the Graph)
# ============================================================
# Formula: Growth(t) = Product of (1 + ri) for i=1 to t
#
# This is what gets plotted on the chart. Each point shows
# what $1 invested at the start would be worth on that day.
#
# If signal = 1 (BUY), you earn the market return that day.
# If signal = 0 (SELL), you earn 0 (sitting in cash).
# ============================================================

def compute_strategy_series(returns, signal):
    if signal is None:
        strat_returns = returns           # Buy and hold
    else:
        strat_returns = returns * signal  # Only earn when invested
    return (1 + strat_returns).cumprod()  # Running growth of $1

# Example (3 days, signal = [1, 0, 1]):
# Day 1: market +2%, signal=1 (BUY)  -> earn +2%  -> $1.00 * 1.02 = $1.02
# Day 2: market +3%, signal=0 (SELL) -> earn  0%  -> $1.02 * 1.00 = $1.02
# Day 3: market -1%, signal=1 (BUY)  -> earn -1%  -> $1.02 * 0.99 = $1.01
