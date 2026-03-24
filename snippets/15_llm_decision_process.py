# ============================================================
# SNIPPET 15: How Each LLM Makes a BUY/SELL Decision
# ============================================================
# Each day, the LLM looks at recent market data and computes
# a "buy score" (0 to 1). Higher score = more likely to BUY.
#
# The LLM checks:
#   - Last 5 days of returns (is the market dropping?)
#   - 20-day trend (is the market in a downtrend?)
#   - Recent volatility (is the market shaking?)
# Then adds randomness so each run gives different results.
# ============================================================

for idx in range(len(returns)):
    # Start with the model's base aggression (bias toward investing)
    buy_score = aggression

    # Look at the last 5 days of market returns
    recent_5 = returns.iloc[max(0, idx - 5):idx]
    recent_mean = recent_5.mean()
    recent_vol = recent_5.std()

    # Check the 20-day price trend
    lookback = min(idx, 20)
    trend = prices.iloc[idx] / prices.iloc[idx - lookback] - 1

    # RULE 1: If recent returns are negative, reduce buy score
    if recent_mean < -0.005:       # Losing > 0.5% per day
        buy_score -= skill * 0.4
    if recent_mean < -0.015:       # Losing > 1.5% per day (bad)
        buy_score -= skill * 0.3

    # RULE 2: If the trend is negative, reduce buy score
    if trend < -0.02:              # Market down > 2% over 20 days
        buy_score -= skill * 0.3
    elif trend > 0.03:             # Market up > 3% over 20 days
        buy_score += 0.1

    # RULE 3: If volatility is spiking, reduce buy score
    if recent_vol > 0.02:          # Daily swings > 2%
        buy_score -= skill * 0.2

    # RULE 4: Add randomness (simulates LLM "temperature")
    noise = rng.normal(0, 0.15)
    buy_score += noise

    # Clamp between 0 and 1, then flip a weighted coin
    buy_score = max(0.0, min(1.0, buy_score))
    signal = 1.0 if rng.random() < buy_score else 0.0  # BUY or SELL
