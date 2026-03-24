"""Generate a publication-quality metrics table image."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np

RUN_DIR = "outputs/run_20260323_162745"
OUT_DIR = os.path.join(RUN_DIR, "paper_charts")
os.makedirs(OUT_DIR, exist_ok=True)

metrics = pd.read_csv(os.path.join(RUN_DIR, "metrics.csv"), index_col=0)

# Display order and short names
order = [
    "S&P 500",
    "Quant Model (Trend + Momentum + RSI + Vol Filter)",
    "Advisor",
    "claude_sonnet",
    "deepseek",
    "gemini",
    "gpt",
    "grok",
    "Hybrid (Advisor + grok)",
]
short_names = {
    "S&P 500": "S&P 500",
    "Quant Model (Trend + Momentum + RSI + Vol Filter)": "Quant Model",
    "Advisor": "Advisor",
    "claude_sonnet": "Claude Sonnet",
    "deepseek": "DeepSeek",
    "gemini": "Gemini",
    "gpt": "GPT",
    "grok": "Grok",
    "Hybrid (Advisor + grok)": "Hybrid (Advisor + Grok)",
}

metrics = metrics.reindex([o for o in order if o in metrics.index])

col_labels = ["Strategy", "Cum. Return", "Ann. Return", "Volatility", "Sharpe", "Max DD", "Excess vs S&P"]

rows = []
for name, row in metrics.iterrows():
    rows.append([
        short_names.get(name, name),
        f"{row['cumulative_return']:+.1%}",
        f"{row['annualized_return']:+.1%}",
        f"{row['volatility']:.1%}",
        f"{row['sharpe']:.2f}",
        f"{row['max_drawdown']:.1%}",
        f"{row['excess_over_sp500']:+.3f}",
    ])

fig, ax = plt.subplots(figsize=(14, 4.8))
ax.axis("off")

COLORS_LIST = [
    "#0072B2", "#D55E00", "#009E73", "#CC79A7",
    "#E69F00", "#56B4E9", "#F0E442", "#000000", "#888888",
]

# Build cell colours — header row + data rows
header_color = "#2c3e50"
sp500_highlight = "#e8f4f8"
row_colors = []
for i, name in enumerate(metrics.index):
    base = "#ffffff" if i % 2 == 0 else "#f7f7f7"
    if name == "S&P 500":
        base = sp500_highlight
    row_colors.append([base] * len(col_labels))

cell_text = rows
col_widths = [0.22, 0.11, 0.11, 0.11, 0.09, 0.09, 0.14]

table = ax.table(
    cellText=cell_text,
    colLabels=col_labels,
    cellLoc="center",
    loc="center",
    colWidths=col_widths,
)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.7)

# Style header
for j in range(len(col_labels)):
    cell = table[0, j]
    cell.set_facecolor(header_color)
    cell.set_text_props(color="white", fontweight="bold", fontsize=10)
    cell.set_edgecolor("#ffffff")

# Style data rows
sp500_idx = None
for i, name in enumerate(metrics.index):
    if name == "S&P 500":
        sp500_idx = i

for i, name in enumerate(metrics.index):
    row_idx = i + 1  # +1 for header
    base_bg = "#f7f7f7" if i % 2 == 0 else "#ffffff"
    is_sp500 = (name == "S&P 500")

    for j in range(len(col_labels)):
        cell = table[row_idx, j]
        cell.set_edgecolor("#e0e0e0")

        if is_sp500:
            cell.set_facecolor("#ddeeff")
            cell.set_text_props(fontweight="bold")
        else:
            cell.set_facecolor(base_bg)

        # Color-code strategy name with its chart color
        if j == 0:
            cell.set_text_props(color=COLORS_LIST[i] if not is_sp500 else "#0072B2",
                                fontweight="bold" if is_sp500 else "normal")

        # Color-code excess column: green > 0, red < 0
        if j == 6 and not is_sp500:
            val = metrics.iloc[i]["excess_over_sp500"]
            cell.set_text_props(color="#006600" if val > 0 else "#990000",
                                fontweight="bold")

ax.set_title(
    "Performance Metrics — All 9 Strategies (Jan 2020 – Jan 2026, Monthly, r_f = 4%)",
    fontsize=12, fontweight="bold", pad=16, color="#2c3e50",
)

fig.tight_layout()
path = os.path.join(OUT_DIR, "metrics_table.png")
fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
plt.close(fig)
print(f"Saved → {path}")
