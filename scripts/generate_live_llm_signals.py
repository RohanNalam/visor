#!/usr/bin/env python3
"""Generate REAL LLM signals by calling the OpenAI API.

Each LLM analyzes past market data and predicts whether to BUY/HOLD/SELL for the next day.
Signals are saved to CSV files so you don't have to regenerate them every time.

Usage:
    # Generate signals for the last 30 days (quick test)
    python scripts/generate_live_llm_signals.py --days 30

    # Generate signals for a specific date range
    python scripts/generate_live_llm_signals.py --start 2024-01-01 --end 2024-12-31

    # Use a specific model
    python scripts/generate_live_llm_signals.py --model gpt-4o --days 60
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import date, timedelta

import pandas as pd
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
LLM_SIGNALS_DIR = os.path.join(DATA_DIR, "llm_signals")
PRICES_CSV = os.path.join(DATA_DIR, "prices.csv")


def load_price_data(start: str, end: str) -> tuple[pd.DataFrame, pd.Series, str, str]:
    """Load price data and calculate returns. Returns adjusted start/end dates."""
    df = pd.read_csv(PRICES_CSV)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()

    # Get the actual date range available in the data
    data_start = df.index.min()
    data_end = df.index.max()

    # Adjust requested dates to available data
    req_start = pd.to_datetime(start)
    req_end = pd.to_datetime(end)

    actual_start = max(req_start, data_start)
    actual_end = min(req_end, data_end)

    if actual_start > actual_end:
        raise ValueError(f"No data available for requested range. Data spans {data_start.date()} to {data_end.date()}")

    # Filter to date range (with extra lookback for indicators)
    lookback_start = actual_start - timedelta(days=60)
    df = df[(df.index >= lookback_start) & (df.index <= actual_end)]

    returns = df["SPX"].pct_change().dropna()
    return df, returns, actual_start.strftime("%Y-%m-%d"), actual_end.strftime("%Y-%m-%d")


def build_detailed_prompt(
    current_date: pd.Timestamp,
    prices: pd.Series,
    returns: pd.Series,
    idx: int,
) -> str:
    """Build a detailed prompt with market data for the LLM to analyze."""

    # Calculate various indicators
    current_price = prices.iloc[idx]

    # Recent returns
    last_5_returns = returns.iloc[max(0, idx-5):idx].tolist()
    last_5_str = ", ".join([f"{r:.2%}" for r in last_5_returns])

    # Moving averages
    ma_5 = prices.iloc[max(0, idx-5):idx+1].mean()
    ma_20 = prices.iloc[max(0, idx-20):idx+1].mean()
    ma_50 = prices.iloc[max(0, idx-50):idx+1].mean() if idx >= 50 else ma_20

    # Trend indicators
    price_vs_ma5 = (current_price / ma_5 - 1) * 100
    price_vs_ma20 = (current_price / ma_20 - 1) * 100

    # Volatility
    volatility_10d = returns.iloc[max(0, idx-10):idx].std() * 100
    volatility_20d = returns.iloc[max(0, idx-20):idx].std() * 100

    # Momentum
    if idx >= 5:
        momentum_5d = (prices.iloc[idx] / prices.iloc[idx-5] - 1) * 100
    else:
        momentum_5d = 0

    if idx >= 20:
        momentum_20d = (prices.iloc[idx] / prices.iloc[idx-20] - 1) * 100
    else:
        momentum_20d = 0

    # Recent high/low
    recent_high = prices.iloc[max(0, idx-20):idx+1].max()
    recent_low = prices.iloc[max(0, idx-20):idx+1].min()
    pct_from_high = (current_price / recent_high - 1) * 100
    pct_from_low = (current_price / recent_low - 1) * 100

    prompt = f"""You are an expert financial analyst making trading decisions for the S&P 500.

Current Date: {current_date.strftime('%Y-%m-%d')}
Current S&P 500 Price: {current_price:.2f}

=== MARKET DATA ===

