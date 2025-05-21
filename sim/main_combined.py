# main_combined.py

import model_parameters as p_orig
import simulation_engine as engine_orig
import model_parameters_proposal as p_prop
import simulation_engine_proposal as engine_prop

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import inspect # For fetching parameters

# --- Functions to run simulations ---

def run_original_simulation():
    """Runs the original simulation and returns its history and parameters."""
    initial_state_orig = {
        "current_year": 1,
        "current_month": 0,
        "circulating_supply": p_orig.INITIAL_CIRCULATING_SUPPLY,
        "total_tokens_burned": 0,
        "total_dria_staked": 0,
        "current_node_count": p_orig.MIN_NODES, # Start with min nodes
        "simulated_dria_price_usd": p_orig.INITIAL_SIMULATED_DRIA_PRICE_USD,
        "remaining_node_rewards_pool_tokens": p_orig.NODE_RUNNER_REWARDS_POOL_TOTAL,
        "remaining_ecosystem_fund_tokens": p_orig.ECOSYSTEM_FUND_TOKENS_TOTAL,
        "vested_team_tokens": 0,
        "vested_advisors_tokens": 0,
        "vested_private_round_tokens": 0,
        "vested_current_round_tokens": 0,
        "current_usd_credit_purchase_per_month": p_orig.INITIAL_USD_CREDIT_PURCHASE_PER_MONTH,
        "current_dria_earned_by_on_prem_users_per_month": p_orig.DRIA_EARNED_BY_ON_PREM_USERS_PER_MONTH,
        "current_oracle_requests_per_month": p_orig.INITIAL_ORACLE_REQUESTS_PER_MONTH,
        "current_compute_demand_gflops_monthly": p_orig.INITIAL_SERVICE_DEMAND_GFLOPS_MONTHLY,
        "current_network_capacity_gflops_monthly": p_orig.INITIAL_NETWORK_CAPACITY_GFLOPS_PER_MONTH,
        "newly_staked_dria_monthly": 0,
        "actual_node_apy_monthly_percentage": 0,
        "node_runner_revenue_monthly_usd": 0,
        "newly_vested_total_monthly": 0,
        "emitted_node_rewards_monthly": 0,
        "ecosystem_fund_released_monthly": 0,
        "burned_from_usd_monthly": 0,
        "burned_from_onprem_monthly": 0,
        "burned_from_oracle_monthly": 0,
        'apy_history': [],
        'average_apy_for_decision': 0,
        'current_adjusted_base_staking_yield_annual': p_orig.BASE_STAKING_YIELD_RATE_ANNUAL,
        # Ensure all keys from engine_orig.run_simulation's state are initialized
        'network_utilization_rate': 0, 
        'current_quarter_ecosystem_release_pool': 0,
        'current_quarter_ecosystem_released_so_far': 0
    }
    history = engine_orig.run_simulation(initial_state_orig, p_orig.SIMULATION_YEARS)
    return pd.DataFrame(history), p_orig

def run_proposal_simulation():
    """Runs the proposal simulation and returns its history and parameters."""
    initial_state_prop = {
        "current_year": 1,
        "current_month": 0,
        "circulating_supply_proposal": p_prop.PROPOSAL_INITIAL_CIRCULATING_SUPPLY,
        "total_tokens_burned_proposal": 0,
        "simulated_dria_price_usd_proposal": p_prop.INITIAL_SIMULATED_DRIA_PRICE_USD_PROPOSAL,
        "remaining_emission_pool_proposal": p_prop.EMISSION_SUPPLY_POOL_PROPOSAL,
        "remaining_ecosystem_fund_tokens_proposal": p_prop.ECOSYSTEM_FUND_TOKENS_TOTAL_PROPOSAL,
        "vested_team_tokens_proposal": 0,
        "vested_advisors_tokens_proposal": 0,
        "vested_investors_tokens_proposal": 0,
        "current_usd_demand_per_month_proposal": p_prop.INITIAL_USD_CREDIT_PURCHASE_PER_MONTH_PROPOSAL,
        "current_dria_demand_per_month_proposal": p_prop.INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH,
        "current_validator_nodes": p_prop.PROPOSAL_INITIAL_VALIDATOR_NODES,
        "current_contributor_nodes": p_prop.PROPOSAL_INITIAL_CONTRIBUTOR_NODES,
        "total_dria_staked_proposal": 0,  # Will be calculated based on initial nodes
        "treasury_balance_proposal": 0,
        "total_tokens_slashed_proposal": 0,
        "burned_from_fees_monthly_proposal": 0,
        "ecosystem_fund_released_monthly_proposal": 0,
        "total_distributed_to_contributors_monthly": 0,
        "validator_staking_rewards_monthly_proposal": 0,
        "monthly_profit_per_node_usd": 0,
        "node_growth_rate": 0
    }
    history = engine_prop.run_simulation_proposal(initial_state_prop, p_prop, p_prop.SIMULATION_YEARS)
    return pd.DataFrame(history), p_prop

