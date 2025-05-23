# sim/compare_all.py

import importlib
import numpy as np
import pandas as pd
import itertools

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

# --- Parameter Sweep Setup ---
PARAM_SWEEP = {
    'INITIAL_NODE_COUNT': [1000, 10000, 30000],
    'USD_DEMAND_GROWTH_RATE_MONTHLY': [0.005, 0.01, 0.02],
    'INITIAL_DRIA_PRICE_USD': [0.25, 0.5, 1.0],
}

# --- Extended Metrics ---
def calc_metrics(df, price_col, node_col, treasury_col=None, demand_col=None, burn_col=None, emit_col=None, apy_col=None, util_col=None, slashed_col=None, outflow_col=None):
    metrics = {}
    metrics['final_price'] = df[price_col].iloc[-1]
    metrics['lowest_price'] = df[price_col].min()
    metrics['price_stability'] = df[price_col].std()
    metrics['final_node_count'] = df[node_col].iloc[-1]
    metrics['peak_node_count'] = df[node_col].max()
    metrics['avg_node_growth'] = df[node_col].diff().mean()
    if treasury_col and treasury_col in df.columns:
        metrics['final_treasury'] = df[treasury_col].iloc[-1]
    if demand_col and demand_col in df.columns:
        metrics['final_demand'] = df[demand_col].iloc[-1]
    if burn_col and burn_col in df.columns:
        metrics['total_burned'] = df[burn_col].sum()
    if emit_col and emit_col in df.columns:
        metrics['total_emitted'] = df[emit_col].sum()
    if apy_col and apy_col in df.columns:
        metrics['avg_apy'] = df[apy_col].mean()
    if util_col and util_col in df.columns:
        metrics['avg_utilization'] = df[util_col].mean()
    if slashed_col and slashed_col in df.columns:
        metrics['total_slashed'] = df[slashed_col].sum()
    if outflow_col and outflow_col in df.columns:
        metrics['treasury_outflows'] = df[outflow_col].sum()
    return metrics

