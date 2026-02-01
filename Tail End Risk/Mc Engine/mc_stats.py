"""Statistics calculations"""
import numpy as np
import pandas as pd

def calculate_statistics(stock_data, historical_window, stock_symbol):
    """Calculate volatility and expected return"""
    print("\nCalculating volatility...")
    
    stock_prices = stock_data['Close'].iloc[-historical_window:]
    stock_returns = stock_prices.pct_change().dropna()
    
    stock_volatility = stock_returns.std() * np.sqrt(252)
    stock_expected_return = stock_returns.mean() * 252
    
    print(f"  {stock_symbol} volatility: {stock_volatility*100:.2f}%")
    print(f"  {stock_symbol} expected return: {stock_expected_return*100:.2f}%")
    
    return {
        'stock_volatility': stock_volatility,
        'stock_expected_return': stock_expected_return
    }