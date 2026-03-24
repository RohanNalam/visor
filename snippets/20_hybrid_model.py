# ============================================================
# SNIPPET 20: The Hybrid Model (Advisor + Best AI Signals)
# ============================================================
# From the methodology: "If the LLM or quant model beats the
# advisor, combine them to see if advisors stay relevant."
#
# The Hybrid takes the BEST model's BUY/SELL signals and
# applies them to the ADVISOR's returns. This answers:
# "If an advisor used AI to tell them when to buy and sell,
#  would they perform better than either one alone?"
# ============================================================

# Step 1: Find which non-advisor strategy performed best
non_advisor_excess = excess_over_sp.drop("Advisor", errors="ignore")
best_signal_strategy = non_advisor_excess.idxmax()

# Step 2: Get that strategy's BUY/SELL signals
if best_signal_strategy in llm_series:
    hybrid_signal = align_signals_to_returns(
        llm_signals[best_signal_strategy], advisor_returns.index
    )
    hybrid_label = f"Hybrid (Advisor + {best_signal_strategy})"

# Step 3: Apply the AI's signals to the advisor's returns
hybrid_series = compute_strategy_series(advisor_returns, hybrid_signal)

# What this means:
# - When GPT says BUY, the advisor invests (earns advisor returns)
# - When GPT says SELL, the advisor goes to cash (earns 0%)
# - The advisor still has their 1.5% underperformance and 1% fee
# - But now they dodge crashes using AI timing
#
# If Hybrid beats both Advisor and the AI alone:
#   -> Advisors have a future WITH AI assistance
# If Hybrid still loses to AI alone:
#   -> Advisors add no value, AI replaces them
