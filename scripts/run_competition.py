#!/usr/bin/env python3
"""VISOR: Evaluating Advisor Relevance in an AI-Driven Investment World.

VISOR is a controlled backtesting framework that compares the numerical performance
of financial advisors, large language models, and quantitative strategies against
the S&P 500 under identical market conditions.

Research Question: Do financial advisors remain numerically relevant when compared
to AI (LLMs) and quantitative models?

Components:
1. LLMs - Adaptive, language-based decision-makers (GPT, Claude, etc.)
2. Quant - Deterministic, math-based decision-maker (fixed parameters)
3. Advisor (Synthetic) - Aggregated average advisor outcome based on SPIVA data
4. Advisor (AOR) - Example advisor-style allocation fund (proxy, not representative of all advisors)
5. Hybrid - Best signal generator applied to advisor returns

Usage:
    python scripts/run_competition.py --days 30  # Quick test with 30 days
    python scripts/run_competition.py --start 2024-01-01 --end 2024-12-31
    python scripts/run_competition.py --skip-llm  # Use existing CSV signals
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import date, timedelta
from typing import Dict, List, Tuple

import pandas as pd
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import VisorConfig
from data import load_prices_csv, to_period_returns
from metrics import performance_metrics
from plotting import plot_series_interactive
from quant import compute_strategy_series

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
LLM_SIGNALS_DIR = os.path.join(DATA_DIR, "llm_signals")
PRICES_CSV = os.path.join(DATA_DIR, "prices.csv")


def load_market_data(start: str, end: str) -> Tuple[pd.DataFrame, pd.Series, str, str]:
    """Load price data and returns. Adjusts dates to available data."""
    df = pd.read_csv(PRICES_CSV)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()

    data_start = df.index.min()
    data_end = df.index.max()

    req_start = pd.to_datetime(start)
    req_end = pd.to_datetime(end)

    actual_start = max(req_start, data_start)
    actual_end = min(req_end, data_end)

    if actual_start > actual_end:
        raise ValueError(f"No data for range. Data: {data_start.date()} to {data_end.date()}")

    # Include lookback for indicators
    lookback_start = actual_start - timedelta(days=60)
    df = df[(df.index >= lookback_start) & (df.index <= actual_end)]

    returns = df["SPX"].pct_change().dropna()
    return df, returns, actual_start.strftime("%Y-%m-%d"), actual_end.strftime("%Y-%m-%d")


def build_llm_prompt(current_date: pd.Timestamp, prices: pd.Series, returns: pd.Series, idx: int) -> str:
    """Build a detailed prompt for the LLM to analyze."""
    current_price = prices.iloc[idx]

    # Recent returns
    last_5 = returns.iloc[max(0, idx-5):idx].tolist()
    last_5_str = ", ".join([f"{r:.2%}" for r in last_5])

    # Moving averages
    ma_5 = prices.iloc[max(0, idx-5):idx+1].mean()
    ma_20 = prices.iloc[max(0, idx-20):idx+1].mean()

    # Trend
    price_vs_ma5 = (current_price / ma_5 - 1) * 100
    price_vs_ma20 = (current_price / ma_20 - 1) * 100

    # Volatility
    vol_10d = returns.iloc[max(0, idx-10):idx].std() * 100

    # Momentum
    momentum_5d = (prices.iloc[idx] / prices.iloc[max(0, idx-5)] - 1) * 100 if idx >= 5 else 0
    momentum_20d = (prices.iloc[idx] / prices.iloc[max(0, idx-20)] - 1) * 100 if idx >= 20 else 0

    return f"""You are an expert trader analyzing S&P 500 data to predict tomorrow's move.

Date: {current_date.strftime('%Y-%m-%d')}
Current Price: {current_price:.2f}

