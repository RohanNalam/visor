# Visor
AP research project: advisor relevance vs LLMs, quant model, and S&P 500.

## Quick Start
```bash
source .venv/bin/activate
python main.py --use-synthetic-data --frequency M
```

## Project Structure
- `main.py` orchestrates the backtest and outputs results.
- `config.py` CLI config and defaults.
- `data.py` price loading (CSV/yfinance/synthetic) + advisor returns.
- `llm.py` LLM signal loading + alignment.
- `quant.py` quant model logic.
- `metrics.py` performance metrics.
- `plotting.py` output chart.
- `data/` input data and templates.
- `prompts/` saved LLM prompt templates and outputs.
- `scripts/` helper utilities for LLM outputs.

## Data Inputs
See `data/README.md` for CSV schemas and examples.

## LLM Signal Helper
Append a single LLM signal to a CSV:
```bash
python scripts/llm_output_to_csv.py --model gpt --date 2025-02-01 --signal BUY
```

## Quick Popup Run
```bash
python scripts/run_popup.py --start 2020-01-01 --end 2024-12-31
```

## Helpers
Merge Yahoo Finance CSVs into `data/prices.csv`:
```bash
python scripts/merge_yahoo_csv.py --spy ~/Downloads/SPY.csv --advisor ~/Downloads/AOR.csv
```

Validate data files:
```bash
python scripts/validate_data.py --prices data/prices.csv --advisor data/advisor_returns.csv
python scripts/validate_llm_signals.py --dir data/llm_signals --start 2020-01-01 --end 2024-12-31
```

Generate date-based LLM prompts:
```bash
python scripts/generate_llm_prompts.py --start 2020-01-01 --end 2024-12-31 --frequency M
```

Interactive chart (pan/zoom):
```bash
python main.py --prices-csv data/prices.csv --interactive-html --open-html
```
