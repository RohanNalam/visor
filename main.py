import json
import os
from dataclasses import asdict

import pandas as pd

from config import VisorConfig, parse_args
from data import (
    download_prices,
    generate_synthetic_prices,
    load_advisor_returns,
    load_prices_csv,
    to_period_returns,
)
from llm import align_signals_to_returns, load_llm_signals
from metrics import performance_metrics
from plotting import (
    plot_advisor_series,
    plot_metrics_bars,
    plot_series,
    plot_series_interactive,
)
from quant import compute_strategy_series, quant_model_name, quant_model_signals

def save_outputs(
    config: VisorConfig,
    series: pd.DataFrame,
    metrics: pd.DataFrame,
) -> str:
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(config.output_dir, f"run_{timestamp}")
    os.makedirs(out_dir, exist_ok=True)

    series.to_csv(os.path.join(out_dir, "strategy_series.csv"))
    metrics.to_csv(os.path.join(out_dir, "metrics.csv"))
    with open(os.path.join(out_dir, "config.json"), "w", encoding="utf-8") as f:
        json.dump(asdict(config), f, indent=2)
    return out_dir


def write_winner_summary(
    output_dir: str,
    best_strategy: str,
    best_excess: float,
    excess_over_sp: pd.Series,
) -> None:
    path = os.path.join(output_dir, "winner_summary.txt")
    lines = [
        "Visor Winner Summary",
        "======================",
        f"Best strategy vs S&P 500: {best_strategy}",
        f"Excess over S&P 500: {best_excess:.4f}",
        "",
        "Excess over S&P 500 by strategy:",
    ]
    for name, value in excess_over_sp.sort_values(ascending=False).items():
        lines.append(f"- {name}: {value:.4f}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def apply_annual_fee(returns: pd.Series, fee_annual: float, frequency: str) -> pd.Series:
    periods_per_year = 12 if frequency == "M" else 52
    fee_period = (1 + fee_annual) ** (1 / periods_per_year) - 1
    return returns - fee_period


def main() -> None:
    config = parse_args()
    os.makedirs(config.output_dir, exist_ok=True)

    tickers = [config.benchmark_ticker, config.advisor_ticker]
    if config.prices_csv:
        prices = load_prices_csv(
            config.prices_csv,
            config.prices_date_column,
            tickers,
            config.start,
            config.end,
        )
    elif config.use_synthetic_data:
        prices = generate_synthetic_prices(tickers, config.start, config.end)
    else:
        prices = download_prices(tickers, config.start, config.end)
    returns = to_period_returns(prices, config.frequency)

    spy_returns = returns[config.benchmark_ticker].dropna()
    if config.advisor_data_csv:
        advisor_returns = load_advisor_returns(
            config.advisor_data_csv,
            config.frequency,
            config.start,
            config.end,
        ).reindex(spy_returns.index)
    else:
        advisor_returns = returns[config.advisor_ticker].reindex(spy_returns.index)
    advisor_returns = advisor_returns.dropna()
    if spy_returns.empty or advisor_returns.empty:
        raise ValueError(
            "No return data in выбранный period. "
            "Check your date range, frequency, and prices CSV."
        )
    advisor_returns = apply_annual_fee(
        advisor_returns, config.advisor_fee_annual, config.frequency
    )

    llm_signals = load_llm_signals(config.llm_signals_dir, config.frequency)
    llm_series = {}
    for model, signal in llm_signals.items():
        aligned_signal = align_signals_to_returns(signal, spy_returns.index)
        llm_series[model] = compute_strategy_series(spy_returns, aligned_signal)

    quant_signal = quant_model_signals(spy_returns, config.quant_model)
    quant_series = compute_strategy_series(spy_returns, quant_signal)
    quant_label = f"Quant Model ({quant_model_name(config.quant_model)})"

    base_series = {
        "S&P 500": compute_strategy_series(spy_returns, None),
        "Advisor": compute_strategy_series(advisor_returns, None),
        quant_label: quant_series,
    }
    series_df = pd.DataFrame({**base_series, **llm_series}).dropna(how="all")

    sp500_final = series_df["S&P 500"].iloc[-1]
    final_values = series_df.iloc[-1]
    excess_over_sp = (final_values - sp500_final).drop("S&P 500")
    best_strategy = excess_over_sp.idxmax()
    best_excess = excess_over_sp.loc[best_strategy]

    hybrid_signal = None
    hybrid_label = None
    if best_excess > 0 and best_strategy != "Advisor":
        if best_strategy == quant_label:
            hybrid_signal = quant_signal.reindex(advisor_returns.index).fillna(0.0)
            hybrid_label = "Hybrid (Advisor + Quant)"
        elif best_strategy in llm_series:
            hybrid_signal = align_signals_to_returns(
                llm_signals[best_strategy], advisor_returns.index
            )
            hybrid_label = "Hybrid (Advisor + LLM)"

    if hybrid_signal is not None:
        hybrid_series = compute_strategy_series(advisor_returns, hybrid_signal)
        series_df[hybrid_label] = hybrid_series

    metric_rows = {}
    for col in series_df.columns:
        if col == "Advisor":
            returns_series = advisor_returns.reindex(series_df.index).dropna()
        elif col == "S&P 500":
            returns_series = spy_returns.reindex(series_df.index).dropna()
        elif col == quant_label:
            returns_series = spy_returns.reindex(series_df.index).dropna() * quant_signal
        elif col == "Hybrid (Advisor + LLM)":
            returns_series = (
                advisor_returns.reindex(series_df.index).dropna() * hybrid_signal
            )
        elif col == "Hybrid (Advisor + Quant)":
            returns_series = (
                advisor_returns.reindex(series_df.index).dropna() * hybrid_signal
            )
        else:
            signal = align_signals_to_returns(llm_signals[col], spy_returns.index)
            returns_series = spy_returns.reindex(series_df.index).dropna() * signal
        metric_rows[col] = performance_metrics(
            returns_series.dropna(),
            config.risk_free_annual,
            config.frequency,
        )

    metrics_df = pd.DataFrame(metric_rows).T
    final_values = series_df.iloc[-1]
    metrics_df["excess_over_sp500"] = final_values - final_values["S&P 500"]

    output_dir = None
    if not config.no_save_outputs:
        output_dir = save_outputs(config, series_df, metrics_df)
        write_winner_summary(
            output_dir, best_strategy, float(best_excess), excess_over_sp
        )

    plot_series(series_df, output_dir, show=config.show_plot)
    plot_advisor_series(series_df["Advisor"], output_dir)
    plot_metrics_bars(metrics_df, output_dir)
    if config.interactive_html:
        plot_series_interactive(
            series_df,
            output_dir,
            open_browser=config.open_html,
        )

    if output_dir:
        print(f"Saved outputs to {output_dir}")
    else:
        print(
            f"Winner vs S&P 500: {best_strategy} "
            f"(excess {float(best_excess):.4f})"
        )


if __name__ == "__main__":
    main()
