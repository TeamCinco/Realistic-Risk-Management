"""Monte Carlo Risk Analysis Engine - uses split modules"""
from mc_data import download_data, set_starting_prices
from mc_stats import calculate_statistics
from mc_simulation import run_monte_carlo
from mc_percentiles import calculate_percentiles, calculate_cvar
from mc_viz import create_visualization

class MonteCarloRiskEngine:
    def __init__(self, stock_symbol, starting_capital, days_to_simulate,
                 num_simulations, historical_window, max_tolerable_loss_pct,
                 custom_stock_price=None):
        
        self.stock_symbol = stock_symbol
        self.starting_capital = starting_capital
        self.days_to_simulate = days_to_simulate
        self.num_simulations = num_simulations
        self.historical_window = historical_window
        self.max_tolerable_loss_pct = max_tolerable_loss_pct
        
        # Download data
        self.stock_data = download_data(stock_symbol, historical_window)
        
        # Set prices
        self.stock_price = set_starting_prices(self.stock_data, stock_symbol, custom_stock_price)
        
        # Calculate stats
        stats = calculate_statistics(self.stock_data, historical_window, stock_symbol)
        self.stock_volatility = stats['stock_volatility']
        self.stock_expected_return = stats['stock_expected_return']
        
        # Run simulation
        sim_results = run_monte_carlo(self.stock_price, stats, days_to_simulate, num_simulations)
        self.stock_paths = sim_results['stock_paths']
        self.stock_final_prices = sim_results['stock_final_prices']
        self.stock_final_returns = sim_results['stock_final_returns']
        
        # Calculate percentiles
        self.stock_percentiles = calculate_percentiles(self.stock_final_returns, self.stock_final_prices)
        
        # Calculate CVaR
        self.stock_cvar = calculate_cvar(self.stock_final_returns)
        
        print(f"\nRisk Metrics:")
        print(f"  VaR (95%):  {self.stock_cvar['var_95']:.2f}% (5th percentile)")
        print(f"  CVaR (95%): {self.stock_cvar['cvar_95']:.2f}% (avg loss in worst 5%)")
        print(f"  VaR (99%):  {self.stock_cvar['var_99']:.2f}% (1st percentile)")
        print(f"  CVaR (99%): {self.stock_cvar['cvar_99']:.2f}% (avg loss in worst 1%)")
        
        print("\n✓ Initialization complete!")
    
    def run_full_analysis(self, target_price_to_check=None):
        """Generate visualization"""
        data = {
            "stock_symbol": self.stock_symbol,
            "num_simulations": self.num_simulations,
            "days_to_simulate": self.days_to_simulate,
            "stock_paths": self.stock_paths,
            "stock_price": self.stock_price,
            "stock_final_returns": self.stock_final_returns,
            "stock_percentiles": self.stock_percentiles,
            "stock_data": self.stock_data,
            "historical_window": self.historical_window,
            "stock_volatility": self.stock_volatility,
            "stock_expected_return": self.stock_expected_return,
            "starting_capital": self.starting_capital,
            "max_tolerable_loss_pct": self.max_tolerable_loss_pct,
            "custom_stock_price": getattr(self, 'custom_stock_price', None),
            "stock_cvar": self.stock_cvar,
            "target_price_to_check": target_price_to_check
        }
        
        return create_visualization(data)