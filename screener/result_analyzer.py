"""
Analyze screening results to find actionable setups
"""

import pandas as pd
import os


INPUT_FILE = "/Users/jazzhashzzz/Documents/Market_Analysis_files/screener/screening_results.xlsx"
OUTPUT_FILE = "/Users/jazzhashzzz/Documents/Market_Analysis_files/output/screener/screening_analysis.xlsx"


def analyze_results(df):
    """
    Analyze screening results and categorize stocks
    """

    NUMERIC_COLS = [
        "current_price",
        "volatility",
        "p5",
        "p10",
        "p50",
        "p95",
        "cvar_95",
    ]

    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Keep only valid simulations
    df = df[df["success"] == True].copy()
    df = df.dropna(subset=["p5", "p50", "p95", "volatility"])

    # Hard sanity filters (prevents GBM blowups)
    df = df[
        (df["volatility"] < 300) &
        (df["p5"] > -100) &
        (df["p95"] < 300)
    ]

    if len(df) == 0:
        return {}

    extreme_oversold = df[(df["p5"] <= -5) & (df["p5"] >= -15)].sort_values("p5")
    catastrophic = df[df["p5"] < -15].sort_values("p5")
    extreme_overbought = df[df["p95"] > 15].sort_values("p95", ascending=False)
    high_vol = df[df["volatility"] > 40].sort_values("volatility", ascending=False)
    moderate_pullback = df[(df["p10"] <= -5) & (df["p10"] >= -10)].sort_values("p10")

    df["percentile_range"] = df["p95"] - df["p5"]
    stable = df[(df["volatility"] < 20) & (df["percentile_range"] < 30)].sort_values("volatility")

    return {
        "extreme_oversold": extreme_oversold,
        "catastrophic": catastrophic,
        "extreme_overbought": extreme_overbought,
        "high_volatility": high_vol,
        "moderate_pullback": moderate_pullback,
        "stable": stable,
        "total": len(df),
    }


def print_analysis(results):
    """Print analysis summary to terminal"""

    print("\n" + "=" * 80)
    print("SCREENING ANALYSIS")
    print("=" * 80)

    print(f"\nTotal stocks analyzed: {results['total']}")

    # EXTREME OVERSOLD
    oversold = results["extreme_oversold"]
    print(f"\n{'='*80}")
    print(f"EXTREME OVERSOLD – Potential Buy Setups ({len(oversold)})")
    print(f"{'='*80}")
    if len(oversold) > 0:
        print("5th percentile between -15% and -5%")
        print(f"\n{'Ticker':<8} {'Price':<12} {'Vol%':<8} {'5th%':<8} {'10th%':<8} {'Median%':<8}")
        print("-" * 80)
        for _, r in oversold.head(10).iterrows():
            print(
                f"{r['ticker']:<8} ${r['current_price']:<11.2f} {r['volatility']:<7.1f} "
                f"{r['p5']:<7.1f} {r['p10']:<7.1f} {r['p50']:<7.1f}"
            )
    else:
        print("None found")

    # CATASTROPHIC
    catastrophic = results["catastrophic"]
    print(f"\n{'='*80}")
    print(f"CATASTROPHIC – Likely Falling Knives ({len(catastrophic)})")
    print(f"{'='*80}")
    if len(catastrophic) > 0:
        print("5th percentile < -15%")
        print(f"\n{'Ticker':<8} {'Price':<12} {'Vol%':<8} {'5th%':<8} {'CVaR95%':<8}")
        print("-" * 80)
        for _, r in catastrophic.head(10).iterrows():
            print(
                f"{r['ticker']:<8} ${r['current_price']:<11.2f} {r['volatility']:<7.1f} "
                f"{r['p5']:<7.1f} {r['cvar_95']:<7.1f}"
            )
    else:
        print("None found")

    # MODERATE PULLBACK
    moderate = results["moderate_pullback"]
    print(f"\n{'='*80}")
    print(f"MODERATE PULLBACKS – Watch List ({len(moderate)})")
    print(f"{'='*80}")
    if len(moderate) > 0:
        print(f"\n{'Ticker':<8} {'Price':<12} {'Vol%':<8} {'10th%':<8} {'Median%':<8}")
        print("-" * 80)
        for _, r in moderate.head(10).iterrows():
            print(
                f"{r['ticker']:<8} ${r['current_price']:<11.2f} {r['volatility']:<7.1f} "
                f"{r['p10']:<7.1f} {r['p50']:<7.1f}"
            )
    else:
        print("None found")

    # HIGH VOLATILITY
    high_vol = results["high_volatility"]
    print(f"\n{'='*80}")
    print(f"HIGH VOLATILITY – Options Candidates ({len(high_vol)})")
    print(f"{'='*80}")
    if len(high_vol) > 0:
        print(f"\n{'Ticker':<8} {'Vol%':<8} {'5th%':<8} {'50th%':<8} {'95th%':<8}")
        print("-" * 80)
        for _, r in high_vol.head(10).iterrows():
            print(
                f"{r['ticker']:<8} {r['volatility']:<7.1f} "
                f"{r['p5']:<7.1f} {r['p50']:<7.1f} {r['p95']:<7.1f}"
            )
    else:
        print("None found")


def save_analyzed_results(results, output_path):
    """Save categorized results to Excel"""

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for name, df in results.items():
            if isinstance(df, pd.DataFrame) and len(df) > 0:
                df.to_excel(writer, sheet_name=name[:31], index=False)

    print(f"\nSaved analyzed results → {output_path}")


def main():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    df = pd.read_excel(INPUT_FILE)

    results = analyze_results(df)

    if not results:
        print("No valid screening results found.")
        return

    print_analysis(results)
    save_analyzed_results(results, OUTPUT_FILE)


if __name__ == "__main__":
    main()
