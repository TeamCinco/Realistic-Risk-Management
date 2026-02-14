"""
Ultra-fast prescreener using bulk price data
Reads JSON ticker list, cuts 12k → ~2–4k in minutes
"""

import yfinance as yf
import pandas as pd
import json
from pathlib import Path
import math

INPUT_JSON = "/Users/jazzhashzzz/Documents/Market_Analysis_files/ticker.json"
OUTPUT_TICKERS = "/Users/jazzhashzzz/Documents/Market_Analysis_files/ticker_filtered.txt"

BATCH_SIZE = 100
MIN_PRICE = 5
MIN_AVG_VOL = 8_000_000


def load_tickers_from_json(path):
    """Load tickers from JSON file"""
    with open(path, 'r') as f:
        data = json.load(f)
    
    # Extract tickers from JSON structure
    tickers = []
    for key in data:
        if 'ticker' in data[key]:
            ticker = data[key]['ticker'].strip().upper()
            tickers.append(ticker)
    
    return tickers


def chunk(lst, n):
    """Split list into chunks of size n"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def main():
    print("\n" + "=" * 60)
    print("PRESCREENER - JSON Input")
    print("=" * 60)
    
    # Load tickers from JSON
    print(f"\nLoading tickers from: {INPUT_JSON}")
    tickers = load_tickers_from_json(INPUT_JSON)
    print(f"Loaded {len(tickers)} tickers")
    
    print(f"\nFilters:")
    print(f"  Min Price: ${MIN_PRICE}")
    print(f"  Min Avg Volume: {MIN_AVG_VOL:,}")
    
    passed = []
    total_batches = math.ceil(len(tickers) / BATCH_SIZE)
    
    print(f"\nProcessing {total_batches} batches of {BATCH_SIZE}...")
    print("=" * 60)

    for i, batch in enumerate(chunk(tickers, BATCH_SIZE), 1):
        print(f"Batch {i:3d} / {total_batches} ({len(batch):3d} tickers)...", end=" ", flush=True)

        try:
            data = yf.download(
                batch,
                period="30d",
                group_by="ticker",
                auto_adjust=True,
                threads=False,
                progress=False
            )
        except Exception as e:
            print(f"✗ Failed to download")
            continue

        batch_passed = 0
        for ticker in batch:
            try:
                # Handle single ticker vs multi-ticker data structure
                if len(batch) == 1:
                    df = data
                else:
                    df = data[ticker]
                
                if len(df) < 10:
                    continue

                price = df["Close"].iloc[-1]
                avg_vol = df["Volume"].mean()

                if price >= MIN_PRICE and avg_vol >= MIN_AVG_VOL:
                    passed.append(ticker)
                    batch_passed += 1

            except:
                continue
        
        print(f"✓ {batch_passed} passed")

    # Save results
    with open(OUTPUT_TICKERS, "w") as f:
        for t in passed:
            f.write(f"{t}\n")

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Started with: {len(tickers):,} tickers")
    print(f"Passed filters: {len(passed):,} tickers")
    print(f"Reduction: {(1 - len(passed)/len(tickers))*100:.1f}%")
    print(f"\nSaved to: {OUTPUT_TICKERS}")
    print("=" * 60)


if __name__ == "__main__":
    main()