# --- Functions to generate HTML content ---

def get_params_as_html_table(params_module, title):
    """Generates an HTML table for parameters from a module."""
    html = f"<h3>{title} Parameters</h3><table><tr><th>Parameter</th><th>Value</th></tr>"
    param_items = []
    for name, value in inspect.getmembers(params_module):
        if not name.startswith('__') and not callable(value) and not inspect.ismodule(value) and name.isupper(): # Typically params are uppercase
            param_items.append((name, value))

    for name, value in param_items:
        value_str = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        html += f"<tr><td>{name}</td><td>{value_str}</td></tr>"
    html += "</table>"
    return html

def get_mechanisms_html():
    """Returns HTML string describing core mechanisms of both models."""
    html = "<h2>Core Tokenomic Mechanisms</h2>"
    html += "<div><h3>Original Dria Model (Based on `docs`)</h3>"
    html += """
    <p>This model simulates Dria's tokenomics as described in the documentation. Key features include:</p>
    <ul>
        <li><strong>Core Principle:</strong> "Trade idle compute directly for inference."</li>
        <li><strong>Token:</strong> $DRIA on Solana.</li>
        <li><strong>Supply:</strong> Capped at 1 billion $DRIA.</li>
        <li><strong>Emission:</strong>
            <ul>
                <li>Linked to verifiable compute (FLOPS) delivered for model inference.</li>
                <li>Distributed from a "Node Runner Rewards Pool" (35% of total supply) over 10 years with a disinflationary schedule.</li>
                <li>New tokens are minted *only* when verified compute is delivered (simulated via utilization of scheduled emissions and direct GFLOP rewards).</li>
            </ul>
        </li>
        <li><strong>Deflationary Mechanisms:</strong>
            <ul>
                <li>USD/Fiat Payments: USD buys $DRIA from the market, which is then burned. Users receive locked credits.</li>
                <li>On-Prem Conversions: $DRIA earned from compute converted to credits may involve a partial burn.</li>
                <li>Oracle Usage: Portion of $DRIA paid for oracle services is burned.</li>
            </ul>
        </li>
        <li><strong>Staking:</strong>
            <ul>
                <li>Node runners stake $DRIA. Earn yield based on active hours/reliability (simulated with target APY driving node growth/churn).</li>
                <li>Slashing for misbehavior (not explicitly detailed in current sim engine beyond stake risk).</li>
            </ul>
        </li>
        <li><strong>Utility:</strong> Payments for inference (locked credits), staking.</li>
        <li><strong>Value Retention:</strong> Payments convert to locked credits.</li>
    </ul>
    </div>"""

    html += "<div><h3>Proposal Model (Based on `proposal.md`)</h3>"
    html += """
    <p>This model simulates the tokenomics suggested in the `proposal.md` document, drawing inspiration from Bittensor and Bitcoin. Key features include:</p>
    <ul>
        <li><strong>Core Principle:</strong> Verifiable contribution (Uptime & FLOPs), staking for security, long-term sustainability with capped supply.</li>
        <li><strong>Supply:</strong> Capped (e.g., 100 million DRIA in parameters).</li>
        <li><strong>Emission:</strong>
            <ul>
                <li>Diminishing schedule with periodic halvings (e.g., every 4 years equivalent in epochs).</li>
                <li>A portion of emissions can go to a community treasury.</li>
            </ul>
        </li>
        <li><strong>Performance-Based Rewards (Contributors):</strong>
            <ul>
                <li>Distributed based on a composite score: P_i = U_i * log(1 + F_i) (Uptime * log(1+FLOPs)).</li>
                <li>Requires minimum uptime.</li>
            </ul>
        </li>
        <li><strong>Staking & Slashing (Validators & potentially Contributors):</strong>
            <ul>
                <li>Validators stake DRIA to secure the network and verify work.</li>
                <li>Contributors might also need to stake.</li>
                <li>Slashing for downtime, malfeasance, or failure to deliver.</li>
            </ul>
        </li>
        <li><strong>Token Utility:</strong>
            <ul>
                <li>Payment for network services (data/compute). These generate fees.</li>
                <li>Staking for participation and security.</li>
                <li>Governance (not yet explicitly simulated in mechanics).</li>
                <li>Transaction fees.</li>
            </ul>
        </li>
        <li><strong>Sustainability:</strong> Transition from emission-based rewards to fee-based rewards as emissions dwindle. A portion of fees can be burned or distributed.</li>
        <li><strong>Treasury:</strong> Funded by a tax on emissions and/or fees.</li>
    </ul>
    </div>"""
    return html

