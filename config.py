"""
CAC40 Sector Rotation Strategy — Configuration
All tunable parameters live here.
"""

# ── Data ──────────────────────────────────────────────────────────────────────
START_DATE: str = "2016-01-01"
END_DATE:   str = "2024-12-31"
BENCHMARK:  str = "^FCHI"          # CAC 40 index

# ── Universe — CAC40 large-cap stocks via Yahoo Finance ───────────────────────
UNIVERSE: list[str] = [
    # Luxury / Consumer Discretionary
    "MC.PA", "RMS.PA", "KER.PA", "CDI.PA",
    # Consumer Staples / Beauty / Beverages
    "OR.PA", "BN.PA", "RI.PA",
    # Telecom / Media / Communication
    "ORA.PA", "VIV.PA", "PUB.PA",
    # Industrials / Aerospace / Construction
    "AIR.PA", "SU.PA", "DG.PA", "HO.PA", "ALO.PA",
    # Technology / IT / Semiconductors
    "CAP.PA", "STMPA.PA",
    # Materials
    "AI.PA", "SGO.PA",
    # Healthcare / Pharma
    "SAN.PA",
    # Energy / Utilities
    "TTE.PA", "ENGI.PA", "VIE.PA",
    # Financials / Insurance
    "BNP.PA", "ACA.PA", "GLE.PA", "CS.PA",
]

SECTOR_MAP: dict[str, str] = {
    "MC.PA":    "Luxury",
    "RMS.PA":   "Luxury",
    "KER.PA":   "Luxury",
    "CDI.PA":   "Luxury",
    "OR.PA":    "ConsStaples",
    "BN.PA":    "ConsStaples",
    "RI.PA":    "ConsStaples",
    "ORA.PA":   "Telecom",
    "VIV.PA":   "Telecom",
    "PUB.PA":   "Telecom",
    "AIR.PA":   "Industrials",
    "SU.PA":    "Industrials",
    "DG.PA":    "Industrials",
    "HO.PA":    "Industrials",
    "ALO.PA":   "Industrials",
    "CAP.PA":   "Technology",
    "STMPA.PA": "Technology",
    "AI.PA":    "Materials",
    "SGO.PA":   "Materials",
    "SAN.PA":   "Healthcare",
    "TTE.PA":   "Energy",
    "ENGI.PA":  "Utilities",
    "VIE.PA":   "Utilities",
    "BNP.PA":   "Financials",
    "ACA.PA":   "Financials",
    "GLE.PA":   "Financials",
    "CS.PA":    "Financials",
}

# ── Momentum Parameters ───────────────────────────────────────────────────────
MOM_LONG:  int = 12     # Long lookback for 12-1 momentum (months)
MOM_SHORT: int = 1      # Skip most recent month (reversal avoidance)
VOL_WIN:   int = 6      # Months for volatility adjustment

# ── Portfolio Construction ────────────────────────────────────────────────────
TOP_K:             int   = 6      # Number of holdings per period
MAX_PER_SECTOR:    int   = 1      # Max 1 stock per sector
REBAL_FREQ:        str   = "ME"   # Monthly rebalancing (ME = Month End)
MIN_HISTORY_MONTHS: int  = 15     # Skip stocks with < 15 months of data

# ── Market Regime / Cash Management ──────────────────────────────────────────
TREND_SMA_LONG:    int   = 10     # SMA-10 months on CAC40 for regime filter
TREND_SMA_SHORT:   int   = 6      # SMA-6 months on CAC40 for deep bear detection
DEEP_BEAR_THRESH:  float = -0.05  # If CAC40 < SMA6 by > 5% → full cash
HALF_CASH_EXPO:    float = 0.50   # Equity exposure when SMA10 breached
FULL_CASH_EXPO:    float = 0.00   # Equity exposure in deep bear

CASH_YIELD_ANNUAL: float = 0.03   # 3% annual yield on cash (ESTER proxy)

# ── Transaction Costs ─────────────────────────────────────────────────────────
ROUND_TRIP_COST: float = 0.003    # 0.30% round-trip (0.15% each side)

# ── Performance ───────────────────────────────────────────────────────────────
INITIAL_EQUITY: float = 100_000.0
ANNUAL_FACTOR:  int   = 12        # Monthly data
ROLLING_SHARPE_WINDOW: int = 24   # Months for rolling Sharpe
