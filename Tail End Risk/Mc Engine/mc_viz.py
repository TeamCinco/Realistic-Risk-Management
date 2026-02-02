"""Visualization functions"""
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path

def create_visualization(data):
    """Create complete visualization - data dict has all needed values"""
    print("\nGenerating visualization...")
    
    # Always use same layout - no extra panel needed
    fig = plt.figure(figsize=(16, 14))
    gs = fig.add_gridspec(3, 2, hspace=0.5, wspace=0.3, height_ratios=[1, 1, 0.7])
    
    fig.suptitle(
        f'Monte Carlo Risk Analysis: {data["stock_symbol"]}\n'
        f'{data["num_simulations"]:,} simulations over {data["days_to_simulate"]} days',
        fontsize=16, fontweight='bold', y=0.99
    )
    
    # 1. Price path distribution
    ax1 = fig.add_subplot(gs[0, 0])
    target_price = data.get("target_price_to_check")
    _plot_price_paths(ax1, data["stock_paths"], data["stock_symbol"], data["stock_price"], 
                     data["days_to_simulate"], target_price)
    
    # 2. Return distribution
    ax2 = fig.add_subplot(gs[0, 1])
    _plot_return_distribution(ax2, data["stock_final_returns"], data["stock_symbol"])
    
    # 3. Percentile table
    ax3 = fig.add_subplot(gs[1, 0])
    _plot_percentile_table(ax3, data)
    
    # 4. Drop Analysis or Statistical summary
    ax4 = fig.add_subplot(gs[1, 1])
    _plot_statistical_summary(ax4, data)
    
    # 5. Strike Placement Guide
    ax5 = fig.add_subplot(gs[2, :])
    _plot_strike_guide(ax5, data)
    
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
    normalized_paths = (paths / starting_price) * 100
    percentiles_to_plot = [5, 25, 50, 75, 95]
    colors = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4', '#9467bd']
    
    for i, p in enumerate(percentiles_to_plot):
        percentile_path = np.percentile(normalized_paths, p, axis=1)
        ax.plot(percentile_path, label=f'{p}th percentile', color=colors[i], linewidth=2)
    
    ax.fill_between(range(days_to_simulate), np.percentile(normalized_paths, 5, axis=1),
                     np.percentile(normalized_paths, 95, axis=1), alpha=0.2, color='blue',
                     label='5th-95th percentile range')
    
    # Add horizontal line at starting price (100)
    ax.axhline(y=100, color='black', linestyle='-', linewidth=2, label=f'Start: ${starting_price:.2f}', alpha=0.7)
    
    # Add horizontal line at target price if provided
    if target_price is not None:
        target_normalized = (target_price / starting_price) * 100
        ax.axhline(y=target_normalized, color='red', linestyle='--', linewidth=2.5, 
                   label=f'Target: ${target_price:.2f}', alpha=0.8)
    
    ax.set_xlabel('Trading Days', fontsize=10)
    ax.set_ylabel('Normalized Price (Start = 100)', fontsize=10)
    ax.set_title(f'{symbol} - Price Path Distribution', fontsize=12, fontweight='bold')
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
        stock_val = data["stock_percentiles"][data["stock_percentiles"]['percentile'] == p]['return'].values[0]
        table_data.append([f'{p}th', f'{stock_val:.2f}%'])
    
    table = ax.table(cellText=table_data, colLabels=['Percentile', data["stock_symbol"]],
                     cellLoc='center', loc='center', colWidths=[0.4, 0.6])
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1, 2.5)
    
    for i, row in enumerate(table_data):
        if i < 3:
            table[(i+1, 1)].set_facecolor('#ffcccc')
        elif i == 4:
            table[(i+1, 1)].set_facecolor('#ffffcc')
        elif i >= 6:
            table[(i+1, 1)].set_facecolor('#ccffcc')
    
    for j in range(2):
        table[(0, j)].set_facecolor('#4CAF50')
        table[(0, j)].set_text_props(weight='bold', color='white')
    
    ax.set_title('Percentile Returns', fontsize=12, fontweight='bold', pad=20)

