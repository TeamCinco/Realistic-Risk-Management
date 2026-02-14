"""Load tickers from ticker.txt"""
from pathlib import Path

def load_tickers(filepath):
    """
    Load tickers from tab-separated file
    Format: ticker\tvolume
    Returns list of ticker symbols
    """
    tickers = []
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split('\t')
                if parts:
                    ticker = parts[0].strip().upper()
                    tickers.append(ticker)
    
    return tickers