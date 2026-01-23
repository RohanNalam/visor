import argparse
import os
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate LLM signal CSVs.")
    parser.add_argument("--dir", default="data/llm_signals")
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    args = parser.parse_args()

    if not os.path.isdir(args.dir):
        raise ValueError(f"Directory not found: {args.dir}")

    files = [f for f in os.listdir(args.dir) if f.endswith(".csv")]
    if not files:
        raise ValueError("No LLM CSV files found.")

    for filename in sorted(files):
        path = os.path.join(args.dir, filename)
        df = pd.read_csv(path)
        if "date" not in df.columns or "signal" not in df.columns:
            raise ValueError(f"{path} must have date and signal columns")

        df["date"] = pd.to_datetime(df["date"])
        if df["date"].isna().any():
            raise ValueError(f"{path} has invalid dates")

        df["signal"] = df["signal"].astype(str).str.upper().str.strip()
        bad = df.loc[~df["signal"].isin(["BUY", "HOLD", "SELL"]), "signal"].unique()
        if len(bad) > 0:
            raise ValueError(f"{path} has invalid signals: {bad}")

        if args.start:
            df = df[df["date"] >= pd.to_datetime(args.start)]
        if args.end:
            df = df[df["date"] <= pd.to_datetime(args.end)]

        if df.empty:
            raise ValueError(f"{path} has no rows in the requested range")

    print("LLM signal validation passed.")


if __name__ == "__main__":
    main()
