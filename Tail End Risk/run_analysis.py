"""
Interactive Monte Carlo Risk Analysis
Easy parameter configuration - just modify the variables below
"""

import sys
from pathlib import Path

# Add Mc Engine folder to Python path
mc_engine_path = Path(__file__).parent / "Mc Engine"
sys.path.insert(0, str(mc_engine_path))

from monte_carlo_risk_engine import MonteCarloRiskEngine
# ============================================================================
# USER INPUTS - MODIFY THESE PARAMETERS
# ============================================================================

# Stock
STOCK_SYMBOL = "TSLA"           # Change to any stock (e.g., "AAPL", "NVDA", "MSFT")

# Capital and Risk Parameters
STARTING_CAPITAL = 1000         # Your starting capital in dollars
MAX_TOLERABLE_LOSS_PCT = 14     # Max % loss you can handle (e.g., 15, 20, 25)

# Simulation Parameters
DAYS_TO_SIMULATE = 90           # Trading days to simulate (252 = 1 year, 126 = 6 months)
NUM_SIMULATIONS = 25000         # Number of Monte Carlo paths (more = slower but more accurate)
HISTORICAL_WINDOW = 252*6       # Days to look back for volatility calculation

# ============================================================================
# CUSTOM STARTING PRICES (NEW FEATURE)
# ============================================================================
# Leave as None to use current market price
# Set to a number to backtest from a specific price point
# 
# Example use cases:
#   - Stock dropped from $400 to $380, want to see where $380 falls in distribution
#     Set CUSTOM_STOCK_PRICE = 400.0, then check output
#   - Want to test "what if" scenarios from different price levels
#
CUSTOM_STOCK_PRICE = 498.83   # Example: 400.0 (CAT price before drop)

# ============================================================================
# TARGET PRICE ANALYSIS (OPTIONAL)
# ============================================================================
# Want to know where a specific price falls in the distribution?
# Set this to check percentile rank of a target price
# 
# Example: Stock dropped to $380, want to know if that's 5th, 10th, or 25th percentile
#
TARGET_PRICE_TO_CHECK = 430.41      # Example: 380.0

# ============================================================================
# RUN THE ANALYSIS
# ============================================================================

print("\n" + "="*80)
print("MONTE CARLO RISK ANALYSIS ENGINE")
print("="*80)
print(f"\nConfiguration:")
print(f"  Stock:              {STOCK_SYMBOL}")
print(f"  Starting Capital:   ${STARTING_CAPITAL:,.2f}")
print(f"  Max Loss Tolerance: {MAX_TOLERABLE_LOSS_PCT}%")
print(f"  Simulation Days:    {DAYS_TO_SIMULATE}")
print(f"  Monte Carlo Paths:  {NUM_SIMULATIONS:,}")

if CUSTOM_STOCK_PRICE is not None:
    print(f"  Custom Stock Price: ${CUSTOM_STOCK_PRICE:.2f} (BACKTEST MODE)")
if TARGET_PRICE_TO_CHECK is not None:
    print(f"  Target Price Check: ${TARGET_PRICE_TO_CHECK:.2f}")

print("="*80)

# Initialize the engine
engine = MonteCarloRiskEngine(
    stock_symbol=STOCK_SYMBOL,
    starting_capital=STARTING_CAPITAL,
    days_to_simulate=DAYS_TO_SIMULATE,
    num_simulations=NUM_SIMULATIONS,
    historical_window=HISTORICAL_WINDOW,
    max_tolerable_loss_pct=MAX_TOLERABLE_LOSS_PCT,
    custom_stock_price=CUSTOM_STOCK_PRICE,
)

