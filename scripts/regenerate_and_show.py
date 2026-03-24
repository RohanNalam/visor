#!/usr/bin/env python3
"""Regenerate LLM signals with fresh randomness and show the chart.

This simulates multiple LLMs trying different strategies to beat the S&P 500.
Each run generates new signals, so the results change every time.

Usage:
    python scripts/regenerate_and_show.py
    python scripts/regenerate_and_show.py --start 2022-01-01 --end 2024-12-31
    python scripts/regenerate_and_show.py --aggressive  # More bullish signals
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import time
from datetime import date

import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import VisorConfig
from main import run_backtest
from plotting import plot_series, plot_series_interactive

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
LLM_SIGNALS_DIR = os.path.join(DATA_DIR, "llm_signals")
PRICES_CSV = os.path.join(DATA_DIR, "prices.csv")


def load_price_data() -> tuple[pd.DatetimeIndex, pd.Series]:
    """Load dates and returns from prices.csv."""
    df = pd.read_csv(PRICES_CSV)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    returns = df["SPX"].pct_change().dropna()
    return returns.index, returns


def generate_smart_signals(
    dates: pd.DatetimeIndex,
    returns: pd.Series,
    model_name: str,
    seed: int,
    aggressive: bool = False,
) -> pd.DataFrame:
    """Generate signals that try to be smart about market conditions.

    Each model has a different "personality":
    - gpt: Trend follower - buys when momentum is positive
    - claude_sonnet: Contrarian - buys on dips
    - gemini: Balanced - uses moving averages
    - deepseek: Volatility-based - avoids high volatility
    - grok: Momentum chaser - follows strong moves
    """
    random.seed(seed)

    # Calculate some market indicators
    prices = (1 + returns).cumprod()
    ma_5 = prices.rolling(5).mean()
    ma_20 = prices.rolling(20).mean()
    volatility = returns.rolling(10).std()
    momentum_5 = prices / prices.shift(5) - 1

    signals = []

    for i, date_val in enumerate(dates):
        if i < 20:
            # Not enough data yet
            signals.append({"date": date_val.strftime("%Y-%m-%d"), "signal": "HOLD"})
            continue

        # Get indicators for this date
        current_price = prices.iloc[i] if i < len(prices) else prices.iloc[-1]
        current_ma5 = ma_5.iloc[i] if i < len(ma_5) else ma_5.iloc[-1]
        current_ma20 = ma_20.iloc[i] if i < len(ma_20) else ma_20.iloc[-1]
        current_vol = volatility.iloc[i] if i < len(volatility) else volatility.iloc[-1]
        current_momentum = momentum_5.iloc[i] if i < len(momentum_5) else momentum_5.iloc[-1]
        avg_vol = volatility.iloc[:i].median() if i > 0 else 0.01

        # Each model has different logic
        if "gpt" in model_name.lower():
            # Trend follower with some randomness
            trend_score = 0.6 if current_ma5 > current_ma20 else 0.3
            if aggressive:
                trend_score += 0.15
            signal = "BUY" if random.random() < trend_score else ("HOLD" if random.random() < 0.5 else "SELL")

        elif "claude" in model_name.lower():
            # Contrarian - buys on dips
            if current_momentum < -0.02:
                buy_prob = 0.7 if aggressive else 0.6
            elif current_momentum > 0.03:
                buy_prob = 0.3
            else:
                buy_prob = 0.5
            signal = "BUY" if random.random() < buy_prob else ("HOLD" if random.random() < 0.6 else "SELL")

        elif "gemini" in model_name.lower():
            # Moving average crossover with noise
            if current_ma5 > current_ma20 * 1.01:
                buy_prob = 0.75 if aggressive else 0.65
            elif current_ma5 < current_ma20 * 0.99:
                buy_prob = 0.25
            else:
                buy_prob = 0.5
            signal = "BUY" if random.random() < buy_prob else ("HOLD" if random.random() < 0.4 else "SELL")

        elif "deepseek" in model_name.lower():
            # Volatility-based - conservative in high vol
            if current_vol > avg_vol * 1.5:
                buy_prob = 0.2  # Cautious in high volatility
            elif current_vol < avg_vol * 0.7:
                buy_prob = 0.7 if aggressive else 0.6  # Confident in low volatility
            else:
                buy_prob = 0.5
            signal = "BUY" if random.random() < buy_prob else ("HOLD" if random.random() < 0.5 else "SELL")

        elif "grok" in model_name.lower():
            # Momentum chaser - aggressive
            if current_momentum > 0.02:
                buy_prob = 0.8 if aggressive else 0.7
            elif current_momentum < -0.02:
                buy_prob = 0.2
            else:
                buy_prob = 0.55
            signal = "BUY" if random.random() < buy_prob else ("HOLD" if random.random() < 0.3 else "SELL")

        else:
            # Default random
            buy_prob = 0.5 if not aggressive else 0.6
            signal = "BUY" if random.random() < buy_prob else ("HOLD" if random.random() < 0.5 else "SELL")

        signals.append({"date": date_val.strftime("%Y-%m-%d"), "signal": signal})

    return pd.DataFrame(signals)


def regenerate_all_signals(aggressive: bool = False) -> None:
    """Regenerate signals for all models with new random seeds."""
    os.makedirs(LLM_SIGNALS_DIR, exist_ok=True)

    dates, returns = load_price_data()

    # Use current time as base seed so each run is different
    base_seed = int(time.time() * 1000) % 1000000

    models = [
        ("gpt", base_seed),
        ("claude_sonnet", base_seed + 1),
        ("gemini", base_seed + 2),
        ("deepseek", base_seed + 3),
        ("grok", base_seed + 4),
    ]

    print(f"Regenerating LLM signals (seed base: {base_seed})...")
    print(f"Mode: {'AGGRESSIVE' if aggressive else 'NORMAL'}")

    for model_name, seed in models:
        df = generate_smart_signals(dates, returns, model_name, seed, aggressive)
        path = os.path.join(LLM_SIGNALS_DIR, f"{model_name}.csv")
        df.to_csv(path, index=False)

        buy_count = (df["signal"] == "BUY").sum()
        hold_count = (df["signal"] == "HOLD").sum()
        sell_count = (df["signal"] == "SELL").sum()
        buy_pct = buy_count / len(df) * 100
        print(f"  {model_name}: BUY={buy_count} ({buy_pct:.1f}%), HOLD={hold_count}, SELL={sell_count}")


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate LLM signals and show chart - results change each run!"
    )
    parser.add_argument(
        "--start",
        default="2020-01-01",
        help="Start date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end",
        default=date.today().isoformat(),
        help="End date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--frequency",
        default="D",
        choices=["D", "W", "M"],
        help="Data frequency: D=daily, W=weekly, M=monthly",
    )
    parser.add_argument(
        "--aggressive",
        action="store_true",
        help="Make LLMs more aggressive (more BUY signals)",
    )
    parser.add_argument(
        "--no-regenerate",
        action="store_true",
        help="Skip regenerating signals, use existing CSV files",
    )
    parser.add_argument(
        "--no-advisor",
        action="store_true",
        help="Exclude advisor from the chart",
    )
    args = parser.parse_args()

    # Regenerate signals with fresh randomness
    if not args.no_regenerate:
        regenerate_all_signals(aggressive=args.aggressive)
        print()

    # Create config
    config = VisorConfig(
        start=args.start,
        end=args.end,
        frequency=args.frequency,
        advisor_ticker="AOR",
        advisor_data_csv=None,
        include_advisor=not args.no_advisor,
        advisor_mode="synthetic",
        advisor_underperformance_annual=0.015,
        benchmark_ticker="SPX",
        llm_signals_dir="data/llm_signals",
        output_dir="outputs",
        prices_csv="data/prices.csv",
        prices_date_column="date",
        use_synthetic_data=False,
        advisor_fee_annual=0.01,
        show_plot=False,
        no_save_outputs=True,
        quant_model="trend_momentum_rsi_vol",
        interactive_html=True,
        open_html=True,
        risk_free_annual=0.02,
        realtime_prices=False,
        llm_mode="csv",
        llm_models=["gpt-4o-mini"],
        llm_temperature=0.7,
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
    )

    print(f"Running backtest from {config.start} to {config.end}...")

    try:
        series_df, metrics_df, best_strategy, best_excess, output_dir = run_backtest(config)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Show results
    print("\n" + "=" * 50)
    print("RESULTS - Who beat the S&P 500?")
    print("=" * 50)

    sp500_final = series_df["S&P 500"].iloc[-1]
    final_values = series_df.iloc[-1].sort_values(ascending=False)

    print(f"\nFinal growth of $1 invested:")
    for name, value in final_values.items():
        excess = value - sp500_final
        status = "BEAT S&P!" if excess > 0 and name != "S&P 500" else ""
        print(f"  {name}: ${value:.4f} ({excess:+.4f}) {status}")

    # Find winner
    winners = [(name, val) for name, val in final_values.items()
               if name != "S&P 500" and val > sp500_final]

    if winners:
        print(f"\n🏆 WINNERS that beat S&P 500:")
        for name, val in winners:
            print(f"   - {name}: ${val:.4f}")
    else:
        print(f"\n😢 No strategy beat the S&P 500 this time. Run again for different results!")

    print("\nOpening interactive chart...")
    path = plot_series_interactive(series_df, output_dir=None, open_browser=True)
    print(f"Chart saved to: {path}")
    print("\n💡 Tip: Run again to see different LLM strategies compete!")


if __name__ == "__main__":
    main()
