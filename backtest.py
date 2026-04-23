"""
Backtest runner and performance analytics for the CAC40 Sector Rotation strategy.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from dataclasses import dataclass
from config import ANNUAL_FACTOR, ROLLING_SHARPE_WINDOW
from data import load_prices
from strategy import run_strategy


@dataclass
class BacktestResult:
    port_returns:    pd.Series
    bench_returns:   pd.Series
    equity_curve:    pd.Series
    bench_curve:     pd.Series
    log_df:          pd.DataFrame


def run_backtest() -> BacktestResult:
    """Load data, run strategy, compute equity curves."""
    print("Loading price data…")
    px, bench_px = load_prices()

    print("Running strategy…")
    port_rets, log_df = run_strategy(px, bench_px)

    bench_rets = bench_px.pct_change().reindex(port_rets.index).dropna()
    port_rets  = port_rets.reindex(bench_rets.index).dropna()

    eq_curve    = (1.0 + port_rets).cumprod()
    bench_curve = (1.0 + bench_rets).cumprod()

    return BacktestResult(
        port_returns=port_rets,
        bench_returns=bench_rets,
        equity_curve=eq_curve,
        bench_curve=bench_curve,
        log_df=log_df,
    )


def _annualized_stats(
    r:   pd.Series,
    ann: int = ANNUAL_FACTOR,
) -> dict:
    """Compute annualised return, Sharpe, Sortino, max drawdown, Calmar."""
    r   = r.dropna()
    if len(r) < 2 or r.std(ddof=1) == 0:
        return {k: float("nan") for k in
                ["Ann Return", "Sharpe", "Sortino", "Max DD", "Calmar", "Win Rate"]}

    cum      = (1.0 + r).cumprod()
    n        = len(r)
    ann_ret  = cum.iloc[-1] ** (ann / n) - 1.0
    sharpe   = (r.mean() / r.std(ddof=1)) * ann ** 0.5
    down_std = r[r < 0].std(ddof=1)
    sortino  = (r.mean() / down_std) * ann ** 0.5 if down_std > 0 else float("inf")
    dd       = (cum / cum.cummax()) - 1.0
    max_dd   = dd.min()
    calmar   = ann_ret / abs(max_dd) if max_dd != 0 else float("nan")
    win_rate = (r > 0).mean()

    return {
        "Ann Return": ann_ret,
        "Sharpe":     sharpe,
        "Sortino":    sortino,
        "Max DD":     max_dd,
        "Calmar":     calmar,
        "Win Rate":   win_rate,
    }


def compute_stats(result: BacktestResult) -> dict[str, dict]:
    """Return stats dict for strategy and benchmark."""
    return {
        "Strategy":  _annualized_stats(result.port_returns),
        "CAC40 B&H": _annualized_stats(result.bench_returns),
    }


def rolling_sharpe(returns: pd.Series, window: int = ROLLING_SHARPE_WINDOW) -> pd.Series:
    """Rolling annualised Sharpe ratio."""
    roll_mean = returns.rolling(window).mean()
    roll_std  = returns.rolling(window).std(ddof=1)
    return (roll_mean / roll_std) * ANNUAL_FACTOR ** 0.5