# Run the full analysis
try:
    viz_path = engine.run_full_analysis(
    target_price_to_check=TARGET_PRICE_TO_CHECK
)
    
    # TARGET PRICE ANALYSIS
    if TARGET_PRICE_TO_CHECK is not None:
        print(f"\n{'='*80}")
        print("TARGET PRICE ANALYSIS")
        print(f"{'='*80}")
        
        stock_final_prices = engine.stock_final_prices
        percentile_rank = (stock_final_prices <= TARGET_PRICE_TO_CHECK).sum() / len(stock_final_prices) * 100
        
        print(f"\nTarget Price: ${TARGET_PRICE_TO_CHECK:.2f}")
        print(f"Percentile Rank: {percentile_rank:.1f}th percentile")
        print(f"\nInterpretation:")
        
        if percentile_rank <= 1:
            print("  ⚠️  EXTREME TAIL EVENT (≤1st percentile)")
            print("  This is a black swan scenario - only 1% of simulations were this bad")
            print("  If fundamentals are intact, this is MAX CONVICTION BUY territory")
        elif percentile_rank <= 5:
            print("  🔴 EXTREME OVERSOLD (1-5th percentile)")
            print("  This is a 2-sigma event - very rare")
            print("  If fundamentals are intact, HIGH CONVICTION BUY")
        elif percentile_rank <= 10:
            print("  🟠 VERY OVERSOLD (5-10th percentile)")
            print("  This is a 1.5-sigma event - uncommon but not impossible")
            print("  If fundamentals are intact, STRONG BUY")
        elif percentile_rank <= 25:
            print("  🟡 OVERSOLD (10-25th percentile)")
            print("  This is below average but within normal variance")
            print("  If fundamentals are intact, MODERATE BUY")
        elif percentile_rank <= 50:
            print("  🟢 BELOW MEDIAN (25-50th percentile)")
            print("  This is slightly below expected outcome")
            print("  Wait for more extreme entry or confirm fundamentals weakening")
        else:
            print("  ⚪ ABOVE MEDIAN (>50th percentile)")
            print("  This is within or above normal expected range")
            print("  Not a pullback - no mean reversion setup")
        
        # Distance from percentile boundaries
        print(f"\nPercentile boundaries for reference:")
        p1 = engine.stock_percentiles[engine.stock_percentiles['percentile'] == 1]['price'].values[0]
        p5 = engine.stock_percentiles[engine.stock_percentiles['percentile'] == 5]['price'].values[0]
        p10 = engine.stock_percentiles[engine.stock_percentiles['percentile'] == 10]['price'].values[0]
        p25 = engine.stock_percentiles[engine.stock_percentiles['percentile'] == 25]['price'].values[0]
        p50 = engine.stock_percentiles[engine.stock_percentiles['percentile'] == 50]['price'].values[0]
        
        print(f"  1st percentile:  ${p1:.2f}")
        print(f"  5th percentile:  ${p5:.2f}")
        print(f"  10th percentile: ${p10:.2f}")
        print(f"  25th percentile: ${p25:.2f}")
        print(f"  50th percentile: ${p50:.2f} (median)")
        
        # Mean reversion potential
        potential_gain_to_median = ((p50 / TARGET_PRICE_TO_CHECK) - 1) * 100
        print(f"\nMean reversion potential to median: +{potential_gain_to_median:.1f}%")
    
    print(f"\n{'='*80}")
    print("SUCCESS! Analysis complete.")
    print(f"{'='*80}")
    print(f"\nVisualization saved to: {viz_path}")
    print("\nNext steps:")
    print("  1. View the output image to see full distribution")
    print("  2. Check fundamentals (earnings, guidance, industry data)")
    print("  3. If fundamentals intact + percentile <10th = potential trade setup")
    print("  4. Modify parameters above and re-run for different scenarios")
    
except Exception as e:
    print(f"\n{'='*80}")
    print("ERROR occurred:")
    print(f"{'='*80}")
    print(f"{str(e)}")
    print("\nPlease check:")
    print("  - You have internet connection for data download")
    print("  - yfinance can access the symbols")
    import traceback
    traceback.print_exc()