Recent Returns (last 5 days): {last_5_str}
5-day MA: {ma_5:.2f} (price {price_vs_ma5:+.2f}% vs MA)
20-day MA: {ma_20:.2f} (price {price_vs_ma20:+.2f}% vs MA)
10-day Volatility: {vol_10d:.2f}%
5-day Momentum: {momentum_5d:+.2f}%
20-day Momentum: {momentum_20d:+.2f}%

Based on this data, should I be invested in the S&P 500 TOMORROW?
Your goal is to BEAT the S&P 500 buy-and-hold strategy.

Respond with exactly one word: BUY, HOLD, or SELL"""


def call_openai(api_key: str, model: str, prompt: str) -> str:
    """Call OpenAI API with retry logic."""
    for attempt in range(8):
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "temperature": 0.3,
                    "max_tokens": 10,
                    "messages": [
                        {"role": "system", "content": "You are a trading expert. Respond with only BUY, HOLD, or SELL."},
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=30,
            )

            if response.status_code == 429:
                wait = min(3 * (2 ** attempt), 60)
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue

            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip().upper()

            if "BUY" in content:
                return "BUY"
            elif "SELL" in content:
                return "SELL"
            return "HOLD"

        except Exception as e:
            if attempt < 7:
                time.sleep(2 * (attempt + 1))
            else:
                print(f"    Error: {e}")
                return "HOLD"

    return "HOLD"


def generate_llm_signals_live(
    api_key: str,
    model: str,
    prices: pd.Series,
    returns: pd.Series,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """Generate fresh LLM signals using live API calls."""
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)

    mask = (returns.index >= start_dt) & (returns.index <= end_dt)
    target_dates = returns.index[mask]

    print(f"\n  Generating signals for {model}...")
    print(f"  Processing {len(target_dates)} days...")

    signals = []
    for i, current_date in enumerate(target_dates):
        idx = returns.index.get_loc(current_date)

        if idx < 20:
            signals.append({"date": current_date.strftime("%Y-%m-%d"), "signal": "HOLD"})
            continue

        prompt = build_llm_prompt(current_date, prices["SPX"], returns, idx)
        decision = call_openai(api_key, model, prompt)
        signals.append({"date": current_date.strftime("%Y-%m-%d"), "signal": decision})

        if (i + 1) % 5 == 0:
            print(f"    {i + 1}/{len(target_dates)} days processed")

        time.sleep(3)  # Rate limit protection - 3 seconds between calls

    return pd.DataFrame(signals)


def compute_quant_signal(returns: pd.Series) -> Tuple[str, pd.Series]:
    """Compute the FIXED quant model signal.

    This is a deterministic, math-based decision-maker with fixed parameters.
    The same inputs will always produce the same outputs (reproducible).

    Strategy: Trend + Momentum + RSI + Volatility Filter
    - Short MA: 6 days, Long MA: 12 days
    - RSI threshold: 70 (avoid overbought)
    - Requires at least 2 of 4 conditions to be invested
    """
    prices = (1 + returns).cumprod()

    # Fixed parameters (deterministic, reproducible)
    SHORT_WINDOW = 6
    LONG_WINDOW = 12
    RSI_THRESHOLD = 70
    MIN_CONDITIONS = 2

    # Calculate indicators
    momentum = prices / prices.shift(3) - 1
    trend = prices.rolling(SHORT_WINDOW).mean() / prices.rolling(LONG_WINDOW).mean() - 1
    volatility = returns.rolling(SHORT_WINDOW).std()
    rsi = _calculate_rsi(prices, 14)

    # Conditions
    trend_up = trend > 0
    momentum_up = momentum > 0
    vol_ok = volatility < volatility.rolling(LONG_WINDOW).median()
    rsi_ok = rsi < RSI_THRESHOLD

    # Signal: invest if at least MIN_CONDITIONS are true
    conditions = trend_up.astype(int) + momentum_up.astype(int) + vol_ok.astype(int) + rsi_ok.astype(int)
    signal = (conditions >= MIN_CONDITIONS).astype(float).fillna(0.0)

    # Shift to avoid look-ahead bias
    signal = signal.shift(1).fillna(0.0)

    name = f"Trend+Mom+RSI+Vol ({SHORT_WINDOW}/{LONG_WINDOW}, RSI<{RSI_THRESHOLD}, min={MIN_CONDITIONS})"
    return name, signal


def compute_synthetic_advisor(returns: pd.Series) -> pd.Series:
    """Compute synthetic advisor returns based on SPIVA data.

    SPIVA (S&P Indices vs Active) research shows that over 15-year periods:
    - ~90% of actively managed funds underperform the S&P 500
    - Average underperformance is approximately 1.5% annually after fees

    This synthetic advisor represents the AVERAGE advisor outcome, not a specific fund.
    It is more academically defensible than using a single ETF proxy.

    Source: SPIVA U.S. Scorecard (https://www.spglobal.com/spdji/en/spiva/)
    """
    ANNUAL_UNDERPERFORMANCE = 0.015  # 1.5% annual underperformance (SPIVA average)
    daily_drag = ANNUAL_UNDERPERFORMANCE / 252  # Convert to daily

    # Advisor returns = S&P 500 returns minus the average underperformance drag
    advisor_returns = returns - daily_drag
    return advisor_returns


def _calculate_rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """Calculate RSI indicator."""
    delta = prices.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss.replace(0, pd.NA)
    return 100 - (100 / (1 + rs))


def load_csv_signals(start_date: str, end_date: str) -> Dict[str, pd.Series]:
    """Load existing LLM signals from CSV files."""
    signals = {}
    if not os.path.isdir(LLM_SIGNALS_DIR):
        return signals

    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)

    for filename in os.listdir(LLM_SIGNALS_DIR):
        if not filename.endswith(".csv"):
            continue

        model_name = os.path.splitext(filename)[0]
        path = os.path.join(LLM_SIGNALS_DIR, filename)

        try:
            df = pd.read_csv(path)
            if df.empty or "date" not in df.columns or "signal" not in df.columns:
                continue

            df["date"] = pd.to_datetime(df["date"])
            df = df[(df["date"] >= start_dt) & (df["date"] <= end_dt)]

            if df.empty:
                continue

            mapped = df["signal"].str.upper().map({"BUY": 1.0, "HOLD": 0.0, "SELL": 0.0})
            series = pd.Series(mapped.values, index=df["date"]).sort_index()
            signals[model_name] = series

        except Exception as e:
            print(f"  Warning: Could not load {filename}: {e}")

    return signals


def run_competition(
    start_date: str,
    end_date: str,
    use_live_llm: bool = True,
    llm_model: str = "gpt-4o-mini",
) -> None:
    """Run the full competition."""

    print("=" * 60)
    print("VISOR COMPETITION: LLM vs Quant vs Advisor vs S&P 500")
    print("=" * 60)

    # Load market data
    print("\n[1] Loading market data...")
    prices_df, returns, actual_start, actual_end = load_market_data(start_date, end_date)
    print(f"  Date range: {actual_start} to {actual_end}")
    print(f"  Trading days: {len(returns)}")

    start_dt = pd.to_datetime(actual_start)
    end_dt = pd.to_datetime(actual_end)
    mask = (returns.index >= start_dt) & (returns.index <= end_dt)
    period_returns = returns[mask]

    # S&P 500 benchmark - this is what you get if you just buy and hold
    sp500_series = compute_strategy_series(period_returns, None)
    sp500_final = sp500_series.iloc[-1]
    sp500_return_pct = (sp500_final - 1) * 100  # Convert to percentage return
    print(f"\n  S&P 500 buy-and-hold: +{sp500_return_pct:.2f}% return")

    results = {"S&P 500": sp500_series}

    # LLM signals
    print("\n[2] LLM Strategies...")
    if use_live_llm:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            print("  ERROR: OPENAI_API_KEY not set. Using CSV signals instead.")
            llm_signals = load_csv_signals(actual_start, actual_end)
        else:
            # Generate fresh signals
            df = generate_llm_signals_live(
                api_key, llm_model, prices_df, returns, actual_start, actual_end
            )
            # Save to CSV
            output_path = os.path.join(LLM_SIGNALS_DIR, f"{llm_model.replace('-', '_')}.csv")
            df.to_csv(output_path, index=False)
            print(f"  Saved signals to {output_path}")

            # Convert to series
            df["date"] = pd.to_datetime(df["date"])
            mapped = df["signal"].map({"BUY": 1.0, "HOLD": 0.0, "SELL": 0.0})
            llm_signals = {llm_model: pd.Series(mapped.values, index=df["date"])}

            # Also load other existing CSV signals
            other_signals = load_csv_signals(actual_start, actual_end)
            for name, sig in other_signals.items():
                if name not in llm_signals:
                    llm_signals[name] = sig
    else:
        llm_signals = load_csv_signals(actual_start, actual_end)
        print(f"  Loaded {len(llm_signals)} LLM models from CSV")

    for model_name, signal in llm_signals.items():
        aligned = signal.reindex(period_returns.index).ffill().fillna(0.0)
        shifted = aligned.shift(1).fillna(0.0)
        series = compute_strategy_series(period_returns, shifted)
        results[f"LLM: {model_name}"] = series
        final = series.iloc[-1]
        return_pct = (final - 1) * 100
        beat = "✓ BEATS S&P!" if final > sp500_final else ""
        print(f"  {model_name}: +{return_pct:.2f}% return {beat}")

    # Quant model (FIXED parameters - deterministic, reproducible)
    print("\n[3] Quant Model (Fixed Parameters)...")
    print("  Strategy: Trend + Momentum + RSI + Volatility Filter")
    quant_name, quant_signal = compute_quant_signal(returns)

    quant_aligned = quant_signal.reindex(period_returns.index).fillna(0.0)
    quant_series = compute_strategy_series(period_returns, quant_aligned)
    results[f"Quant: {quant_name}"] = quant_series
    quant_final = quant_series.iloc[-1]
    quant_return_pct = (quant_final - 1) * 100
    beat = "✓ BEATS S&P!" if quant_final > sp500_final else ""
    print(f"  Quant: +{quant_return_pct:.2f}% return {beat}")

    # Advisor (Synthetic) - based on SPIVA average underperformance
    print("\n[4] Advisor Strategies...")
    print("  4a. Synthetic Advisor (SPIVA-based average):")
    print("      - Based on SPIVA data: ~90% of funds underperform S&P 500")
    print("      - Average underperformance: 1.5% annually after fees")
    synthetic_advisor_returns = compute_synthetic_advisor(period_returns)
    synthetic_advisor_series = (1 + synthetic_advisor_returns).cumprod()
    results["Advisor (Synthetic/SPIVA)"] = synthetic_advisor_series
    synthetic_final = synthetic_advisor_series.iloc[-1]
    synthetic_return_pct = (synthetic_final - 1) * 100
    print(f"      Synthetic Advisor: +{synthetic_return_pct:.2f}% return")

    # Advisor (AOR) - real ETF proxy (NOT representative of all advisors)
    print("\n  4b. AOR ETF (Advisor-style allocation fund proxy):")
    print("      - iShares Core Growth Allocation ETF")
    print("      - NOTE: This is ONE fund, not representative of all advisors")
    if "AOR" in prices_df.columns:
        advisor_prices = prices_df["AOR"]
        advisor_returns_full = advisor_prices.pct_change().dropna()
        aor_period_returns = advisor_returns_full.reindex(period_returns.index).fillna(0.0)
        aor_series = (1 + aor_period_returns).cumprod()
        results["Advisor (AOR Proxy)"] = aor_series
        aor_final = aor_series.iloc[-1]
        aor_return_pct = (aor_final - 1) * 100
        print(f"      AOR ETF: +{aor_return_pct:.2f}% return")
    else:
        print("      Warning: No AOR data found in prices.csv")
        aor_period_returns = period_returns
        aor_series = sp500_series

    # Find the best non-S&P500, non-Advisor strategy for hybrid
    print("\n[5] Creating Hybrid Strategy...")
    print("  (Uses best signal generator + Synthetic Advisor returns)")
    best_strategy = None
    best_final = 0
    best_signal_for_hybrid = None

    for name, series in results.items():
        if name == "S&P 500" or "Advisor" in name:
            continue
        if series.iloc[-1] > best_final:
            best_final = series.iloc[-1]
            best_strategy = name
            if "LLM:" in name:
                model_key = name.replace("LLM: ", "")
                if model_key in llm_signals:
                    sig = llm_signals[model_key].reindex(period_returns.index).ffill().fillna(0.0)
                    best_signal_for_hybrid = sig.shift(1).fillna(0.0)
            elif "Quant:" in name:
                best_signal_for_hybrid = quant_aligned

    if best_signal_for_hybrid is not None:
        # Hybrid: Use best signal to time when to be invested (using synthetic advisor returns)
        hybrid_returns = synthetic_advisor_returns * best_signal_for_hybrid.reindex(synthetic_advisor_returns.index).fillna(0.0)
        hybrid_series = (1 + hybrid_returns).cumprod()
        results[f"Hybrid ({best_strategy} + Advisor)"] = hybrid_series
        hybrid_final = hybrid_series.iloc[-1]
        hybrid_return_pct = (hybrid_final - 1) * 100
        print(f"  Best signal generator: {best_strategy}")
        print(f"  Hybrid: +{hybrid_return_pct:.2f}% return")

    # Final results
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)

    final_values = {name: series.iloc[-1] for name, series in results.items()}
    sorted_results = sorted(final_values.items(), key=lambda x: x[1], reverse=True)

    print(f"\nRanking (% Return from investing in S&P 500):")
    for i, (name, value) in enumerate(sorted_results, 1):
        return_pct = (value - 1) * 100
        excess_pct = (value - sp500_final) * 100
        status = "👑 WINNER!" if i == 1 and value > sp500_final else ("✓ BEATS S&P" if value > sp500_final else "")
        print(f"  {i}. {name}: +{return_pct:.2f}% ({excess_pct:+.2f}% vs S&P) {status}")

    # Winners
    winners = [(name, val) for name, val in sorted_results if val > sp500_final and name != "S&P 500"]
    if winners:
        print(f"\n🏆 {len(winners)} strategies beat the S&P 500!")
    else:
        print(f"\n😢 No strategy beat S&P 500 this time. Try again!")

    # Create DataFrame and show chart
    series_df = pd.DataFrame(results)

    print("\nOpening interactive chart...")
    path = plot_series_interactive(series_df, output_dir=None, open_browser=True)
    print(f"Chart saved to: {path}")


def main():
    parser = argparse.ArgumentParser(description="Run LLM vs Quant vs Advisor competition")
    parser.add_argument("--start", default=None, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", default=date.today().isoformat(), help="End date")
    parser.add_argument("--days", type=int, default=60, help="Days if --start not specified")
    parser.add_argument("--skip-llm", action="store_true", help="Use existing CSV signals")
    parser.add_argument("--llm-model", default="gpt-4o-mini", help="OpenAI model")
    args = parser.parse_args()

    if args.start:
        start_date = args.start
    else:
        start_date = (date.today() - timedelta(days=args.days)).isoformat()

    run_competition(
        start_date=start_date,
        end_date=args.end,
        use_live_llm=not args.skip_llm,
        llm_model=args.llm_model,
    )


if __name__ == "__main__":
    main()
