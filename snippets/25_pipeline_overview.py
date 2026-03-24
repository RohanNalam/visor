# ============================================================
# SNIPPET 25: The Full Pipeline (How Everything Connects)
# ============================================================
# This is main.py - the brain that runs the entire competition.
# It loads data, runs all models, finds the winner, and shows
# the chart.
# ============================================================

def main():
    config = parse_args()  # Read settings (dates, frequency, etc.)

    # STEP 1: Run the backtest competition
    series_df, metrics_df, best_strategy, best_excess, output_dir = (
        run_backtest(config)
    )
    # series_df = table with growth-of-$1 for ALL strategies
    # metrics_df = table with 5 metrics for ALL strategies
    # best_strategy = name of the winner
    # best_excess = how much the winner beat S&P 500 by

    # STEP 2: Save charts as PNG files (for the research paper)
    plot_series(series_df, output_dir, show=False)
    plot_excess_over_sp500(series_df, output_dir, show=False)
    plot_metrics_bars(metrics_df, output_dir)

    # STEP 3: Print the winner
    print(f"Winner vs S&P 500: {best_strategy} (excess {best_excess:.4f})")

    # STEP 4: Show the popup chart (Excess Return vs S&P 500)
    plot_excess_over_sp500(series_df, output_dir=None, show=True)

# Inside run_backtest(), the steps are:
#   1. Load S&P 500 prices from CSV          (data.py)
#   2. Convert prices to returns              (data.py)
#   3. Create advisor curve (S&P - 1.5% - 1% fee)
#   4. Generate 5 LLM BUY/SELL signals       (llm.py)
#   5. Generate quant model BUY/SELL signals  (quant.py)
#   6. Apply all signals with shift(1) to prevent look-ahead bias
#   7. Build growth-of-$1 curves for all strategies
#   8. Find winner (highest excess over S&P 500)
#   9. Create Hybrid if AI beats advisor      (main.py)
#  10. Compute all 5 metrics                  (metrics.py)
