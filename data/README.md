# Data Folder

This folder holds all input data. You can use the templates in `data/templates/`.

## Prices CSV (S&P 500 + Advisor ETF)
File example: `data/prices.csv`
Columns:
- `date` (YYYY-MM-DD)
- `SPY` (benchmark price)
- `AOR` (advisor proxy price) or your chosen advisor ticker

## Advisor Returns CSV (Optional)
File example: `data/advisor_returns.csv`
Columns:
- `date` (YYYY-MM-DD)
- `return` (period return as decimal, e.g. 0.012)
or
- `value` (portfolio value to be converted to returns)

## LLM Signals
Folder: `data/llm_signals/`
One CSV per model with:
- `date` (YYYY-MM-DD)
- `signal` (BUY, HOLD, SELL)

## Templates
See `data/templates/` for sample formats.
