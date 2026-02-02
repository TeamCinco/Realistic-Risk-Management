"""
Monte Carlo Stock Screener
Analyzes all stocks in ticker.txt and outputs to Excel
"""
import sys
from pathlib import Path

# Add engine directory to path
engine_path = Path(__file__).parent / "engine"
sys.path.insert(0, str(engine_path))

from engine.ticker_loader import load_tickers
from engine.screener_engine import analyze_stock
from engine.excel_writer import write_results_to_excel

# ============================================================================
# CONFIGURATION
# ============================================================================

TICKER_FILE = "/Users/jazzhashzzz/Documents/Market_Analysis_files/ticker.txt"
OUTPUT_FILE = "/Users/jazzhashzzz/Documents/Market_Analysis_files/output/screener/screening_results.xlsx"

DAYS_TO_SIMULATE = 90
NUM_SIMULATIONS = 10000
HISTORICAL_WINDOW = 252*6

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*80)
    print("MONTE CARLO STOCK SCREENER")
    print("="*80)
    
    # Load tickers
    print(f"\nLoading tickers from: {TICKER_FILE}")
    tickers = load_tickers(TICKER_FILE)
    print(f"Found {len(tickers)} tickers")
    
    # Run analysis
    print(f"\nRunning Monte Carlo analysis ({NUM_SIMULATIONS:,} simulations, {DAYS_TO_SIMULATE} days)")
    print("="*80)
    
    results = []
    for i, ticker in enumerate(tickers, 1):
        print(f"[{i}/{len(tickers)}] {ticker}...", end=" ", flush=True)
        
        result = analyze_stock(
            ticker,
            days_to_simulate=DAYS_TO_SIMULATE,
            num_simulations=NUM_SIMULATIONS,
            historical_window=HISTORICAL_WINDOW
        )
        
        if result['success']:
            results.append(result)
            print(f"✓ (5th: {result['p5']:.1f}%, 50th: {result['p50']:.1f}%)")
        else:
            print(f"✗ {result['error'][:50]}")
    
    # Write to Excel
    print("\n" + "="*80)
    print(f"Successful: {len(results)}/{len(tickers)}")
    
    if results:
        write_results_to_excel(results, OUTPUT_FILE)
        
        # Summary stats
        import pandas as pd
        df = pd.DataFrame(results)
        
        print("\nSUMMARY STATISTICS:")
        print(f"  Avg Volatility: {df['volatility'].mean():.1f}%")
        print(f"  Avg 5th Percentile: {df['p5'].mean():.1f}%")
        print(f"  Avg Median Return: {df['p50'].mean():.1f}%")
        print(f"  Avg 95th Percentile: {df['p95'].mean():.1f}%")
        
        # Extreme movers
        extreme_down = df[df['p5'] <= -10]
        extreme_up = df[df['p95'] >= 10]
        
        print(f"\nEXTREME MOVES:")
        print(f"  Stocks with 5th percentile <= -10%: {len(extreme_down)}")
        print(f"  Stocks with 95th percentile >= +10%: {len(extreme_up)}")
        
        if len(extreme_down) > 0:
            print(f"\nMost Downside Risk (5th percentile):")
            for _, row in extreme_down.nsmallest(5, 'p5').iterrows():
                print(f"    {row['ticker']}: {row['p5']:.1f}%")
        
        if len(extreme_up) > 0:
            print(f"\nMost Upside Potential (95th percentile):")
            for _, row in extreme_up.nlargest(5, 'p95').iterrows():
                print(f"    {row['ticker']}: {row['p95']:.1f}%")
    
    print("\n" + "="*80)
    print("DONE")
    print("="*80)

if __name__ == "__main__":
    main()