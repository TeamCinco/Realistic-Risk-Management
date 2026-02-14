"""
Opportunity Analyzer Configuration
Adjust these values to change scoring behavior
"""

# ============================================================================
# FILE PATHS
# ============================================================================

INPUT_FILE = "/Users/jazzhashzzz/Documents/Market_Analysis_files/output/screener/screening_results_enhanced.xlsx"
OUTPUT_FILE = "/Users/jazzhashzzz/Documents/Market_Analysis_files/output/screener/opportunities_ranked.xlsx"

# ============================================================================
# SCORING CRITERIA
# ============================================================================
# Each metric has:
#   optimal_range: Values in this range get 100 points
#   acceptable_range: Values outside this get 0-50 points
#   weight: How important this metric is (must sum to 1.0)

CRITERIA = {
    'z_score': {
        'optimal_range': (-3.0, -2.0),      # Sweet spot: moderately oversold
        'acceptable_range': (-4.0, -1.5),   # Too oversold or not enough
        'weight': 0.25,
        'description': 'Statistical oversold condition'
    },
    
    'pe_ratio': {
        'optimal_range': (5, 25),           # Value territory
        'acceptable_range': (0, 40),        # Not overvalued
        'weight': 0.20,
        'description': 'Valuation survivability'
    },
    
    'drop_from_high_pct': {
        'optimal_range': (-40, -20),        # Good dislocation
        'acceptable_range': (-60, -10),     # Not broken, not trivial
        'weight': 0.15,
        'description': 'Recent drawdown magnitude'
    },
    
    'p10': {
        'optimal_range': (-40, -15),        # Limited further downside
        'acceptable_range': (-60, -10),     # Monte Carlo tail risk
        'weight': 0.20,
        'description': 'Forward tail risk (10th percentile)'
    },
    
    'volatility': {
        'optimal_range': (30, 60),          # Good premium, manageable
        'acceptable_range': (20, 80),       # Tradeable range
        'weight': 0.20,
        'description': 'Volatility for spread pricing'
    }
}

# ============================================================================
# QUALITY FILTERS (HARD CUTOFFS)
# ============================================================================
# Stocks failing these are excluded completely

FILTERS = {
    'min_volume': 500_000,          # Minimum average daily volume
    'max_drop': -70,                # Don't touch stocks down >70%
    'max_volatility': 150,          # Avoid lottery tickets
    'min_z_score': -4.5,            # Too oversold = structural issue
    'max_z_score': -1.5,            # Not oversold enough
    'require_pe': True,             # Must have P/E data
    'require_profitable': True,     # P/E must be positive
}

# ============================================================================
# RISK SETTINGS
# ============================================================================

RISK_SETTINGS = {
    'max_per_sector': 3,            # Flag if >3 signals in same sector
    'min_score_strong': 70,         # Score threshold for "Strong" tier
    'min_score_review': 50,         # Score threshold for "Review" tier
}

# ============================================================================
# OUTPUT SETTINGS
# ============================================================================

OUTPUT = {
    'show_top_n': 20,               # Display top N in terminal
    'create_strong_sheet': True,    # Separate sheet for strong setups
    'create_sector_sheet': True,    # Sector summary sheet
}
