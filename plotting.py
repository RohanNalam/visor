import os
from typing import Optional

import pandas as pd

if "MPLCONFIGDIR" not in os.environ:
    cache_dir = os.path.join(os.getcwd(), ".mpl_cache")
    os.makedirs(cache_dir, exist_ok=True)
    os.environ["MPLCONFIGDIR"] = cache_dir

import matplotlib


def _get_pyplot(show: bool):
    backend = "MacOSX" if show else "Agg"
    try:
        matplotlib.use(backend, force=True)
    except Exception:
        matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    return plt


def plot_advisor_series(advisor_series: pd.Series, output_dir: Optional[str]) -> None:
    plt = _get_pyplot(show=False)
    plt.figure(figsize=(10, 5))
    plt.plot(advisor_series.index, advisor_series.values, label="Advisor")
    plt.title("Advisor Performance Curve")
    plt.xlabel("Date")
    plt.ylabel("Growth of $1")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    if output_dir:
        path = os.path.join(output_dir, "advisor_curve.png")
        plt.savefig(path, dpi=200)


def plot_metrics_bars(metrics: pd.DataFrame, output_dir: Optional[str]) -> None:
    plt = _get_pyplot(show=False)
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
        if output_dir:
            path = os.path.join(output_dir, f"{col}_bar.png")
            plt.savefig(path, dpi=200)


def plot_series(
    series: pd.DataFrame, output_dir: Optional[str], show: bool = False
) -> None:
    plt = _get_pyplot(show=show)
    plt.figure(figsize=(12, 6))
    for col in series.columns:
        plt.plot(series.index, series[col], label=col)
    plt.title("Visor Strategy Comparison")
    plt.xlabel("Date")
    plt.ylabel("Growth of $1")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    if output_dir:
        path = os.path.join(output_dir, "visor_chart.png")
        plt.savefig(path, dpi=200)
    if show:
        plt.show()


def plot_series_interactive(
    series: pd.DataFrame,
    output_dir: Optional[str],
    open_browser: bool = False,
) -> Optional[str]:
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise SystemExit(
            "plotly is required for interactive charts. Install with: pip install plotly"
        ) from exc

    fig = go.Figure()
    for col in series.columns:
        fig.add_trace(go.Scatter(x=series.index, y=series[col], mode="lines", name=col))
    fig.update_layout(
        title="Visor Strategy Comparison (Interactive)",
        xaxis_title="Date",
        yaxis_title="Growth of $1",
        hovermode="x unified",
    )

    if output_dir:
        path = os.path.join(output_dir, "visor_chart_interactive.html")
    else:
        tmp_dir = os.path.join(os.getcwd(), ".tmp")
        os.makedirs(tmp_dir, exist_ok=True)
        path = os.path.join(tmp_dir, "visor_chart_interactive.html")

    fig.write_html(path, include_plotlyjs="cdn")

    if open_browser:
        import webbrowser

        webbrowser.open(f"file://{path}")

    return path
