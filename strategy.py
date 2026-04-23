"""
CAC40 Sector Rotation — Strategy Logic

Scoring:
    score(t) = momentum_12_1(t) / realized_vol_6m(t)

    where momentum_12_1 = price(t-1) / price(t-13) - 1
    (skip most recent month to avoid short-term reversal)

Portfolio construction:
    - Select best-scoring stock per sector
    - Take top-K across sectors
    - Equal weight within selected stocks

Market regime (cash management):
    - CAC40 above SMA-10M  → 100% equity
    - CAC40 below SMA-10M  → 50% equity, 50% cash
    - CAC40 below SMA-6M by > 5% → 0% equity, 100% cash
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from config import (
    SECTOR_MAP, TOP_K, MAX_PER_SECTOR, MIN_HISTORY_MONTHS,
    MOM_LONG, MOM_SHORT, VOL_WIN,
    TREND_SMA_LONG, TREND_SMA_SHORT, DEEP_BEAR_THRESH,
    HALF_CASH_EXPO, FULL_CASH_EXPO,
    CASH_YIELD_ANNUAL, ANNUAL_FACTOR, ROUND_TRIP_COST,
)


def compute_monthly_returns(px: pd.DataFrame) -> pd.DataFrame:
    """Compute month-over-month returns."""
    return px.pct_change()


def compute_scores(px: pd.DataFrame) -> pd.DataFrame:
    """
    Compute momentum / volatility score for every stock at every month-end date.
    Momentum = 12-1 month return (skip last month).
    Volatility = 6-month rolling std of monthly returns.
    Score = momentum / vol  (higher = better)
    """
    rets  = px.pct_change()
    mom   = px.shift(MOM_SHORT) / px.shift(MOM_LONG + MOM_SHORT) - 1.0
    vol   = rets.rolling(VOL_WIN).std(ddof=1)
    score = mom.div(vol.replace(0.0, np.nan))
    return score


def market_exposure(
    bench_px:   pd.Series,
    date:       pd.Timestamp,
    sma_long:   pd.Series,
    sma_short:  pd.Series,
) -> float:
    """
    Determine equity exposure for the given date based on CAC40 trend filters.

    Returns
    -------
    1.0  — fully invested (bull regime)
    0.5  — half cash (mild bear: below SMA-10)
    0.0  — full cash (deep bear: below SMA-6 by more than DEEP_BEAR_THRESH)
    """
    if pd.isna(sma_long.loc[date]) or pd.isna(sma_short.loc[date]):
        return 1.0

    price  = bench_px.loc[date]
    sma10  = sma_long.loc[date]
    sma6   = sma_short.loc[date]

    if price < sma6 * (1.0 + DEEP_BEAR_THRESH):   # deep bear (e.g. price < SMA6 - 5%)
        return FULL_CASH_EXPO
    elif price < sma10:                             # mild bear
        return HALF_CASH_EXPO
    else:
        return 1.0


def select_portfolio(
    scores:     pd.Series,              # Score series for one rebalancing date
    px_row:     pd.Series,              # Prices for the same date (availability check)
) -> list[str]:
    """
    Select up to TOP_K stocks with:
    - Valid score (not NaN)
    - Minimum history (not NaN in px_row)
    - At most MAX_PER_SECTOR from each sector
    """
    valid = scores.dropna()
    valid = valid[px_row.reindex(valid.index).notna()]

    if valid.empty:
        return []

    df = pd.DataFrame({
        "ticker": valid.index,
        "score":  valid.values,
    }).set_index("ticker")
    df["sector"] = df.index.map(SECTOR_MAP)
    df = df.dropna(subset=["sector"])

    # Pick best per sector, then sort globally
    best_per_sector = (
        df.groupby("sector")["score"]
        .nlargest(MAX_PER_SECTOR)
        .reset_index(level=0, drop=True)
    )
    top = (
        df.loc[best_per_sector.index]
        .sort_values("score", ascending=False)
        .head(TOP_K)
    )
    return top.index.tolist()


def run_strategy(
    px:          pd.DataFrame,
    bench_px:    pd.Series,
) -> tuple[pd.Series, pd.DataFrame]:
    """
    Execute the monthly sector-rotation backtest.

    Parameters
    ----------
    px       : Monthly close prices of universe stocks.
    bench_px : Monthly close prices of benchmark (CAC40).

    Returns
    -------
    port_returns : Monthly strategy returns (pd.Series).
    log_df       : DataFrame with portfolio composition per period.
    """
    rets     = compute_monthly_returns(px)
    scores   = compute_scores(px)
    bench_ret= bench_px.pct_change()

    # Pre-compute trend SMAs on benchmark
    sma_long  = bench_px.rolling(TREND_SMA_LONG).mean()
    sma_short = bench_px.rolling(TREND_SMA_SHORT).mean()

    cash_yield_monthly = (1.0 + CASH_YIELD_ANNUAL) ** (1.0 / ANNUAL_FACTOR) - 1.0

    dates      = rets.index
    port_rets  : list[tuple[pd.Timestamp, float]] = []
    log_rows   : list[dict] = []
    prev_portfolio: list[str] = []

    for i in range(MIN_HISTORY_MONTHS, len(dates) - 1):
        t_signal = dates[i]       # Date when we compute scores
        t_hold   = dates[i + 1]   # Date when we hold the portfolio

        # ── Score on signal date ───────────────────────────────────────────────
        score_row = scores.loc[t_signal]
        px_row    = px.loc[t_signal]
        portfolio = select_portfolio(score_row, px_row)

        if not portfolio:
            continue

        # ── Market regime (exposure) ───────────────────────────────────────────
        expo = market_exposure(bench_px, t_signal, sma_long, sma_short)

        # ── Transaction cost on turnover ──────────────────────────────────────
        prev_set = set(prev_portfolio)
        curr_set = set(portfolio)
        turnover = len(prev_set.symmetric_difference(curr_set)) / max(len(curr_set), 1)
        tc_drag  = turnover * ROUND_TRIP_COST

        # ── Portfolio return for t_hold ────────────────────────────────────────
        hold_rets = rets.loc[t_hold, portfolio].dropna()
        if hold_rets.empty:
            continue
        eq_ret     = hold_rets.mean()                          # equal weight
        cash_ret   = cash_yield_monthly
        period_ret = expo * eq_ret + (1.0 - expo) * cash_ret - tc_drag

        port_rets.append((t_hold, period_ret))
        log_rows.append({
            "Date":      t_hold.strftime("%Y-%m"),
            "Portfolio": ", ".join(portfolio),
            "Sectors":   ", ".join(SECTOR_MAP.get(t, "?") for t in portfolio),
            "Exposure":  f"{expo:.0%}",
            "Turnover":  f"{turnover:.1%}",
        })
        prev_portfolio = portfolio

    returns_series = pd.Series(
        [r for _, r in port_rets],
        index=[d for d, _ in port_rets],
        name="Strategy",
    )
    return returns_series, pd.DataFrame(log_rows)
