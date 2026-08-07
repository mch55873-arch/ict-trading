# ICT Institutional Engine v8.0 | Complete SMC & PA Toolkit

Professional-grade **Smart Money Concepts (SMC)** and **Inner Circle Trader (ICT)** execution engine for TradingView (Pine Script v6). Optimized specifically for **Gold (XAUUSD)** and **Forex pairs** with native **Pakistani Standard Time (PKT - UTC+5)** support.

---

## 🏛️ Architecture Overview

The indicator is engineered using a **Deterministic 8-Stage Finite State Machine (FSM)** and an **Asynchronous Event Bus Engine** to eliminate false signals and repaint bugs:

```
[Triple Timeframe Hierarchy (Daily -> 4H -> LTF)]
                        │
                        ▼
[Liquidity Engine (BSL / SSL / EQH / EQL + Vol Filter)]
                        │
                        ▼
[Displacement & FVG Engine (ATR + Volume Expansion + FVG)]
                        │
                        ▼
[Displacement-Origin OB Engine (Exact Origin + 5-Stage Lifecycle)]
                        │
                        ▼
[Event Bus & Timestamp Queue (Ordered Event Timestamps)]
                        │
                        ▼
[Deterministic FSM Engine (Freeze Setup Sweep Price)]
                        │
                        ▼
[Trade Management Engine (Entry + SL + Break-Even + Partial TP)]
                        │
                        ▼
[Realtime Dashboard & Confirmed Bar Alert Engine]
```

---

## 🇵🇰 Pakistani Standard Time (PKT / UTC+5) Killzone Schedule

| ICT Killzone | UTC Window | Pakistani Time (PKT) | Role |
|---|---|---|---|
| **Asian Session** | 00:00 - 09:00 UTC | **05:00 AM - 02:00 PM PKT** | Asia High/Low Range Build-up |
| **London Killzone** | 07:00 - 10:00 UTC | **12:00 PM - 03:00 PM PKT** | London Open Liquidity Sweep & Manipulation |
| **NY Open Killzone** | 12:00 - 15:00 UTC | **05:00 PM - 08:00 PM PKT** | New York Expansion & Trend Continuation |
| **NY Silver Bullet** | 14:00 - 15:00 UTC | **07:00 PM - 08:00 PM PKT** | 10:00 - 11:00 AM EST High-Probability Window |

---

## 🚀 Key Features

1. **Deterministic Single-Transition FSM Engine**: Gated execution prevents multiple state skips within a single bar.
2. **Setup Sweep Freeze**: Pre-trade sweep price is locked at State 1 (`SWEEP`), preventing Stop Loss mutation from subsequent market sweeps.
3. **Displacement Origin OB Scanner**: Locates the exact opposing candle at the start of impulse expansion (`lastDisplacementBar - 1`).
4. **5-Stage OB Lifecycle**: Fresh ➔ Partial Mitigation ➔ Full 50% Mean Threshold ➔ Reclaimed Breaker Block ➔ Invalidated.
5. **Volume-Filtered FVG Engine**: Validates Fair Value Gaps using 60%+ body ratio, ATR range expansion, and volume spike filters.
6. **Institutional Trade Manager**: Includes **Entry**, **Frozen SL**, **Partial TP (1:2 RR)**, **Break-Even (BE) Shift**, and **Final Target (Opposite Liquidity)**.
7. **Replay & Bar Confirmation Determinism**: All signal executions and alerts are bound to `barstate.isconfirmed`, guaranteeing 100% identical performance across Historical, Bar Replay, and Real-time execution.

---

## 📋 How to Use in TradingView

1. Open TradingView and select **XAUUSD** or your target pair.
2. Open the **Pine Editor** tab at the bottom.
3. Paste the contents of `PriceActionPro_MEGA_v8.pine`.
4. Click **Save** and **Add to Chart**.
5. Enable **High-Probability Signals** in the indicator settings to display trades with a Confluence Score $\ge 75\%$.
