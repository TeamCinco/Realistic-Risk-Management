"""Excel output - enhanced with P/E and Z-score columns"""
import pandas as pd
from pathlib import Path

def write_results_to_excel(results, output_path):
    """
    Write screening results to Excel
    Now includes P/E, sector, and Z-score for mean reversion
    """
    # Create output directory if it doesn't exist
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    df = pd.DataFrame(results)
    
    # Filter successful results
    df = df[df['success'] == True].copy()
    
    if len(df) == 0:
        print("No successful results to save")
        return
    
    # Sort by Z-score (most oversold first for mean reversion opportunities)
    df = df.sort_values('z_score')
    
    # Reorder columns for easy scanning
    column_order = [
        'ticker',
        'signal',                    # NEW: OVERSOLD/OVERBOUGHT/NEUTRAL
        'z_score',                   # NEW: Statistical deviation
        'distance_from_mean_pct',    # NEW: % from rolling mean
        'pe_ratio',                  # NEW: P/E for survivability check
        'forward_pe',                # NEW: Forward P/E
        'sector',                    # NEW: Sector
        'days_to_earnings',          # NEW: Days until earnings
        'earnings_date',             # NEW: Earnings date
        'current_price', 
        'recent_high',
        'drop_from_high_pct',
        'p10',
        'volatility',
        'p5',
        'p50',
        'avg_volume',                # NEW: Volume filter
    ]
    
    # Only include columns that exist
    available_cols = [col for col in column_order if col in df.columns]
    df = df[available_cols]
    
    # Write to Excel
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Main sheet
        df.to_excel(writer, index=False, sheet_name='All Results')
        
        # Sheet 2: Oversold opportunities (Z < -2)
        oversold = df[df['signal'] == 'OVERSOLD'].copy()
        if len(oversold) > 0:
            oversold.to_excel(writer, index=False, sheet_name='Oversold')
        
        # Sheet 3: Overbought (Z > 2)
        overbought = df[df['signal'] == 'OVERBOUGHT'].copy()
        if len(overbought) > 0:
            overbought.to_excel(writer, index=False, sheet_name='Overbought')
    
    print(f"\nResults saved to: {output_path}")
    print(f"Sorted by Z-score (most oversold first)")
    print(f"  - Total results: {len(df)}")
    print(f"  - Oversold signals: {len(df[df['signal'] == 'OVERSOLD'])}")
    print(f"  - Overbought signals: {len(df[df['signal'] == 'OVERBOUGHT'])}")