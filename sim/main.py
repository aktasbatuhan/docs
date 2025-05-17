import model_parameters as params
import simulation_engine as engine
import pandas as pd
import matplotlib.pyplot as plt

def main():
    """Sets up and runs the tokenomics simulation."""
    initial_state = {
        "current_year": 1,
        "current_month": 0,  # Will be incremented to 1 at the start of the first step
        
        # Core Supply & Price Metrics
        "circulating_supply": params.INITIAL_CIRCULATING_SUPPLY, # Assuming 0 as per user
        "total_tokens_burned": 0,
        "simulated_dria_price_usd": params.INITIAL_SIMULATED_DRIA_PRICE_USD,
        
        # Remaining Token Pools
        "remaining_node_rewards_pool_tokens": params.NODE_RUNNER_REWARDS_POOL_TOTAL,
        "remaining_ecosystem_fund_tokens": params.ECOSYSTEM_FUND_COMMUNITY_TOKENS_TOTAL,
        
        # Cumulative Vested Tokens (all start at 0)
        "vested_team_tokens": 0,
        "vested_advisors_tokens": 0,
        "vested_private_round_tokens": 0,
        "vested_current_round_tokens": 0,
        
        # Current Demand Driver Values (will be updated monthly by growth rates)
        "current_usd_credit_purchase_per_month": params.INITIAL_USD_CREDIT_PURCHASE_PER_MONTH,
        "current_dria_earned_by_on_prem_users_per_month": params.DRIA_EARNED_BY_ON_PREM_USERS_PER_MONTH,
        "current_oracle_requests_per_month": params.INITIAL_ORACLE_REQUESTS_PER_MONTH,

        # Current Compute Metrics (will be updated monthly by growth rates)
        "current_compute_demand_gflops_monthly": params.INITIAL_COMPUTE_DEMAND_GFLOPS_PER_MONTH,
        "current_network_capacity_gflops_monthly": params.INITIAL_NETWORK_CAPACITY_GFLOPS_PER_MONTH,

        # Staking & Node State
        "current_node_count": params.INITIAL_NODE_COUNT,
        "total_dria_staked": params.INITIAL_NODE_COUNT * params.MINIMUM_NODE_STAKE_DRIA,
        "newly_staked_dria_monthly": 0, # Will be updated by handle_staking

        # Node Economics State
        "actual_node_apy_monthly_percentage": 0, # Calculated APY for nodes this month
        "node_runner_revenue_monthly_usd": 0, # Total revenue for nodes in USD this month

        # Monthly Flow Trackers (initialized by engine functions, listed for completeness)
        "newly_vested_total_monthly": 0,
        "emitted_node_rewards_monthly": 0,
        "ecosystem_fund_released_monthly": 0,
        "burned_from_usd_monthly": 0,
        "burned_from_onprem_monthly": 0,
        "burned_from_oracle_monthly": 0,
        'apy_history': [], # For moving average APY calculation
        'average_apy_for_decision': 0, # For logging the APY used in node churn
        'current_adjusted_base_staking_yield_annual': params.BASE_STAKING_YIELD_RATE_ANNUAL # Initial base yield
    }

    print("--- Starting Dria Tokenomics Simulation ---")
    print(f"Initial State: {initial_state}")
    print(f"Simulating for {params.SIMULATION_YEARS} years with monthly timesteps.\n")

    simulation_history = engine.run_simulation(initial_state, params.SIMULATION_YEARS)

    print("--- Simulation Complete ---")
    print("\n--- Simulation History (Selected Metrics) ---")
    header = f"{'Month':<6} | {'Year':<5} | {'Circ. Supply':<15} | {'Total Burned':<15} | {'DRIA Price':<12} | {'Nodes':<10} | {'Total Staked':<15} | {'Staked M':<12} | {'Actual APY%':<12} | {'Vested M':<12} | {'Emitted M':<12} | {'Eco Rel M':<12} | {'Burn USD M':<12} | {'Burn OnP M':<12} | {'Burn Ora M':<12} | {'Util %':<8} | {'Avg APY Decision':<15} | {'Adj Base Yield %':<15}"
    print(header)
    print("-" * len(header))

    for i, state_snapshot in enumerate(simulation_history):
        sim_month_abs = (state_snapshot['current_year'] -1) * 12 + state_snapshot['current_month']
        util_rate_pct = state_snapshot.get('network_utilization_rate', 0) * 100
        actual_apy_pct = state_snapshot.get('actual_node_apy_monthly_percentage', 0)
        print(f"{sim_month_abs:<6} | "
              f"{state_snapshot['current_year']:<5} | "
              f"{state_snapshot['circulating_supply']:<15.2f} | "
              f"{state_snapshot['total_tokens_burned']:<15.2f} | "
              f"{state_snapshot['simulated_dria_price_usd']:<12.4f} | "
              f"{state_snapshot.get('current_node_count', 0):<10.0f} | "
              f"{state_snapshot.get('total_dria_staked', 0):<15.2f} | "
              f"{state_snapshot.get('newly_staked_dria_monthly', 0):<12.2f} | "
              f"{actual_apy_pct:<12.2f} | "
              f"{state_snapshot.get('newly_vested_total_monthly', 0):<12.2f} | "
              f"{state_snapshot.get('emitted_node_rewards_monthly', 0):<12.2f} | "
              f"{state_snapshot.get('ecosystem_fund_released_monthly', 0):<12.2f} | "
              f"{state_snapshot.get('burned_from_usd_monthly', 0):<12.2f} | "
              f"{state_snapshot.get('burned_from_onprem_monthly', 0):<12.2f} | "
              f"{state_snapshot.get('burned_from_oracle_monthly', 0):<12.2f} | "
              f"{util_rate_pct:<8.2f} | "
              f"{state_snapshot.get('average_apy_for_decision', 0):<15.2f} | "
              f"{state_snapshot.get('current_adjusted_base_staking_yield_annual', 0) * 100:<15.2f}"
        )

    print("\nNote: 'M' denotes Monthly values for flows. 'Util %': Network Utilization Rate.")

    # --- Plotting --- 
    df = pd.DataFrame(simulation_history)
    df['simulation_month'] = range(1, len(df) + 1)

    plt.figure(figsize=(18, 24)) # Increased height for 6x2 grid

    plt.subplot(6, 2, 1) # Changed to 6x2 grid
    plt.plot(df['simulation_month'], df['circulating_supply'], label='Circulating Supply (Liquid)')
    plt.xlabel('Month')
    plt.ylabel('Tokens')
    plt.title('Circulating Supply Over Time')
    plt.legend()
    plt.grid(True)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    plt.subplot(6, 2, 2) # Changed to 6x2 grid
    plt.plot(df['simulation_month'], df['total_tokens_burned'], label='Total Tokens Burned', color='red')
    plt.xlabel('Month')
    plt.ylabel('Tokens')
    plt.title('Total Tokens Burned Over Time')
    plt.legend()
    plt.grid(True)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    plt.subplot(6, 2, 3) # Changed to 6x2 grid
    plt.plot(df['simulation_month'], df['simulated_dria_price_usd'], label='Simulated DRIA Price (USD)', color='green')
    plt.xlabel('Month')
    plt.ylabel('Price (USD)')
    plt.title('Simulated DRIA Price Over Time')
    plt.legend()
    plt.grid(True)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    plt.subplot(6, 2, 4) # Changed to 6x2 grid
    plt.plot(df['simulation_month'], df['newly_vested_total_monthly'], label='Vested M')
    plt.plot(df['simulation_month'], df['emitted_node_rewards_monthly'], label='Emitted (Actual) M', linestyle='--')
    # To plot potential emission, we would need to calculate it here or save it in state
    plt.plot(df['simulation_month'], df['ecosystem_fund_released_monthly'], label='Eco Released M')
    plt.xlabel('Month')
    plt.ylabel('Tokens')
    plt.title('Monthly Token Inflows')
    plt.legend()
    plt.grid(True)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    plt.subplot(6, 2, 5) # Changed to 6x2 grid
    plt.plot(df['simulation_month'], df['burned_from_usd_monthly'], label='Burned (USD Purchase)')
    plt.plot(df['simulation_month'], df['burned_from_onprem_monthly'], label='Burned (OnPrem Convert)')
    plt.plot(df['simulation_month'], df['burned_from_oracle_monthly'], label='Burned (Oracle Usage)')
    plt.xlabel('Month')
    plt.ylabel('Tokens')
    plt.title('Monthly Tokens Burned by Source')
    plt.legend()
    plt.grid(True)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
    
    plt.subplot(6, 2, 6) # Changed to 6x2 grid
    plt.plot(df['simulation_month'], df['current_compute_demand_gflops_monthly'], label='Compute Demand (GFLOPS)', color='blue')
    plt.plot(df['simulation_month'], df['current_network_capacity_gflops_monthly'], label='Network Capacity (GFLOPS)', color='orange', linestyle=':')
    plt.xlabel('Month')
    plt.ylabel('GFLOPS per Month')
    plt.title('Compute Demand vs. Network Capacity')
    plt.legend()
    plt.grid(True)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    plt.subplot(6, 2, 7) # Changed to 6x2 grid
    plt.plot(df['simulation_month'], df['network_utilization_rate'] * 100, label='Network Utilization Rate (%)', color='purple')
    plt.xlabel('Month')
    plt.ylabel('Utilization (%)')
    plt.title('Network Utilization Rate Over Time')
    plt.ylim(0, 110) # Set y-limit to 0-110% for clarity
    plt.legend()
    plt.grid(True)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    plt.subplot(6, 2, 8) # Changed to 6x2 grid
    plt.plot(df['simulation_month'], df['actual_node_apy_monthly_percentage'], label=f'Actual Node APY (%)')
    plt.plot(df['simulation_month'], df['average_apy_for_decision'], label=f'Avg APY for Decision ({params.APY_MOVING_AVERAGE_MONTHS}m MA)', color='orange', linestyle=':')
    plt.axhline(y=params.TARGET_NODE_APY_PERCENTAGE, color='r', linestyle='--', label=f'Target APY ({params.TARGET_NODE_APY_PERCENTAGE}%)')
    plt.xlabel('Month')
    plt.ylabel('APY (%)')
    plt.title('Actual vs Target Node APY')
    plt.legend()
    plt.grid(True)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    plt.subplot(6, 2, 9) # Changed to 6x2 grid
    plt.plot(df['simulation_month'], df['current_node_count'], label='Current Node Count', color='teal')
    plt.xlabel('Month')
    plt.ylabel('Number of Nodes')
    plt.title('Current Node Count Over Time')
    plt.legend()
    plt.grid(True)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    plt.subplot(6, 2, 10) # Changed to 6x2 grid
    plt.plot(df['simulation_month'], df['total_dria_staked'], label='Total DRIA Staked', color='brown')
    plt.xlabel('Month')
    plt.ylabel('Tokens')
    plt.title('Total DRIA Staked Over Time')
    plt.legend()
    plt.grid(True)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    plt.subplot(6, 2, 11) # New 11th plot for Adjusted Base Yield
    plt.plot(df['simulation_month'], df['current_adjusted_base_staking_yield_annual'] * 100, label='Adjusted Base Staking Yield Ann. %', color='magenta')
    plt.axhline(y=params.BASE_STAKING_YIELD_RATE_ANNUAL * 100, color='gray', linestyle='--', label=f'Base Yield ({params.BASE_STAKING_YIELD_RATE_ANNUAL*100}% Static)')
    plt.xlabel('Month')
    plt.ylabel('Yield (%)')
    plt.title('Adjusted Base Staking Yield (Annual %)')
    plt.legend()
    plt.grid(True)
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main() 