# --- Plotting Functions (Adapted to save files) ---
def format_y_axis_for_plot(ax): 
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if abs(x) >= 1e6 else (f'{x/1e3:.1f}K' if abs(x) >= 1e3 else f'{x:.1f}')))
    ax.grid(True, linestyle='--', alpha=0.7)
    if ax.get_legend_handles_labels()[0]: 
        ax.legend()

def generate_plots_original(df_orig, params_module, filename="original_model_plots.png"): # Added params_module
    """Generates and saves plots for the original simulation model."""
    if df_orig.empty: return None
    df_orig['simulation_month_abs'] = range(1, len(df_orig) + 1)
    
    plt.figure(figsize=(18, 24)) # Adjusted for potentially 11 plots + suptitle
    plt.suptitle("Original Dria Model Simulation Results", fontsize=16)

    plt.subplot(6, 2, 1)
    plt.plot(df_orig['simulation_month_abs'], df_orig['circulating_supply'], label='Circulating Supply (Liquid)')
    plt.title('Circulating Supply Over Time'); format_y_axis_for_plot(plt.gca())

    plt.subplot(6, 2, 2)
    plt.plot(df_orig['simulation_month_abs'], df_orig['total_tokens_burned'], label='Total Tokens Burned', color='red')
    plt.title('Total Tokens Burned Over Time'); format_y_axis_for_plot(plt.gca())

    plt.subplot(6, 2, 3)
    plt.plot(df_orig['simulation_month_abs'], df_orig['simulated_dria_price_usd'], label='Simulated DRIA Price (USD)', color='green')
    plt.title('Simulated DRIA Price (USD)'); plt.gca().grid(True, linestyle='--', alpha=0.7); plt.gca().legend()

    plt.subplot(6, 2, 4)
    plt.plot(df_orig['simulation_month_abs'], df_orig.get('newly_vested_total_monthly',0), label='Vested M')
    plt.plot(df_orig['simulation_month_abs'], df_orig.get('emitted_node_rewards_monthly',0), label='Emitted (Actual) M', linestyle='--')
    plt.plot(df_orig['simulation_month_abs'], df_orig.get('ecosystem_fund_released_monthly',0), label='Eco Released M')
    plt.title('Monthly Token Inflows'); format_y_axis_for_plot(plt.gca())

    plt.subplot(6, 2, 5)
    plt.plot(df_orig['simulation_month_abs'], df_orig.get('burned_from_usd_monthly',0), label='Burned (USD Purchase)')
    plt.plot(df_orig['simulation_month_abs'], df_orig.get('burned_from_onprem_monthly',0), label='Burned (OnPrem Convert)')
    plt.plot(df_orig['simulation_month_abs'], df_orig.get('burned_from_oracle_monthly',0), label='Burned (Oracle Usage)')
    plt.title('Monthly Tokens Burned by Source'); format_y_axis_for_plot(plt.gca())
    
    plt.subplot(6, 2, 6)
    plt.plot(df_orig['simulation_month_abs'], df_orig.get('current_compute_demand_gflops_monthly',0), label='Compute Demand (GFLOPS)', color='blue')
    plt.plot(df_orig['simulation_month_abs'], df_orig.get('current_network_capacity_gflops_monthly',0), label='Network Capacity (GFLOPS)', color='orange', linestyle=':')
    plt.title('Compute Demand vs. Network Capacity'); format_y_axis_for_plot(plt.gca())

    plt.subplot(6, 2, 7)
    plt.plot(df_orig['simulation_month_abs'], df_orig.get('network_utilization_rate', 0) * 100, label='Network Utilization Rate (%)', color='purple')
    plt.title('Network Utilization Rate Over Time'); plt.ylim(0, 110); format_y_axis_for_plot(plt.gca())

    plt.subplot(6, 2, 8)
    plt.plot(df_orig['simulation_month_abs'], df_orig.get('actual_node_apy_monthly_percentage',0), label='Actual Node APY (%)')
    plt.plot(df_orig['simulation_month_abs'], df_orig.get('average_apy_for_decision',0), label=f'Avg APY for Decision MA', color='orange', linestyle=':')
    if hasattr(params_module, 'TARGET_NODE_APY_PERCENTAGE'):
        plt.axhline(y=params_module.TARGET_NODE_APY_PERCENTAGE, color='r', linestyle='--', label=f'Target APY ({params_module.TARGET_NODE_APY_PERCENTAGE}%)')
    plt.title('Actual vs Target Node APY'); format_y_axis_for_plot(plt.gca())

    plt.subplot(6, 2, 9)
    plt.plot(df_orig['simulation_month_abs'], df_orig.get('current_node_count',0), label='Current Node Count', color='teal')
    plt.title('Current Node Count Over Time'); format_y_axis_for_plot(plt.gca())

    plt.subplot(6, 2, 10)
    plt.plot(df_orig['simulation_month_abs'], df_orig.get('total_dria_staked',0), label='Total DRIA Staked', color='brown')
    plt.title('Total DRIA Staked Over Time'); format_y_axis_for_plot(plt.gca())

    plt.subplot(6, 2, 11)
    plt.plot(df_orig['simulation_month_abs'], df_orig.get('current_adjusted_base_staking_yield_annual',0) * 100, label='Adjusted Base Staking Yield Ann. %', color='magenta')
    if hasattr(params_module, 'BASE_STAKING_YIELD_RATE_ANNUAL'):
        plt.axhline(y=params_module.BASE_STAKING_YIELD_RATE_ANNUAL * 100, color='gray', linestyle='--', label=f'Base Yield Static ({params_module.BASE_STAKING_YIELD_RATE_ANNUAL*100:.1f}%)')
    plt.title('Adjusted Base Staking Yield (Annual %)'); format_y_axis_for_plot(plt.gca())
    
    # Placeholder for a 12th plot if needed, or remove one subplot if 11 is the max.
    # For now, let's make sure it fits.

    plt.tight_layout(rect=[0, 0, 1, 0.96]) 
    plt.savefig(filename)
    plt.close() 
    print(f"Saved original model plots to {filename}")
    return filename

