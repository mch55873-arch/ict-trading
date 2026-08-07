# Quantitative Research & Risk Protocol (v9.4 Institutional Standard)

**Repository:** [`github.com/mch55873-arch/ict-trading`](https://github.com/mch55873-arch/ict-trading)  
**Specification Level:** Hedge Fund Quantitative Research Standard (v9.4)  
**Primary Focus:** Expectancy ($E$), 23-Column Trade Journal, Walk-Forward Rolling Windows & Monte Carlo  

---

## 1. Quantitative Core Directives

> **1. Expectancy Over Win Rate:** Win rate percentage is not an isolated target. System quality is governed strictly by **Expectancy ($E > +0.5R$)** and **Profit Factor ($PF > 1.8$)**.  
> **2. Sample Size Integrity:** Minimum sample size requirement is **$N \ge 500$ verified trades** across Bull, Bear, Ranging, High Volatility, and Low Volatility market regimes.  
> **3. Automated Journaling:** Eliminates manual logging errors, biases, and missing trades via automatic code-generated logs.  

---

## 2. 23-Column Automated CSV Trade Journal Specification

Every trade generates a complete 23-parameter analytical record for automated quantitative analysis:

```csv
TradeID, Symbol, Timeframe, Session, Weekday, Direction, HTFBias, SweepType, FvgSize, ObQuality, DisplacementScore, ConfluenceScore, ATR, Spread, EntryPrice, SLPrice, TPPrice, ExitPrice, RR, RMultiple, DurationBars, MFE, MAE, ReasonClosed
1, XAUUSD, M5, London KZ, Tue, LONG, Bullish, SSL Sweep, 2.45, 90%, 85%, 85%, 3.20, 0.25, 2380.50, 2374.20, 2405.00, 2399.40, 1:3.8, +3.0R, 18, +3.8R, -0.4R, CLOSED_TP2
2, EURUSD, M15, NY Open, Wed, SHORT, Bearish, BSL Sweep, 0.0012, 80%, 75%, 75%, 0.0018, 0.0001, 1.0850, 1.0880, 1.0760, 1.0850, 1:3.0, 0.0R, 12, +1.8R, -0.2R, CLOSED_BE
```

---

## 3. Walk-Forward Rolling Window Protocol

Walk-forward validation tests whether parameter sets retain profitability on unseen future market regimes:

```
┌───────────────────────────────────────────────────────────┐
│ Rolling Window 1: Jan-Apr (In-Sample) ──► May (Out-of-Sample) │
├───────────────────────────────────────────────────────────┤
│ Rolling Window 2: Feb-May (In-Sample) ──► Jun (Out-of-Sample) │
├───────────────────────────────────────────────────────────┤
│ Rolling Window 3: Mar-Jun (In-Sample) ──► Jul (Out-of-Sample) │
└───────────────────────────────────────────────────────────┘
```

- **Retention Criterion:** Out-of-Sample Profit Factor must maintain at least **$80\%$ of In-Sample Profit Factor**.

---

## 4. Monte Carlo Simulation Engine

Simulates **1,000 random trade sequence reshuffles** from $500+$ historical trade logs:

| Metric | Target Boundary | Description |
|---|---|---|
| **Probability of Ruin ($P_{\text{ruin}}$)** | $< 0.5\%$ | Risk of losing $50\%$ account equity over 100 trade sequences. |
| **95% Confidence Max Drawdown** | $\le 14.5\%$ | 95th percentile worst-case drawdown from 1,000 iterations. |
| **Ulcer Index (UI)** | $< 3.5$ | Depth and duration penalty metric for equity drawdowns. |

---

## 5. Market Regime Filter Matrix

| Market Regime | Detection Condition | Required Action | Target Profit Factor |
|---|---|---|---|
| **1. High Volatility Trending** | `ATR > SMA(20) * 1.3 AND ADX > 25` | Full Execution | $PF \ge 2.5$ |
| **2. Low Volatility Trending** | `ATR <= SMA(20) * 1.3 AND ADX > 25` | Full Execution | $PF \ge 2.0$ |
| **3. High Volatility Ranging** | `ATR > SMA(20) * 1.3 AND ADX <= 25` | Reduce Risk ($0.5\%$) | $PF \ge 1.5$ |
| **4. Low Volatility Ranging** | `ATR <= SMA(20) * 1.3 AND ADX <= 25` | Filter / Off-Hours | Filter Out |
