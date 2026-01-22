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

## Data Inputs
See `data/README.md` for CSV schemas and examples.