def generate_plots_proposal(df_prop, filename="proposal_model_plots.png"):
    """Generates and saves plots for the proposal simulation model."""
    if df_prop.empty: return None
    df_prop['simulation_month_abs'] = range(1, len(df_prop) + 1)

    num_plots_y = 7; num_plots_x = 2 # Allows 14 plots, we use 12
    plt.figure(figsize=(18, num_plots_y * 3.5)) # Adjusted height
    plt.suptitle("Proposal-Based Dria Model Simulation Results", fontsize=16)

    plt.subplot(num_plots_y, num_plots_x, 1)
    plt.plot(df_prop['simulation_month_abs'], df_prop['circulating_supply_proposal'], label='Circulating Supply')
    plt.plot(df_prop['simulation_month_abs'], df_prop['remaining_emission_pool_proposal'], label='Remaining Emission Pool', linestyle=':')
    plt.title('Circulating Supply & Emission Pool'); format_y_axis_for_plot(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 2)
    plt.plot(df_prop['simulation_month_abs'], df_prop['total_tokens_burned_proposal'], label='Total Burned', color='red')
    plt.plot(df_prop['simulation_month_abs'], df_prop['total_tokens_slashed_proposal'], label='Total Slashed', color='orange')
    plt.title('Cumulative Burned & Slashed Tokens'); format_y_axis_for_plot(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 3)
    plt.plot(df_prop['simulation_month_abs'], df_prop['simulated_dria_price_usd_proposal'], label='DRIA Price (USD)', color='green')
    plt.title('Simulated DRIA Price (USD)'); plt.gca().grid(True, linestyle='--', alpha=0.7); plt.gca().legend()
    
    plt.subplot(num_plots_y, num_plots_x, 4)
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('current_epoch_reward_after_halving',0), label='Epoch Reward (Post-Halving)')
    ax_halvings = plt.gca().twinx() # Create a twin Y axis
    ax_halvings.plot(df_prop['simulation_month_abs'], df_prop.get('halvings_occurred',0), label='Halvings', color='purple', linestyle='--')
    ax_halvings.set_ylabel('Number of Halvings'); ax_halvings.legend(loc='upper right')
    plt.title('Epoch Reward and Halvings'); format_y_axis_for_plot(plt.gca())
    
    plt.subplot(num_plots_y, num_plots_x, 5)
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('treasury_balance_proposal',0), label='Treasury Balance', color='cyan')
    plt.title('Treasury Balance'); format_y_axis_for_plot(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 6)
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('newly_vested_total_monthly_proposal',0), label='Vested M')
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('emitted_rewards_monthly_proposal',0), label='Net Emitted (Rewards) M', linestyle='--')
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('ecosystem_fund_released_monthly_proposal',0), label='Eco Fund Released M')
    plt.title('Monthly Token Inflows (Circulating)'); format_y_axis_for_plot(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 7)
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('burned_from_fees_monthly_proposal', 0), label='Burned (Fees) M')
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('burned_from_usd_payments_monthly_proposal', 0), label='Burned (USD Payments) M')
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('slashed_dria_monthly_proposal', 0), label='Slashed M')
    plt.title('Monthly Token Outflows (from Circulating)'); format_y_axis_for_plot(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 8)
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('total_distributed_to_contributors_monthly',0), label='Rewards to Uptime/FLOPs M')
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('validator_staking_rewards_monthly_proposal',0), label='Validator Stake Rewards M', linestyle='-.')
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('fee_rewards_for_validators_monthly_proposal',0), label='Fee Rewards to Validators M', linestyle=':')
    plt.title('Monthly Rewards Distribution'); format_y_axis_for_plot(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 9)
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('current_usd_demand_per_month_proposal',0), label='USD Demand for Services M')
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('current_dria_demand_per_month_proposal',0), label='DRIA Demand for Services M', linestyle='--')
    plt.title('Service Demand Per Month'); format_y_axis_for_plot(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 10)
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('total_dria_staked_proposal',0), label='Total DRIA Staked', color='brown')
    plt.title('Total DRIA Staked'); format_y_axis_for_plot(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 11)
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('current_contributor_nodes',0), label='Contributor Nodes')
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('current_validator_nodes',0), label='Validator Nodes', linestyle='--')
    plt.title('Node Counts'); plt.gca().grid(True, linestyle='--', alpha=0.7); plt.gca().legend()
    
    plt.subplot(num_plots_y, num_plots_x, 12)
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('total_emitted_this_timestep_before_treasury', 0), label='Total Gross Emissions M')
    plt.plot(df_prop['simulation_month_abs'], df_prop.get('total_fees_generated_dria_monthly', 0), label='Total Fees Generated M', linestyle='--')
    plt.title('Gross Emissions vs. Fees Generated Monthly'); format_y_axis_for_plot(plt.gca())
    
    # Two empty plot slots remaining if num_plots_y = 7, num_plots_x = 2

    plt.tight_layout(rect=[0, 0, 1, 0.96]) 
    plt.savefig(filename)
    plt.close() 
    print(f"Saved proposal model plots to {filename}")
    return filename


