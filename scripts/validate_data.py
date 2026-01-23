import argparse
import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate price/advisor CSVs.")
    parser.add_argument("--prices", default="data/prices.csv")
    parser.add_argument("--advisor", default=None)
    args = parser.parse_args()

    prices = pd.read_csv(args.prices)
    required = {"date", "SPY", "AOR"}
    missing = required - set(prices.columns)
    if missing:
        raise ValueError(f"prices CSV missing columns: {missing}")

    prices["date"] = pd.to_datetime(prices["date"])
    if prices["date"].isna().any():
        raise ValueError("prices CSV has invalid dates")

    if prices[["SPY", "AOR"]].isna().any().any():
        raise ValueError("prices CSV has missing values in SPY/AOR")

    if args.advisor:
        advisor = pd.read_csv(args.advisor)
        if "date" not in advisor.columns:
            raise ValueError("advisor CSV missing date column")
        if "return" not in advisor.columns and "value" not in advisor.columns:
            raise ValueError("advisor CSV needs return or value column")

    print("Data validation passed.")


if __name__ == "__main__":
    main()
