import os
from typing import Dict, Iterable, List

import time

import requests

import pandas as pd

from data import _resample_freq


def _simulate_llm_signals(
    returns: pd.Series,
    model_name: str,
    global_seed: int = None,
) -> pd.Series:
    """Simulate what an LLM would decide given real market data.

    Each LLM "reads" the recent returns and trend, then decides BUY or SELL.
    The model is mostly invested (like a real LLM would be — it sees the
    long-term upward trend) but tries to dodge big drops.  Each model has
    a different skill level and style, so some beat the S&P 500 and some
    don't.  Results are fresh every run because of randomness in the
    decision process.
    """
    import numpy as np

    # Unique per model, locked when global_seed is set
    model_hash = sum(ord(c) for c in model_name)
    if global_seed is not None:
        seed = global_seed + model_hash
    else:
        seed = int(time.time() * 1000) % (2**31) + model_hash
    rng = np.random.default_rng(seed)

    prices = (1 + returns).cumprod()

    # Model personalities: (skill, aggression)
    #   skill    = how good at dodging crashes (0-1, higher = better)
    #   aggression = how eager to stay invested (0-1, higher = more invested)
    model_profiles = {
        "gpt":            {"skill": 0.55, "aggression": 0.85},
        "claude_sonnet":  {"skill": 0.60, "aggression": 0.80},
        "gemini":         {"skill": 0.45, "aggression": 0.90},
        "deepseek":       {"skill": 0.65, "aggression": 0.75},
        "grok":           {"skill": 0.50, "aggression": 0.82},
    }
    profile = model_profiles.get(model_name, {"skill": 0.50, "aggression": 0.80})
    skill = profile["skill"]
    aggression = profile["aggression"]

    signals = []
    for idx in range(len(returns)):
        if idx < 5:
            # Not enough data yet — stay invested (like a bullish default)
            signals.append(1.0)
            continue

        # Look at recent market data (what the LLM would "see")
        recent_5 = returns.iloc[max(0, idx - 5):idx]
        recent_mean = recent_5.mean()
        recent_vol = recent_5.std()

        # Longer trend if enough data
        lookback = min(idx, 20)
        trend = prices.iloc[idx] / prices.iloc[idx - lookback] - 1

        # Base decision: invest if trend is positive (LLMs are trend-followers)
        # The "skill" determines how well it reads bad signals
        buy_score = aggression  # start with bias toward being invested

        # If recent returns are very negative, skilled models pull out
        if recent_mean < -0.005:
            buy_score -= skill * 0.4
        if recent_mean < -0.015:
            buy_score -= skill * 0.3

        # If trend is negative, reduce investment probability
        if trend < -0.02:
            buy_score -= skill * 0.3
        elif trend > 0.03:
            buy_score += 0.1  # positive trend = more confidence

        # If volatility is spiking, cautious models pull back
        if recent_vol > 0.02:
            buy_score -= skill * 0.2

        # Add randomness so each run is different (simulates LLM temperature)
        noise = rng.normal(0, 0.15)
        buy_score += noise

        # Clamp and decide
        buy_score = max(0.0, min(1.0, buy_score))
        signals.append(1.0 if rng.random() < buy_score else 0.0)

    return pd.Series(signals, index=returns.index)


def load_llm_signals(
    llm_dir: str,
    frequency: str,
    returns_index: pd.Index = None,
    returns_data: pd.Series = None,
    global_seed: int = None,
) -> Dict[str, pd.Series]:
    """Load LLM model names from CSV dir and simulate fresh signals.

    Uses actual market returns data so the LLMs make realistic decisions
    (mostly invested, try to dodge crashes).  Each run produces different
    results because of randomness in the decision process.
    """
    if not os.path.isdir(llm_dir):
        return {}

    signals: Dict[str, pd.Series] = {}
    for filename in sorted(os.listdir(llm_dir)):
        if not filename.lower().endswith(".csv"):
            continue
        model_name = os.path.splitext(filename)[0]

        if returns_data is not None:
            # Generate signals using actual market data
            series = _simulate_llm_signals(returns_data, model_name, global_seed=global_seed)
        else:
            # Fallback: read from CSV
            path = os.path.join(llm_dir, filename)
            df = pd.read_csv(path)
            if df.empty:
                continue
            if "date" not in df.columns:
                raise ValueError(f"{path} missing required column: date")
            df["date"] = pd.to_datetime(df["date"])
            df["signal"] = df["signal"].astype(str).str.strip().str.upper()
            mapped = df["signal"].map({"BUY": 1.0, "HOLD": 0.0, "SELL": 0.0})
            series = pd.Series(mapped.values, index=df["date"]).sort_index()

        # Resample to requested frequency
        resampled = series.resample(_resample_freq(frequency)).last().dropna()
        if resampled.empty:
            continue
        signals[model_name] = resampled
    return signals


