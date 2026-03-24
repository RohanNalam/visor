from __future__ import annotations

import argparse
import os
import subprocess
from datetime import date, datetime, timedelta

from config import VisorConfig
from main import run_backtest
from plotting import save_series_chart


def _default_dates() -> tuple[str, str]:
    end = date.today()
    start = end - timedelta(days=365 * 5)
    return start.isoformat(), end.isoformat()


def _normalize_date(value: str) -> str:
    raw = value.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y"):
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            continue
    raise ValueError("Date must be YYYY-MM-DD or MM/DD/YYYY.")


def _prompt_if_missing(value: str, label: str, default: str) -> str:
    if value:
        return value
    entered = input(f"{label} [{default}]: ").strip()
    return entered or default


def run_headless(
    start: str,
    end: str,
    frequency: str,
    include_advisor: bool,
    llm_mode: str,
) -> None:
    config = VisorConfig(
        start=_normalize_date(start),
        end=_normalize_date(end),
        frequency=frequency.strip().upper(),
        advisor_ticker="AOR",
        advisor_data_csv=None,
        include_advisor=include_advisor,
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
        no_save_outputs=False,
        quant_model="trend_momentum_rsi_vol",
        interactive_html=False,
        open_html=False,
        risk_free_annual=0.02,
        realtime_prices=False,
        llm_mode=llm_mode,
        llm_models=["gpt-4o-mini"],
        llm_temperature=0.7,
        openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", ""),
    )
    series_df, _, _, _, output_dir = run_backtest(config)
    start_dt = datetime.fromisoformat(config.start)
    end_dt = datetime.fromisoformat(config.end)
    series_df = series_df.loc[(series_df.index >= start_dt) & (series_df.index <= end_dt)]
    if series_df.empty:
        raise SystemExit("No data for the selected date range.")
    if not output_dir:
        raise SystemExit("No output directory created.")
    safe_start = config.start.replace("-", "")
    safe_end = config.end.replace("-", "")
    chart_path = os.path.join(output_dir, f"visor_chart_{safe_start}_{safe_end}.png")
    save_series_chart(series_df, chart_path, frequency=config.frequency, daily_grid=True)
    subprocess.run(["open", "-a", "Preview", chart_path], check=False)
    print(f"Opened chart: {chart_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Visor chart runner")
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--frequency", default="D", choices=["D", "W", "M"])
    parser.add_argument("--include-advisor", action="store_true")
    parser.add_argument(
        "--llm-mode",
        default=None,
        choices=["openai", "csv"],
        help="Use live OpenAI calls or CSV signals",
    )
    args = parser.parse_args()

    start_default, end_default = _default_dates()
    start = _prompt_if_missing(args.start, "Start date (YYYY-MM-DD)", start_default)
    end = _prompt_if_missing(args.end, "End date (YYYY-MM-DD)", end_default)
    frequency = args.frequency
    include = args.include_advisor
    if not args.start and not args.end:
        include_input = input("Include advisor? (y/n) [y]: ").strip().lower() or "y"
        include = include_input.startswith("y")

    if args.llm_mode:
        llm_mode = args.llm_mode
    else:
        llm_mode = "openai" if os.environ.get("OPENAI_API_KEY") else "csv"

    run_headless(start, end, frequency, include, llm_mode)
