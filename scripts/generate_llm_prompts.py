import argparse
from datetime import datetime

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate date-based LLM prompts for a timeline."
    )
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--frequency", default="M", choices=["D", "W", "M"])
    parser.add_argument("--out", default="prompts/llm_prompt_batch.txt")
    args = parser.parse_args()

    start = pd.to_datetime(args.start)
    end = pd.to_datetime(args.end)
    dates = pd.date_range(start=start, end=end, freq=args.frequency)
    if dates.empty:
        raise ValueError("No dates generated for the given range.")

    lines = []
    for dt in dates:
        date_str = dt.strftime("%Y-%m-%d")
        lines.append("====")
        lines.append(f"DATE: {date_str}")
        lines.append(
            "Based only on the information available as of this date, should an "
            "investor be invested in the S&P 500 for the NEXT period?"
        )
        lines.append("Output exactly one word: BUY, HOLD, or SELL.")
        lines.append("Information: [PASTE HEADLINES / EARNINGS / MACRO HERE]")
        lines.append("")

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Saved {len(dates)} prompts to {args.out}")


if __name__ == "__main__":
    main()
