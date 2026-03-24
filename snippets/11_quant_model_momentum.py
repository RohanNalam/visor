# ============================================================
# SNIPPET 11: Momentum Indicator
# ============================================================
# Formula: Momentum = Pt / Pt-3 - 1
#
# Compares today's price to the price 3 periods ago.
# If today's price is higher, the market has upward momentum.
# Momentum traders believe things going up keep going up.
# ============================================================

prices = (1 + returns).cumprod()  # Convert returns to prices

# How much has the price changed over the last 3 periods?
momentum = prices / prices.shift(3) - 1
momentum_up = momentum > 0  # True if price went up

# Example:
# Price today = $4200, Price 3 months ago = $4000
# Momentum = (4200/4000) - 1 = +5% -> momentum_up = True (BUY)
#
# Price today = $3800, Price 3 months ago = $4000
# Momentum = (3800/4000) - 1 = -5% -> momentum_up = False (SELL)
