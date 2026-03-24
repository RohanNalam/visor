"""Generate sample LLM signals for backtesting.

This script creates realistic-looking LLM signals that span the full
date range of the prices.csv file.
"""

import os
import random
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
LLM_SIGNALS_DIR = os.path.join(DATA_DIR, "llm_signals")
PRICES_CSV = os.path.join(DATA_DIR, "prices.csv")


def load_price_dates() -> pd.DatetimeIndex:
    """Load dates from prices.csv."""
    df = pd.read_csv(PRICES_CSV)
    df["date"] = pd.to_datetime(df["date"])
    return df["date"].sort_values()


def generate_signals(dates: pd.DatetimeIndex, model_name: str, seed: int) -> pd.DataFrame:
    """Generate sample signals for a model.

    Uses a simple momentum-like logic with some randomness to create
    realistic-looking signals that vary by model.
    """
    random.seed(seed)

    signals = []
    prev_signal = "HOLD"

    for i, date in enumerate(dates):
        # Base probability weighted toward staying in same state
        if prev_signal == "BUY":
            probs = {"BUY": 0.7, "HOLD": 0.2, "SELL": 0.1}
        elif prev_signal == "SELL":
            probs = {"BUY": 0.15, "HOLD": 0.25, "SELL": 0.6}
        else:  # HOLD
            probs = {"BUY": 0.35, "HOLD": 0.4, "SELL": 0.25}

        # Add some model-specific bias
        if "gpt" in model_name.lower():
            probs["BUY"] += 0.05
        elif "claude" in model_name.lower():
            probs["HOLD"] += 0.05
        elif "gemini" in model_name.lower():
            probs["SELL"] += 0.03

        # Normalize
        total = sum(probs.values())
        probs = {k: v / total for k, v in probs.items()}

        # Random selection
        r = random.random()
        cumsum = 0
        signal = "HOLD"
        for s, p in probs.items():
            cumsum += p
            if r < cumsum:
                signal = s
                break

        signals.append({"date": date.strftime("%Y-%m-%d"), "signal": signal})
        prev_signal = signal

    return pd.DataFrame(signals)


def main():
    os.makedirs(LLM_SIGNALS_DIR, exist_ok=True)

    dates = load_price_dates()
    print(f"Loaded {len(dates)} dates from prices.csv")
    print(f"Date range: {dates.iloc[0]} to {dates.iloc[-1]}")

    models = [
        ("gpt", 42),
        ("claude_sonnet", 123),
        ("gemini", 456),
        ("deepseek", 789),
        ("grok", 101112),
    ]

    for model_name, seed in models:
        df = generate_signals(dates, model_name, seed)
        path = os.path.join(LLM_SIGNALS_DIR, f"{model_name}.csv")
        df.to_csv(path, index=False)

        buy_count = (df["signal"] == "BUY").sum()
        hold_count = (df["signal"] == "HOLD").sum()
        sell_count = (df["signal"] == "SELL").sum()
        print(f"Generated {model_name}.csv: BUY={buy_count}, HOLD={hold_count}, SELL={sell_count}")

    print(f"\nSignal files saved to {LLM_SIGNALS_DIR}")


if __name__ == "__main__":
    main()
