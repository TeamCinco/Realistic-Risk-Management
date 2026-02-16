"""Statistics calculations"""
import numpy as np
import pandas as pd

def calculate_statistics(stock_data, historical_window, stock_symbol, risk_free_rate=0.04):
    """
    Calculate volatility and use risk-free rate as drift proxy.
    """
    print("\nCalculating statistics...")
    
    stock_prices = stock_data['Close'].iloc[-historical_window:]
    stock_returns = stock_prices.pct_change().dropna()
    
    stock_volatility = stock_returns.std() * np.sqrt(252)
    stock_expected_return = risk_free_rate  # Use risk-free proxy
    
    print(f"  {stock_symbol} volatility: {stock_volatility*100:.2f}%")
    print(f"  Risk-free proxy (drift): {stock_expected_return*100:.2f}%")
    
    return {
        'stock_volatility': stock_volatility,
        'stock_expected_return': stock_expected_return
    }
