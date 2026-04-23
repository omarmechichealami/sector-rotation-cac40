"""
CAC40 Sector Rotation Strategy — Main Entry Point

Run:
    python main.py

Outputs:
    - Performance statistics to console
    - 5 charts saved to ./charts/
    - Portfolio composition log printed
"""

from __future__ import annotations
import pandas as pd
from backtest import run_backtest, compute_stats
from visualize import (
    plot_equity_curve,
    plot_drawdown,
    plot_rolling_sharpe,
    plot_sector_allocation,
    plot_summary_table,
)


def print_stats(stats: dict[str, dict]) -> None:
    """Pretty-print strategy vs benchmark performance table."""
    sep   = "═" * 62
    labels = list(stats.keys())
    metrics = list(next(iter(stats.values())).keys())

    print(f"\n{sep}")
    header = f"  {'Metric':<26}" + "".join(f"{lbl:>16}" for lbl in labels)
    print(header)
    print(sep)

    for m in metrics:
        row = f"  {m:<26}"
        for lbl in labels:
            v = stats[lbl][m]
            if isinstance(v, float):
                if m in ("Ann Return", "Max DD", "Win Rate"):
                    row += f"{v:>15.2%} "
                else:
                    row += f"{v:>15.3f} "
            else:
                row += f"{'—':>15} "
        print(row)
    print(sep + "\n")


def main() -> None:
    result = run_backtest()

    if result.port_returns.empty:
        print("No portfolio returns generated. Check universe data availability.")
        return

    # ── Performance stats ──────────────────────────────────────────────────────
    stats = compute_stats(result)
    print_stats(stats)

    # ── Portfolio log (last 12 months) ────────────────────────────────────────
    print("── Recent Portfolio Compositions (last 12 periods) ──────────────")
    print(result.log_df.tail(12).to_string(index=False))

    # ── Charts ────────────────────────────────────────────────────────────────
    print("\nGenerating charts…")
    plot_equity_curve(result)
    plot_drawdown(result)
    plot_rolling_sharpe(result)
    plot_sector_allocation(result.log_df)
    plot_summary_table(stats)
    print("Done. Charts saved in ./charts/")


if __name__ == "__main__":
    main()