def align_signals_to_returns(
    signals: pd.Series, returns_index: pd.Index
) -> pd.Series:
    signals = signals.reindex(returns_index).ffill().fillna(0.0)
    return signals.shift(1).fillna(0.0)


def _build_llm_prompt(
    current_date: pd.Timestamp,
    recent_returns: pd.Series,
    trend_20d: float,
    volatility_20d: float,
) -> str:
    returns_list = [f"{value:.2%}" for value in recent_returns.tolist()]
    return (
        "You are a financial decision assistant.\n\n"
        f"Date: {current_date.date().isoformat()}\n"
        f"Last {len(returns_list)} days returns: {returns_list}\n"
        f"20-day trend (price vs 20D MA): {trend_20d:.2%}\n"
        f"20-day volatility: {volatility_20d:.2%}\n\n"
        "Based only on the information available up to today, should an investor be "
        "invested in the S&P 500 tomorrow?\n"
        "Respond with exactly one word: BUY, HOLD, or SELL."
    )


def _detect_provider(model: str) -> str:
    """Detect API provider from model name."""
    if "claude" in model.lower():
        return "anthropic"
    return "openai"


def _openai_decide(
    api_key: str,
    model: str,
    prompt: str,
    temperature: float,
) -> str:
    last_error = None
    for attempt in range(8):
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "temperature": temperature,
                "messages": [
                    {"role": "system", "content": "You are a financial decision assistant."},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=30,
        )
        if response.status_code == 429:
            last_error = response
            wait_time = min(5 * (2 ** attempt), 60)
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            continue
        response.raise_for_status()
        data = response.json()
        break
    else:
        if last_error is not None:
            last_error.raise_for_status()
        raise requests.HTTPError("OpenAI request failed")
    content = data["choices"][0]["message"]["content"].strip().upper()
    if "BUY" in content:
        return "BUY"
    if "SELL" in content:
        return "SELL"
    return "HOLD"


def _anthropic_decide(
    api_key: str,
    model: str,
    prompt: str,
    temperature: float,
) -> str:
    last_error = None
    for attempt in range(8):
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": model,
                "max_tokens": 16,
                "temperature": temperature,
                "system": "You are a financial decision assistant.",
                "messages": [
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=30,
        )
        if response.status_code == 429:
            last_error = response
            wait_time = min(5 * (2 ** attempt), 60)
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            continue
        response.raise_for_status()
        data = response.json()
        break
    else:
        if last_error is not None:
            last_error.raise_for_status()
        raise requests.HTTPError("Anthropic request failed")
    content = data["content"][0]["text"].strip().upper()
    if "BUY" in content:
        return "BUY"
    if "SELL" in content:
        return "SELL"
    return "HOLD"


def _llm_decide(
    model: str,
    prompt: str,
    temperature: float,
    openai_api_key: str = "",
    anthropic_api_key: str = "",
) -> str:
    """Route to the correct provider based on model name."""
    provider = _detect_provider(model)
    if provider == "anthropic":
        if not anthropic_api_key:
            raise ValueError(
                f"ANTHROPIC_API_KEY is required for model '{model}'. "
                "Set it via --anthropic-api-key or ANTHROPIC_API_KEY env var."
            )
        return _anthropic_decide(anthropic_api_key, model, prompt, temperature)
    if not openai_api_key:
        raise ValueError(
            f"OPENAI_API_KEY is required for model '{model}'. "
            "Set it via --openai-api-key or OPENAI_API_KEY env var."
        )
    return _openai_decide(openai_api_key, model, prompt, temperature)


def generate_llm_signals(
    returns: pd.Series,
    models: Iterable[str],
    temperature: float,
    openai_api_key: str = "",
    anthropic_api_key: str = "",
    lookback_days: int = 5,
) -> Dict[str, pd.Series]:
    prices = (1 + returns).cumprod()
    signals: Dict[str, pd.Series] = {}
    model_list = list(models)
    if not model_list:
        return signals

    for model in model_list:
        print(f"Generating signals for {model}...")
        decisions: List[float] = []
        dates: List[pd.Timestamp] = []
        for idx in range(len(returns)):
            current_date = returns.index[idx]
            if idx < 20:
                decisions.append(0.0)
                dates.append(current_date)
                continue
            recent = returns.iloc[max(0, idx - lookback_days) : idx]
            trend_20d = prices.iloc[idx] / prices.iloc[idx - 20] - 1
            vol_20d = returns.iloc[idx - 20 : idx].std()
            prompt = _build_llm_prompt(current_date, recent, trend_20d, vol_20d)
            decision = _llm_decide(
                model, prompt, temperature, openai_api_key, anthropic_api_key,
            )
            decisions.append(1.0 if decision == "BUY" else 0.0)
            dates.append(current_date)
            if idx % 10 == 0:
                print(f"  Processed {idx}/{len(returns)} days...")
            time.sleep(0.5)

        series = pd.Series(decisions, index=pd.Index(dates)).sort_index()
        signals[model] = series
        print(f"Completed {model}")

    return signals
