#!/usr/bin/env python3
"""
Generate comprehensive visualizations from simulation results
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import itertools
from pathlib import Path

# Set style for better looking plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Ensure output directory exists
Path("output/charts").mkdir(parents=True, exist_ok=True)

# Parameter sweep configuration (from actual simulation)
PARAM_SWEEP_CONFIG = {
    'INITIAL_NODE_COUNT': [1000, 5000, 20000],
    'BASE_USD_DEMAND_GROWTH_RATE_MONTHLY': [0.005, 0.01, 0.02],
    'INITIAL_DRIA_PRICE_USD': [0.25, 0.5, 1.0],
    'MARKET_TREND_IMPACT_FACTOR': [0.25, 0.5, 0.75],
    'INITIAL_USD_CREDIT_PURCHASE_PER_MONTH': [50000, 100000, 200000],
    'INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH': [100000, 200000, 400000],
    'SIMULATION_YEARS': [5, 10]
}

def parse_simulation_results(filename):
    """Parse the comprehensive simulation results file"""
    print(f"Parsing simulation results from {filename}...")
    
    results = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Find lines with scenario data (contain Baseline, Bear, Bull, or HighVol)
    scenario_lines = [line.strip() for line in lines if any(scenario in line for scenario in ['Baseline', 'Bear', 'Bull', 'HighVol'])]
    
    print(f"Found {len(scenario_lines)} scenario result lines")
    
    for line in scenario_lines:
        try:
            # Split the line and clean up whitespace
            parts = [part.strip() for part in line.split() if part.strip()]
            
            if len(parts) < 20:  # Need enough parts for all data
                continue
            
            # Find scenario position
            scenario_idx = next((i for i, part in enumerate(parts) if part in ['Baseline', 'Bear', 'Bull', 'HighVol']), None)
            if scenario_idx is None:
                continue
                
            scenario = parts[scenario_idx]
            
            # Extract parameters (they should be at the beginning)
            try:
                node_count = int(float(parts[0]))
                growth_rate = float(parts[1])
                initial_price = float(parts[2])
                trend_impact = float(parts[3]) if len(parts) > 3 else 0.25
                usd_purchase = int(float(parts[4])) if len(parts) > 4 else 50000
                dria_payments = int(float(parts[5])) if len(parts) > 5 else 100000
                sim_years = int(float(parts[6])) if len(parts) > 6 else 5
                
                # Extract final prices - they should be after the scenario
                # Looking for 3 consecutive numeric values that look like prices
                price_candidates = []
                for i in range(scenario_idx + 1, min(len(parts), scenario_idx + 10)):
                    try:
                        price = float(parts[i])
                        if 0.01 <= price <= 100:  # Reasonable price range
                            price_candidates.append(price)
                    except ValueError:
                        continue
                
                if len(price_candidates) >= 3:
                    sim1_price = price_candidates[0]
                    sim2_price = price_candidates[1] 
                    sim3_price = price_candidates[2]
                    
                    result = {
                        'INITIAL_NODE_COUNT': node_count,
                        'BASE_USD_DEMAND_GROWTH_RATE_MONTHLY': growth_rate,
                        'INITIAL_DRIA_PRICE_USD': initial_price,
                        'MARKET_TREND_IMPACT_FACTOR': trend_impact,
                        'INITIAL_USD_CREDIT_PURCHASE_PER_MONTH': usd_purchase,
                        'INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH': dria_payments,
                        'SIMULATION_YEARS': sim_years,
                        'market_scenario': scenario,
                        'Sim1_final_price': sim1_price,
                        'Sim2_final_price': sim2_price,
                        'Sim3_final_price': sim3_price
                    }
                    results.append(result)
                    
            except (ValueError, IndexError) as e:
                continue
                
        except Exception as e:
            continue
    
    df = pd.DataFrame(results)
    print(f"Parsed {len(df)} simulation results")
    if len(df) > 0:
        print(f"Price ranges found:")
        for col in ['Sim1_final_price', 'Sim2_final_price', 'Sim3_final_price']:
            if col in df.columns:
                print(f"  {col}: {df[col].min():.3f} - {df[col].max():.3f}")
    return df

def plot_final_price_distributions(results_df):
    """Generate price distribution charts"""
    print("Generating price distribution charts...")
    
    # Histogram
    plt.figure(figsize=(12, 8))
    plt.hist(results_df['Sim1_final_price'], bins=50, alpha=0.6, label='Sim1', color='#1f77b4')
    plt.hist(results_df['Sim2_final_price'], bins=50, alpha=0.6, label='Sim2', color='#ff7f0e')
    plt.hist(results_df['Sim3_final_price'], bins=50, alpha=0.6, label='Sim3 (BME)', color='#2ca02c')
    plt.xlabel('Final Price (USD)', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title('Distribution of Final Token Prices Across All Scenarios\n(17,496 simulation runs)', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('output/charts/price_distribution_histogram.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Boxplot
    melted = pd.melt(results_df, value_vars=['Sim1_final_price', 'Sim2_final_price', 'Sim3_final_price'], 
                     var_name='Model', value_name='Final_Price')
    melted['Model'] = melted['Model'].map({
        'Sim1_final_price': 'Sim1',
        'Sim2_final_price': 'Sim2', 
        'Sim3_final_price': 'Sim3 (BME)'
    })
    
    plt.figure(figsize=(10, 8))
    sns.boxplot(x='Model', y='Final_Price', data=melted)
    plt.ylabel('Final Price (USD)', fontsize=12)
    plt.title('Final Price Distribution by Tokenomics Model\n(Statistical Summary)', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('output/charts/price_distribution_boxplot.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_scenario_comparison(results_df):
    """Generate scenario comparison charts"""
    print("Generating scenario comparison charts...")
    
    melted = pd.melt(
        results_df,
        id_vars=['market_scenario'],
        value_vars=['Sim1_final_price', 'Sim2_final_price', 'Sim3_final_price'],
        var_name='Model', value_name='Final_Price'
    )
    melted['Model'] = melted['Model'].map({
        'Sim1_final_price': 'Sim1',
        'Sim2_final_price': 'Sim2',
        'Sim3_final_price': 'Sim3 (BME)'
    })
    
    # Boxplot by scenario
    plt.figure(figsize=(14, 8))
    sns.boxplot(x='market_scenario', y='Final_Price', hue='Model', data=melted)
    plt.ylabel('Final Price (USD)', fontsize=12)
    plt.xlabel('Market Scenario', fontsize=12)
    plt.title('Token Price Performance Across Market Scenarios\n(All Models Comparison)', fontsize=14, fontweight='bold')
    plt.legend(title='Tokenomics Model', fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('output/charts/scenario_comparison_boxplot.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Mean price by scenario
    grouped = melted.groupby(['market_scenario', 'Model'])['Final_Price'].mean().unstack()
    ax = grouped.plot(kind='bar', figsize=(12, 8), width=0.8)
    plt.ylabel('Mean Final Price (USD)', fontsize=12)
    plt.xlabel('Market Scenario', fontsize=12)
    plt.title('Average Token Price by Market Scenario\n(Model Performance Comparison)', fontsize=14, fontweight='bold')
    plt.legend(title='Tokenomics Model', fontsize=11)
    plt.grid(True, axis='y', alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('output/charts/scenario_comparison_mean_price.png', dpi=300, bbox_inches='tight')
    plt.close()

def plot_parameter_sensitivity(results_df):
    """Generate parameter sensitivity analysis"""
    print("Generating parameter sensitivity charts...")
    
    models = [('Sim1_final_price', 'Sim1'), ('Sim2_final_price', 'Sim2'), ('Sim3_final_price', 'Sim3 (BME)')]
    key_params = ['INITIAL_NODE_COUNT', 'BASE_USD_DEMAND_GROWTH_RATE_MONTHLY', 'INITIAL_DRIA_PRICE_USD', 'MARKET_TREND_IMPACT_FACTOR']
    
    for param in key_params:
        if param not in results_df.columns:
            continue
            
        plt.figure(figsize=(12, 8))
        for price_col, model_name in models:
            grouped = results_df.groupby(param)[price_col].mean()
            plt.plot(grouped.index, grouped.values, marker='o', linewidth=2.5, markersize=8, label=f'{model_name} Model')
        
        plt.xlabel(param.replace('_', ' ').title(), fontsize=12)
        plt.ylabel('Mean Final Price (USD)', fontsize=12)
        plt.title(f'Parameter Sensitivity Analysis: {param.replace("_", " ").title()}\n(Impact on Token Price)', fontsize=14, fontweight='bold')
        plt.legend(fontsize=11)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(f'output/charts/parameter_sensitivity_{param.lower()}.png', dpi=300, bbox_inches='tight')
        plt.close()

def plot_model_statistics(results_df):
    """Generate model performance statistics"""
    print("Generating model performance statistics...")
    
    models = ['Sim1_final_price', 'Sim2_final_price', 'Sim3_final_price']
    model_names = ['Sim1', 'Sim2', 'Sim3 (BME)']
    
    stats = {}
    for model, name in zip(models, model_names):
        data = results_df[model].dropna()
        stats[name] = {
            'Mean': data.mean(),
            'Std Dev': data.std(),
            'Min': data.min(),
            'Max': data.max(),
            'Median': data.median(),
            'IQR': data.quantile(0.75) - data.quantile(0.25)
        }
    
    # Standard deviation comparison
    plt.figure(figsize=(10, 6))
    plt.bar(model_names, [stats[name]['Std Dev'] for name in model_names], 
            color=['#1f77b4', '#ff7f0e', '#2ca02c'], alpha=0.8)
    plt.ylabel('Standard Deviation (USD)', fontsize=12)
    plt.title('Model Volatility Comparison\n(Price Standard Deviation)', fontsize=14, fontweight='bold')
    plt.grid(True, axis='y', alpha=0.3)
    for i, name in enumerate(model_names):
        plt.text(i, stats[name]['Std Dev'] + 0.01, f'${stats[name]["Std Dev"]:.3f}', 
                ha='center', va='bottom', fontweight='bold')
    plt.tight_layout()
    plt.savefig('output/charts/model_volatility_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Price range comparison
    plt.figure(figsize=(12, 8))
    x = np.arange(len(model_names))
    width = 0.35
    
    plt.bar(x - width/2, [stats[name]['Min'] for name in model_names], width, 
            label='Minimum Price', alpha=0.8, color='#d62728')
    plt.bar(x + width/2, [stats[name]['Max'] for name in model_names], width,
            label='Maximum Price', alpha=0.8, color='#2ca02c')
    
    plt.ylabel('Price (USD)', fontsize=12)
    plt.xlabel('Tokenomics Model', fontsize=12)
    plt.title('Price Range Comparison Across Models\n(Min/Max Values from All Scenarios)', fontsize=14, fontweight='bold')
    plt.xticks(x, model_names)
    plt.legend(fontsize=11)
    plt.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig('output/charts/model_price_range_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Save statistics table
    stats_df = pd.DataFrame(stats).T
    stats_df.to_csv('output/charts/model_performance_statistics.csv')
    print("\nModel Performance Statistics:")
    print(stats_df.round(4))

def generate_summary_dashboard():
    """Create a summary dashboard image"""
    print("Generating summary dashboard...")
    
    # Read statistics
    stats_df = pd.read_csv('output/charts/model_performance_statistics.csv', index_col=0)
    
    # Create dashboard
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Tokenomics Simulation Analysis Dashboard\n5,832 Simulation Scenarios Across 3 Models', 
                 fontsize=16, fontweight='bold', y=0.95)
    
    # Plot 1: Mean prices
    models = stats_df.index
    ax1.bar(models, stats_df['Mean'], color=['#1f77b4', '#ff7f0e', '#2ca02c'], alpha=0.8)
    ax1.set_title('Average Final Price by Model', fontweight='bold')
    ax1.set_ylabel('Price (USD)')
    ax1.grid(True, alpha=0.3)
    for i, (model, mean_val) in enumerate(zip(models, stats_df['Mean'])):
        ax1.text(i, mean_val + 0.02, f'${mean_val:.3f}', ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: Volatility
    ax2.bar(models, stats_df['Std Dev'], color=['#1f77b4', '#ff7f0e', '#2ca02c'], alpha=0.8)
    ax2.set_title('Price Volatility (Standard Deviation)', fontweight='bold')
    ax2.set_ylabel('Std Dev (USD)')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Price ranges
    x = np.arange(len(models))
    width = 0.35
    ax3.bar(x - width/2, stats_df['Min'], width, label='Min', alpha=0.8, color='#d62728')
    ax3.bar(x + width/2, stats_df['Max'], width, label='Max', alpha=0.8, color='#2ca02c')
    ax3.set_title('Price Range (Min/Max)', fontweight='bold')
    ax3.set_ylabel('Price (USD)')
    ax3.set_xticks(x)
    ax3.set_xticklabels(models)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Summary metrics table
    ax4.axis('tight')
    ax4.axis('off')
    table_data = stats_df.round(3).values
    table = ax4.table(cellText=table_data, rowLabels=models, 
                     colLabels=stats_df.columns, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.5)
    ax4.set_title('Performance Statistics Summary', fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig('output/charts/simulation_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Main function to generate all visualizations"""
    print("=== GENERATING COMPREHENSIVE SIMULATION VISUALIZATIONS ===")
    
    # Parse simulation results
    try:
        results_df = parse_simulation_results('output/comprehensive_simulation_results.txt')
        if results_df.empty:
            print("ERROR: No simulation results found!")
            return
        
        print(f"Successfully parsed {len(results_df)} simulation results")
        print(f"Market scenarios: {results_df['market_scenario'].unique()}")
        print(f"Price ranges:")
        for col in ['Sim1_final_price', 'Sim2_final_price', 'Sim3_final_price']:
            print(f"  {col}: ${results_df[col].min():.3f} - ${results_df[col].max():.3f}")
        
        # Generate all visualizations
        plot_final_price_distributions(results_df)
        plot_scenario_comparison(results_df)
        plot_parameter_sensitivity(results_df)
        plot_model_statistics(results_df)
        generate_summary_dashboard()
        
        print("\n=== VISUALIZATION GENERATION COMPLETE ===")
        print("Charts saved to: output/charts/")
        print("Generated files:")
        chart_files = [
            "price_distribution_histogram.png",
            "price_distribution_boxplot.png", 
            "scenario_comparison_boxplot.png",
            "scenario_comparison_mean_price.png",
            "model_volatility_comparison.png",
            "model_price_range_comparison.png",
            "simulation_dashboard.png",
            "model_performance_statistics.csv"
        ]
        for filename in chart_files:
            print(f"  - {filename}")
            
        # Parameter sensitivity charts
        for param in ['initial_node_count', 'base_usd_demand_growth_rate_monthly', 
                     'initial_dria_price_usd', 'market_trend_impact_factor']:
            print(f"  - parameter_sensitivity_{param}.png")
        
    except Exception as e:
        print(f"ERROR: Failed to generate visualizations: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 