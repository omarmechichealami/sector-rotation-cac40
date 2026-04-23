"""
Professional charts for the CAC40 Sector Rotation strategy.
Generates 5 figures saved to ./charts/.
"""

from __future__ import annotations
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from backtest import BacktestResult, rolling_sharpe
from config import ROLLING_SHARPE_WINDOW, SECTOR_MAP

OUTPUT_DIR = Path("charts")
OUTPUT_DIR.mkdir(exist_ok=True)

COLORS = {
    "strategy":  "#1a73e8",
    "benchmark": "#ea4335",
    "positive":  "#34a853",
    "negative":  "#ea4335",
    "neutral":   "#9e9e9e",
    "bg":        "#f8f9fa",
}

SECTOR_PALETTE = [
    "#4285F4", "#EA4335", "#FBBC05", "#34A853",
    "#FF6D00", "#46BDC6", "#7B61FF", "#E91E63",
    "#00BCD4", "#8BC34A",
]


def _save(fig: plt.Figure, name: str) -> None:
    path = OUTPUT_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    print(f"  Saved → {path}")
    plt.close(fig)


def plot_equity_curve(result: BacktestResult) -> None:
    """Strategy equity curve vs CAC40 buy-and-hold."""
    strat = result.equity_curve
    bench = result.bench_curve.reindex(strat.index).ffill()

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_facecolor(COLORS["bg"])
    ax.plot(strat.index, strat.values,
            color=COLORS["strategy"], lw=2.4, label="CAC40 Sector Rotation Strategy")
    ax.plot(bench.index, bench.values,
            color=COLORS["benchmark"], lw=1.6, ls="--", alpha=0.85, label="CAC40 Buy & Hold")
    ax.fill_between(strat.index,
                    strat.values, bench.values,
                    where=(strat.values >= bench.values),
                    alpha=0.12, color=COLORS["positive"], label="Outperformance")
    ax.fill_between(strat.index,
                    strat.values, bench.values,
                    where=(strat.values < bench.values),
                    alpha=0.12, color=COLORS["negative"])

    ax.set_title("CAC40 Sector Rotation — Cumulative Performance vs Benchmark",
                 fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel("Growth of $1")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, "equity_curve.png")


def plot_drawdown(result: BacktestResult) -> None:
    """Underwater equity chart for strategy and benchmark."""
    def dd_series(eq: pd.Series) -> pd.Series:
        return (eq / eq.cummax()) - 1.0

    strat_dd = dd_series(result.equity_curve)
    bench_dd = dd_series(result.bench_curve.reindex(result.equity_curve.index).ffill())

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.set_facecolor(COLORS["bg"])
    ax.fill_between(strat_dd.index, strat_dd.values, 0,
                    color=COLORS["strategy"], alpha=0.45, label="Strategy DD")
    ax.fill_between(bench_dd.index, bench_dd.values, 0,
                    color=COLORS["benchmark"], alpha=0.25, label="CAC40 DD")
    ax.plot(strat_dd.index, strat_dd.values, color=COLORS["strategy"], lw=0.9)

    ax.set_title("Drawdown Chart — Strategy vs CAC40",
                 fontsize=13, fontweight="bold", pad=12)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, "drawdown.png")


def plot_rolling_sharpe(result: BacktestResult) -> None:
    """Rolling Sharpe ratio (strategy vs benchmark)."""
    strat_rs = rolling_sharpe(result.port_returns, ROLLING_SHARPE_WINDOW)
    bench_rs = rolling_sharpe(result.bench_returns, ROLLING_SHARPE_WINDOW)

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.set_facecolor(COLORS["bg"])
    ax.plot(strat_rs.index, strat_rs.values,
            color=COLORS["strategy"], lw=2.0, label=f"Strategy (rolling {ROLLING_SHARPE_WINDOW}m Sharpe)")
    ax.plot(bench_rs.index, bench_rs.values,
            color=COLORS["benchmark"], lw=1.4, ls="--", alpha=0.8,
            label=f"CAC40 (rolling {ROLLING_SHARPE_WINDOW}m Sharpe)")
    ax.axhline(0, color="black", lw=0.8, ls=":")
    ax.axhline(1, color=COLORS["positive"], lw=0.8, ls=":", alpha=0.7, label="Sharpe = 1")

    ax.set_title(f"Rolling {ROLLING_SHARPE_WINDOW}-Month Sharpe Ratio",
                 fontsize=13, fontweight="bold", pad=12)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, "rolling_sharpe.png")


def plot_sector_allocation(log_df: pd.DataFrame) -> None:
    """Bar chart of sector frequency in the portfolio over time."""
    if log_df.empty:
        return

    all_sectors: list[str] = []
    for row in log_df["Sectors"]:
        all_sectors.extend([s.strip() for s in str(row).split(",")])

    counts  = Counter(all_sectors)
    sectors = list(counts.keys())
    values  = list(counts.values())
    colors  = SECTOR_PALETTE[: len(sectors)]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.set_facecolor(COLORS["bg"])
    bars = ax.barh(sectors, values, color=colors, edgecolor="white", linewidth=0.5)
    ax.bar_label(bars, fmt="%d", padding=4, fontsize=10)
    ax.set_title("Sector Frequency in Portfolio (All Rebalancing Periods)",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Number of months held")
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    _save(fig, "sector_allocation.png")


def plot_summary_table(stats: dict[str, dict]) -> None:
    """Side-by-side performance comparison table."""
    metrics = list(next(iter(stats.values())).keys())
    labels  = list(stats.keys())

    def fmt(k: str, v: float) -> str:
        if isinstance(v, float) and not np.isnan(v):
            if k in ("Ann Return", "Max DD", "Win Rate"):
                return f"{v:.2%}"
            return f"{v:.3f}"
        return "—"

    header  = ["Metric"] + labels
    rows    = [header, ["─" * 26] + ["─" * 14] * len(labels)]
    for m in metrics:
        row = [m] + [fmt(m, stats[lbl][m]) for lbl in labels]
        rows.append(row)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.axis("off")
    tbl = ax.table(cellText=rows, cellLoc="left", loc="center", bbox=[0, 0, 1, 1])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(11)

    # Header row styling
    for j in range(len(header)):
        tbl[0, j].set_facecolor("#1a73e8")
        tbl[0, j].set_text_props(color="white", fontweight="bold")
    # Strategy column highlight
    for i in range(2, len(rows)):
        tbl[i, 1].set_facecolor("#e8f0fe")

    ax.set_title("CAC40 Sector Rotation — Performance Summary",
                 fontsize=13, fontweight="bold", pad=10)
    fig.tight_layout()
    _save(fig, "summary_table.png")
