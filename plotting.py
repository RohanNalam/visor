import os
from typing import Optional

import pandas as pd

if "MPLCONFIGDIR" not in os.environ:
    cache_dir = os.path.join(os.getcwd(), ".mpl_cache")
    os.makedirs(cache_dir, exist_ok=True)
    os.environ["MPLCONFIGDIR"] = cache_dir

import matplotlib

# Publication-ready styling constants
PUBLICATION_DPI = 300
PUBLICATION_FIGSIZE = (10, 5.5)
PUBLICATION_TITLE_SIZE = 14
PUBLICATION_FONT_SIZE = 12
PUBLICATION_TICK_SIZE = 10
PUBLICATION_LEGEND_SIZE = 9

# Colorblind-friendly palette (Wong 2011 — standard for Nature/Science papers)
PUBLICATION_COLORS = [
    "#0072B2",  # Blue
    "#D55E00",  # Vermillion
    "#009E73",  # Bluish green
    "#CC79A7",  # Reddish purple
    "#E69F00",  # Orange
    "#56B4E9",  # Sky blue
    "#F0E442",  # Yellow
    "#000000",  # Black
]


def _get_pyplot(show: bool = False):
    if show:
        # Interactive popup requested — try native backend, fall back to Agg
        try:
            matplotlib.use("MacOSX", force=True)
        except Exception:
            matplotlib.use("Agg", force=True)
    else:
        # Non-interactive (saving to file) — always use Agg to avoid display requirement
        matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt
    return plt


