"""
Data loading for the CAC40 Sector Rotation strategy.
Downloads adjusted monthly close prices for all universe stocks + benchmark.
"""

from __future__ import annotations
import pandas as pd
import yfinance as yf
from config import UNIVERSE, BENCHMARK, START_DATE, END_DATE, REBAL_FREQ


def load_prices(
    universe:   list[str] = UNIVERSE,
    benchmark:  str       = BENCHMARK,
    start:      str       = START_DATE,
    end:        str       = END_DATE,
    freq:       str       = REBAL_FREQ,
) -> tuple[pd.DataFrame, pd.Series]:
    """
    Download daily adjusted-close prices, resample to month-end,
    and return (stock_prices, benchmark_prices).

    Parameters
    ----------
    universe  : List of Yahoo Finance tickers.
    benchmark : Benchmark ticker (e.g. "^FCHI").
    start     : ISO date string.
    end       : ISO date string.
    freq      : Pandas resample frequency (default "ME" = month-end).

    Returns
    -------
    px_monthly : DataFrame of monthly close prices (rows=dates, cols=tickers).
    bench_monthly : Series of monthly benchmark closes.
    """
    all_tickers = sorted(set(universe)) + [benchmark]

    print(f"  Downloading {len(all_tickers)} tickers from Yahoo Finance…")
    raw = yf.download(
        all_tickers,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        group_by="ticker",
    )

    # Extract close prices — handle both multi-level and single-level columns
    if isinstance(raw.columns, pd.MultiIndex):
        close_daily = raw.xs("Close", axis=1, level=1)
    else:
        close_daily = raw[["Close"]] if "Close" in raw.columns else raw

    close_daily = close_daily.reindex(columns=all_tickers)
    close_daily.ffill(inplace=True)
    close_daily.bfill(inplace=True)
    close_daily.index = pd.to_datetime(close_daily.index)

    # Resample to month-end
    px_monthly = close_daily.resample(freq).last().dropna(how="all")

    bench_monthly = px_monthly.pop(benchmark)
    return px_monthly, bench_monthly
