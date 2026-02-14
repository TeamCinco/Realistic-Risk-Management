"""
Simple Enhanced Screener - Adds P/E and Z-score to existing Monte Carlo analysis
Minimal modifications to existing code
"""
import sys
from pathlib import Path
import yfinance as yf
import numpy as np
from datetime import date, timedelta
import pandas as pd
# Add MC Engine to path
mc_engine_path = Path("/Users/jazzhashzzz/Documents/Market_Analysis_files/Tail End Risk/Mc Engine")
sys.path.insert(0, str(mc_engine_path))

from monte_carlo_risk_engine import MonteCarloRiskEngine
import warnings
warnings.filterwarnings('ignore')


def get_simple_fundamentals(ticker):
    """Get basic valuation metrics - P/E, Forward P/E, sector, earnings date"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get earnings date
        earnings_date = None
        days_to_earnings = None
        try:
            calendar = stock.calendar
            if calendar is not None and 'Earnings Date' in calendar.index:
                earnings_date = calendar.loc['Earnings Date'][0]
                
                # Calculate days until earnings
                from datetime import datetime
                if pd.notna(earnings_date):
                    today = datetime.now()
                    if isinstance(earnings_date, str):
                        earnings_dt = pd.to_datetime(earnings_date)
                    else:
                        earnings_dt = earnings_date
                    
                    days_to_earnings = (earnings_dt - today).days
        except:
            pass
        
        return {
            'pe_ratio': info.get('trailingPE', None),
            'forward_pe': info.get('forwardPE', None),
            'sector': info.get('sector', 'Unknown'),
            'avg_volume': info.get('averageVolume', None),
            'earnings_date': earnings_date,
            'days_to_earnings': days_to_earnings,
        }
    except:
        return {
            'pe_ratio': None,
            'forward_pe': None,
            'sector': 'Unknown',
            'avg_volume': None,
            'earnings_date': None,
            'days_to_earnings': None,
        }


def get_z_score(ticker, lookback_days=60):
    """
    Calculate Z-score for mean reversion signal
    Z = (Current Price - Rolling Mean) / Rolling Std
    """
    try:
        # Try to get more data buffer for safety
        end_date = date.today()
        start_date = end_date - timedelta(days=lookback_days + 50)
        
        hist_data = yf.download(
            ticker, 
            start=start_date, 
            end=end_date, 
            progress=False,
            timeout=10
        )
        
        # Need minimum 30 days of data
        if hist_data is None or len(hist_data) < 30:
            return None
        
        # Use whatever data we have (minimum 30, target 60)
        actual_lookback = min(lookback_days, len(hist_data))
        recent_data = hist_data.tail(actual_lookback)
        
        # Price-based Z-score
        rolling_mean = float(recent_data['Close'].mean())
        rolling_std = float(recent_data['Close'].std())
        current_price = float(recent_data['Close'].iloc[-1])
        
        if rolling_std > 0 and rolling_mean > 0:
            z_score = (current_price - rolling_mean) / rolling_std
            distance_pct = ((current_price - rolling_mean) / rolling_mean) * 100
        else:
            return None
        
        # Simple signal
        if z_score <= -2:
            signal = 'OVERSOLD'
        elif z_score >= 2:
            signal = 'OVERBOUGHT'
        else:
            signal = 'NEUTRAL'
        
        return {
            'z_score': z_score,
            'distance_from_mean_pct': distance_pct,
            'signal': signal
        }
    except Exception as e:
        # Silently fail - return None
        return None


def analyze_stock(ticker, days_to_simulate=90, num_simulations=10000, historical_window=252*6):
    """
    Enhanced analysis - adds P/E and Z-score to existing Monte Carlo
    Drop-in replacement for original analyze_stock function
    """
    try:
        # Get fundamentals
        fundamentals = get_simple_fundamentals(ticker)
        
        # Get Z-score
        z_data = get_z_score(ticker)
        
        # Set defaults if Z-score calculation failed
        if z_data:
            z_score = z_data['z_score']
            distance_from_mean_pct = z_data['distance_from_mean_pct']
            signal = z_data['signal']
        else:
            z_score = 0.0
            distance_from_mean_pct = 0.0
            signal = 'UNKNOWN'
        
        # Run existing Monte Carlo analysis
        engine = MonteCarloRiskEngine(
            stock_symbol=ticker,
            starting_capital=1000,
            days_to_simulate=days_to_simulate,
            num_simulations=num_simulations,
            historical_window=historical_window,
            max_tolerable_loss_pct=80
        )
        
        # Get 52-week high (existing logic)
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=365)
            hist_data = yf.download(ticker, start=start_date, end=end_date, progress=False)
            
            if len(hist_data) > 0:
                recent_high = float(hist_data['High'].max())
                drop_from_high_pct = ((engine.stock_price - recent_high) / recent_high) * 100
            else:
                recent_high = engine.stock_price
                drop_from_high_pct = 0.0
        except:
            recent_high = engine.stock_price
            drop_from_high_pct = 0.0
        
        # Extract percentiles (existing logic)
        p5 = engine.stock_percentiles[engine.stock_percentiles['percentile'] == 5]['return'].values[0]
        p10 = engine.stock_percentiles[engine.stock_percentiles['percentile'] == 10]['return'].values[0]
        p50 = engine.stock_percentiles[engine.stock_percentiles['percentile'] == 50]['return'].values[0]
        
        # Build result with new metrics added
        return {
            'ticker': ticker,
            'current_price': engine.stock_price,
            'recent_high': recent_high,
            'drop_from_high_pct': drop_from_high_pct,
            'volatility': engine.stock_volatility * 100,
            'p5': p5,
            'p10': p10,
            'p50': p50,
            
            # NEW: Valuation metrics
            'pe_ratio': fundamentals['pe_ratio'],
            'forward_pe': fundamentals['forward_pe'],
            'sector': fundamentals['sector'],
            'avg_volume': fundamentals['avg_volume'],
            'earnings_date': fundamentals['earnings_date'],
            'days_to_earnings': fundamentals['days_to_earnings'],
            
            # NEW: Z-score mean reversion signal
            'z_score': z_score,
            'distance_from_mean_pct': distance_from_mean_pct,
            'signal': signal,
            
            'success': True
        }
        
    except Exception as e:
        return {
            'ticker': ticker,
            'success': False,
            'error': str(e)
        }