# --- Main function to generate HTML report ---
def main_combined_report():
    print("Starting Combined Simulation Report Generation...\n")

    # Run simulations
    print("Running Original Dria Model Simulation...")
    df_orig, params_o_module = run_original_simulation() # Capture the module itself
    print("Original Dria Model Simulation COMPLETE.\n")

    print("Running Proposal-Based Dria Model Simulation...")
    df_prop, params_p_module = run_proposal_simulation() # Capture the module itself
    print("Proposal-Based Dria Model Simulation COMPLETE.\n")

    # Generate plot images
    plot_file_orig = None
    if not df_orig.empty:
        plot_file_orig = generate_plots_original(df_orig, params_o_module, "original_model_plots.png") # Pass module
    else:
        print("Original simulation data is empty. Skipping plots.")

    plot_file_prop = None
    if not df_prop.empty:
        plot_file_prop = generate_plots_proposal(df_prop, "proposal_model_plots.png")
    else:
        print("Proposal simulation data is empty. Skipping plots.")

    # Start HTML content
    html_content = """<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dria Tokenomics Simulation Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; background-color: #f4f4f4; color: #333; }
            h1 { text-align: center; color: #2c3e50; margin-bottom: 30px; }
            h2 { color: #2980b9; border-bottom: 2px solid #3498db; padding-bottom: 5px; margin-top: 30px;}
            h3 { color: #16a085; margin-top: 20px;}
            table { border-collapse: collapse; width: 100%; margin-bottom: 20px; font-size: 0.9em; box-shadow: 0 2px 3px rgba(0,0,0,0.1); background-color: white; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
            th { background-color: #3498db; color: white; }
            tr:nth-child(even) { background-color: #ecf0f1; }
            .main-container { max-width: 1200px; margin: auto; background-color: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            .section { margin-bottom: 30px; padding: 15px; border-radius: 5px;}
            .param-section-container { display: flex; flex-direction: row; flex-wrap: wrap; justify-content: space-between; }
            .param-section { flex-basis: 48%; box-sizing: border-box; background-color: #fff; padding:15px; border-radius:5px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); margin-bottom:15px;}
            .plot-section img { max-width: 100%; height: auto; display: block; margin-top: 10px; border: 1px solid #ddd; border-radius: 4px; }
            ul { margin-left: 20px; }
            p { text-align: justify; }
        </style>
    </head>
    <body>
        <div class="main-container">
            <h1>Dria Tokenomics Simulation Comparison Report</h1>
    """

    html_content += "<div class='section'>"
    html_content += get_mechanisms_html()
    html_content += "</div>"
    
    html_content += "<div class='section'><h2>Model Parameters</h2><div class='param-section-container'>" 
    html_content += "<div class='param-section'>"
    html_content += get_params_as_html_table(params_o_module, "Original Model") # Pass module
    html_content += "</div>"
    html_content += "<div class='param-section'>"
    html_content += get_params_as_html_table(params_p_module, "Proposal Model") # Pass module
    html_content += "</div></div></div>" # End param-section-container and section

    html_content += "<div class='section'><h2>Simulation Graphs</h2>"
    if plot_file_orig:
        html_content += f"<div class='plot-section'><h3>Original Model Graphs</h3><img src='{plot_file_orig}' alt='Original Model Plots'></div>"
    if plot_file_prop:
        html_content += f"<div class='plot-section'><h3>Proposal Model Graphs</h3><img src='{plot_file_prop}' alt='Proposal Model Plots'></div>"
    html_content += "</div>" # End section for graphs

    html_content += """
        </div> <!-- end main-container -->
    </body>
    </html>
    """

    report_filename = "dria_simulation_report.html"
    with open(report_filename, "w", encoding="utf-8") as f: # Added encoding
        f.write(html_content)
    
    print(f"\nHTML report generated: {report_filename}")

if __name__ == "__main__":
    main_combined_report() 