Recent Daily Returns (last 5 days): {last_5_str}

Moving Averages:
- 5-day MA: {ma_5:.2f} (price is {price_vs_ma5:+.2f}% vs MA)
- 20-day MA: {ma_20:.2f} (price is {price_vs_ma20:+.2f}% vs MA)

Momentum:
- 5-day momentum: {momentum_5d:+.2f}%
- 20-day momentum: {momentum_20d:+.2f}%

Volatility:
- 10-day volatility: {volatility_10d:.2f}%
- 20-day volatility: {volatility_20d:.2f}%

Recent Range (20 days):
- High: {recent_high:.2f} (current is {pct_from_high:.2f}% from high)
- Low: {recent_low:.2f} (current is {pct_from_low:+.2f}% from low)

=== YOUR TASK ===

Based on this data, should an investor be invested in the S&P 500 TOMORROW?

Consider:
1. Is the trend bullish or bearish?
2. Is volatility increasing or decreasing?
3. Are we near support or resistance?
4. What does momentum suggest?

Respond with EXACTLY one word: BUY, HOLD, or SELL

Your decision:"""

    return prompt


def call_openai(api_key: str, model: str, prompt: str, temperature: float = 0.3) -> str:
    """Call OpenAI API with retry logic for rate limits."""
    max_retries = 10
    base_wait = 2

    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": 10,
                    "messages": [
                        {"role": "system", "content": "You are a financial trading expert. Respond with only BUY, HOLD, or SELL."},
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=30,
            )

            if response.status_code == 429:
                wait_time = base_wait * (2 ** attempt)
                wait_time = min(wait_time, 120)  # Cap at 2 minutes
                print(f"    Rate limited. Waiting {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip().upper()

            # Parse the response
            if "BUY" in content:
                return "BUY"
            elif "SELL" in content:
                return "SELL"
            else:
                return "HOLD"

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = base_wait * (2 ** attempt)
                print(f"    Error: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise

    return "HOLD"  # Default if all retries fail


def call_anthropic(api_key: str, model: str, prompt: str, temperature: float = 0.3) -> str:
    """Call Anthropic Messages API with retry logic for rate limits."""
    max_retries = 10
    base_wait = 2

    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": 10,
                    "system": "You are a financial trading expert. Respond with only BUY, HOLD, or SELL.",
                    "messages": [
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=30,
            )

            if response.status_code == 429:
                wait_time = base_wait * (2 ** attempt)
                wait_time = min(wait_time, 120)
                print(f"    Rate limited. Waiting {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue

            response.raise_for_status()
            data = response.json()
            content = data["content"][0]["text"].strip().upper()

            if "BUY" in content:
                return "BUY"
            elif "SELL" in content:
                return "SELL"
            else:
                return "HOLD"

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = base_wait * (2 ** attempt)
                print(f"    Error: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise

    return "HOLD"  # Default if all retries fail


def _detect_provider(model: str) -> str:
    """Detect API provider from model name."""
    if "claude" in model.lower():
        return "anthropic"
    return "openai"


def generate_signals_for_model(
    model_name: str,
    api_key: str,
    prices: pd.Series,
    returns: pd.Series,
    start_date: str,
    end_date: str,
    delay_between_calls: float = 1.0,
    anthropic_api_key: str = "",
) -> pd.DataFrame:
    """Generate signals for a single model."""

    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)

    # Filter to the actual date range we want signals for
    mask = (returns.index >= start_dt) & (returns.index <= end_dt)
    target_dates = returns.index[mask]

    print(f"\nGenerating signals for {model_name}...")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Total days to process: {len(target_dates)}")

    signals = []

    for i, current_date in enumerate(target_dates):
        # Find the index in the full returns series
        idx = returns.index.get_loc(current_date)

        # Skip if not enough history
        if idx < 20:
            signals.append({"date": current_date.strftime("%Y-%m-%d"), "signal": "HOLD"})
            continue

        # Build prompt and get prediction
        prompt = build_detailed_prompt(current_date, prices["SPX"], returns, idx)
        if _detect_provider(model_name) == "anthropic":
            decision = call_anthropic(anthropic_api_key or api_key, model_name, prompt)
        else:
            decision = call_openai(api_key, model_name, prompt)

        signals.append({"date": current_date.strftime("%Y-%m-%d"), "signal": decision})

        # Progress update
        if (i + 1) % 10 == 0 or i == len(target_dates) - 1:
            pct = (i + 1) / len(target_dates) * 100
            print(f"  Processed {i + 1}/{len(target_dates)} days ({pct:.1f}%) - Last: {decision}")

        # Delay to avoid rate limits
        time.sleep(delay_between_calls)

    return pd.DataFrame(signals)


def main():
    parser = argparse.ArgumentParser(
        description="Generate real LLM trading signals using OpenAI API"
    )
    parser.add_argument(
        "--start",
        default=None,
        help="Start date (YYYY-MM-DD). If not specified, uses --days",
    )
    parser.add_argument(
        "--end",
        default=date.today().isoformat(),
        help="End date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to generate (if --start not specified)",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="Model to use (e.g., gpt-4o-mini, claude-sonnet-4-5-20250929)",
    )
    parser.add_argument(
        "--output-name",
        default=None,
        help="Name for the output CSV file (default: model name)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Delay between API calls in seconds (to avoid rate limits)",
    )
    args = parser.parse_args()

    # Check for API key
    provider = _detect_provider(args.model)
    api_key = os.environ.get("OPENAI_API_KEY", "")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if provider == "anthropic" and not anthropic_key:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set!")
        print("\nTo set it, run:")
        print('  export ANTHROPIC_API_KEY="your-api-key-here"')
        sys.exit(1)
    if provider == "openai" and not api_key:
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        print("\nTo set it, run:")
        print('  export OPENAI_API_KEY="your-api-key-here"')
        sys.exit(1)

    # Determine date range
    if args.start:
        start_date = args.start
    else:
        start_dt = date.today() - timedelta(days=args.days)
        start_date = start_dt.isoformat()

    end_date = args.end

    # Load price data
    print("Loading price data...")
    try:
        prices, returns, actual_start, actual_end = load_price_data(start_date, end_date)
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if actual_start != start_date or actual_end != end_date:
        print(f"Note: Adjusted date range to available data: {actual_start} to {actual_end}")
        start_date = actual_start
        end_date = actual_end

    print(f"Loaded {len(returns)} days of return data")

    # Generate signals
    df = generate_signals_for_model(
        model_name=args.model,
        api_key=api_key,
        prices=prices,
        returns=returns,
        start_date=start_date,
        end_date=end_date,
        delay_between_calls=args.delay,
        anthropic_api_key=anthropic_key,
    )

    if df.empty:
        print("ERROR: No signals were generated. Check your date range.")
        sys.exit(1)

    # Save to CSV
    os.makedirs(LLM_SIGNALS_DIR, exist_ok=True)
    output_name = args.output_name or args.model.replace("-", "_").replace(".", "_")
    output_path = os.path.join(LLM_SIGNALS_DIR, f"{output_name}.csv")
    df.to_csv(output_path, index=False)

    # Summary
    buy_count = (df["signal"] == "BUY").sum()
    hold_count = (df["signal"] == "HOLD").sum()
    sell_count = (df["signal"] == "SELL").sum()

    print(f"\n=== SUMMARY ===")
    print(f"Model: {args.model}")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Total signals: {len(df)}")
    print(f"  BUY:  {buy_count} ({buy_count/len(df)*100:.1f}%)")
    print(f"  HOLD: {hold_count} ({hold_count/len(df)*100:.1f}%)")
    print(f"  SELL: {sell_count} ({sell_count/len(df)*100:.1f}%)")
    print(f"\nSaved to: {output_path}")
    print(f"\nNow run: python scripts/show_popup.py --interactive")


if __name__ == "__main__":
    main()
