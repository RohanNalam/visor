# ============================================================
# SNIPPET 18: The LLM Prompt Template (for Live API Mode)
# ============================================================
# When using real LLM APIs (GPT, Claude, etc.), each model
# receives this exact prompt for every trading day.
#
# The prompt ONLY gives data up to today. It never reveals
# tomorrow's prices. This prevents look-ahead bias.
# ============================================================

def _build_llm_prompt(current_date, recent_returns, trend_20d, volatility_20d):
    returns_list = [f"{value:.2%}" for value in recent_returns.tolist()]
    return (
        "You are a financial decision assistant.\n\n"
        f"Date: {current_date.date().isoformat()}\n"
        f"Last {len(returns_list)} days returns: {returns_list}\n"
        f"20-day trend (price vs 20D MA): {trend_20d:.2%}\n"
        f"20-day volatility: {volatility_20d:.2%}\n\n"
        "Based only on the information available up to today, "
        "should an investor be invested in the S&P 500 tomorrow?\n"
        "Respond with exactly one word: BUY, HOLD, or SELL."
    )

# Example prompt sent to GPT for June 15, 2024:
# --------------------------------------------------
# You are a financial decision assistant.
#
# Date: 2024-06-15
# Last 5 days returns: ['0.50%', '-0.20%', '0.80%', '0.10%', '-0.30%']
# 20-day trend (price vs 20D MA): 3.20%
# 20-day volatility: 1.10%
#
# Based only on the information available up to today,
# should an investor be invested in the S&P 500 tomorrow?
# Respond with exactly one word: BUY, HOLD, or SELL.
# --------------------------------------------------
# GPT responds: "BUY" -> converted to signal = 1.0
