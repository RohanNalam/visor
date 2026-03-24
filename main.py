import json
import os
from dataclasses import asdict

import pandas as pd

from typing import Optional, Tuple

from config import VisorConfig, parse_args
from data import (
    download_prices,
    fetch_latest_prices,
    generate_synthetic_prices,
    load_advisor_returns,
    load_prices_csv,
    append_latest_prices,
    to_period_returns,
)
from llm import align_signals_to_returns, generate_llm_signals, load_llm_signals, _detect_provider, _build_llm_prompt
from metrics import performance_metrics
from plotting import (
    plot_advisor_series,
    plot_excess_interactive,
    plot_excess_over_sp500,
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
    periods_per_year = _periods_per_year(frequency)
    fee_period = (1 + fee_annual) ** (1 / periods_per_year) - 1
    return returns - fee_period


def _periods_per_year(frequency: str) -> int:
    if frequency == "D":
        return 252
    if frequency == "W":
        return 52
    return 12


def run_backtest(
    config: VisorConfig,
) -> Tuple[pd.DataFrame, pd.DataFrame, str, float, Optional[str]]:
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
    if config.realtime_prices:
        latest_prices = fetch_latest_prices(tickers)
        prices = append_latest_prices(prices, latest_prices)
    returns = to_period_returns(prices, config.frequency)

    spy_returns = returns[config.benchmark_ticker].dropna()
    if spy_returns.empty:
        raise ValueError(
            "No return data in selected period. "
            "Check your date range, frequency, and prices CSV."
        )

    advisor_returns = None
    if config.include_advisor:
        if config.advisor_mode == "synthetic":
            periods_per_year = _periods_per_year(config.frequency)
            advisor_drag = config.advisor_underperformance_annual / periods_per_year
            advisor_returns = spy_returns - advisor_drag
        else:
            if config.advisor_data_csv:
                advisor_returns = load_advisor_returns(
                    config.advisor_data_csv,
                    config.frequency,
                    config.start,
                    config.end,
                ).reindex(spy_returns.index)
            else:
                advisor_returns = returns[config.advisor_ticker].reindex(
                    spy_returns.index
                )
            advisor_returns = advisor_returns.dropna()
            if advisor_returns.empty:
                raise ValueError(
                    "Advisor returns are empty. Check advisor data or disable with --no-advisor."
                )
            advisor_returns = apply_annual_fee(
                advisor_returns, config.advisor_fee_annual, config.frequency
            )

    if config.llm_mode in ("openai", "api"):
        needs_openai = any(_detect_provider(m) == "openai" for m in config.llm_models)
        needs_anthropic = any(_detect_provider(m) == "anthropic" for m in config.llm_models)
        if needs_openai and not config.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required for OpenAI models. "
                "Set it via --openai-api-key or OPENAI_API_KEY env var, "
                "or use --llm-mode csv."
            )
        if needs_anthropic and not config.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is required for Anthropic models. "
                "Set it via --anthropic-api-key or ANTHROPIC_API_KEY env var, "
                "or use --llm-mode csv."
            )
        llm_signals = generate_llm_signals(
            spy_returns,
            config.llm_models,
            config.llm_temperature,
            openai_api_key=config.openai_api_key,
            anthropic_api_key=config.anthropic_api_key,
        )
    else:
        llm_signals = load_llm_signals(
            config.llm_signals_dir, config.frequency,
            returns_index=spy_returns.index, returns_data=spy_returns,
            global_seed=config.random_seed,
        )
    llm_series = {}
    llm_signal_logs = {}
    for model, signal in llm_signals.items():
        raw_signal = signal.reindex(spy_returns.index).ffill().fillna(0.0)
        aligned_signal = raw_signal.shift(1).fillna(0.0)
        llm_series[model] = compute_strategy_series(spy_returns, aligned_signal)
        llm_signal_logs[model] = pd.DataFrame(
            {
                "date": spy_returns.index,
                "signal_raw": raw_signal.values,
                "signal_executed": aligned_signal.values,
            }
        )

    quant_signal = quant_model_signals(spy_returns, config.quant_model)
    quant_series = compute_strategy_series(spy_returns, quant_signal)
    quant_label = f"Quant Model ({quant_model_name(config.quant_model)})"

    base_series = {
        "S&P 500": compute_strategy_series(spy_returns, None),
        quant_label: quant_series,
    }
    if advisor_returns is not None:
        base_series["Advisor"] = compute_strategy_series(advisor_returns, None)
    series_df = pd.DataFrame({**base_series, **llm_series}).dropna(how="all")

    sp500_final = series_df["S&P 500"].iloc[-1]
    final_values = series_df.iloc[-1]
    excess_over_sp = (final_values - sp500_final).drop("S&P 500")
    best_strategy = excess_over_sp.idxmax()
    best_excess = excess_over_sp.loc[best_strategy]

    # Always create Hybrid line: best non-advisor strategy signals + advisor returns
    # This shows what happens if advisor follows the best signal generator
    hybrid_signal = None
    hybrid_label = None

    # Find best non-advisor, non-S&P strategy
    non_advisor_excess = excess_over_sp.drop("Advisor", errors="ignore")
    if not non_advisor_excess.empty:
        best_signal_strategy = non_advisor_excess.idxmax()

        if advisor_returns is not None and best_signal_strategy != "Advisor":
            if best_signal_strategy == quant_label:
                hybrid_signal = quant_signal.reindex(advisor_returns.index).fillna(0.0)
                hybrid_label = f"Hybrid (Advisor + Quant)"
            elif best_signal_strategy in llm_series:
                hybrid_signal = align_signals_to_returns(
                    llm_signals[best_signal_strategy], advisor_returns.index
                )
                hybrid_label = f"Hybrid (Advisor + {best_signal_strategy})"

    if hybrid_signal is not None:
        hybrid_series = compute_strategy_series(advisor_returns, hybrid_signal)
        series_df[hybrid_label] = hybrid_series

    metric_rows = {}
    for col in series_df.columns:
        if col == "Advisor":
            if advisor_returns is None:
                continue
            returns_series = advisor_returns.reindex(series_df.index).dropna()
        elif col == "S&P 500":
            returns_series = spy_returns.reindex(series_df.index).dropna()
        elif col == quant_label:
            returns_series = spy_returns.reindex(series_df.index).dropna() * quant_signal
        elif col.startswith("Hybrid (Advisor +"):
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
        for model, df in llm_signal_logs.items():
            path = os.path.join(output_dir, f"llm_decisions_{model}.csv")
            df.to_csv(path, index=False)
        quant_log = pd.DataFrame(
            {
                "date": spy_returns.index,
                "signal_executed": quant_signal.reindex(spy_returns.index)
                .fillna(0.0)
                .values,
            }
        )
        quant_log.to_csv(os.path.join(output_dir, "quant_decisions.csv"), index=False)

        # Save LLM prompt template for reproducibility
        sample_prompt = _build_llm_prompt(
            pd.Timestamp("2024-06-15"),
            pd.Series([0.005, -0.002, 0.008, 0.001, -0.003]),
            trend_20d=0.032,
            volatility_20d=0.011,
        )
        prompt_path = os.path.join(output_dir, "llm_prompt_template.txt")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write("=== LLM PROMPT TEMPLATE ===\n")
            f.write("This is the exact prompt format sent to each LLM.\n")
            f.write("Actual values are filled in from historical market data.\n\n")
            f.write("--- SAMPLE PROMPT ---\n\n")
            f.write(sample_prompt)
            f.write("\n\n--- END ---\n")

    return series_df, metrics_df, best_strategy, float(best_excess), output_dir


def main() -> None:
    config = parse_args()
    series_df, metrics_df, best_strategy, best_excess, output_dir = run_backtest(
        config
    )

    # Save static PNG charts (for the research paper)
    plot_series(series_df, output_dir, show=False)
    plot_excess_over_sp500(series_df, output_dir, show=False)
    if "Advisor" in series_df.columns:
        plot_advisor_series(series_df["Advisor"], output_dir)
    plot_metrics_bars(metrics_df, output_dir)

    if output_dir:
        print(f"\nSaved outputs to {output_dir}")
    print(
        f"Winner vs S&P 500: {best_strategy} "
        f"(excess {float(best_excess):.4f})"
    )

    # Show the excess-over-S&P-500 chart as a matplotlib popup window
    # (NOT an HTML file, NOT Safari — a native desktop popup)
    plot_excess_over_sp500(series_df, output_dir=None, show=True)


if __name__ == "__main__":
    main()
