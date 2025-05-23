# sim/compare_all.py

import importlib
import numpy as np
import pandas as pd

# Import all engines and parameter modules
import model_parameters as p1
import simulation_engine as engine1
import model_parameters_proposal as p2
import simulation_engine_proposal as engine2
import model_parameters_bme as p3
import simulation_engine_bme as engine3

# --- Shared Parameters ---
SHARED_PARAMS = {
    'INITIAL_CIRCULATING_SUPPLY': 1_000_000,
    'INITIAL_NODE_COUNT': 30000,
    'INITIAL_DRIA_PRICE_USD': 0.50,
    'INITIAL_USD_CREDIT_PURCHASE_PER_MONTH': 100_000,
    'INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH': 200_000,
    'USD_DEMAND_GROWTH_RATE_MONTHLY': 0.01,
    'DRIA_DEMAND_GROWTH_RATE_MONTHLY': 0.01,
    'SIMULATION_YEARS': 10,
}

# --- Sim 1 ---
def run_sim1():
    initial_state = {
        "current_year": 1,
        "current_month": 0,
        "circulating_supply": SHARED_PARAMS['INITIAL_CIRCULATING_SUPPLY'],
        "total_tokens_burned": 0,
        "total_dria_staked": 0,
        "current_node_count": SHARED_PARAMS['INITIAL_NODE_COUNT'],
        "simulated_dria_price_usd": SHARED_PARAMS['INITIAL_DRIA_PRICE_USD'],
        "remaining_node_rewards_pool_tokens": p1.NODE_RUNNER_REWARDS_POOL_TOTAL,
        "remaining_ecosystem_fund_tokens": p1.ECOSYSTEM_FUND_TOKENS_TOTAL,
        "vested_team_tokens": 0,
        "vested_advisors_tokens": 0,
        "vested_private_round_tokens": 0,
        "vested_current_round_tokens": 0,
        "current_usd_credit_purchase_per_month": SHARED_PARAMS['INITIAL_USD_CREDIT_PURCHASE_PER_MONTH'],
        "current_dria_earned_by_on_prem_users_per_month": 0,
        "current_oracle_requests_per_month": 0,
        "current_compute_demand_gflops_monthly": 0,
        "current_network_capacity_gflops_monthly": 0,
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
        'current_adjusted_base_staking_yield_annual': 0,
        'network_utilization_rate': 0,
        'current_quarter_ecosystem_release_pool': 0,
        'current_quarter_ecosystem_released_so_far': 0,
    }
    history = engine1.run_simulation(initial_state, SHARED_PARAMS['SIMULATION_YEARS'])
    return pd.DataFrame(history)

# --- Sim 2 ---
def run_sim2():
    initial_state = {
        "current_year": 1,
        "current_month": 0,
        "circulating_supply_proposal": SHARED_PARAMS['INITIAL_CIRCULATING_SUPPLY'],
        "total_tokens_burned_proposal": 0,
        "total_tokens_slashed_proposal": 0,
        "simulated_dria_price_usd_proposal": SHARED_PARAMS['INITIAL_DRIA_PRICE_USD'],
        "remaining_emission_pool_proposal": p2.EMISSION_SUPPLY_POOL_PROPOSAL,
        "remaining_ecosystem_fund_tokens_proposal": p2.ECOSYSTEM_FUND_TOKENS_TOTAL_PROPOSAL,
        "treasury_balance_proposal": 0,
        "vested_team_tokens_proposal": 0,
        "vested_advisors_tokens_proposal": 0,
        "vested_investors_tokens_proposal": 0,
        "current_usd_demand_per_month_proposal": SHARED_PARAMS['INITIAL_USD_CREDIT_PURCHASE_PER_MONTH'],
        "current_dria_demand_per_month_proposal": SHARED_PARAMS['INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH'],
        "current_contributor_nodes": SHARED_PARAMS['INITIAL_NODE_COUNT'],
        "current_validator_nodes": 50,
        "total_dria_staked_proposal": 0,
        "current_total_epochs_passed": 0,
        "halvings_occurred": 0,
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
        "total_available_gflops_monthly": 0,
        "total_utilized_gflops_monthly": 0,
        "demand_supply_ratio_monthly": 0,
        "reward_scaling_factor_monthly": 0,
        "rewards_to_distribute_after_scaling_monthly": 0,
        "emissions_to_treasury_monthly_proposal": 0,
        "treasury_outflow_monthly_proposal": 0,
        "user_churn_event": False,
        "demand_shock_event": 0,
        "monthly_profit_per_validator_usd": 0,
        "validator_growth_rate": 0,
        "monthly_profit_per_contributor_usd": 0,
        "contributor_growth_rate": 0,
    }
    history = engine2.run_simulation_proposal(initial_state, p2, SHARED_PARAMS['SIMULATION_YEARS'])
    return pd.DataFrame(history)

# --- Sim 3 ---
def run_sim3():
    initial_state = {
        "current_year": 1,
        "current_month": 0,
        "circulating_supply": SHARED_PARAMS['INITIAL_CIRCULATING_SUPPLY'],
        "total_tokens_burned": 0,
        "total_tokens_emitted": 0,
        "dria_price_usd": SHARED_PARAMS['INITIAL_DRIA_PRICE_USD'],
        "node_count": SHARED_PARAMS['INITIAL_NODE_COUNT'],
        "usd_demand_per_month": SHARED_PARAMS['INITIAL_USD_CREDIT_PURCHASE_PER_MONTH'],
        "dria_demand_per_month": SHARED_PARAMS['INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH'],
        "burned_from_usd_monthly": 0,
        "burned_from_dria_fees_monthly": 0,
        "emitted_rewards_monthly": 0,
        "monthly_profit_per_node_usd": 0,
        "node_growth_rate": 0,
    }
    history = engine3.run_simulation_bme(initial_state, p3, SHARED_PARAMS['SIMULATION_YEARS'])
    return pd.DataFrame(history)

# --- Metric Calculation ---
def calc_metrics(df, price_col, node_col, treasury_col=None, demand_col=None):
    metrics = {}
    metrics['final_price'] = df[price_col].iloc[-1]
    metrics['price_stability'] = df[price_col].std()
    metrics['final_node_count'] = df[node_col].iloc[-1]
    metrics['avg_node_growth'] = df[node_col].diff().mean()
    if treasury_col and treasury_col in df.columns:
        metrics['final_treasury'] = df[treasury_col].iloc[-1]
    if demand_col and demand_col in df.columns:
        metrics['final_demand'] = df[demand_col].iloc[-1]
    return metrics

# --- Run All Sims ---
df1 = run_sim1()
df2 = run_sim2()
df3 = run_sim3()

metrics1 = calc_metrics(df1, 'simulated_dria_price_usd', 'current_node_count')
metrics2 = calc_metrics(df2, 'simulated_dria_price_usd_proposal', 'current_contributor_nodes', treasury_col='treasury_balance_proposal', demand_col='current_usd_demand_per_month_proposal')
metrics3 = calc_metrics(df3, 'dria_price_usd', 'node_count')

# --- Print Comparison Table ---
print("\nComparison Table (Final Values and Key Metrics):")
print(f"{'Metric':<20} {'Sim 1':<15} {'Sim 2':<15} {'Sim 3':<15}")
print("-"*65)
for key in sorted(set(metrics1.keys()) | set(metrics2.keys()) | set(metrics3.keys())):
    v1 = metrics1.get(key, '-')
    v2 = metrics2.get(key, '-')
    v3 = metrics3.get(key, '-')
    print(f"{key:<20} {v1:<15} {v2:<15} {v3:<15}") 