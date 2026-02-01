"""Visualization functions"""
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path


def create_visualization(data):
    """Create complete visualization - data dict has all needed values"""
    print("\nGenerating visualization...")
    
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    fig.suptitle(
        f'Monte Carlo Risk Analysis: {data["stock_symbol"]}\n'
        f'{data["num_simulations"]:,} simulations over {data["days_to_simulate"]} days',
        fontsize=16,
        fontweight='bold'
    )
    
    # 1. Price path distribution
    ax1 = fig.add_subplot(gs[0, 0])
    target_price = data.get("target_price_to_check")
    _plot_price_paths(
        ax1,
        data["stock_paths"],
        data["stock_symbol"],
        data["stock_price"],
        data["days_to_simulate"],
        target_price
    )
    
    # 2. Return distribution
    ax2 = fig.add_subplot(gs[0, 1])
    _plot_return_distribution(ax2, data["stock_final_returns"], data["stock_symbol"])
    
    # 3. Percentile table
    ax3 = fig.add_subplot(gs[1, 0])
    _plot_percentile_table(ax3, data)
    
    # 4. Statistical summary with CVaR
    ax4 = fig.add_subplot(gs[1, 1])
    _plot_statistical_summary(ax4, data)
    
    # Save
    output_dir = Path('/Users/jazzhashzzz/Documents/Market_Analysis_files/output/monte_carlo_risk_engine')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if data.get("custom_stock_price") is not None:
        filename = f'monte_carlo_{data["stock_symbol"]}_BACKTEST_{timestamp}.png'
    else:
        filename = f'monte_carlo_{data["stock_symbol"]}_{timestamp}.png'
    
    output_path = output_dir / filename
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    return str(output_path)


def _plot_price_paths(ax, paths, symbol, starting_price, days_to_simulate, target_price=None):
    percentiles_to_plot = [5, 25, 50, 75, 95]
    colors = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4', '#9467bd']

    for i, p in enumerate(percentiles_to_plot):
        percentile_path = np.percentile(paths, p, axis=1)
        ax.plot(
            percentile_path,
            label=f'{p}th percentile',
            color=colors[i],
            linewidth=2
        )

    ax.fill_between(
        range(days_to_simulate),
        np.percentile(paths, 5, axis=1),
        np.percentile(paths, 95, axis=1),
        alpha=0.2,
        color='blue',
        label='5th–95th percentile range'
    )

    # Starting price
    ax.axhline(
        y=starting_price,
        color='black',
        linestyle='-',
        linewidth=2,
        label=f'Start: ${starting_price:.2f}',
        alpha=0.7
    )

    # TARGET PRICE + PERCENTILE RANK
    if target_price is not None:
        final_prices = paths[-1]
        percentile_rank = (
            np.sum(final_prices <= target_price) / len(final_prices)
        ) * 100

        ax.axhline(
            y=target_price,
            color='red',
            linestyle='--',
            linewidth=2.5,
            alpha=0.9,
            label=f'Target: ${target_price:.2f} (~{percentile_rank:.1f}th pct)'
        )

    ax.set_xlabel('Trading Days', fontsize=10)
    ax.set_ylabel('Price ($)', fontsize=10)
    ax.set_title(f'{symbol} – Price Path Distribution', fontsize=12, fontweight='bold')
    ax.legend(fontsize=8, loc='best')
    ax.grid(True, alpha=0.3)


def _plot_return_distribution(ax, returns, symbol):
    ax.hist(returns, bins=100, alpha=0.7, color='blue', edgecolor='black')

    p5 = np.percentile(returns, 5)
    p50 = np.percentile(returns, 50)
    p95 = np.percentile(returns, 95)

    ax.axvline(p5, color='red', linestyle='--', linewidth=2, label='5th percentile')
    ax.axvline(p50, color='yellow', linestyle='--', linewidth=2, label='Median')
    ax.axvline(p95, color='green', linestyle='--', linewidth=2, label='95th percentile')

    ax.set_xlabel('Return (%)', fontsize=10)
    ax.set_ylabel('Frequency', fontsize=10)
    ax.set_title(f'{symbol} - Final Return Distribution', fontsize=12, fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)


def _plot_percentile_table(ax, data):
    ax.axis('tight')
    ax.axis('off')

    table_data = []
    percentiles_to_show = [1, 5, 10, 25, 50, 75, 90, 95, 99]

    for p in percentiles_to_show:
        stock_val = data["stock_percentiles"][
            data["stock_percentiles"]['percentile'] == p
        ]['return'].values[0]
        table_data.append([f'{p}th', f'{stock_val:.2f}%'])
    
    table = ax.table(
        cellText=table_data,
        colLabels=['Percentile', data["stock_symbol"]],
        cellLoc='center',
        loc='center',
        colWidths=[0.4, 0.6]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)
    
    for i in range(len(table_data)):
        if i < 3:
            table[(i + 1, 1)].set_facecolor('#ffcccc')
        elif i == 4:
            table[(i + 1, 1)].set_facecolor('#ffffcc')
        elif i >= 6:
            table[(i + 1, 1)].set_facecolor('#ccffcc')
    
    for j in range(2):
        table[(0, j)].set_facecolor('#4CAF50')
        table[(0, j)].set_text_props(weight='bold', color='white')
    
    ax.set_title('Percentile Returns', fontsize=12, fontweight='bold', pad=20)


def _plot_statistical_summary(ax, data):
    ax.axis('tight')
    ax.axis('off')

    table_data = [
        ['Metric', data["stock_symbol"]],
        ['Ann. Return', f'{data["stock_expected_return"] * 100:.2f}%'],
        ['Ann. Volatility', f'{data["stock_volatility"] * 100:.2f}%'],
        ['', ''],
        ['VaR (95%)', f'{data["stock_cvar"]["var_95"]:.2f}%'],
        ['CVaR (95%)', f'{data["stock_cvar"]["cvar_95"]:.2f}%'],
        ['VaR (99%)', f'{data["stock_cvar"]["var_99"]:.2f}%'],
        ['CVaR (99%)', f'{data["stock_cvar"]["cvar_99"]:.2f}%'],
    ]
    
    table = ax.table(
        cellText=table_data,
        cellLoc='center',
        loc='center',
        colWidths=[0.5, 0.5]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)
    
    for j in range(2):
        table[(0, j)].set_facecolor('#4CAF50')
        table[(0, j)].set_text_props(weight='bold', color='white')
    
    table[(5, 0)].set_facecolor('#fff3cd')
    table[(5, 1)].set_facecolor('#fff3cd')
    table[(7, 0)].set_facecolor('#fff3cd')
    table[(7, 1)].set_facecolor('#fff3cd')
    
    ax.set_title('Statistical Summary', fontsize=12, fontweight='bold', pad=20)
