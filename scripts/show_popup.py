#!/usr/bin/env python3
"""Show a popup chart with all strategy lines: LLM, Advisor, S&P 500, and Quant Model.

Usage:
    python scripts/show_popup.py
    python scripts/show_popup.py --start 2022-01-01 --end 2024-12-31
    python scripts/show_popup.py --frequency M  # Monthly
    python scripts/show_popup.py --interactive  # Open interactive HTML chart
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import VisorConfig
from main import run_backtest
from plotting import plot_series, plot_series_interactive


def main():
    parser = argparse.ArgumentParser(
        description="Show popup chart with LLM, Advisor, S&P 500, and Quant lines"
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
        "--interactive",
        action="store_true",
        help="Open interactive HTML chart instead of matplotlib popup",
    )
    parser.add_argument(
        "--no-advisor",
        action="store_true",
        help="Exclude advisor from the chart",
    )
    parser.add_argument(
        "--quant-model",
        default="trend_momentum_rsi_vol",
        choices=["trend_momentum_rsi_vol", "sma_crossover", "vol_adjusted_momentum"],
        help="Quantitative model to use",
    )
    parser.add_argument(
        "--live-llm",
        action="store_true",
        help="Use live OpenAI API calls instead of CSV signals (requires OPENAI_API_KEY)",
    )
    parser.add_argument(
        "--llm-model",
        default="gpt-4o-mini",
        help="OpenAI model to use for live LLM mode (e.g., gpt-4o-mini, gpt-4o)",
    )
    args = parser.parse_args()

    # Create config - using SPX since that's what prices.csv has
    config = VisorConfig(
        start=args.start,
        end=args.end,
        frequency=args.frequency,
        advisor_ticker="AOR",
        advisor_data_csv=None,
        include_advisor=not args.no_advisor,
        advisor_mode="synthetic",
        advisor_underperformance_annual=0.015,
        benchmark_ticker="SPX",  # Match prices.csv column name
        llm_signals_dir="data/llm_signals",
        output_dir="outputs",
        prices_csv="data/prices.csv",
        prices_date_column="date",
        use_synthetic_data=False,
        advisor_fee_annual=0.01,
        show_plot=not args.interactive,  # Show matplotlib if not interactive
        no_save_outputs=True,  # Don't save files for quick popup
        quant_model=args.quant_model,
        interactive_html=args.interactive,
        open_html=args.interactive,
        risk_free_annual=0.02,
        realtime_prices=False,
        llm_mode="openai" if args.live_llm else "csv",
        llm_models=[args.llm_model],
        llm_temperature=0.7,
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
    )

    print(f"Running backtest from {config.start} to {config.end} ({config.frequency})...")
    print(f"Quant model: {config.quant_model}")
    print(f"Include advisor: {config.include_advisor}")
    print(f"LLM mode: {config.llm_mode}" + (f" ({args.llm_model})" if args.live_llm else " (from CSV files)"))
    print()

    try:
        series_df, metrics_df, best_strategy, best_excess, output_dir = run_backtest(config)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("\n=== Strategy Performance ===")
    print(f"Date range: {series_df.index[0].date()} to {series_df.index[-1].date()}")
    print(f"Number of periods: {len(series_df)}")
    print()

    # Show final values
    final_values = series_df.iloc[-1].sort_values(ascending=False)
    print("Final growth of $1:")
    for name, value in final_values.items():
        print(f"  {name}: ${value:.4f}")

    print()
    print(f"Best strategy vs S&P 500: {best_strategy} (excess: {best_excess:.4f})")

    # Show the chart
    if args.interactive:
        print("\nOpening interactive chart in browser...")
        path = plot_series_interactive(series_df, output_dir=None, open_browser=True)
        print(f"Chart saved to: {path}")
    else:
        print("\nShowing matplotlib popup...")
        plot_series(series_df, output_dir=None, show=True, frequency=config.frequency)


if __name__ == "__main__":
    main()
