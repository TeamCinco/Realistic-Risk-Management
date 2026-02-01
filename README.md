# Monte Carlo Risk Engine

Monte Carlo simulation for single stock analysis. Built to identify statistical extremes in price movements.

## What it does

Runs 25,000 simulated price paths over 60 days to answer: "Is this price drop a 5th percentile event or normal variance?"

Used for options entry timing on quality stocks during volatile bull markets.

## Structure

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

Total: 331 lines

## Usage

Configure in `run_analysis.py`:

```python
STOCK_SYMBOL = "CAT"
STARTING_CAPITAL = 1000 *ignore*
DAYS_TO_SIMULATE = 60 
NUM_SIMULATIONS = 25000
HISTORICAL_WINDOW = 252*6 
```

Run:
```bash
python run_analysis.py
```

## Output

4-panel visualization saved to `/output/monte_carlo_risk_engine/`:
- Price path distribution
- Return distribution histogram
- Percentile table (1st through 99th)
- Statistical summary with CVaR

Terminal output:
```
Realized Vol: 32.53%
VaR (95%):  -19.69%
CVaR (95%): -25.72%
```

## Backtest mode

Check where historical prices fell in distribution:

```python
CUSTOM_STOCK_PRICE = 400.0      # Price before drop
TARGET_PRICE_TO_CHECK = 380.0   # Price after drop
```

Terminal shows percentile rank and interpretation.

## Workflow

1. Run analysis Sunday night on watchlist
2. Note percentile prices from output
3. Set price alerts at 10th percentile
4. When alert triggers, run backtest with TARGET_PRICE_TO_CHECK
5. Check if current price is 5th-15th percentile
6. If yes, verify fundamentals and IV before trade

## What this tells you

- Where current price sits in 60-day distribution
- Expected volatility over holding period
- Tail risk metrics (CVaR)
- Median outcome (50th percentile target)

Does not predict direction or provide entry signals. Just statistical context.

## Technical details

- Geometric Brownian Motion simulation
- Historical volatility from 6-year window
- Random seed 42 for reproducibility
- CVaR = average of all returns below VaR threshold
- Assumes log-normal returns (understates tail risk)

## Removed features

Stripped out benchmark/correlation analysis from original version:
- No SPY comparison
- No beta calculation
- No correlation metrics
- No scatter plots
- No position sizing recommendations

Focus is purely on single stock percentile analysis.

## Limitations

- Only works in mean-reverting environments
- Uses historical volatility (breaks in regime changes)
- No earnings announcements modeled
- Assumes continuous price movement (no gaps)
- Single asset only

## Dependencies

```
yfinance
numpy
pandas
matplotlib
```

## Use case

Built for low-frequency tactical options trading (3-5 trades/year) on blue chip stocks during volatile bull markets. Not for day trading, market timing, or portfolio optimization.

The Monte Carlo tells you where you are in the distribution. You still need to check fundamentals and IV before executing trades.