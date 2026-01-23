import argparse
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class VisorConfig:
    start: str
    end: str
    frequency: str  # "M" or "W"
    advisor_ticker: str
    advisor_data_csv: Optional[str]
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


def parse_args() -> VisorConfig:
    parser = argparse.ArgumentParser(description="Visor backtest runner")
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default=datetime.today().strftime("%Y-%m-%d"))
    parser.add_argument("--frequency", default="M", choices=["D", "W", "M"])
    parser.add_argument("--advisor-ticker", default="AOR")
    parser.add_argument(
        "--advisor-data-csv",
        default=None,
        help="Optional CSV with advisor returns or values (columns: date + return|value)",
    )
    parser.add_argument("--benchmark-ticker", default="SPY")
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
    parser.add_argument("--risk-free-annual", type=float, default=0.02)
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
    args = parser.parse_args()
    return VisorConfig(
        start=args.start,
        end=args.end,
        frequency=args.frequency,
        advisor_ticker=args.advisor_ticker,
        advisor_data_csv=args.advisor_data_csv,
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
    )
