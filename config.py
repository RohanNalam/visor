import argparse
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class VisorConfig:
    start: str
    end: str
    frequency: str  # "M" or "W"
    advisor_ticker: str
    advisor_data_csv: Optional[str]
    include_advisor: bool
    advisor_mode: str
    advisor_underperformance_annual: float
    benchmark_ticker: str
    llm_signals_dir: str
    output_dir: str
    prices_csv: Optional[str]
    prices_date_column: str
    use_synthetic_data: bool
    advisor_fee_annual: float
    show_plot: bool
    no_save_outputs: bool
    quant_model: str
    interactive_html: bool
    open_html: bool
    risk_free_annual: float
    realtime_prices: bool
    llm_mode: str
    llm_models: list[str]
    llm_temperature: float
    openai_api_key: str
    anthropic_api_key: str
    random_seed: Optional[int]


def parse_args() -> VisorConfig:
    parser = argparse.ArgumentParser(description="Visor backtest runner")
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default="2026-03-31")
    parser.add_argument("--frequency", default="M", choices=["D", "W", "M"])
    parser.add_argument("--advisor-ticker", default="AOR")
    parser.add_argument(
        "--advisor-data-csv",
        default=None,
        help="Optional CSV with advisor returns or values (columns: date + return|value)",
    )
    parser.add_argument(
        "--advisor-mode",
        default="synthetic",
        choices=["synthetic", "proxy"],
        help="Advisor series mode: synthetic underperformance or proxy ticker",
    )
    parser.add_argument(
        "--advisor-underperformance-annual",
        type=float,
        default=0.015,
        help="Annual underperformance for synthetic advisor (e.g., 0.015 = 1.5%%)",
    )
    parser.add_argument(
        "--no-advisor",
        action="store_true",
        help="Skip advisor series and metrics",
    )
    parser.add_argument("--benchmark-ticker", default="SPX")
    parser.add_argument("--llm-signals-dir", default="data/llm_signals")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument(
        "--prices-csv",
        default=None,
        help="Optional CSV of prices with date column and ticker columns",
    )
    parser.add_argument("--prices-date-column", default="date")
    parser.add_argument(
        "--use-synthetic-data",
        action="store_true",
        help="Generate synthetic price data instead of fetching",
    )
    parser.add_argument("--risk-free-annual", type=float, default=0.04)
    parser.add_argument("--advisor-fee-annual", type=float, default=0.01)
    parser.add_argument(
        "--show-plot",
        action="store_true",
        help="Show the main chart in a popup window",
    )
    parser.add_argument(
        "--no-save-outputs",
        action="store_true",
        help="Do not write files to outputs/, only show plot/console",
    )
    parser.add_argument(
        "--quant-model",
        default="trend_momentum_rsi_vol",
        choices=["trend_momentum_rsi_vol", "sma_crossover", "vol_adjusted_momentum"],
    )
    parser.add_argument(
        "--interactive-html",
        action="store_true",
        help="Create an interactive HTML chart (pan/zoom)",
    )
    parser.add_argument(
        "--open-html",
        action="store_true",
        help="Open the interactive chart in the browser",
    )
    parser.add_argument(
        "--realtime-prices",
        action="store_true",
        help="Append latest intraday prices from yfinance",
    )
    parser.add_argument(
        "--llm-mode",
        default="csv",
        choices=["csv", "openai", "api"],
        help="LLM signal source: csv files or live API calls (api/openai)",
    )
    parser.add_argument(
        "--llm-models",
        default="gpt-4o-mini",
        help="Comma-separated LLM model names",
    )
    parser.add_argument(
        "--llm-temperature",
        type=float,
        default=0.7,
        help="LLM sampling temperature",
    )
    parser.add_argument(
        "--openai-api-key",
        default=None,
        help="OpenAI API key (or set OPENAI_API_KEY env var)",
    )
    parser.add_argument(
        "--anthropic-api-key",
        default=None,
        help="Anthropic API key (or set ANTHROPIC_API_KEY env var)",
    )
    parser.add_argument(
        "--random-seed",
        type=int,
        default=42,
        help="Global random seed for reproducible LLM simulation (set to lock results)",
    )
    args = parser.parse_args()
    return VisorConfig(
        start=args.start,
        end=args.end,
        frequency=args.frequency,
        advisor_ticker=args.advisor_ticker,
        advisor_data_csv=args.advisor_data_csv,
        include_advisor=not args.no_advisor,
        advisor_mode=args.advisor_mode,
        advisor_underperformance_annual=args.advisor_underperformance_annual,
        benchmark_ticker=args.benchmark_ticker,
        llm_signals_dir=args.llm_signals_dir,
        output_dir=args.output_dir,
        prices_csv=args.prices_csv,
        prices_date_column=args.prices_date_column,
        use_synthetic_data=args.use_synthetic_data,
        advisor_fee_annual=args.advisor_fee_annual,
        show_plot=args.show_plot,
        no_save_outputs=args.no_save_outputs,
        quant_model=args.quant_model,
        interactive_html=args.interactive_html,
        open_html=args.open_html,
        risk_free_annual=args.risk_free_annual,
        realtime_prices=args.realtime_prices,
        llm_mode=args.llm_mode,
        llm_models=[m.strip() for m in args.llm_models.split(",") if m.strip()],
        llm_temperature=args.llm_temperature,
        openai_api_key=args.openai_api_key or os.environ.get("OPENAI_API_KEY", ""),
        anthropic_api_key=args.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY", ""),
        random_seed=args.random_seed,
    )
