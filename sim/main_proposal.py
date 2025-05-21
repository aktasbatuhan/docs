# sim/main_proposal.py

import model_parameters_proposal as p # Using 'p' as alias for parameters module
import simulation_engine_proposal as engine
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def main_proposal():
    """Sets up and runs the proposal-based tokenomics simulation."""
    initial_state_proposal = {
        "current_year": 1,
        "current_month": 0,  # Will be incremented to 1 at the start of the first step
        
        "circulating_supply_proposal": p.PROPOSAL_INITIAL_CIRCULATING_SUPPLY,
        "total_tokens_burned_proposal": 0,
        "total_tokens_slashed_proposal": 0,
        "simulated_dria_price_usd_proposal": p.INITIAL_SIMULATED_DRIA_PRICE_USD_PROPOSAL,
        
        "remaining_emission_pool_proposal": p.EMISSION_SUPPLY_POOL_PROPOSAL,
        "remaining_ecosystem_fund_tokens_proposal": p.ECOSYSTEM_FUND_TOKENS_TOTAL_PROPOSAL,
        "treasury_balance_proposal": 0,
        
        "vested_team_tokens_proposal": 0,
        "vested_advisors_tokens_proposal": 0,
        "vested_investors_tokens_proposal": 0,
        
        "current_usd_demand_per_month_proposal": p.INITIAL_USD_CREDIT_PURCHASE_PER_MONTH_PROPOSAL,
        "current_dria_demand_per_month_proposal": p.INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH,

        "current_contributor_nodes": p.PROPOSAL_INITIAL_CONTRIBUTOR_NODES,
        "current_validator_nodes": p.PROPOSAL_INITIAL_VALIDATOR_NODES,
        "total_dria_staked_proposal": 0, # Initialized in run_simulation based on node counts and min stake
        
        "current_total_epochs_passed": 0,
        "halvings_occurred": 0,
        
        # Monthly trackers (initialized or updated by engine functions)
        "newly_vested_total_monthly_proposal": 0,
        "ecosystem_fund_released_monthly_proposal": 0,
        "emitted_rewards_monthly_proposal": 0,
        "total_distributed_to_contributors_monthly": 0,
        "slashed_dria_monthly_proposal": 0,
        "validator_staking_rewards_monthly_proposal": 0,
        "total_fees_generated_dria_monthly": 0,
        "burned_from_fees_monthly_proposal": 0,
        "burned_from_usd_payments_monthly_proposal": 0,
        "current_epoch_reward_after_halving": 0,
        "total_emitted_this_timestep_before_treasury":0,
        "fee_rewards_for_validators_monthly_proposal":0,

        # New keys for demand scaling and detailed emission tracking
        "total_available_gflops_monthly": 0,
        "total_utilized_gflops_monthly": 0,
        "demand_supply_ratio_monthly": 0,
        "reward_scaling_factor_monthly": 0,
        "rewards_to_distribute_after_scaling_monthly": 0,
        "emissions_to_treasury_monthly_proposal": 0,
    }

    print("--- Starting Dria Tokenomics Simulation (Proposal Model) ---\n")
    # print(f"Initial Parameters: {vars(p)}") # Can be verbose
    print(f"Initial State: {initial_state_proposal}\n")
    print(f"Simulating for {p.SIMULATION_YEARS} years with monthly timesteps.\n")

    simulation_history = engine.run_simulation_proposal(initial_state_proposal, p, p.SIMULATION_YEARS)

    print("--- Proposal Simulation Complete ---\n")
    print(f"Total simulation steps (months): {len(simulation_history)}\n")

    if not simulation_history:
        print("No simulation history recorded. Exiting.")
        return

    print("\n--- Proposal Simulation History (Selected Metrics) ---\n")
    header_cols = [
        'Month', 'Year', 'Circ. Supply', 'Tot. Burned', 'Tot. Slashed', 'DRIA Price',
        'Epoch Reward', 'Halvings', 'Treasury Bal', 'Remain Emission', 'Vested M', 'Emitted M', 'Eco Rel M',
        'Fees Gen M', 'Burn Fee M', 'Burn USD M', 'Slash M', 'Distrib Contr M', 'Val Stake Rew M'
    ]
    header = " | ".join([f'{col:<13}' for col in header_cols])
    print(header)
    print("-" * len(header))

    for i, state_snapshot in enumerate(simulation_history):
        sim_month_abs = (state_snapshot['current_year'] -1) * 12 + state_snapshot['current_month']
        row_data = [
            f"{sim_month_abs:<13}",
            f"{state_snapshot['current_year']:<13}",
            f"{state_snapshot['circulating_supply_proposal']:<13.2f}",
            f"{state_snapshot['total_tokens_burned_proposal']:<13.2f}",
            f"{state_snapshot['total_tokens_slashed_proposal']:<13.2f}",
            f"{state_snapshot['simulated_dria_price_usd_proposal']:<13.4f}",
            f"{state_snapshot.get('current_epoch_reward_after_halving', 0):<13.2f}",
            f"{state_snapshot.get('halvings_occurred', 0):<13}",
            f"{state_snapshot['treasury_balance_proposal']:<13.2f}",
            f"{state_snapshot['remaining_emission_pool_proposal']:<13.2f}",
            f"{state_snapshot.get('newly_vested_total_monthly_proposal', 0):<13.2f}",
            f"{state_snapshot.get('emitted_rewards_monthly_proposal', 0):<13.2f}",
            f"{state_snapshot.get('ecosystem_fund_released_monthly_proposal', 0):<13.2f}",
            f"{state_snapshot.get('total_fees_generated_dria_monthly', 0):<13.2f}",
            f"{state_snapshot.get('burned_from_fees_monthly_proposal', 0):<13.2f}",
            f"{state_snapshot.get('burned_from_usd_payments_monthly_proposal', 0):<13.2f}",
            f"{state_snapshot.get('slashed_dria_monthly_proposal', 0):<13.2f}",
            f"{state_snapshot.get('total_distributed_to_contributors_monthly', 0):<13.2f}",
            f"{state_snapshot.get('validator_staking_rewards_monthly_proposal',0):<13.2f}"
        ]
        print(" | ".join(row_data))
        
    print("\nNote: 'M' denotes Monthly values for flows.")

    # --- Plotting --- 
    df = pd.DataFrame(simulation_history)
    if df.empty:
        print ("DataFrame is empty, skipping plots.")
        return
        
    df['simulation_month_abs'] = range(1, len(df) + 1)

    num_plots_y = 7
    num_plots_x = 2
    plt.figure(figsize=(18, num_plots_y * 4))

    def format_y_axis(ax):
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else (f'{x/1e3:.1f}K' if x >= 1e3 else f'{x:.1f}')))
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()

    plt.subplot(num_plots_y, num_plots_x, 1)
    plt.plot(df['simulation_month_abs'], df['circulating_supply_proposal'], label='Circulating Supply')
    plt.plot(df['simulation_month_abs'], df['remaining_emission_pool_proposal'], label='Remaining Emission Pool', linestyle=':')
    plt.title('Circulating Supply & Emission Pool')
    format_y_axis(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 2)
    plt.plot(df['simulation_month_abs'], df['total_tokens_burned_proposal'], label='Total Burned', color='red')
    plt.plot(df['simulation_month_abs'], df['total_tokens_slashed_proposal'], label='Total Slashed', color='orange')
    plt.title('Cumulative Burned & Slashed Tokens')
    format_y_axis(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 3)
    plt.plot(df['simulation_month_abs'], df['simulated_dria_price_usd_proposal'], label='DRIA Price (USD)', color='green')
    plt.title('Simulated DRIA Price (USD)')
    plt.gca().grid(True, linestyle='--', alpha=0.7); plt.gca().legend() # No scientific notation for price usually
    
    plt.subplot(num_plots_y, num_plots_x, 4)
    plt.plot(df['simulation_month_abs'], df['current_epoch_reward_after_halving'], label='Epoch Reward (Post-Halving)')
    ax_halvings = plt.gca().twinx()
    ax_halvings.plot(df['simulation_month_abs'], df['halvings_occurred'], label='Halvings', color='purple', linestyle='--')
    ax_halvings.set_ylabel('Number of Halvings')
    ax_halvings.legend(loc='upper right')
    plt.title('Epoch Reward and Halvings')
    format_y_axis(plt.gca())
    
    plt.subplot(num_plots_y, num_plots_x, 5)
    plt.plot(df['simulation_month_abs'], df['treasury_balance_proposal'], label='Treasury Balance', color='cyan')
    plt.title('Treasury Balance')
    format_y_axis(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 6)
    plt.plot(df['simulation_month_abs'], df['newly_vested_total_monthly_proposal'], label='Vested M')
    plt.plot(df['simulation_month_abs'], df['emitted_rewards_monthly_proposal'], label='Net Emitted (Rewards) M', linestyle='--')
    plt.plot(df['simulation_month_abs'], df['ecosystem_fund_released_monthly_proposal'], label='Eco Fund Released M')
    plt.title('Monthly Token Inflows (Circulating)')
    format_y_axis(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 7)
    plt.plot(df['simulation_month_abs'], df.get('burned_from_fees_monthly_proposal', 0), label='Burned (Fees) M')
    plt.plot(df['simulation_month_abs'], df.get('burned_from_usd_payments_monthly_proposal', 0), label='Burned (USD Payments) M')
    plt.plot(df['simulation_month_abs'], df.get('slashed_dria_monthly_proposal', 0), label='Slashed M')
    plt.title('Monthly Token Outflows (from Circulating)')
    format_y_axis(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 8)
    plt.plot(df['simulation_month_abs'], df['total_distributed_to_contributors_monthly'], label='Rewards to Uptime/FLOPs M')
    plt.plot(df['simulation_month_abs'], df.get('validator_staking_rewards_monthly_proposal',0), label='Validator Stake Rewards M', linestyle='-.')
    plt.plot(df['simulation_month_abs'], df.get('fee_rewards_for_validators_monthly_proposal',0), label='Fee Rewards to Validators M', linestyle=':')
    plt.title('Monthly Rewards Distribution')
    format_y_axis(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 9)
    plt.plot(df['simulation_month_abs'], df['current_usd_demand_per_month_proposal'], label='USD Demand for Services M')
    plt.plot(df['simulation_month_abs'], df['current_dria_demand_per_month_proposal'], label='DRIA Demand for Services M', linestyle='--')
    plt.title('Service Demand Per Month')
    format_y_axis(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 10)
    plt.plot(df['simulation_month_abs'], df['total_dria_staked_proposal'], label='Total DRIA Staked', color='brown')
    plt.title('Total DRIA Staked')
    format_y_axis(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 11)
    plt.plot(df['simulation_month_abs'], df['current_contributor_nodes'], label='Contributor Nodes')
    plt.plot(df['simulation_month_abs'], df['current_validator_nodes'], label='Validator Nodes', linestyle='--')
    plt.title('Node Counts')
    plt.gca().grid(True, linestyle='--', alpha=0.7); plt.gca().legend()
    
    # Add total emissions vs fees plot
    plt.subplot(num_plots_y, num_plots_x, 12)
    plt.plot(df['simulation_month_abs'], df.get('total_emitted_this_timestep_before_treasury', 0), label='Total Gross Emissions M')
    plt.plot(df['simulation_month_abs'], df.get('total_fees_generated_dria_monthly', 0), label='Total Fees Generated M', linestyle='--')
    plt.title('Gross Emissions vs. Fees Generated Monthly')
    format_y_axis(plt.gca())

    plt.tight_layout(pad=3.0)
    plt.show()

if __name__ == "__main__":
    main_proposal() 