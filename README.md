# CAC40 Sector Rotation Strategy

> A systematic, monthly-rebalanced equity strategy that rotates into the highest-momentum
> stocks of the CAC40, diversified across sectors, with a macro regime filter that
> dynamically shifts allocation to cash during market downturns.

---

## Strategy Thesis

Cross-sectional momentum — the tendency of recent winners to keep outperforming recent
losers over the following months — is one of the most robust and well-documented anomalies
in academic finance (Jegadeesh & Titman, 1993; Carhart, 1997).

This strategy systematically exploits momentum within the CAC40 universe by:

1. **Ranking stocks** monthly by risk-adjusted momentum (12-1 month return ÷ 6-month volatility)
2. **Enforcing sector diversification** — at most 1 stock per sector prevents concentration in
   a single theme (e.g., all-Luxury during LVMH rallies)
3. **Adapting to market regimes** — a dual-threshold cash filter cuts equity exposure when
   the CAC40 is in a downtrend, dramatically reducing maximum drawdown

The result is a strategy that captures the equity risk premium more efficiently than
buy-and-hold, while limiting the catastrophic drawdowns seen during bear markets.

---

## Methodology

### 1. Momentum Score

```
Score(i, t) = [Price(i, t-1) / Price(i, t-13) - 1] / σ_6m(i, t)
```

- **12-1 momentum**: 12-month return, skipping the most recent month (avoids short-term
  reversal contamination — a well-known bias in raw momentum strategies)
- **Volatility adjustment**: dividing by 6-month realized volatility penalises erratic
  stocks and rewards smooth, consistent trends

### 2. Portfolio Construction

| Parameter | Value |
|-----------|-------|
| Universe | 27 CAC40 large-cap stocks |
| Holdings | Top 6 stocks |
| Sector diversification | Max 1 stock per sector |
| Weighting | Equal weight |
| Rebalancing | Monthly (month-end) |
| Min. history | 15 months before inclusion |

### 3. Market Regime Filter (Cash Management)

| Condition | Equity Exposure |
|-----------|----------------|
| CAC40 > SMA(10M) | 100% equities |
| CAC40 < SMA(10M) | 50% equities + 50% cash |
| CAC40 < SMA(6M) × 0.95 | 0% equities + 100% cash |

Cash earns 3%/year (ESTER proxy). This filter significantly reduces drawdown during
extended bear markets (2018 Q4, 2020 COVID crash, 2022 rate-shock).

### 4. Transaction Costs

A 0.30% round-trip cost is applied, proportional to the portfolio turnover at each
rebalancing — making the backtest realistic for institutional-grade execution.

---

## Backtest Results

> Run `python main.py` to reproduce all figures.
> Period: January 2016 — December 2024 (9-year backtest, monthly frequency)

| Metric | Strategy | CAC40 B&H |
|--------|----------|-----------|
| Annualized Return | see charts | — |
| Sharpe Ratio | see charts | — |
| Sortino Ratio | see charts | — |
| Max Drawdown | see charts | — |
| Calmar Ratio | see charts | — |
| Win Rate (months) | see charts | — |

**Generated Charts** (in `./charts/` after running):

| File | Description |
|------|-------------|
| `equity_curve.png` | Cumulative return vs CAC40 with outperformance shading |
| `drawdown.png` | Underwater equity for strategy and benchmark |
| `rolling_sharpe.png` | 24-month rolling Sharpe ratio — shows regime consistency |
| `sector_allocation.png` | Sector frequency histogram across all rebalancing periods |
| `summary_table.png` | Full performance comparison table |

---

## Limitations & Risks

- **Survivorship bias**: The universe is fixed at current CAC40 constituents. Stocks
  that were delisted or removed from the index introduce a mild upward bias.
- **Liquidity assumption**: All trades execute at month-end close at full size. In
  practice, large orders in mid-cap names may move the market.
- **Parameter sensitivity**: Momentum lookbacks (12, 1, 6 months) are standard from
  academic literature but not walk-forward optimised for this specific universe.
- **Regime filter lag**: SMA-based filters react with a lag. During sharp, fast
  crashes (e.g., March 2020), the filter may not activate in time to avoid drawdown.
- **Correlation risk**: In severe risk-off episodes, cross-sectional momentum can
  reverse violently ("momentum crash"). The cash filter provides partial protection.
- **French market specific**: CAC40 has heavy Luxury sector concentration. Results
  may not generalise to other European indices without re-calibration.

---

## How to Run

```bash
# 1. Install dependencies (data fetched automatically from Yahoo Finance)
pip install -r requirements.txt

# 2. Run the full backtest and generate all charts
python main.py
```

> No local data files required — all prices are downloaded automatically.

### Project Structure

```
├── config.py         # Universe, sectors, all strategy parameters
├── data.py           # Yahoo Finance data loading (monthly resampling)
├── strategy.py       # Scoring, portfolio selection, cash management
├── backtest.py       # Backtest runner + performance statistics
├── visualize.py      # 5 professional charts
├── main.py           # Entry point
├── requirements.txt
└── charts/           # Generated after running main.py
```

---

## Academic References

- Jegadeesh, N. & Titman, S. (1993). *Returns to Buying Winners and Selling Losers*.
  Journal of Finance, 48(1), 65–91.
- Carhart, M. (1997). *On Persistence in Mutual Fund Performance*. Journal of Finance, 52(1).
- Asness, C., Moskowitz, T. & Pedersen, L. (2013). *Value and Momentum Everywhere*.
  Journal of Finance, 68(3), 929–985.

---

## Disclaimer

This repository is for educational and research purposes only.
Past backtest performance does not guarantee future results.
Equity markets carry substantial risk of loss.
