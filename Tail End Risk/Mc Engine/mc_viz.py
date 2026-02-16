"""Enhanced Visualization functions — Full Risk Dashboard"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path


# ==========================================================
# MAIN ENTRY
# ==========================================================

def create_visualization(data):

    print("\nGenerating enhanced risk dashboard...")

    fig = plt.figure(figsize=(18, 20))
    gs = fig.add_gridspec(
        4, 2,
        hspace=0.5,
        wspace=0.3
    )

    fig.suptitle(
        f'Monte Carlo Risk Dashboard: {data["stock_symbol"]}\n'
        f'{data["num_simulations"]:,} simulations | {data["days_to_simulate"]} days',
        fontsize=16,
        fontweight='bold',
        y=0.99
    )

    # ROW 1
    ax1 = fig.add_subplot(gs[0, 0])
    _plot_price_paths(ax1, data)

    ax2 = fig.add_subplot(gs[0, 1])
    _plot_return_distribution(ax2, data)

    # ROW 2
    ax3 = fig.add_subplot(gs[1, 0])
    _plot_percentile_table(ax3, data)

    ax4 = fig.add_subplot(gs[1, 1])
    _plot_statistical_summary(ax4, data)

    # ROW 3
    ax5 = fig.add_subplot(gs[2, 0])
    _plot_stress_distributions(ax5, data)

    ax6 = fig.add_subplot(gs[2, 1])
    _plot_stress_tail_shift(ax6, data)

    # ROW 4
    ax7 = fig.add_subplot(gs[3, 0])
    _plot_strike_guide(ax7, data)

    ax8 = fig.add_subplot(gs[3, 1])
    _plot_risk_state_panel(ax8, data)

    # Save
    output_dir = Path(
        '/Users/jazzhashzzz/Documents/Market_Analysis_files/output/monte_carlo_risk_engine'
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'monte_carlo_dashboard_{data["stock_symbol"]}_{timestamp}.png'
    output_path = output_dir / filename

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

    return str(output_path)


# ==========================================================
# PRICE PATHS
# ==========================================================

def _plot_price_paths(ax, data):

    paths = data["stock_paths"]
    starting_price = data["stock_price"]
    days = data["days_to_simulate"]

    normalized = (paths / starting_price) * 100
    percentiles = [5, 25, 50, 75, 95]

    for p in percentiles:
        ax.plot(
            np.percentile(normalized, p, axis=1),
            linewidth=2,
            label=f'{p}th'
        )

    ax.fill_between(
        range(days),
        np.percentile(normalized, 5, axis=1),
        np.percentile(normalized, 95, axis=1),
        alpha=0.2
    )

    ax.axhline(100, linewidth=2)
    ax.set_title("Price Path Percentiles", fontweight='bold')
    ax.set_xlabel("Trading Days")
    ax.set_ylabel("Normalized Price")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)


# ==========================================================
# BASE RETURN DISTRIBUTION
# ==========================================================

def _plot_return_distribution(ax, data):

    returns = data["stock_final_returns"]

    ax.hist(returns, bins=100, alpha=0.7)

    p5 = np.percentile(returns, 5)
    p1 = np.percentile(returns, 1)
    median = np.percentile(returns, 50)

    ax.axvline(p5, linestyle='--', linewidth=2, label="5th")
    ax.axvline(p1, linestyle='--', linewidth=2, label="1st")
    ax.axvline(median, linestyle='--', linewidth=2, label="Median")

    ax.set_title("Final Return Distribution (Base)", fontweight='bold')
    ax.set_xlabel("Return (%)")
    ax.set_ylabel("Frequency")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)


# ==========================================================
# PERCENTILE TABLE (Crash-proof)
# ==========================================================

def _plot_percentile_table(ax, data):

    ax.axis('off')

    table_data = []
    df = data["stock_percentiles"]

    for _, row in df.iterrows():
        p = int(row["percentile"])
        r = row["return"]
        table_data.append([f"{p}th", f"{r:.2f}%"])

    table = ax.table(
        cellText=table_data,
        colLabels=["Percentile", "Return"],
        loc='center',
        cellLoc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    ax.set_title("Return Percentiles", fontweight='bold')


# ==========================================================
# RISK SUMMARY
# ==========================================================

def _plot_statistical_summary(ax, data):

    ax.axis('off')

    cvar = data["stock_cvar"]

    table_data = [
        ["Annual Drift (rf proxy)", f'{data["stock_expected_return"]*100:.2f}%'],
        ["Annual Volatility", f'{data["stock_volatility"]*100:.2f}%'],
        ["VaR 95%", f'{cvar["var_95"]:.2f}%'],
        ["CVaR 95%", f'{cvar["cvar_95"]:.2f}%'],
        ["VaR 99%", f'{cvar["var_99"]:.2f}%'],
        ["CVaR 99%", f'{cvar["cvar_99"]:.2f}%'],
    ]

    table = ax.table(
        cellText=table_data,
        colLabels=["Metric", "Value"],
        loc='center',
        cellLoc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    ax.set_title("Risk Summary", fontweight='bold')


# ==========================================================
# STRESS DISTRIBUTIONS
# ==========================================================

def _plot_stress_distributions(ax, data):

    stress_results = data.get("stress_results")

    if not stress_results or len(stress_results) == 0:
        ax.text(
            0.5, 0.5,
            "No Stress Simulations Run",
            ha='center',
            va='center',
            fontsize=12
        )
        ax.set_title("Stress Regime Distributions", fontweight='bold')
        return

    plotted = False

    for mult, result in stress_results.items():

        returns = result.get("stock_final_returns")

        if returns is None or len(returns) == 0:
            continue

        ax.hist(
            returns,
            bins=80,
            alpha=0.4,
            label=f"{mult}x Vol"
        )
        plotted = True

    if plotted:
        ax.legend(fontsize=8)

    ax.set_title("Stress Regime Distributions", fontweight='bold')
    ax.set_xlabel("Return (%)")
    ax.set_ylabel("Frequency")
    ax.grid(True, alpha=0.3)



# ==========================================================
# STRESS TAIL SHIFT
# ==========================================================

def _plot_stress_tail_shift(ax, data):

    ax.axis('off')

    stress_results = data.get("stress_results")

    # ---- Defensive handling ----
    if not stress_results or len(stress_results) == 0:
        ax.text(
            0.5, 0.5,
            "No Stress Data Available",
            ha='center',
            va='center',
            fontsize=12
        )
        ax.set_title("Tail Shift Under Stress", fontweight='bold')
        return

    rows = []

    for mult, result in stress_results.items():

        returns = result.get("stock_final_returns")

        if returns is None or len(returns) == 0:
            continue

        p5 = np.percentile(returns, 5)
        p1 = np.percentile(returns, 1)

        rows.append([
            f"{mult}x",
            f"{p5:.2f}%",
            f"{p1:.2f}%"
        ])

    # If after filtering nothing valid remains
    if len(rows) == 0:
        ax.text(
            0.5, 0.5,
            "Stress Data Invalid",
            ha='center',
            va='center',
            fontsize=12
        )
        ax.set_title("Tail Shift Under Stress", fontweight='bold')
        return

    table = ax.table(
        cellText=rows,
        colLabels=["Vol Regime", "5th %", "1st %"],
        loc='center',
        cellLoc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    ax.set_title("Tail Shift Under Stress", fontweight='bold')


# ==========================================================
# STRIKE GUIDE
# ==========================================================

def _plot_strike_guide(ax, data):

    ax.axis('off')

    current_price = data["stock_price"]
    returns = data["stock_final_returns"]
    df = data["stock_percentiles"]

    table_data = []

    for _, row in df.iterrows():
        p = int(row["percentile"])
        r = row["return"]

        strike = current_price * (1 + r / 100)
        prob_below = (returns <= r).mean() * 100

        table_data.append([
            f"{p}th",
            f"{r:.1f}%",
            f"${strike:.2f}",
            f"{prob_below:.1f}%"
        ])

    table = ax.table(
        cellText=table_data,
        colLabels=["Percentile", "Return", "Strike", "Prob Finish Below"],
        loc='center',
        cellLoc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)

    ax.set_title("Strike Probability Guide", fontweight='bold')


# ==========================================================
# RISK STATE PANEL
# ==========================================================

def _plot_risk_state_panel(ax, data):

    ax.axis('off')

    risk_state = data.get("risk_state", {})

    score = risk_state.get("risk_score", 0)
    regime = risk_state.get("regime", "Unknown")

    rows = [
        ["Risk Score", f"{score:.1f} / 100"],
        ["Regime", regime],
        ["Vol Z-Score", f'{risk_state.get("vol_z", 0):.2f}'],
        ["Tail Ratio", f'{risk_state.get("tail_ratio", 0):.2f}'],
    ]

    table = ax.table(
        cellText=rows,
        colLabels=["Metric", "Value"],
        loc='center',
        cellLoc='center'
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    ax.set_title("Risk State Engine", fontweight='bold')
