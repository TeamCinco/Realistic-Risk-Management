# Opportunity Analyzer

**Standalone script that scores your screening results to find the best mean reversion setups.**

## What It Does

Reads your Excel output from the screener and:

1. **Filters out junk** (broken stocks, no data, extreme volatility)
2. **Scores each stock** based on 5 factors (Z-score, P/E, drop, tail risk, vol)
3. **Ranks opportunities** from best to worst
4. **Flags sector clustering risk** (too many signals in one sector)
5. **Outputs clean Excel** with ranked opportunities

## Scoring System

Each stock gets 0-100 points based on:

| Factor | Weight | Optimal Range | What It Means |
|--------|--------|---------------|---------------|
| **Z-Score** | 25% | -3.0 to -2.0 | Moderately oversold, not destroyed |
| **P/E Ratio** | 20% | 5 to 25 | Value territory, survivable |
| **Drop from High** | 15% | -40% to -20% | Meaningful dislocation |
| **P10 (tail risk)** | 20% | -40% to -15% | Limited further downside |
| **Volatility** | 20% | 30% to 60% | Good premium, tradeable |

### Scoring Tiers

- **STRONG (>70)**: Best setups, review first
- **REVIEW (50-70)**: Decent, needs more diligence
- **PASS (<50)**: Skip

## Usage

### Basic Run
```bash
python analyze_opportunities.py
```

### Custom Input File
```bash
python analyze_opportunities.py /path/to/your/screening_results.xlsx
```

## Output

Creates `opportunities_ranked.xlsx` with 3 sheets:

### 1. Ranked Opportunities
All filtered stocks, sorted by score (best first)

Columns:
- `opportunity_score` - Overall score (0-100)
- `tier` - STRONG / REVIEW / PASS
- `sector_cluster_risk` - Warning if too many signals in sector
- All your original metrics

### 2. Strong Setups
Only stocks with score >70

**These are your focus list.**

### 3. Sector Summary
Breakdown by sector showing:
- Count of opportunities per sector
- Average score per sector

## Quality Filters (Auto-Applied)

Stock must pass ALL of these to be scored:

- ✓ Has P/E data and is profitable (P/E > 0)
- ✓ Has Z-score data
- ✓ Oversold (Z < -1.5)
- ✓ Not completely broken (drop > -70%)
- ✓ Decent volume (>500k avg daily)
- ✓ Not lottery ticket (vol < 150%)

## Example Output

```
TOP OPPORTUNITIES
================================================================================

ticker  opportunity_score  tier    z_score  pe_ratio  drop_from_high_pct  p10     volatility  sector
INFY    87.5              STRONG  -4.0     18.95     -51.35              -18.88  30.81       Technology
BSX     82.3              STRONG  -2.6     39.19     -30.58              -16.56  28.30       Healthcare
MSFT    78.9              STRONG  -2.3     25.13     -27.39              -16.51  29.91       Technology
UBER    76.4              STRONG  -2.4     14.84     -31.17              -30.65  51.91       Technology  ⚠ 8 signals
JD      74.2              STRONG  -2.3     8.91      -39.20              -34.85  53.49       Consumer
```

## How to Use Results

1. **Open "Strong Setups" sheet**
2. **Check `sector_cluster_risk` column**
   - Avoid loading up in one sector
   - Pick 3-5 setups across different sectors
3. **Express via spreads**
   - Bull put spreads (if oversold)
   - Call debit spreads (if oversold)
   - $300-400 max loss per spread
4. **Size based on correlation**
   - Don't take 5 tech stocks at once
   - Diversify across sectors

## Adjusting Criteria

Edit `analyzer_config.py` to tune:

### Make Z-score More Important
```python
'z_score': {
    'weight': 0.35,  # Increase from 0.25
}
```

### Require Lower P/E
```python
'pe_ratio': {
    'optimal_range': (5, 20),  # Was (5, 25)
}
```

### Increase Volume Filter
```python
FILTERS = {
    'min_volume': 1_000_000,  # Was 500k
}
```

## What Makes a Good Setup

From the scored results, you want:

**Ideal candidate:**
- Score >75
- Z-score: -2.5 to -3.0 (oversold, not broken)
- P/E: 8-20 (cheap, profitable)
- Drop: -30% to -40% (opportunity)
- P10: -20% to -35% (limited tail)
- Vol: 35-55% (good premium)
- No sector cluster warning

**Red flags:**
- Score <60
- Sector cluster warning (>3 signals in sector)
- P/E >40 (overvalued)
- Drop >-60% (structurally broken)
- Vol >80% (too wild)

## Output Example

Your terminal will show:
```
OPPORTUNITY ANALYZER - Mean Reversion + Valuation Scoring
================================================================================

Loading: screening_results_enhanced.xlsx
Loaded 1243 stocks

Applying quality filters...
  → 87 passed filters

Calculating opportunity scores...

TOP OPPORTUNITIES
[... shows top 20 ...]

SUMMARY
Total opportunities: 87
  STRONG (>70):  15
  REVIEW (50-70): 42
  PASS (<50):     30

By Sector:
                  Count  Avg Score
Technology         23     64.2
Consumer Cyclical  18     61.8
Healthcare         12     68.5
Financial Services 11     59.3

SAVING RESULTS
Saved to: opportunities_ranked.xlsx

NEXT STEPS
1. Review 'Strong Setups' sheet
2. Check sector_cluster_risk column
3. Pick 3-5 setups across different sectors
4. Express via bull put spreads or call debit spreads
5. Size: $300-400 max loss per spread
```

## Philosophy

This analyzer implements the hybrid framework:

1. **Statistical trigger** (Z-score) - your friend's approach
2. **Valuation filter** (P/E) - survivability check
3. **Risk quantification** (Monte Carlo p10) - your edge
4. **Structure expression** (via spreads) - risk management

You're not forecasting. You're finding:
- Mispriced dislocations
- With survivable fundamentals
- That you can express with defined risk

That's it.
