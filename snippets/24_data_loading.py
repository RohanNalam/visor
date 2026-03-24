# ============================================================
# SNIPPET 24: Loading S&P 500 Price Data from CSV
# ============================================================
# The CSV file (data/prices.csv) has columns:
#   date, SPX (S&P 500 prices), AOR (advisor proxy ETF)
#
# This function reads the file, filters to the chosen dates,
# and returns a clean table of prices.
# ============================================================

def load_prices_csv(path, date_column, tickers, start, end):
    # Step 1: Read the CSV file
    df = pd.read_csv(path)

    # Step 2: Convert date strings to actual dates
    df[date_column] = pd.to_datetime(df[date_column])

    # Step 3: Set date as the index and sort chronologically
    df = df.set_index(date_column).sort_index()

    # Step 4: Filter to only the date range we want
    df = df[(df.index >= pd.to_datetime(start))
            & (df.index <= pd.to_datetime(end))]

    # Step 5: Return only the columns we need
    return df[tickers].dropna(how="all")

# Example:
# load_prices_csv("data/prices.csv", "date", ["SPX","AOR"],
#                 "2025-01-01", "2025-01-31")
#
# Returns:
# date        | SPX      | AOR
# 2025-01-02  | 5881.63  | 52.71
# 2025-01-03  | 5942.47  | 52.89
# 2025-01-06  | 5975.38  | 52.95
# ...
