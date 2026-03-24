# ============================================================
# SNIPPET 16: Worked Example - DeepSeek Dodging a Crash
# ============================================================
# DeepSeek: skill=0.65 (best at spotting crashes), aggression=0.75
#
# Scenario: March 2020 COVID crash. The market has been
# dropping for 5 days straight, trend is very negative.
# ============================================================

# DeepSeek starts with its aggression as the base buy score
buy_score = 0.75

# Step 1: Last 5 days averaged -2% per day (market is crashing)
recent_mean = -0.02
# recent_mean < -0.005, so:
buy_score -= 0.65 * 0.4   # buy_score = 0.75 - 0.26 = 0.49
# recent_mean < -0.015, so ALSO:
buy_score -= 0.65 * 0.3   # buy_score = 0.49 - 0.195 = 0.295

# Step 2: 20-day trend is -15% (massive downtrend)
trend = -0.15
# trend < -0.02, so:
buy_score -= 0.65 * 0.3   # buy_score = 0.295 - 0.195 = 0.10

# Step 3: Volatility is 4% per day (extremely shaky)
recent_vol = 0.04
# recent_vol > 0.02, so:
buy_score -= 0.65 * 0.2   # buy_score = 0.10 - 0.13 = -0.03

# Step 4: Add random noise of +0.05
buy_score += 0.05          # buy_score = 0.02

# Clamp to [0, 1]
buy_score = max(0.0, min(1.0, 0.02))  # buy_score = 0.02

# RESULT: Only 2% chance of buying.
# DeepSeek almost certainly stays in cash and DODGES the crash.
# While the S&P 500 drops -12% that month, DeepSeek loses 0%.
