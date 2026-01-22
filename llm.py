import os
from typing import Dict

import pandas as pd


def load_llm_signals(llm_dir: str, frequency: str) -> Dict[str, pd.Series]:
    if not os.path.isdir(llm_dir):
        return {}

    signals: Dict[str, pd.Series] = {}
    for filename in sorted(os.listdir(llm_dir)):
        if not filename.lower().endswith(".csv"):
            continue
        model_name = os.path.splitext(filename)[0]
        path = os.path.join(llm_dir, filename)
        df = pd.read_csv(path)
        if "date" not in df.columns:
            raise ValueError(f"{path} missing required column: date")
        if "signal" not in df.columns:
            raise ValueError(f"{path} missing required column: signal")

        df["date"] = pd.to_datetime(df["date"])
        df["signal"] = df["signal"].astype(str).str.strip().str.upper()
        mapped = df["signal"].map({"BUY": 1.0, "HOLD": 0.0, "SELL": 0.0})
        if mapped.isna().any():
            bad = df.loc[mapped.isna(), "signal"].unique()
            raise ValueError(f"{path} has invalid signals: {bad}")

        series = pd.Series(mapped.values, index=df["date"]).sort_index()
        series = series.resample(frequency).last().dropna()
        signals[model_name] = series
    return signals


def align_signals_to_returns(
    signals: pd.Series, returns_index: pd.Index
) -> pd.Series:
    signals = signals.reindex(returns_index).ffill().fillna(0.0)
    return signals.shift(1).fillna(0.0)
