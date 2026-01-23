import argparse
import pandas as pd


def load_yahoo_csv(path: str, date_col: str = "Date") -> pd.DataFrame:
    df = pd.read_csv(path)
    if date_col not in df.columns:
        raise ValueError(f"{path} missing column: {date_col}")
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col)
    return df


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge Yahoo Finance CSVs into data/prices.csv"
    )
    parser.add_argument("--spy", required=True, help="Path to SPY CSV")
    parser.add_argument("--advisor", required=True, help="Path to advisor CSV (AOR)")
    parser.add_argument("--out", default="data/prices.csv")
    parser.add_argument("--date-col", default="Date")
    parser.add_argument(
        "--price-col",
        default="Adj Close",
        help="Price column to use (Adj Close recommended)",
    )
    args = parser.parse_args()

    spy = load_yahoo_csv(args.spy, args.date_col)
    advisor = load_yahoo_csv(args.advisor, args.date_col)

    if args.price_col not in spy.columns or args.price_col not in advisor.columns:
        raise ValueError(f"Missing price column: {args.price_col}")

    merged = pd.DataFrame(
        {
            "date": spy[args.date_col],
            "SPY": spy[args.price_col].astype(float),
        }
    ).merge(
        pd.DataFrame(
            {
                "date": advisor[args.date_col],
                "AOR": advisor[args.price_col].astype(float),
            }
        ),
        on="date",
        how="inner",
    )

    merged.to_csv(args.out, index=False)
    print(f"Saved {len(merged)} rows to {args.out}")


if __name__ == "__main__":
    main()
