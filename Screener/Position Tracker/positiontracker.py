"""
Position Tracker - Check where your trades are at NOW
Reads opportunities_ranked.xlsx and shows current Z-scores for your positions
"""
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import date, timedelta

# ============================================================================
# YOUR POSITIONS - Edit this list
# ============================================================================

MY_POSITIONS = [
    'GOOGL',
    'MSFT',
    'NFLX',
    'PINS',
    'CPNG'
]

OPPORTUNITIES_FILE = "/Users/jazzhashzzz/Documents/Market_Analysis_files/output/screener/opportunities_ranked.xlsx"

# ============================================================================
# QUICK Z-SCORE CALCULATOR
# ============================================================================

def get_current_z_score(ticker, lookback_days=60):
    """Get live Z-score right now"""
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_days + 50)
        
        hist_data = yf.download(ticker, start=start_date, end=end_date, progress=False, timeout=10)
        
        if hist_data is None or len(hist_data) < 30:
            return None
        
        actual_lookback = min(lookback_days, len(hist_data))
        recent_data = hist_data.tail(actual_lookback)
        
        rolling_mean = float(recent_data['Close'].mean())
        rolling_std = float(recent_data['Close'].std())
        current_price = float(recent_data['Close'].iloc[-1])
        
        if rolling_std > 0:
            z_score = (current_price - rolling_mean) / rolling_std
            return {
                'current_price': current_price,
                'z_score': z_score,
                'rolling_mean': rolling_mean
            }
        return None
    except:
        return None

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*80)
    print("POSITION TRACKER - Where Are My Trades At?")
    print("="*80)
    
    # Load original opportunities
    print(f"\nLoading: {OPPORTUNITIES_FILE}")
    df_original = pd.read_excel(OPPORTUNITIES_FILE, sheet_name='Strong Setups')
    
    print(f"\nChecking {len(MY_POSITIONS)} positions...\n")
    
    results = []
    
    for ticker in MY_POSITIONS:
        print(f"Fetching {ticker}...", end=" ", flush=True)
        
        # Get current Z-score
        current = get_current_z_score(ticker)
        
        if current is None:
            print("✗ Failed")
            continue
        
        # Get original data from screener
        original = df_original[df_original['ticker'] == ticker]
        
        if len(original) > 0:
            original_z = original['z_score'].values[0]
            original_score = original['opportunity_score'].values[0]
            sector = original['sector'].values[0]
        else:
            original_z = None
            original_score = None
            sector = 'Unknown'
        
        # Calculate change
        if original_z is not None:
            z_change = current['z_score'] - original_z
            
            # Determine status
            if z_change > 0.5:
                status = "📈 IMPROVING"
                status_color = "Mean reversion working"
            elif z_change < -0.5:
                status = "📉 WORSENING"
                status_color = "Getting more oversold"
            else:
                status = "➡️ FLAT"
                status_color = "No change"
        else:
            z_change = None
            status = "❓ NEW"
            status_color = "Not in original screener"
        
        results.append({
            'ticker': ticker,
            'sector': sector,
            'current_price': current['current_price'],
            'current_z': current['z_score'],
            'original_z': original_z,
            'z_change': z_change,
            'status': status,
            'status_msg': status_color,
            'original_score': original_score
        })
        
        print(f"✓ Z={current['z_score']:.2f}")
    
    # Display results
    print("\n" + "="*80)
    print("CURRENT STATUS")
    print("="*80)
    
    df_results = pd.DataFrame(results)
    
    for _, row in df_results.iterrows():
        print(f"\n{row['ticker']} ({row['sector']})")
        print(f"  Current Price: ${row['current_price']:.2f}")
        print(f"  Current Z-Score: {row['current_z']:.2f}")
        
        if row['original_z'] is not None:
            print(f"  Original Z-Score: {row['original_z']:.2f}")
            print(f"  Change: {row['z_change']:+.2f}")
            print(f"  Status: {row['status']} - {row['status_msg']}")
            print(f"  Original Score: {row['original_score']:.1f}")
        else:
            print(f"  Status: {row['status']} - {row['status_msg']}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    improving = df_results[df_results['status'].str.contains('IMPROVING')]
    worsening = df_results[df_results['status'].str.contains('WORSENING')]
    flat = df_results[df_results['status'].str.contains('FLAT')]
    
    print(f"\n📈 Improving (mean reversion working): {len(improving)}")
    if len(improving) > 0:
        print(f"   {', '.join(improving['ticker'].values)}")
    
    print(f"\n📉 Worsening (getting more oversold): {len(worsening)}")
    if len(worsening) > 0:
        print(f"   {', '.join(worsening['ticker'].values)}")
    
    print(f"\n➡️ Flat (no major change): {len(flat)}")
    if len(flat) > 0:
        print(f"   {', '.join(flat['ticker'].values)}")
    
    # Recommendations
    print("\n" + "="*80)
    print("QUICK TAKE")
    print("="*80)
    
    print("\nGood signs (Z-score improving toward 0):")
    for _, row in improving.iterrows():
        if row['current_z'] > -2.0:
            print(f"  ✅ {row['ticker']}: Z went from {row['original_z']:.2f} → {row['current_z']:.2f} (close to mean)")
        else:
            print(f"  🟡 {row['ticker']}: Z went from {row['original_z']:.2f} → {row['current_z']:.2f} (improving but still oversold)")
    
    print("\nConcern (Z-score getting worse):")
    for _, row in worsening.iterrows():
        print(f"  ⚠️ {row['ticker']}: Z went from {row['original_z']:.2f} → {row['current_z']:.2f} (structural issue?)")
    
    print("\n" + "="*80)
    print("Next: Run this daily to track mean reversion progress")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()