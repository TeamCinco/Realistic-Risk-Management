"""
Standalone Excel Analyzer - Identifies Best Mean Reversion Opportunities
Reads screening results and scores based on valuation + statistical dislocation
"""
import pandas as pd
import sys
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

INPUT_FILE = "/Users/jazzhashzzz/Documents/Market_Analysis_files/output/screener/screening_results_enhanced.xlsx"
OUTPUT_FILE = "/Users/jazzhashzzz/Documents/Market_Analysis_files/output/screener/opportunities_ranked.xlsx"

# Scoring criteria
CRITERIA = {
    'z_score': {
        'optimal_range': (-3.0, -2.0),      # Sweet spot for mean reversion
        'acceptable_range': (-4.0, -1.5),   # Still tradeable
        'weight': 0.25
    },
    'pe_ratio': {
        'optimal_range': (5, 25),           # Value but not broken
        'acceptable_range': (0, 40),        # Max tolerance
        'weight': 0.20
    },
    'drop_from_high_pct': {
        'optimal_range': (-40, -20),        # Meaningful drop, not disaster
        'acceptable_range': (-60, -10),     # Bounds
        'weight': 0.15
    },
    'p10': {
        'optimal_range': (-40, -15),        # Limited further downside
        'acceptable_range': (-60, -10),     # Max downside tolerance
        'weight': 0.20
    },
    'volatility': {
        'optimal_range': (30, 60),          # Good premium, tradeable
        'acceptable_range': (20, 80),       # Bounds
        'weight': 0.20
    }
}

# ============================================================================
# SCORING FUNCTIONS
# ============================================================================

def score_metric(value, optimal_range, acceptable_range):
    """
    Score a metric from 0-100
    100 = in optimal range
    50 = in acceptable range but not optimal
    0 = outside acceptable range
    """
    if pd.isna(value):
        return 0
    
    opt_min, opt_max = optimal_range
    acc_min, acc_max = acceptable_range
    
    # Perfect score if in optimal range
    if opt_min <= value <= opt_max:
        return 100
    
    # Partial score if in acceptable range
    if acc_min <= value <= acc_max:
        # Linear decay from optimal to acceptable boundary
        if value < opt_min:
            distance = opt_min - value
            max_distance = opt_min - acc_min
        else:
            distance = value - opt_max
            max_distance = acc_max - opt_max
        
        return 100 - (distance / max_distance * 50)
    
    # Zero if outside acceptable range
    return 0


def calculate_composite_score(row):
    """Calculate weighted composite score for a stock"""
    total_score = 0
    total_weight = 0
    
    for metric, params in CRITERIA.items():
        if metric in row.index:
            value = row[metric]
            score = score_metric(
                value,
                params['optimal_range'],
                params['acceptable_range']
            )
            weighted_score = score * params['weight']
            total_score += weighted_score
            total_weight += params['weight']
    
    # Normalize to 0-100
    if total_weight > 0:
        return total_score / total_weight
    return 0


def apply_quality_filters(df):
    """Apply hard filters to remove junk"""
    filtered = df.copy()
    
    # Filter 1: Must have P/E data and be profitable
    filtered = filtered[filtered['pe_ratio'].notna()]
    filtered = filtered[filtered['pe_ratio'] > 0]
    
    # Filter 2: Must have Z-score data
    filtered = filtered[filtered['z_score'].notna()]
    
    # Filter 3: Must be oversold (Z < -1.5)
    filtered = filtered[filtered['z_score'] < -1.5]
    
    # Filter 4: Not completely broken (drop < -70%)
    filtered = filtered[filtered['drop_from_high_pct'] > -70]
    
    # Filter 5: Has reasonable volume data
    filtered = filtered[filtered['avg_volume'].notna()]
    filtered = filtered[filtered['avg_volume'] > 500_000]
    
    # Filter 6: Volatility not insane (< 150%)
    filtered = filtered[filtered['volatility'] < 150]
    
    # Add earnings risk flag
    def flag_earnings(row):
        if 'days_to_earnings' in row.index and pd.notna(row['days_to_earnings']):
            days = row['days_to_earnings']
            if 0 <= days <= 7:
                return f'⚠️ {days}d to earnings'
            elif -7 <= days < 0:
                return f'Just reported'
        return ''
    
    filtered['earnings_risk'] = filtered.apply(flag_earnings, axis=1)
    
    return filtered


def detect_sector_clustering(df, max_per_sector=3):
    """Flag tickers if too many from same sector"""
    sector_counts = df['sector'].value_counts()
    
    def flag_cluster(row):
        if row['sector'] in sector_counts.index:
            count = sector_counts[row['sector']]
            if count > max_per_sector:
                return f'⚠ {count} signals in sector'
        return ''
    
    df['sector_cluster_risk'] = df.apply(flag_cluster, axis=1)
    return df