# --- Batch Runner ---
def run_batch():
    sweep_keys = list(PARAM_SWEEP.keys())
    sweep_values = list(PARAM_SWEEP.values())
    results = []
    for values in itertools.product(*sweep_values):
        # Set up parameter set
        param_set = dict(zip(sweep_keys, values))
        # Update shared params
        shared = SHARED_PARAMS.copy()
        shared.update(param_set)
        # --- Sim 1 ---
        initial_state1 = {
            "current_year": 1,
            "current_month": 0,
            "circulating_supply": shared['INITIAL_CIRCULATING_SUPPLY'],
            "total_tokens_burned": 0,
            "total_dria_staked": 0,
            "current_node_count": shared['INITIAL_NODE_COUNT'],
            "simulated_dria_price_usd": shared['INITIAL_DRIA_PRICE_USD'],
            "remaining_node_rewards_pool_tokens": p1.NODE_RUNNER_REWARDS_POOL_TOTAL,
            "remaining_ecosystem_fund_tokens": p1.ECOSYSTEM_FUND_TOKENS_TOTAL,
            "vested_team_tokens": 0,
            "vested_advisors_tokens": 0,
            "vested_private_round_tokens": 0,
            "vested_current_round_tokens": 0,
            "current_usd_credit_purchase_per_month": shared['INITIAL_USD_CREDIT_PURCHASE_PER_MONTH'],
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
        # Patch growth rates
        p1.USD_CREDIT_PURCHASE_GROWTH_RATE_MONTHLY = shared['USD_DEMAND_GROWTH_RATE_MONTHLY']
        p1.INITIAL_SIMULATED_DRIA_PRICE_USD = shared['INITIAL_DRIA_PRICE_USD']
        df1 = pd.DataFrame(engine1.run_simulation(initial_state1, shared['SIMULATION_YEARS']))
        metrics1 = calc_metrics(df1, 'simulated_dria_price_usd', 'current_node_count', burn_col='burned_from_usd_monthly', emit_col='emitted_node_rewards_monthly', apy_col='actual_node_apy_monthly_percentage', util_col='network_utilization_rate')
        # --- Sim 2 ---
        initial_state2 = {
            "current_year": 1,
            "current_month": 0,
            "circulating_supply_proposal": shared['INITIAL_CIRCULATING_SUPPLY'],
            "total_tokens_burned_proposal": 0,
            "total_tokens_slashed_proposal": 0,
            "simulated_dria_price_usd_proposal": shared['INITIAL_DRIA_PRICE_USD'],
            "remaining_emission_pool_proposal": p2.EMISSION_SUPPLY_POOL_PROPOSAL,
            "remaining_ecosystem_fund_tokens_proposal": p2.ECOSYSTEM_FUND_TOKENS_TOTAL_PROPOSAL,
            "treasury_balance_proposal": 0,
            "vested_team_tokens_proposal": 0,
            "vested_advisors_tokens_proposal": 0,
            "vested_investors_tokens_proposal": 0,
            "current_usd_demand_per_month_proposal": shared['INITIAL_USD_CREDIT_PURCHASE_PER_MONTH'],
            "current_dria_demand_per_month_proposal": shared['INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH'],
            "current_contributor_nodes": shared['INITIAL_NODE_COUNT'],
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
        p2.USD_DEMAND_GROWTH_RATE_MONTHLY_PROPOSAL = shared['USD_DEMAND_GROWTH_RATE_MONTHLY']
        p2.INITIAL_SIMULATED_DRIA_PRICE_USD_PROPOSAL = shared['INITIAL_DRIA_PRICE_USD']
        df2 = pd.DataFrame(engine2.run_simulation_proposal(initial_state2, p2, shared['SIMULATION_YEARS']))
        metrics2 = calc_metrics(
            df2, 'simulated_dria_price_usd_proposal', 'current_contributor_nodes', treasury_col='treasury_balance_proposal', demand_col='current_usd_demand_per_month_proposal', burn_col='burned_from_usd_payments_monthly_proposal', emit_col='emitted_rewards_monthly_proposal', apy_col=None, util_col='demand_supply_ratio_monthly', slashed_col='slashed_dria_monthly_proposal', outflow_col='treasury_outflow_monthly_proposal')
        # --- Sim 3 ---
        initial_state3 = {
            "current_year": 1,
            "current_month": 0,
            "circulating_supply": shared['INITIAL_CIRCULATING_SUPPLY'],
            "total_tokens_burned": 0,
            "total_tokens_emitted": 0,
            "dria_price_usd": shared['INITIAL_DRIA_PRICE_USD'],
            "node_count": shared['INITIAL_NODE_COUNT'],
            "usd_demand_per_month": shared['INITIAL_USD_CREDIT_PURCHASE_PER_MONTH'],
            "dria_demand_per_month": shared['INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH'],
            "burned_from_usd_monthly": 0,
            "burned_from_dria_fees_monthly": 0,
            "emitted_rewards_monthly": 0,
            "monthly_profit_per_node_usd": 0,
            "node_growth_rate": 0,
        }
        p3.USD_DEMAND_GROWTH_RATE_MONTHLY_BME = shared['USD_DEMAND_GROWTH_RATE_MONTHLY']
        p3.INITIAL_DRIA_PRICE_USD_BME = shared['INITIAL_DRIA_PRICE_USD']
        df3 = pd.DataFrame(engine3.run_simulation_bme(initial_state3, p3, shared['SIMULATION_YEARS']))
        metrics3 = calc_metrics(df3, 'dria_price_usd', 'node_count', burn_col='burned_from_usd_monthly', emit_col='emitted_rewards_monthly', apy_col=None, util_col=None)
        # Store results
        results.append({
            'params': param_set,
            'sim1': metrics1,
            'sim2': metrics2,
            'sim3': metrics3,
        })
    return results

# --- Print Results Table ---
def print_results_table(results):
    print("\nParameter Sweep Results (Final Values and Key Metrics):")
    for res in results:
        print("\nParams:", res['params'])
        print(f"{'Metric':<20} {'Sim 1':<15} {'Sim 2':<15} {'Sim 3':<15}")
        print("-"*65)
        all_keys = set(res['sim1'].keys()) | set(res['sim2'].keys()) | set(res['sim3'].keys())
        for key in sorted(all_keys):
            v1 = res['sim1'].get(key, '-')
            v2 = res['sim2'].get(key, '-')
            v3 = res['sim3'].get(key, '-')
            print(f"{key:<20} {v1:<15} {v2:<15} {v3:<15}")

if __name__ == "__main__":
    results = run_batch()
    print_results_table(results) 