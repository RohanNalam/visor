# ============================================================
# SNIPPET 21: Finding the Winner
# ============================================================
# After all strategies run over the same time period,
# compare final values to determine who beat the S&P 500.
#
# Excess = strategy's final value - S&P 500's final value
# Positive excess = BEAT the market
# Negative excess = LOST to the market
# Highest excess = WINNER
# ============================================================

# Get the final value of each strategy (what $1 became)
sp500_final = series_df["S&P 500"].iloc[-1]   # e.g., $2.14
final_values = series_df.iloc[-1]              # All strategies

# Subtract S&P 500 from each to get excess return
excess_over_sp = (final_values - sp500_final).drop("S&P 500")

# The strategy with the highest excess wins
best_strategy = excess_over_sp.idxmax()
best_excess = excess_over_sp.loc[best_strategy]

# Example output:
# S&P 500:       $2.14 (the benchmark - always at 0 excess)
# Advisor:       $1.96  -> excess = 1.96 - 2.14 = -0.18 (lost $0.18)
# GPT:           $2.21  -> excess = 2.21 - 2.14 = +0.07 (beat by $0.07)
# Claude Sonnet: $1.94  -> excess = 1.94 - 2.14 = -0.20 (lost $0.20)
# Quant Model:   $1.88  -> excess = 1.88 - 2.14 = -0.26 (lost $0.26)
#
# Winner: GPT with +0.07 excess over S&P 500
