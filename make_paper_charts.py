"""Generate all paper charts for the latest run."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

RUN_DIR = "outputs/run_20260323_171214"
OUT_DIR = os.path.join(RUN_DIR, "paper_charts")
os.makedirs(OUT_DIR, exist_ok=True)

COLORS = [
    "#0072B2", "#D55E00", "#009E73", "#CC79A7",
    "#E69F00", "#56B4E9", "#F0E442", "#000000", "#888888",
]
DPI = 300

series = pd.read_csv(os.path.join(RUN_DIR, "strategy_series.csv"), index_col=0, parse_dates=True)
metrics = pd.read_csv(os.path.join(RUN_DIR, "metrics.csv"), index_col=0)

print("Strategies:", list(series.columns))

# ── Chart 1: Excess Return vs S&P 500 ────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5.5))
excess = series.subtract(series["S&P 500"], axis=0).drop(columns=["S&P 500"])
for i, col in enumerate(excess.columns):
    ax.plot(excess.index, excess[col], label=col, color=COLORS[i % len(COLORS)], linewidth=1.5)
ax.axhline(0, color="black", linewidth=1, linestyle="--", label="S&P 500 Baseline")
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.set_title("Excess Return vs S&P 500", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Date", fontsize=12); ax.set_ylabel("Excess over S&P 500", fontsize=12)
ax.legend(fontsize=8, frameon=True, fancybox=False, edgecolor="#ccc")
ax.grid(True, axis="y", alpha=0.2)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "1_excess_return_vs_sp500.png"), dpi=DPI, bbox_inches="tight")
plt.close(fig)
print("Saved 1")

# ── Chart 2A: Cumulative Growth All Together ──────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5.5))
for i, col in enumerate(series.columns):
    lw = 2.2 if col == "S&P 500" else 1.5
    ax.plot(series.index, series[col], label=col, color=COLORS[i % len(COLORS)], linewidth=lw)
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.set_title("Visor Strategy Comparison", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Date", fontsize=12); ax.set_ylabel("Growth of $1", fontsize=12)
ax.legend(fontsize=8, frameon=True, fancybox=False, edgecolor="#ccc")
ax.grid(True, axis="y", alpha=0.2)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "2A_cumulative_growth_all.png"), dpi=DPI, bbox_inches="tight")
plt.close(fig)
print("Saved 2A")

# ── Chart 2B: Split Panel ─────────────────────────────────────────────────
hybrid_col = [c for c in series.columns if c.startswith("Hybrid")][0] if any(c.startswith("Hybrid") for c in series.columns) else None
left_cols = ["S&P 500", "Advisor", "Quant Model (Trend + Momentum + RSI + Vol Filter)"] + ([hybrid_col] if hybrid_col else [])
llm_models = [c for c in series.columns if c not in ["S&P 500", "Advisor", "Quant Model (Trend + Momentum + RSI + Vol Filter)"] and not (hybrid_col and c == hybrid_col)]
left_cols = [c for c in left_cols if c in series.columns]
right_cols = ["S&P 500"] + llm_models

fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(16, 5.5))
for i, col in enumerate(left_cols):
    lw = 2.2 if col == "S&P 500" else 1.6
    ls = "--" if col == "S&P 500" else "-"
    ax_l.plot(series.index, series[col], label=col, color=COLORS[i], linewidth=lw, linestyle=ls)
ax_l.set_title("S&P 500 · Advisor · Quant · Hybrid", fontsize=13, fontweight="bold")
ax_l.set_xlabel("Date"); ax_l.set_ylabel("Growth of $1")
ax_l.legend(fontsize=8, frameon=True, fancybox=False, edgecolor="#ccc")
ax_l.spines["top"].set_visible(False); ax_l.spines["right"].set_visible(False)
ax_l.grid(True, axis="y", alpha=0.2)
ax_l.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

for i, col in enumerate(right_cols):
    lw = 2.2 if col == "S&P 500" else 1.4
    ls = "--" if col == "S&P 500" else "-"
    ax_r.plot(series.index, series[col], label=col, color=COLORS[i], linewidth=lw, linestyle=ls)
ax_r.set_title("S&P 500 vs. Individual LLM Models", fontsize=13, fontweight="bold")
ax_r.set_xlabel("Date"); ax_r.set_ylabel("Growth of $1")
ax_r.legend(fontsize=8, frameon=True, fancybox=False, edgecolor="#ccc")
ax_r.spines["top"].set_visible(False); ax_r.spines["right"].set_visible(False)
ax_r.grid(True, axis="y", alpha=0.2)
ax_r.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

fig.suptitle("Cumulative Growth of $1 — Split by Strategy Category (2020–2026)", fontsize=14, fontweight="bold", y=1.01)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "2B_cumulative_growth_split.png"), dpi=DPI, bbox_inches="tight")
plt.close(fig)
print("Saved 2B")

# ── Chart 2C: Year-by-Year Bar ────────────────────────────────────────────
year_ends = {}
for year in [2020, 2021, 2022, 2023, 2024, 2025, 2026]:
    mask = series.index.year == year
    if mask.any():
        year_ends[year] = series[mask].iloc[-1]
ydf = (pd.DataFrame(year_ends).T - 1.0) * 100

all_strats = list(series.columns)
n_strats = len(all_strats)
n_years = len(ydf)
x = np.arange(n_years)
bar_width = 0.8 / n_strats

fig, ax = plt.subplots(figsize=(16, 6))
for i, col in enumerate(all_strats):
    if col not in ydf.columns: continue
    offset = (i - n_strats / 2 + 0.5) * bar_width
    ax.bar(x + offset, ydf[col].values, bar_width * 0.92,
           label=col, color=COLORS[i % len(COLORS)], edgecolor="white", linewidth=0.4)
ax.set_xticks(x)
ax.set_xticklabels([str(y) for y in ydf.index], fontsize=11)
ax.set_xlabel("Year-End", fontsize=12); ax.set_ylabel("Cumulative Return from Jan 2020 (%)", fontsize=12)
ax.set_title("Year-by-Year Cumulative Return — All 9 Strategies (2020–2026)", fontsize=14, fontweight="bold", pad=12)
ax.axhline(0, color="black", linewidth=0.8)
ax.legend(fontsize=7.5, frameon=True, fancybox=False, edgecolor="#ccc", ncol=3, loc="upper left")
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", alpha=0.2)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "2C_cumulative_return_by_year.png"), dpi=DPI, bbox_inches="tight")
plt.close(fig)
print("Saved 2C")

# ── Chart 3: Sharpe Bar ───────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5.5))
colors = [COLORS[i % len(COLORS)] for i in range(len(metrics))]
ax.bar(metrics.index.astype(str), metrics["sharpe"].values, color=colors, edgecolor="white", linewidth=0.5)
ax.set_xticks(range(len(metrics)))
ax.set_xticklabels(metrics.index.astype(str), rotation=30, ha="right")
ax.spines["top"].set_visible(False); ax.spines["right"].set_visible(False)
ax.set_title("Sharpe Ratio by Strategy", fontsize=14, fontweight="bold", pad=12)
ax.set_xlabel("Strategy", fontsize=12); ax.set_ylabel("Sharpe Ratio", fontsize=12)
ax.grid(True, axis="y", alpha=0.2)
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "3_sharpe_by_strategy.png"), dpi=DPI, bbox_inches="tight")
plt.close(fig)
print("Saved 3")

# ── Metrics Table Image ───────────────────────────────────────────────────
order = ["S&P 500", "Quant Model (Trend + Momentum + RSI + Vol Filter)", "Advisor",
         "claude_sonnet", "deepseek", "gemini", "gpt", "grok"]
if hybrid_col:
    order.append(hybrid_col)
short_names = {
    "S&P 500": "S&P 500",
    "Quant Model (Trend + Momentum + RSI + Vol Filter)": "Quant Model",
    "Advisor": "Advisor",
    "claude_sonnet": "Claude Sonnet",
    "deepseek": "DeepSeek",
    "gemini": "Gemini",
    "gpt": "GPT",
    "grok": "Grok",
}
if hybrid_col:
    short_names[hybrid_col] = hybrid_col.replace("Hybrid (Advisor + ", "Hybrid + ").rstrip(")")

metrics_ordered = metrics.reindex([o for o in order if o in metrics.index])
col_labels = ["Strategy", "Cum. Return", "Ann. Return", "Volatility", "Sharpe", "Max DD", "Excess vs S&P"]
rows = []
for name, row in metrics_ordered.iterrows():
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
col_widths = [0.22, 0.11, 0.11, 0.11, 0.09, 0.09, 0.14]
table = ax.table(cellText=rows, colLabels=col_labels, cellLoc="center", loc="center", colWidths=col_widths)
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.7)

header_color = "#2c3e50"
for j in range(len(col_labels)):
    cell = table[0, j]
    cell.set_facecolor(header_color)
    cell.set_text_props(color="white", fontweight="bold", fontsize=10)
    cell.set_edgecolor("#ffffff")

for i, name in enumerate(metrics_ordered.index):
    row_idx = i + 1
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
        if j == 0:
            cell.set_text_props(color=COLORS[i % len(COLORS)] if not is_sp500 else "#0072B2",
                                fontweight="bold" if is_sp500 else "normal")
        if j == 6 and not is_sp500:
            val = metrics_ordered.iloc[i]["excess_over_sp500"]
            cell.set_text_props(color="#006600" if val > 0 else "#990000", fontweight="bold")

ax.set_title("Performance Metrics — All 9 Strategies (Jan 2020 – Jan 2026, Monthly, r_f = 4%)",
             fontsize=12, fontweight="bold", pad=16, color="#2c3e50")
fig.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "metrics_table.png"), dpi=DPI, bbox_inches="tight", facecolor="white")
plt.close(fig)
print("Saved table")
print(f"\nAll charts saved to {OUT_DIR}")