def _plot_statistical_summary(ax, data):
    ax.axis('tight')
    ax.axis('off')
    
    # Check if backtest mode
    custom_price = data.get("custom_stock_price")
    target_price = data.get("target_price_to_check")
    
    if custom_price and target_price:
        # Backtest mode - show drop analysis
        drop_pct = ((target_price - custom_price) / custom_price) * 100
        drop_dollars = target_price - custom_price
        percentile_rank = np.sum(data["stock_final_returns"] <= drop_pct) / len(data["stock_final_returns"]) * 100
        
        # Determine classification
        if percentile_rank <= 1:
            classification = "Catastrophic"
        elif percentile_rank <= 5:
            classification = "Extreme Oversold"
        elif percentile_rank <= 15:
            classification = "Very Oversold"
        elif percentile_rank <= 25:
            classification = "Oversold"
        else:
            classification = "Normal"
        
        table_data = [
            ['Metric', data["stock_symbol"]],
            ['Starting Price', f'${custom_price:.2f}'],
            ['Current Price', f'${target_price:.2f}'],
            ['Drop Amount', f'${drop_dollars:.2f}'],
            ['Drop %', f'{drop_pct:.2f}%'],
            ['', ''],
            ['Percentile Rank', f'{percentile_rank:.1f}th'],
            ['Classification', classification],
            ['', ''],
            ['Ann. Volatility', f'{data["stock_volatility"]*100:.2f}%'],
            ['', ''],
            ['VaR (95%)', f'{data["stock_cvar"]["var_95"]:.2f}%'],
            ['CVaR (95%)', f'{data["stock_cvar"]["cvar_95"]:.2f}%'],
            ['VaR (99%)', f'{data["stock_cvar"]["var_99"]:.2f}%'],
            ['CVaR (99%)', f'{data["stock_cvar"]["cvar_99"]:.2f}%'],
        ]
        
        table = ax.table(cellText=table_data, cellLoc='center', loc='center', colWidths=[0.5, 0.5])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.8)
        
        # Header styling
        for j in range(2):
            table[(0, j)].set_facecolor('#4CAF50')
            table[(0, j)].set_text_props(weight='bold', color='white')
        
        # Highlight percentile rank
        table[(6, 0)].set_facecolor('#fff3cd')
        table[(6, 1)].set_facecolor('#fff3cd')
        table[(6, 1)].set_text_props(weight='bold', size=11)
        
        # Color code classification
        if percentile_rank <= 5:
            table[(7, 1)].set_facecolor('#ffcccc')
        elif percentile_rank <= 15:
            table[(7, 1)].set_facecolor('#ffe0cc')
        elif percentile_rank <= 25:
            table[(7, 1)].set_facecolor('#ffffcc')
        table[(7, 1)].set_text_props(weight='bold')
        
        # Highlight CVaR rows
        table[(12, 0)].set_facecolor('#fff3cd')
        table[(12, 1)].set_facecolor('#fff3cd')
        table[(14, 0)].set_facecolor('#fff3cd')
        table[(14, 1)].set_facecolor('#fff3cd')
        
        ax.set_title('Drop Analysis', fontsize=12, fontweight='bold', pad=20)
    
    else:
        # Normal mode - show standard stats
        table_data = [
            ['Metric', data["stock_symbol"]],
            ['Ann. Return', f'{data["stock_expected_return"]*100:.2f}%'],
            ['Ann. Volatility', f'{data["stock_volatility"]*100:.2f}%'],
            ['', ''],
            ['VaR (95%)', f'{data["stock_cvar"]["var_95"]:.2f}%'],
            ['CVaR (95%)', f'{data["stock_cvar"]["cvar_95"]:.2f}%'],
            ['VaR (99%)', f'{data["stock_cvar"]["var_99"]:.2f}%'],
            ['CVaR (99%)', f'{data["stock_cvar"]["cvar_99"]:.2f}%'],
        ]
        
        table = ax.table(cellText=table_data, cellLoc='center', loc='center', colWidths=[0.5, 0.5])
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2.5)
        
        # Header styling
        for j in range(2):
            table[(0, j)].set_facecolor('#4CAF50')
            table[(0, j)].set_text_props(weight='bold', color='white')
        
        # Highlight CVaR rows
        table[(5, 0)].set_facecolor('#fff3cd')
        table[(5, 1)].set_facecolor('#fff3cd')
        table[(7, 0)].set_facecolor('#fff3cd')
        table[(7, 1)].set_facecolor('#fff3cd')
        
        ax.set_title('Statistical Summary', fontsize=12, fontweight='bold', pad=20)

def _plot_strike_guide(ax, data):
    """Strike placement guide for options trading"""
    ax.axis('tight')
    ax.axis('off')
    
    current_price = data["stock_price"]
    percentiles_to_show = [1, 5, 10, 15, 25, 50, 75, 85, 90, 95, 99]
    
    table_data = []
    for p in percentiles_to_show:
        row = data["stock_percentiles"][data["stock_percentiles"]['percentile'] == p]
        if len(row) > 0:
            return_pct = row['return'].values[0]
            strike_price = current_price * (1 + return_pct / 100)
            
            # Add interpretation
            if p <= 5:
                zone = "Catastrophic"
            elif p <= 15:
                zone = "Extreme Tail"
            elif p <= 25:
                zone = "Significant"
            elif p <= 50:
                zone = "Below Expected"
            elif p <= 75:
                zone = "Above Expected"
            elif p <= 90:
                zone = "Strong Move"
            else:
                zone = "Extreme Upside"
            
            table_data.append([
                f'{p}th',
                f'{return_pct:>6.1f}%',
                f'${strike_price:>8.2f}',
                zone
            ])
    
    table = ax.table(
        cellText=table_data,
        colLabels=['Percentile', 'Return', 'Strike Price', 'Zone'],
        cellLoc='center',
        loc='center',
        colWidths=[0.15, 0.15, 0.2, 0.25]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Color code rows
    for i, row_data in enumerate(table_data, start=1):
        percentile = int(row_data[0].replace('th', ''))
        
        if percentile <= 5:
            # Red - catastrophic
            for j in range(4):
                table[(i, j)].set_facecolor('#ffcccc')
        elif percentile <= 15:
            # Orange - extreme tail (put selling zone)
            for j in range(4):
                table[(i, j)].set_facecolor('#ffe0cc')
        elif percentile <= 25:
            # Yellow - significant
            for j in range(4):
                table[(i, j)].set_facecolor('#ffffcc')
        elif percentile >= 85:
            # Light green - upside
            for j in range(4):
                table[(i, j)].set_facecolor('#ccffcc')
    
    # Header styling
    for j in range(4):
        table[(0, j)].set_facecolor('#4CAF50')
        table[(0, j)].set_text_props(weight='bold', color='white')
    
    title_text = f'Strike Placement Guide (Current: ${current_price:.2f})'
    ax.set_title(title_text, fontsize=12, fontweight='bold', pad=20)