# Monte Carlo Risk Engine

A Monte Carlo–based risk analysis tool for **single-asset price distributions**, built to identify **statistical extremes** in price movement and frame **forward downside risk** for options execution.

This tool provides **context**, not predictions.

---

## What It Does

Runs **25,000 Monte Carlo simulations** over a **60-day horizon** to answer:

> *“Is this price move statistically extreme, or normal variance?”*

Designed to support **options entry timing** (primarily credit structures) on **high-quality assets** during **volatile bull market regimes**.

---

## Core Concept

The engine separates two questions:

1. **Backward-looking:**
   Where does a realized price move fall in the historical distribution?

2. **Forward-looking:**
   From *this price*, what does normal downside risk look like over the next 60 days?

This distinction is critical:

* **Backward percentiles** = signal (oversold / stretched)
* **Forward percentiles** = strike placement & risk definition

---

## Project Structure

```
/Tail End Risk/
├── run_analysis.py
└── /Mc Engine/
    ├── monte_carlo_risk_engine.py
    ├── mc_data.py          (35 lines)
    ├── mc_stats.py         (21 lines)
    ├── mc_simulation.py    (25 lines)
    ├── mc_percentiles.py   (35 lines)
    └── mc_viz.py           (144 lines)
```

**Total:** ~331 lines

---

## Usage

Configure parameters in `run_analysis.py`:

```python
STOCK_SYMBOL = "CAT"
STARTING_CAPITAL = 1000  # ignored, legacy
DAYS_TO_SIMULATE = 60
NUM_SIMULATIONS = 25000
HISTORICAL_WINDOW = 252 * 6
```

Run:

```bash
python run_analysis.py
```

---

## Output

### Saved Visualization (`/output/monte_carlo_risk_engine/`)

A 4-panel chart including:

* Simulated price path fan
* Return distribution histogram
* Percentile table (1st–99th)
* Risk summary (VaR & CVaR)

### Terminal Summary

```
Realized Vol: 32.53%
VaR (95%):  -19.69%
CVaR (95%): -25.72%
```

---

## Backtest Mode (Realized Move Analysis)

Used to determine **where an actual price move falls** in the distribution.

```python
CUSTOM_STOCK_PRICE = 400.0      # price before move
TARGET_PRICE_TO_CHECK = 380.0  # price after move
```

Outputs:

* Percentile rank of the move
* Interpretation (normal, rare, extreme)

This answers:
**“How unusual was the drop that already happened?”**

---

## Standard Workflow

1. Run MC analysis on watchlist (weekly)
2. Record percentile price levels (p5, p10, p50, etc.)
3. Set alerts near **10th percentile**
4. When triggered:

   * Run backtest with actual price
   * Confirm price sits in **5th–15th percentile**
5. Remove backtest inputs
6. Use forward percentiles to convert returns → strike prices
7. Verify **fundamentals + volatility regime + IV**
8. Execute options structure if conditions pass

---

## What This Tool Tells You

* Where price sits in a **60-day return distribution**
* Expected volatility over holding period
* Tail risk severity (CVaR)
* Median outcome (mean-reversion reference)

### What It Does *Not* Do

* Predict direction
* Generate buy/sell signals
* Replace fundamentals or macro analysis

It provides **statistical context only**.

---

## Notes: How to Use This for Options

Typical use case:

1. A stock experiences a sharp drop
2. Backtest shows price at **low percentile (e.g. 5–10%)**
3. Forward MC shows **contained downside tails**
4. Convert forward percentiles to price levels:

   ```
   strike = current_price × (1 + percentile_return)
   ```
5. Sell credit put spreads **below p10**, protected near p5
6. Rely on:

   * Mean reversion
   * Time decay
   * Elevated IV

This structure benefits from **fear already priced in**, not from further downside.

---

## Missing Piece: IV vs Realized Volatility

The Monte Carlo engine uses **realized volatility**.
Execution requires comparing that to **implied volatility**.

### IV vs Realized Vol Framework

| Realized Vol | Current IV | Interpretation | Action             |
| ------------ | ---------- | -------------- | ------------------ |
| 17.1%        | 14%        | IV cheap       | Don’t sell premium |
| 17.1%        | 18%        | Fair           | Marginal           |
| 17.1%        | 25%+       | IV expensive   | **Sell puts ✓**    |

This comparison determines **whether the statistical edge is tradable**.

---

## Technical Details

* Geometric Brownian Motion
* Log-normal return assumption
* Historical volatility from 6-year window
* Random seed = 42 (reproducibility)
* CVaR = mean of worst tail outcomes
* Understates extreme tail risk (known limitation)

---

## Removed Features

Intentionally stripped to maintain focus:

* No SPY benchmark
* No beta or correlation
* No market regime detection
* No position sizing logic
* No portfolio context

Single asset. Single distribution. Clean signal.

---

## Limitations

* Assumes mean-reverting behavior
* Breaks during regime shifts
* No earnings or macro events modeled
* No overnight gap modeling
* Single asset only

---

## Intended Use Case

Low-frequency **tactical options trading**
(~3–5 trades per year) on liquid, high-quality assets during **volatile but non-crisis bull markets**.

The Monte Carlo tells you **where you are in the distribution**.
You still must:

* Validate regime
* Check fundamentals
* Confirm IV edge
* Define failure conditions

