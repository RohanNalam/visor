# ============================================================
# SNIPPET 13: The Quant Model Decision Rule (2 out of 4)
# ============================================================
# The quant model checks 4 conditions every period:
#   1. Trend up?      (Moving Average Crossover)
#   2. Momentum up?   (Price higher than 3 periods ago)
#   3. RSI < 70?      (Market not overbought)
#   4. Volatility OK? (Market calmer than usual)
#
# If at least 2 out of 4 are True -> BUY (invest in S&P 500)
# If fewer than 2 are True        -> SELL (stay in cash)
# ============================================================

def _trend_momentum_rsi_vol(returns):
    prices = (1 + returns).cumprod()

    # The 4 indicators
    momentum = prices / prices.shift(3) - 1
    trend = prices.rolling(6).mean() / prices.rolling(12).mean() - 1
    volatility = returns.rolling(6).std()
    rsi = _rsi(prices, window=14)

    # Check each condition
    trend_up = trend > 0               # Condition 1
    momentum_up = momentum > 0         # Condition 2
    vol_ok = volatility < volatility.rolling(12).median()  # Condition 3
    rsi_ok = rsi < 70                  # Condition 4

    # Count how many conditions are True
    conditions_met = (trend_up.astype(int) + momentum_up.astype(int)
                      + vol_ok.astype(int) + rsi_ok.astype(int))

    # BUY if at least 2 out of 4 conditions are met
    signal = conditions_met >= 2
    return signal.astype(float).fillna(0.0)

# Example:
# trend_up=True(1), momentum_up=True(1), vol_ok=False(0), rsi_ok=True(1)
# conditions_met = 1 + 1 + 0 + 1 = 3
# 3 >= 2, so signal = 1.0 (BUY)
#
# trend_up=False(0), momentum_up=False(0), vol_ok=True(1), rsi_ok=False(0)
# conditions_met = 0 + 0 + 1 + 0 = 1
# 1 < 2, so signal = 0.0 (SELL, stay in cash)
