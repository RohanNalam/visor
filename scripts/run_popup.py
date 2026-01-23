import argparse
import os
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Quick popup run with default inputs."
    )
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default="2024-12-31")
    parser.add_argument("--frequency", default="M", choices=["M", "W"])
    parser.add_argument("--advisor-fee-annual", default="0.01")
    args = parser.parse_args()

    cmd = [
        sys.executable,
        "main.py",
        "--prices-csv",
        "data/prices.csv",
        "--advisor-data-csv",
        "data/advisor_returns.csv",
        "--frequency",
        args.frequency,
        "--start",
        args.start,
        "--end",
        args.end,
        "--advisor-fee-annual",
        args.advisor_fee_annual,
        "--show-plot",
        "--no-save-outputs",
    ]

    if not os.path.exists("data/prices.csv"):
        print("Missing data/prices.csv. Add real price data first.")
        sys.exit(1)

    subprocess.run(cmd, check=False)


if __name__ == "__main__":
    main()
