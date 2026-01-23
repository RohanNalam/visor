import argparse
import csv
import os
from datetime import datetime


def normalize_signal(text: str) -> str:
    cleaned = text.strip().upper()
    if cleaned in {"BUY", "HOLD", "SELL"}:
        return cleaned
    raise ValueError(f"Invalid signal: {text}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Append a single LLM signal to a CSV file."
    )
    parser.add_argument("--model", required=True, help="Model name, e.g. gpt")
    parser.add_argument("--date", required=True, help="Signal date (YYYY-MM-DD)")
    parser.add_argument("--signal", required=True, help="BUY, HOLD, or SELL")
    parser.add_argument(
        "--output-dir", default="data/llm_signals", help="Destination folder"
    )
    args = parser.parse_args()

    signal = normalize_signal(args.signal)
    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Date must be YYYY-MM-DD") from exc

    os.makedirs(args.output_dir, exist_ok=True)
    path = os.path.join(args.output_dir, f"{args.model}.csv")
    write_header = not os.path.exists(path)

    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["date", "signal"])
        writer.writerow([args.date, signal])

    print(f"Saved {signal} for {args.model} on {args.date} -> {path}")


if __name__ == "__main__":
    main()
