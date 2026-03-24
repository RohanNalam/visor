# ============================================================
# SNIPPET 10: Trend / Moving Average Crossover
# ============================================================
# Formula: Trend = SMA(6) / SMA(12) - 1
#
# SMA(6)  = Simple Moving Average over 6 periods (short-term)
# SMA(12) = Simple Moving Average over 12 periods (long-term)
#
# If the short-term average is ABOVE the long-term average,
# the market is trending upward = BUY signal.
# This is one of the most classic trading indicators.
# ============================================================

prices = (1 + returns).cumprod()  # Convert returns back to prices

# Calculate the two moving averages
short_average = prices.rolling(6).mean()   # 6-period average
long_average = prices.rolling(12).mean()   # 12-period average

# Trend = how much the short average is above/below the long average
trend = short_average / long_average - 1
trend_up = trend > 0  # True if short average > long average

# Example:
# 6-month average price  = $4200
# 12-month average price = $4100
# Trend = (4200/4100) - 1 = +2.4% -> trend_up = True (BUY)
#
# If 6-month avg = $3900, 12-month avg = $4100:
# Trend = (3900/4100) - 1 = -4.9% -> trend_up = False (SELL)
