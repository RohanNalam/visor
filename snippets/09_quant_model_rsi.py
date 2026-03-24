# ============================================================
# SNIPPET 9: RSI (Relative Strength Index)
# ============================================================
# Formula: RS = Average Gain / Average Loss (over 14 periods)
#          RSI = 100 - (100 / (1 + RS))
#
# RSI ranges from 0 to 100.
# Above 70 = "overbought" (market went up too fast, might crash)
# Below 30 = "oversold" (market dropped too hard, might bounce)
# Below 70 = safe to invest
# ============================================================

def _rsi(prices, window=14):
    delta = prices.diff()                               # Price changes
    gain = delta.clip(lower=0).rolling(window).mean()   # Average gains
    loss = (-delta.clip(upper=0)).rolling(window).mean() # Average losses
    rs = gain / loss.replace(0, pd.NA)                  # Relative strength
    return 100 - (100 / (1 + rs))                       # RSI formula

rsi = _rsi(prices, window=14)
rsi_ok = rsi < 70  # True = safe to buy, False = overbought

# Example:
# Average gain over 14 days = $20, Average loss = $10
# RS = 20/10 = 2
# RSI = 100 - (100 / (1+2)) = 100 - 33.3 = 66.7
# 66.7 < 70, so rsi_ok = True (safe to buy)
