# Monte Carlo Stock Screener

Batch analysis tool. Runs Monte Carlo simulations on your entire watchlist and outputs to Excel.

## What it does

Reads tickers from `ticker.txt`, runs 10k simulations per stock, exports percentile data to Excel with color coding.

## Structure

```
/screener/
├── main.py                      # Run this
└── /engine/
    ├── ticker_loader.py         # Read ticker.txt
    ├── screener_engine.py       # Run MC analysis
    └── excel_writer.py          # Export to Excel
```

## Usage

```bash
cd /Users/jazzhashzzz/Documents/Market_Analysis_files/screener
python main.py
```

## Input

`ticker.txt` format:
```
aapl    320193
msft    789019
nvda    1046179
```

Tab-separated. Second column ignored (volume data).

## Output

`screening_results.xlsx` with columns:
- ticker
- current_price
- volatility (annualized %)
- expected_return (annualized %)
- var_95, cvar_95, var_99, cvar_99
- p1, p5, p10, p25, p50, p75, p90, p95, p99 (percentile returns)

## Color coding

Percentile columns auto-colored:
- **Red**: ≤ -10% (extreme downside)
- **Yellow**: -10% to -5% or +5% to +10% (moderate move)
- **Green**: ≥ +10% (extreme upside)

## Terminal output

Shows:
- Progress per ticker
- Summary stats (avg volatility, median returns)
- Extreme movers (5th percentile ≤ -10% or 95th ≥ +10%)
- Top 5 downside risks
- Top 5 upside potential

## Configuration

Edit in `main.py`:
```python
DAYS_TO_SIMULATE = 90        # Forward simulation period
NUM_SIMULATIONS = 10000      # Monte Carlo paths
HISTORICAL_WINDOW = 252*6    # Lookback period
```

## Use case

Find statistical extremes across your watchlist. Identifies stocks at tail percentiles without running individual analysis on each.

Example: After market selloff, run screener to see which stocks hit 5th-10th percentile (potential buy setups).

## Dependencies

Same as main Monte Carlo engine:
- yfinance
- numpy
- pandas
- openpyxl (for Excel color formatting)

## Notes

- No charts generated (Excel only)
- Failed tickers print error, continue to next
- Results sorted by ticker in Excel
- Color coding applied to all percentile columns automatically