# ============================================================================
# ANALYSIS
# ============================================================================

def analyze_opportunities(input_file, output_file):
    """Main analysis function"""
    
    print("\n" + "="*80)
    print("OPPORTUNITY ANALYZER - Mean Reversion + Valuation Scoring")
    print("="*80)
    
    # Load data
    print(f"\nLoading: {input_file}")
    df = pd.read_excel(input_file, sheet_name='All Results')
    print(f"Loaded {len(df)} stocks")
    
    # Apply quality filters
    print("\nApplying quality filters...")
    df_filtered = apply_quality_filters(df)
    print(f"  → {len(df_filtered)} passed filters")
    
    if len(df_filtered) == 0:
        print("\nNo stocks passed quality filters!")
        return
    
    # Calculate composite scores
    print("\nCalculating opportunity scores...")
    df_filtered['opportunity_score'] = df_filtered.apply(calculate_composite_score, axis=1)
    
    # Sort by score
    df_filtered = df_filtered.sort_values('opportunity_score', ascending=False)
    
    # Add sector clustering risk
    df_filtered = detect_sector_clustering(df_filtered)
    
    # Categorize opportunities
    df_filtered['tier'] = pd.cut(
        df_filtered['opportunity_score'],
        bins=[0, 50, 70, 100],
        labels=['PASS', 'REVIEW', 'STRONG']
    )
    
    # ========================================================================
    # OUTPUT RESULTS
    # ========================================================================
    
    print("\n" + "="*80)
    print("TOP OPPORTUNITIES")
    print("="*80)
    
    # Show top 20
    top_20 = df_filtered.head(20)
    
    display_cols = [
        'ticker',
        'opportunity_score',
        'tier',
        'z_score',
        'pe_ratio',
        'drop_from_high_pct',
        'p10',
        'volatility',
        'sector',
        'sector_cluster_risk',
        'earnings_risk',
        'days_to_earnings'
    ]
    
    print("\n" + top_20[display_cols].to_string(index=False))
    
    # Summary stats
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    print(f"\nTotal opportunities: {len(df_filtered)}")
    print(f"  STRONG (>70):  {len(df_filtered[df_filtered['tier'] == 'STRONG'])}")
    print(f"  REVIEW (50-70): {len(df_filtered[df_filtered['tier'] == 'REVIEW'])}")
    print(f"  PASS (<50):     {len(df_filtered[df_filtered['tier'] == 'PASS'])}")
    
    # Sector breakdown
    print("\nBy Sector:")
    sector_summary = df_filtered.groupby('sector').agg({
        'ticker': 'count',
        'opportunity_score': 'mean'
    }).sort_values('opportunity_score', ascending=False)
    sector_summary.columns = ['Count', 'Avg Score']
    print(sector_summary.head(10).to_string())
    
    # ========================================================================
    # SAVE TO EXCEL
    # ========================================================================
    
    print("\n" + "="*80)
    print("SAVING RESULTS")
    print("="*80)
    
    # Prepare output columns
    output_cols = [
        'ticker',
        'opportunity_score',
        'tier',
        'sector',
        'sector_cluster_risk',
        'earnings_risk',
        'days_to_earnings',
        'earnings_date',
        'z_score',
        'distance_from_mean_pct',
        'pe_ratio',
        'forward_pe',
        'current_price',
        'drop_from_high_pct',
        'recent_high',
        'p10',
        'p50',
        'volatility',
        'avg_volume',
        'signal',
    ]
    
    output_df = df_filtered[output_cols]
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Sheet 1: All ranked opportunities
        output_df.to_excel(writer, sheet_name='Ranked Opportunities', index=False)
        
        # Sheet 2: Strong only (>70 score)
        strong = output_df[output_df['tier'] == 'STRONG']
        if len(strong) > 0:
            strong.to_excel(writer, sheet_name='Strong Setups', index=False)
        
        # Sheet 3: By sector
        sector_summary.to_excel(writer, sheet_name='Sector Summary')
    
    print(f"\nSaved to: {output_file}")
    print("\nSheets created:")
    print("  1. Ranked Opportunities (all filtered)")
    print("  2. Strong Setups (score >70)")
    print("  3. Sector Summary")
    
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("\n1. Review 'Strong Setups' sheet")
    print("2. Check sector_cluster_risk column")
    print("3. Pick 3-5 setups across different sectors")
    print("4. Express via bull put spreads or call debit spreads")
    print("5. Size: $300-400 max loss per spread")
    print("\n" + "="*80)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Allow command-line override of input file
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = INPUT_FILE
    
    # Check if file exists
    if not Path(input_file).exists():
        print(f"\nERROR: File not found: {input_file}")
        print("\nUsage:")
        print(f"  python {Path(__file__).name} [path/to/excel_file.xlsx]")
        sys.exit(1)
    
    # Run analysis
    analyze_opportunities(input_file, OUTPUT_FILE)