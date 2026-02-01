"""Data download and price management"""
import yfinance as yf
import pandas as pd
from datetime import date, timedelta

def download_data(stock_symbol, historical_window):
    """Download historical price data from yfinance"""
    print("\nDownloading historical data...")
    calendar_days = int(historical_window * (365/252)) + 100
    start_date = date.today() - timedelta(days=calendar_days)
    
    stock_data = yf.download(stock_symbol, start=start_date, progress=False, auto_adjust=True)
    
    if len(stock_data) == 0:
        raise ValueError(f"No data found for {stock_symbol}")
    
    # Flatten multi-level columns if present
    if isinstance(stock_data.columns, pd.MultiIndex):
        stock_data.columns = stock_data.columns.get_level_values(0)
    
    return stock_data

def set_starting_prices(stock_data, stock_symbol, custom_stock_price=None):
    """Set starting prices from custom values or current market prices"""
    print("\nSetting starting prices...")
    
    if custom_stock_price is not None:
        stock_price = custom_stock_price
        print(f"  Using custom {stock_symbol} price: ${custom_stock_price:.2f}")
    else:
        close_value = stock_data['Close'].iloc[-1]
        stock_price = float(close_value.item() if hasattr(close_value, 'item') else close_value)
        print(f"  Using current {stock_symbol} price: ${stock_price:.2f}")
    
    return stock_price