# ============================================================
# SNIPPET 22: The Final Chart (Excess Return vs S&P 500)
# ============================================================
# This is the main output of the entire project.
# The S&P 500 is shown as a flat dashed line at zero.
# Every other strategy shows how much it is above or below.
#
# Lines ABOVE zero = BEAT the S&P 500
# Lines BELOW zero = LOST to the S&P 500
# ============================================================

def plot_excess_over_sp500(series, output_dir, show=False):
    # Subtract S&P 500 from every strategy
    excess = series.subtract(series["S&P 500"], axis=0)
    excess = excess.drop(columns=["S&P 500"])

    fig, ax = plt.subplots(figsize=(10, 5.5))

    # Plot each strategy's excess return over time
    for i, col in enumerate(excess.columns):
        color = PUBLICATION_COLORS[i % len(PUBLICATION_COLORS)]
        ax.plot(excess.index, excess[col], label=col, color=color)

    # S&P 500 = flat line at zero (the benchmark)
    ax.axhline(y=0, color="black", linewidth=1, linestyle="--",
               label="S&P 500 Baseline")

    ax.legend()
    ax.set_title("Excess Return vs S&P 500")
    ax.set_xlabel("Date")
    ax.set_ylabel("Excess over S&P 500")

    if show:
        plt.show()  # Opens a popup window on your screen

# How to read this chart:
# - Dashed line at 0 = S&P 500 (buy and hold)
# - Advisor line at -0.18 = lost 18 cents per dollar vs S&P
# - GPT line at +0.07 = made 7 cents more per dollar vs S&P
# - If lines cross above zero, that model is currently winning
# - If lines cross below zero, that model is currently losing
