# ============================================================
# SNIPPET 8: Preventing Look-Ahead Bias
# ============================================================
# Formula: rt_portfolio = Signal(t-1) * rt
#
# The decision from YESTERDAY is applied to TODAY's return.
# This prevents the model from "cheating" by seeing the future.
#
# shift(1) moves every signal forward by one period.
# Monday's decision -> applied to Tuesday's return.
# ============================================================

# Quant model: shift signals by 1 period
def quant_model_signals(returns, model):
    signals = QUANT_MODELS[model](returns)
    return signals.shift(1).fillna(0.0)  # Yesterday's signal for today

# LLM models: same shift applied
for model, signal in llm_signals.items():
    raw_signal = signal.reindex(spy_returns.index).ffill().fillna(0.0)
    aligned_signal = raw_signal.shift(1).fillna(0.0)  # Yesterday's signal
    llm_series[model] = compute_strategy_series(spy_returns, aligned_signal)

# Example:
# Day  | Signal computed | Signal USED | Market return | You earn
# Mon  | BUY (1)        | --          | +1%           | 0% (no signal yet)
# Tue  | SELL (0)       | BUY (1)     | -2%           | -2% (Mon's BUY)
# Wed  | BUY (1)        | SELL (0)    | +3%           | 0% (Tue's SELL)
# Thu  | BUY (1)        | BUY (1)     | +1%           | +1% (Wed's BUY)