def _apply_publication_style(ax, title: str, xlabel: str, ylabel: str) -> None:
    """Apply publication-ready styling to a matplotlib Axes."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(0.8)
    ax.spines["bottom"].set_linewidth(0.8)

    ax.set_title(title, fontsize=PUBLICATION_TITLE_SIZE, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, fontsize=PUBLICATION_FONT_SIZE)
    ax.set_ylabel(ylabel, fontsize=PUBLICATION_FONT_SIZE)
    ax.tick_params(axis="both", labelsize=PUBLICATION_TICK_SIZE)

    ax.grid(True, axis="y", alpha=0.2, linewidth=0.5)
    ax.grid(True, axis="x", alpha=0.1, linewidth=0.3)

    legend = ax.get_legend()
    if legend is not None:
        ax.legend(
            fontsize=PUBLICATION_LEGEND_SIZE,
            frameon=True,
            fancybox=False,
            edgecolor="#cccccc",
            framealpha=0.9,
        )


def plot_advisor_series(advisor_series: pd.Series, output_dir: Optional[str]) -> None:
    plt = _get_pyplot(show=False)
    fig, ax = plt.subplots(figsize=PUBLICATION_FIGSIZE)
    ax.plot(
        advisor_series.index, advisor_series.values,
        label="Advisor", color=PUBLICATION_COLORS[0], linewidth=1.5,
    )
    ax.legend()
    _apply_publication_style(ax, "Advisor Performance Curve", "Date", "Growth of $1")
    fig.tight_layout()
    if output_dir:
        path = os.path.join(output_dir, "advisor_curve.png")
        fig.savefig(path, dpi=PUBLICATION_DPI, bbox_inches="tight")


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
        fig, ax = plt.subplots(figsize=PUBLICATION_FIGSIZE)
        colors = [PUBLICATION_COLORS[i % len(PUBLICATION_COLORS)] for i in range(len(metrics))]
        ax.bar(metrics.index.astype(str), metrics[col].values, color=colors, edgecolor="white", linewidth=0.5)
        ax.set_xticks(range(len(metrics)))
        ax.set_xticklabels(metrics.index.astype(str), rotation=30, ha="right")
        title = col.replace("_", " ").title() + " by Strategy"
        _apply_publication_style(ax, title, "Strategy", col.replace("_", " ").title())
        fig.tight_layout()
        if output_dir:
            path = os.path.join(output_dir, f"{col}_bar.png")
            fig.savefig(path, dpi=PUBLICATION_DPI, bbox_inches="tight")


def plot_series(
    series: pd.DataFrame,
    output_dir: Optional[str],
    show: bool = False,
    frequency: Optional[str] = None,
    daily_grid: bool = False,
) -> None:
    plt = _get_pyplot(show=show)
    fig, ax = plt.subplots(figsize=PUBLICATION_FIGSIZE)
    for i, col in enumerate(series.columns):
        color = PUBLICATION_COLORS[i % len(PUBLICATION_COLORS)]
        linewidth = 2.0 if col == "S&P 500" else 1.5
        ax.plot(series.index, series[col], label=col, color=color, linewidth=linewidth)
    if daily_grid and frequency == "D":
        import matplotlib.dates as mdates

        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        ax.grid(True, axis="x", which="minor", alpha=0.1)
    ax.legend()
    _apply_publication_style(ax, "Visor Strategy Comparison", "Date", "Growth of $1")
    fig.tight_layout()
    if output_dir:
        path = os.path.join(output_dir, "visor_chart.png")
        fig.savefig(path, dpi=PUBLICATION_DPI, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)


def save_series_chart(
    series: pd.DataFrame,
    path: str,
    frequency: Optional[str] = None,
    daily_grid: bool = False,
) -> None:
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates

    fig = Figure(figsize=PUBLICATION_FIGSIZE)
    ax = fig.add_subplot(111)
    for i, col in enumerate(series.columns):
        color = PUBLICATION_COLORS[i % len(PUBLICATION_COLORS)]
        ax.plot(series.index, series[col], label=col, color=color, linewidth=1.5)
    if daily_grid and frequency == "D":
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_minor_locator(mdates.DayLocator(interval=1))
        ax.grid(True, axis="x", which="minor", alpha=0.1)
    ax.legend()
    _apply_publication_style(ax, "Visor Strategy Comparison", "Date", "Growth of $1")
    fig.tight_layout()
    fig.savefig(path, dpi=PUBLICATION_DPI, bbox_inches="tight")


def plot_excess_over_sp500(
    series: pd.DataFrame,
    output_dir: Optional[str],
    show: bool = False,
) -> None:
    if "S&P 500" not in series.columns:
        return
    plt = _get_pyplot(show=show)
    excess = series.subtract(series["S&P 500"], axis=0)
    excess = excess.drop(columns=["S&P 500"])

    fig, ax = plt.subplots(figsize=PUBLICATION_FIGSIZE)
    for i, col in enumerate(excess.columns):
        color = PUBLICATION_COLORS[i % len(PUBLICATION_COLORS)]
        ax.plot(excess.index, excess[col], label=col, color=color, linewidth=1.5)
    ax.axhline(y=0, color="black", linewidth=1, linestyle="--", label="S&P 500 Baseline")
    ax.legend()
    _apply_publication_style(ax, "Excess Return vs S&P 500", "Date", "Excess over S&P 500")
    fig.tight_layout()
    if output_dir:
        path = os.path.join(output_dir, "excess_over_sp500.png")
        fig.savefig(path, dpi=PUBLICATION_DPI, bbox_inches="tight")
    if show:
        plt.show()
    else:
        plt.close(fig)


def _plotly_config() -> dict:
    return {
        "displayModeBar": True,
        "scrollZoom": True,
        "modeBarButtonsToAdd": [
            "zoomIn2d",
            "zoomOut2d",
            "pan2d",
            "resetScale2d",
            "autoScale2d",
        ],
    }


def _plotly_output_path(output_dir: Optional[str], filename: str) -> str:
    if output_dir:
        return os.path.join(output_dir, filename)
    tmp_dir = os.path.join(os.getcwd(), ".tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    return os.path.join(tmp_dir, filename)


def _open_in_browser(path: str) -> None:
    import webbrowser
    import subprocess

    try:
        opened = webbrowser.open(f"file://{path}")
    except Exception:
        opened = False
    if not opened:
        subprocess.run(["open", path], check=False)


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
    for i, col in enumerate(series.columns):
        color = PUBLICATION_COLORS[i % len(PUBLICATION_COLORS)]
        fig.add_trace(go.Scatter(
            x=series.index, y=series[col], mode="lines", name=col,
            line=dict(color=color),
        ))
    fig.update_layout(
        title="Visor Strategy Comparison (Interactive)",
        xaxis_title="Date",
        yaxis_title="Growth of $1",
        hovermode="x unified",
        dragmode="pan",
    )
    fig.update_xaxes(rangeslider={"visible": True})

    path = _plotly_output_path(output_dir, "visor_chart_interactive.html")
    fig.write_html(path, include_plotlyjs="cdn", config=_plotly_config())

    if open_browser:
        _open_in_browser(path)

    return path


def plot_excess_interactive(
    series: pd.DataFrame,
    output_dir: Optional[str],
    open_browser: bool = False,
) -> Optional[str]:
    if "S&P 500" not in series.columns:
        return None
    try:
        import plotly.graph_objects as go
    except ImportError as exc:
        raise SystemExit(
            "plotly is required for interactive charts. Install with: pip install plotly"
        ) from exc

    excess = series.subtract(series["S&P 500"], axis=0)
    excess = excess.drop(columns=["S&P 500"])

    fig = go.Figure()
    for i, col in enumerate(excess.columns):
        color = PUBLICATION_COLORS[i % len(PUBLICATION_COLORS)]
        fig.add_trace(go.Scatter(
            x=excess.index, y=excess[col], mode="lines", name=col,
            line=dict(color=color),
        ))
    fig.add_hline(y=0, line_dash="dash", line_color="black",
                  annotation_text="S&P 500 Baseline")
    fig.update_layout(
        title="Excess Return vs S&P 500 (Interactive)",
        xaxis_title="Date",
        yaxis_title="Excess over S&P 500",
        hovermode="x unified",
        dragmode="pan",
    )
    fig.update_xaxes(rangeslider={"visible": True})

    path = _plotly_output_path(output_dir, "excess_over_sp500_interactive.html")
    fig.write_html(path, include_plotlyjs="cdn", config=_plotly_config())

    if open_browser:
        _open_in_browser(path)

    return path
