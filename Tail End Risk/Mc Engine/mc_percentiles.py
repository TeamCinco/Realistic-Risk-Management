"""Percentile calculations"""
import numpy as np
import pandas as pd

def calculate_percentiles(stock_final_returns, stock_final_prices=None):
    """Calculate percentile statistics"""
    print("\nCalculating percentiles...")
    
    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    
    stock_percentiles = pd.DataFrame({
        'percentile': percentiles,
        'return': np.percentile(stock_final_returns, percentiles)
    })
    
    # Add price percentiles if prices are provided
    if stock_final_prices is not None:
        stock_percentiles['price'] = np.percentile(stock_final_prices, percentiles)
    
    return stock_percentiles

def calculate_cvar(returns):
    """Calculate Conditional Value at Risk (CVaR) / Expected Shortfall"""
    var_95 = np.percentile(returns, 5)
    var_99 = np.percentile(returns, 1)
    
    cvar_95 = returns[returns <= var_95].mean()
    cvar_99 = returns[returns <= var_99].mean()
    
    return {
        'var_95': var_95,
        'cvar_95': cvar_95,
        'var_99': var_99,
        'cvar_99': cvar_99
    }