"""Monte Carlo simulation"""
import numpy as np

def run_monte_carlo(stock_price, stats, days_to_simulate, num_simulations):
    """Run Monte Carlo simulations"""
    print(f"\nRunning {num_simulations:,} Monte Carlo simulations...")
    
    np.random.seed(42)
    
    z = np.random.standard_normal((days_to_simulate, num_simulations))
    
    stock_daily_returns = (
        stats['stock_expected_return'] / 252 +
        stats['stock_volatility'] / np.sqrt(252) * z
    )
    
    stock_paths = stock_price * np.cumprod(1 + stock_daily_returns, axis=0)
    stock_final_prices = stock_paths[-1]
    stock_final_returns = (stock_final_prices / stock_price - 1) * 100
    
    return {
        'stock_paths': stock_paths,
        'stock_final_prices': stock_final_prices,
        'stock_final_returns': stock_final_returns
    }