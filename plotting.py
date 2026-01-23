import os

import pandas as pd

if "MPLCONFIGDIR" not in os.environ:
    cache_dir = os.path.join(os.getcwd(), ".mpl_cache")
    os.makedirs(cache_dir, exist_ok=True)
    os.environ["MPLCONFIGDIR"] = cache_dir

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot_advisor_series(advisor_series: pd.Series, output_dir: str) -> None:
    plt.figure(figsize=(10, 5))
    plt.plot(advisor_series.index, advisor_series.values, label="Advisor")
    plt.title("Advisor Performance Curve")
    plt.xlabel("Date")
    plt.ylabel("Growth of $1")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    path = os.path.join(output_dir, "advisor_curve.png")
    plt.savefig(path, dpi=200)


def plot_metrics_bars(metrics: pd.DataFrame, output_dir: str) -> None:
    metric_cols = [
        "cumulative_return",
        "annualized_return",
        "volatility",
        "sharpe",
        "max_drawdown",
    ]
    available = [col for col in metric_cols if col in metrics.columns]
    if not available:
        return

    for col in available:
        plt.figure(figsize=(10, 5))
        plt.bar(metrics.index.astype(str), metrics[col].values)
        plt.title(f"{col.replace('_', ' ').title()} by Strategy")
        plt.xlabel("Strategy")
        plt.ylabel(col.replace("_", " ").title())
        plt.xticks(rotation=30, ha="right")
        plt.tight_layout()
        path = os.path.join(output_dir, f"{col}_bar.png")
        plt.savefig(path, dpi=200)


def plot_series(series: pd.DataFrame, output_dir: str, show: bool = False) -> None:
    plt.figure(figsize=(12, 6))
    for col in series.columns:
        plt.plot(series.index, series[col], label=col)
    plt.title("Visor Strategy Comparison")
    plt.xlabel("Date")
    plt.ylabel("Growth of $1")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    path = os.path.join(output_dir, "visor_chart.png")
    plt.savefig(path, dpi=200)
    if show:
        plt.show()
