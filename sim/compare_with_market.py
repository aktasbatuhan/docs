# sim/compare_with_market.py

import importlib
import numpy as np
import pandas as pd
import itertools
import time
from datetime import datetime, timedelta
import os
import concurrent.futures
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for saving plots
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

# Attempt to import pycoingecko, provide instructions if not found
try:
    from pycoingecko import CoinGeckoAPI
except ImportError:
    print("PyCoinGecko library not found. Please install it: pip install pycoingecko")
    # You might want to exit or use mock data if pycoingecko is essential and not found.
    # For now, we'll let it proceed, and API calls will fail later if it's not installed.
    CoinGeckoAPI = None 

# Import all engines and parameter modules
import model_parameters as p1_module
import simulation_engine as engine1
import model_parameters_proposal as p2_module
import simulation_engine_proposal as engine2
import model_parameters_bme as p3_module
import simulation_engine_bme as engine3

# --- Configuration ---
CG_API_REQUEST_DELAY = 1.5  # Seconds to wait between CoinGecko API calls to avoid rate limiting

GENERAL_TOKEN_IDS = ['bitcoin', 'ethereum', 'binancecoin', 'ripple', 'solana', 'dogecoin', 'cardano', 'avalanche-2', 'tron', 'the-open-network', 'polkadot', 'matic-network', 'chainlink', 'near', 'optimism', 'arbitrum', 'aptos', 'sui', 'blockstack', 'internet-computer']
DEPIN_TOKEN_IDS = ['bittensor', 'render-token', 'akash-network', 'filecoin', 'helium', 'fetch-ai', 'golem', 'storj', 'livepeer', 'ocean-protocol']
MARKET_DATA_DAYS = 5 * 365  # 5 years

# --- Shared Simulation Parameters (can be overridden by sweep) ---
BASE_SHARED_PARAMS = {
    'INITIAL_CIRCULATING_SUPPLY': 1_000_000,
    'INITIAL_NODE_COUNT': 10000, # Default for sweep start
    'INITIAL_DRIA_PRICE_USD': 0.50, # Default for sweep start
    'INITIAL_USD_CREDIT_PURCHASE_PER_MONTH': 100_000,
    'INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH': 200_000,
    'SIMULATION_YEARS': 10,
    # Base growth rates, will be modulated by market trends
    'BASE_USD_DEMAND_GROWTH_RATE_MONTHLY': 0.01, 
    'BASE_DRIA_DEMAND_GROWTH_RATE_MONTHLY': 0.01,
    'MARKET_TREND_IMPACT_FACTOR': 0.5 # How much the market trend influences demand growth (0 to 1+)
}

# --- Parameter Sweep Setup (Robustness/Stress Test) ---
PARAM_SWEEP_CONFIG = {
    'INITIAL_NODE_COUNT': [1000, 5000, 20000],  # Node ecosystem size
    'BASE_USD_DEMAND_GROWTH_RATE_MONTHLY': [0.005, 0.01, 0.02],  # Demand growth
    'INITIAL_DRIA_PRICE_USD': [0.25, 0.5, 1.0],  # Starting price
    'MARKET_TREND_IMPACT_FACTOR': [0.25, 0.5, 0.75],  # Market sensitivity
    'INITIAL_USD_CREDIT_PURCHASE_PER_MONTH': [50000, 100000, 200000],  # Initial USD demand
    'INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH': [100000, 200000, 400000],  # Initial DRIA demand
    'SIMULATION_YEARS': [5, 10],  # Simulation duration
    # Add more as needed for further robustness
}

# --- CoinGecko Data Fetching ---
def fetch_coingecko_historical_data(token_ids, days):
    """Fetches historical daily price data for a list of token IDs from CoinGecko."""
    if CoinGeckoAPI is None:
        print("CoinGeckoAPI not initialized because pycoingecko is not installed.")
        return {}
        
    cg = CoinGeckoAPI()
    token_data = {}
    print(f"Fetching data for {len(token_ids)} tokens for the last {days} days...")
    for token_id in token_ids:
        try:
            print(f"Fetching {token_id}...")
            history = cg.get_coin_market_chart_by_id(id=token_id, vs_currency='usd', days=days)
            if history and 'prices' in history:
                # Convert to DataFrame
                df = pd.DataFrame(history['prices'], columns=['timestamp', 'price'])
                df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.normalize()
                df = df.groupby('date')['price'].mean().reset_index() # Ensure one price per day
                df.set_index('date', inplace=True)
                token_data[token_id] = df['price']
            else:
                print(f"Warning: No price data returned for {token_id}")
            time.sleep(CG_API_REQUEST_DELAY)  # Rate limiting
        except Exception as e:
            print(f"Error fetching data for {token_id}: {e}")
            time.sleep(CG_API_REQUEST_DELAY) # Wait even on error
    print("Finished fetching CoinGecko data.")
    return token_data

# --- Trend Calculation ---
def calculate_trend_index(token_price_data_dict):
    """
    Calculates a normalized trend index from a dictionary of token price series.
    Normalizes each token's price to start at 100 and averages them.
    """
    if not token_price_data_dict:
        return pd.Series(dtype=float)

    # Combine all price series into a single DataFrame, forward-filling missing values
    combined_df = pd.DataFrame(token_price_data_dict)
    combined_df = combined_df.ffill().bfill() # Fill NaNs robustly

    if combined_df.empty:
        return pd.Series(dtype=float)

    # Normalize each token's price series to start at 100
    normalized_df = combined_df.apply(lambda x: (x / x.iloc[0]) * 100 if x.iloc[0] != 0 else x, axis=0)
    
    # Calculate the average normalized price across all tokens for each day
    trend_index = normalized_df.mean(axis=1)
    return trend_index

def resample_daily_trend_to_monthly(daily_trend_series, method='mean'):
    """Resamples a daily trend series to monthly, typically by averaging."""
    if daily_trend_series.empty:
        return pd.Series(dtype=float)
    # Calculate monthly percentage change of the daily trend index
    # The idea is to capture the *change* or *momentum* of the trend month-over-month
    monthly_avg_trend_value = daily_trend_series.resample('M').mean()
    # Calculate month-over-month percentage change of this average value
    monthly_trend_pct_change = monthly_avg_trend_value.pct_change() 
    # The first value will be NaN due to pct_change, fill with 0 (no change from a "previous" non-existent month)
    monthly_trend_pct_change = monthly_trend_pct_change.fillna(0)
    return monthly_trend_pct_change
    
# --- Simulation Logic with Market Influence (Placeholders for now) ---
# We will need to adapt the simulation runners or the engines themselves.
# For now, let's assume the main simulation loop will fetch the monthly trend 
# and adjust parameters like demand growth.

# --- KPI Calculation (Can reuse/adapt from compare_all.py) ---
def calc_metrics_market(df, price_col, node_col, **kwargs):
    metrics = {}
    # Use the exact column names provided
    if price_col not in df.columns:
        print(f"Warning: Price column '{price_col}' not found in DataFrame. Available: {df.columns.tolist()}")
        return metrics
    if node_col not in df.columns:
        print(f"Warning: Node column '{node_col}' not found in DataFrame. Available: {df.columns.tolist()}")
        # Fallback or skip node metrics
    metrics['final_price'] = df[price_col].iloc[-1] if price_col in df.columns else np.nan
    metrics['lowest_price'] = df[price_col].min() if price_col in df.columns else np.nan
    metrics['price_std_dev'] = df[price_col].std() if price_col in df.columns else np.nan
    metrics['final_node_count'] = df[node_col].iloc[-1] if node_col in df.columns else np.nan
    metrics['peak_node_count'] = df[node_col].max() if node_col in df.columns else np.nan
    metrics['avg_node_growth'] = df[node_col].diff().mean() if node_col in df.columns else np.nan
    # Optional metrics based on kwargs mapping to actual DataFrame columns
    for kpi_name, df_col_name in kwargs.items():
        if df_col_name and df_col_name in df.columns:
            if "total_" in kpi_name or "outflows" in kpi_name or "_slashed" in kpi_name:
                metrics[kpi_name] = df[df_col_name].sum()
            elif "avg_" in kpi_name:
                metrics[kpi_name] = df[df_col_name].mean()
            else: # Typically final values like treasury balance
                metrics[kpi_name] = df[df_col_name].iloc[-1]
        else:
            metrics[kpi_name] = np.nan
            if df_col_name:
                print(f"Warning: Optional KPI column '{df_col_name}' for '{kpi_name}' not found.")
    return metrics

def run_single_scenario_param(scenario, scenario_trend, current_params_set, BASE_SHARED_PARAMS):
    # Import modules inside the function for multiprocessing safety
    import model_parameters as p1_module
    import simulation_engine as engine1
    import model_parameters_proposal as p2_module
    import simulation_engine_proposal as engine2
    import model_parameters_bme as p3_module
    import simulation_engine_bme as engine3
    import pandas as pd
    sim_shared_params = BASE_SHARED_PARAMS.copy()
    sim_shared_params.update(current_params_set)
    # --- Sim 1 (Original) ---
    p1_module.USD_CREDIT_PURCHASE_GROWTH_RATE_MONTHLY = sim_shared_params['BASE_USD_DEMAND_GROWTH_RATE_MONTHLY']
    p1_module.INITIAL_USD_CREDIT_PURCHASE_PER_MONTH = sim_shared_params['INITIAL_USD_CREDIT_PURCHASE_PER_MONTH']
    p1_module.INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH = sim_shared_params['INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH']
    p1_module.INITIAL_SIMULATED_DRIA_PRICE_USD = sim_shared_params['INITIAL_DRIA_PRICE_USD']
    initial_state1 = {
        "current_year": 1, "current_month": 0,
        "circulating_supply": sim_shared_params['INITIAL_CIRCULATING_SUPPLY'],
        "total_tokens_burned": 0, "total_dria_staked": 0,
        "current_node_count": sim_shared_params['INITIAL_NODE_COUNT'],
        "simulated_dria_price_usd": sim_shared_params['INITIAL_DRIA_PRICE_USD'],
        "remaining_node_rewards_pool_tokens": p1_module.NODE_RUNNER_REWARDS_POOL_TOTAL,
        "remaining_ecosystem_fund_tokens": p1_module.ECOSYSTEM_FUND_TOKENS_TOTAL,
        "vested_team_tokens": 0, "vested_advisors_tokens": 0,
        "vested_private_round_tokens": 0, "vested_current_round_tokens": 0,
        "current_usd_credit_purchase_per_month": sim_shared_params['INITIAL_USD_CREDIT_PURCHASE_PER_MONTH'],
        "current_dria_earned_by_on_prem_users_per_month": 0, "current_oracle_requests_per_month": 0,
        "current_compute_demand_gflops_monthly": 0, "current_network_capacity_gflops_monthly": 0,
        "newly_staked_dria_monthly": 0, "actual_node_apy_monthly_percentage": 0,
        "node_runner_revenue_monthly_usd": 0, "newly_vested_total_monthly": 0,
        "emitted_node_rewards_monthly": 0, "ecosystem_fund_released_monthly": 0,
        "burned_from_usd_monthly": 0, "burned_from_onprem_monthly": 0, "burned_from_oracle_monthly": 0,
        'apy_history': [], 'average_apy_for_decision': 0,
        'current_adjusted_base_staking_yield_annual': 0, 'network_utilization_rate': 0,
        'current_quarter_ecosystem_release_pool': 0,'current_quarter_ecosystem_released_so_far': 0,
        'market_trend_monthly_pct_change': scenario_trend,
        'base_usd_demand_growth_rate': sim_shared_params['BASE_USD_DEMAND_GROWTH_RATE_MONTHLY'],
        'market_trend_impact_factor': sim_shared_params['MARKET_TREND_IMPACT_FACTOR']
    }
    df1_raw = engine1.run_simulation(initial_state1, sim_shared_params['SIMULATION_YEARS'])
    df1 = pd.DataFrame(df1_raw)
    metrics1 = calc_metrics_market(
        df1,
        price_col='simulated_dria_price_usd',
        node_col='current_node_count',
        total_burned_monthly='total_tokens_burned',
        total_emitted_monthly='emitted_node_rewards_monthly',
        avg_apy='actual_node_apy_monthly_percentage',
        avg_utilization='network_utilization_rate'
    )
    # --- Sim 2 (Proposal) ---
    p2_module.USD_DEMAND_GROWTH_RATE_MONTHLY_PROPOSAL = sim_shared_params['BASE_USD_DEMAND_GROWTH_RATE_MONTHLY']
    p2_module.INITIAL_USD_CREDIT_PURCHASE_PER_MONTH_PROPOSAL = sim_shared_params['INITIAL_USD_CREDIT_PURCHASE_PER_MONTH']
    p2_module.INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH = sim_shared_params['INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH']
    p2_module.INITIAL_SIMULATED_DRIA_PRICE_USD_PROPOSAL = sim_shared_params['INITIAL_DRIA_PRICE_USD']
    initial_state2 = {
        "current_year": 1, "current_month": 0,
        "circulating_supply_proposal": sim_shared_params['INITIAL_CIRCULATING_SUPPLY'],
        "total_tokens_burned_proposal": 0, "total_tokens_slashed_proposal": 0,
        "simulated_dria_price_usd_proposal": sim_shared_params['INITIAL_DRIA_PRICE_USD'],
        "remaining_emission_pool_proposal": p2_module.EMISSION_SUPPLY_POOL_PROPOSAL,
        "remaining_ecosystem_fund_tokens_proposal": p2_module.ECOSYSTEM_FUND_TOKENS_TOTAL_PROPOSAL,
        "treasury_balance_proposal": 0,
        "vested_team_tokens_proposal": 0, "vested_advisors_tokens_proposal": 0, "vested_investors_tokens_proposal": 0,
        "current_usd_demand_per_month_proposal": sim_shared_params['INITIAL_USD_CREDIT_PURCHASE_PER_MONTH'],
        "current_dria_demand_per_month_proposal": sim_shared_params['INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH'],
        "current_contributor_nodes": sim_shared_params['INITIAL_NODE_COUNT'],
        "current_validator_nodes": 50, # Example, could be swept
        "total_dria_staked_proposal": 0,"current_total_epochs_passed": 0, "halvings_occurred": 0,
        "newly_vested_total_monthly_proposal": 0, "ecosystem_fund_released_monthly_proposal": 0,
        "emitted_rewards_monthly_proposal": 0, "total_distributed_to_contributors_monthly": 0,
        "slashed_dria_monthly_proposal": 0, "validator_staking_rewards_monthly_proposal": 0,
        "total_fees_generated_dria_monthly": 0, "burned_from_fees_monthly_proposal": 0,
        "burned_from_usd_payments_monthly_proposal": 0, "current_epoch_reward_after_halving": 0,
        "total_emitted_this_timestep_before_treasury":0, "fee_rewards_for_validators_monthly_proposal":0,
        "total_available_gflops_monthly": 0, "total_utilized_gflops_monthly": 0,
        "demand_supply_ratio_monthly": 0, "reward_scaling_factor_monthly": 0,
        "rewards_to_distribute_after_scaling_monthly": 0, "emissions_to_treasury_monthly_proposal": 0,
        "treasury_outflow_monthly_proposal": 0, "user_churn_event": False, "demand_shock_event": 0,
        "monthly_profit_per_validator_usd": 0, "validator_growth_rate": 0,
        "monthly_profit_per_contributor_usd": 0, "contributor_growth_rate": 0,
        'market_trend_monthly_pct_change': scenario_trend,
        'base_usd_demand_growth_rate': sim_shared_params['BASE_USD_DEMAND_GROWTH_RATE_MONTHLY'],
        'market_trend_impact_factor': sim_shared_params['MARKET_TREND_IMPACT_FACTOR']
    }
    df2_raw = engine2.run_simulation_proposal(initial_state2, p2_module, sim_shared_params['SIMULATION_YEARS'])
    df2 = pd.DataFrame(df2_raw)
    metrics2 = calc_metrics_market(
        df2,
        price_col='simulated_dria_price_usd_proposal',
        node_col='current_contributor_nodes',
        treasury_col='treasury_balance_proposal',
        demand_col='current_usd_demand_per_month_proposal',
        total_burned_monthly='burned_from_usd_payments_monthly_proposal',
        total_emitted_monthly='emitted_rewards_monthly_proposal',
        avg_utilization='demand_supply_ratio_monthly',
        total_slashed='slashed_dria_monthly_proposal',
        treasury_outflows='treasury_outflow_monthly_proposal'
    )
    # --- Sim 3 (BME) ---
    p3_module.USD_DEMAND_GROWTH_RATE_MONTHLY_BME = sim_shared_params['BASE_USD_DEMAND_GROWTH_RATE_MONTHLY']
    p3_module.INITIAL_USD_CREDIT_PURCHASE_PER_MONTH_BME = sim_shared_params['INITIAL_USD_CREDIT_PURCHASE_PER_MONTH']
    p3_module.INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH_BME = sim_shared_params['INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH']
    p3_module.INITIAL_DRIA_PRICE_USD_BME = sim_shared_params['INITIAL_DRIA_PRICE_USD']
    initial_state3 = {
        "current_year": 1, "current_month": 0,
        "circulating_supply": sim_shared_params['INITIAL_CIRCULATING_SUPPLY'],
        "total_tokens_burned": 0, "total_tokens_emitted": 0,
        "dria_price_usd": sim_shared_params['INITIAL_DRIA_PRICE_USD'],
        "node_count": sim_shared_params['INITIAL_NODE_COUNT'],
        "usd_demand_per_month": sim_shared_params['INITIAL_USD_CREDIT_PURCHASE_PER_MONTH'],
        "dria_demand_per_month": sim_shared_params['INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH'],
        "burned_from_usd_monthly": 0, "burned_from_dria_fees_monthly": 0,
        "emitted_rewards_monthly": 0, "monthly_profit_per_node_usd": 0, "node_growth_rate": 0,
        'market_trend_monthly_pct_change': scenario_trend,
        'base_usd_demand_growth_rate': sim_shared_params['BASE_USD_DEMAND_GROWTH_RATE_MONTHLY'],
        'market_trend_impact_factor': sim_shared_params['MARKET_TREND_IMPACT_FACTOR']
    }
    df3_raw = engine3.run_simulation_bme(initial_state3, p3_module, sim_shared_params['SIMULATION_YEARS'])
    df3 = pd.DataFrame(df3_raw)
    metrics3 = calc_metrics_market(
        df3,
        price_col='dria_price_usd',
        node_col='node_count',
        total_burned_monthly='burned_from_usd_monthly',
        total_emitted_monthly='emitted_rewards_monthly'
    )
    return {
        'params_set': current_params_set,
        'market_scenario': scenario['name'],
        'sim1_metrics': metrics1,
        'sim2_metrics': metrics2,
        'sim3_metrics': metrics3,
    }

def trend_modifier_baseline(trend):
    return trend

def trend_modifier_bull(trend):
    return trend * 1.0

def trend_modifier_bear(trend):
    return trend * -1.0

def trend_modifier_highvol(trend):
    return trend * 2.0

def run_batch_with_market_trends(general_trend_monthly, depin_trend_monthly):
    """
    Runs the parameter sweep for multiple market scenarios. Each scenario modifies the market trend series
    (e.g., Baseline, Bull, Bear, HighVol) and stores the scenario name in the results.
    """
    from concurrent.futures import ProcessPoolExecutor, as_completed
    sweep_keys = list(PARAM_SWEEP_CONFIG.keys())
    sweep_values = list(PARAM_SWEEP_CONFIG.values())
    all_results = []
    SCENARIOS = [
        {
            'name': 'Baseline',
            'trend_modifier': trend_modifier_baseline
        },
        {
            'name': 'Bull',
            'trend_modifier': trend_modifier_bull
        },
        {
            'name': 'Bear',
            'trend_modifier': trend_modifier_bear
        },
        {
            'name': 'HighVol',
            'trend_modifier': trend_modifier_highvol
        },
    ]
    jobs = []
    for scenario in SCENARIOS:
        scenario_trend = scenario['trend_modifier'](general_trend_monthly)
        for param_values in itertools.product(*sweep_values):
            current_params_set = dict(zip(sweep_keys, param_values))
            jobs.append((scenario, scenario_trend, current_params_set, BASE_SHARED_PARAMS))
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(run_single_scenario_param, scenario, scenario_trend, current_params_set, BASE_SHARED_PARAMS) for scenario, scenario_trend, current_params_set, BASE_SHARED_PARAMS in jobs]
        for future in as_completed(futures):
            all_results.append(future.result())
    return all_results

# --- Print Results ---
def print_market_results_table(results_list):
    print("\n--- Parameter Sweep with Market Trends Results ---")
    if not results_list:
        print("No results to display.")
        return

    # Create a flat list of dicts for DataFrame conversion
    flat_results = []
    for res_item in results_list:
        row = {}
        row.update(res_item['params_set']) # Add parameters from the sweep
        row['market_scenario'] = res_item['market_scenario']
        
        # Add metrics for each sim, prefixing with sim name
        for sim_name, metrics_dict in [('Sim1', res_item['sim1_metrics']), 
                                       ('Sim2', res_item['sim2_metrics']), 
                                       ('Sim3', res_item['sim3_metrics'])]:
            if metrics_dict: # Check if metrics were actually calculated
                for k, v in metrics_dict.items():
                    row[f'{sim_name}_{k}'] = v
            else: # If no metrics, fill with NaN for consistency
                # Need to know expected metric keys if some sims might fail partially
                # For now, just indicate this sim's metrics are missing for this run
                row[f'{sim_name}_metrics_status'] = "Not Available"


        flat_results.append(row)
    
    results_df = pd.DataFrame(flat_results)
    
    # Reorder columns for better readability: params, scenario, then metrics
    param_cols = list(PARAM_SWEEP_CONFIG.keys())
    scenario_col = ['market_scenario']
    metric_cols = [col for col in results_df.columns if col not in param_cols and col not in scenario_col]
    
    # Sort by params first, then by scenario to group them
    results_df = results_df[param_cols + scenario_col + metric_cols].sort_values(by=param_cols + scenario_col)

    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 2000) # Wide display for many columns
    pd.set_option('display.float_format', '{:.2f}'.format) # Format floats

    print(results_df.to_string(index=False))


# --- Fetch or Load Market Data ---
def fetch_or_load_market_data(token_ids, days, filename):
    yahoo_file = 'yahoo_crypto_prices.csv'
    if os.path.exists(yahoo_file):
        df = pd.read_csv(yahoo_file, index_col=0, parse_dates=True)
        if not df.empty:
            print(f"Loading Yahoo-only market data from {yahoo_file}")
            return df
        else:
            print(f"Yahoo-only file {yahoo_file} is empty. Will attempt to fetch new data.")
    # Fallback: try to fetch or load as before (should not happen in normal use)
    if os.path.exists(filename):
        df = pd.read_csv(filename, index_col=0, parse_dates=True)
        if not df.empty:
            print(f"Loading cached market data from {filename}")
            return df
        else:
            print(f"Cached file {filename} is empty. Will attempt to fetch new data.")
    data = fetch_coingecko_historical_data(token_ids, days)
    df = pd.DataFrame(data)
    if df.empty:
        print(f"Warning: No data fetched for {token_ids}. File {filename} will not be saved.")
        return df
    df.to_csv(filename)
    return df

# --- Advanced Feature Extraction ---
def extract_market_features(price_df):
    """
    Given a DataFrame of token prices (columns: tokens, index: date),
    returns a DataFrame with:
      - trend_index: average normalized price
      - volatility_30d: 30-day rolling std of daily returns
      - volatility_90d: 90-day rolling std of daily returns
      - rolling_avg_30d: 30-day rolling mean of trend_index
      - rolling_avg_90d: 90-day rolling mean of trend_index
      - drawdown: running max drawdown of trend_index
      - regime: bull/bear/sideways label
      - extreme_event: flag for >10% monthly drop/gain
    """
    # Ensure index is a DatetimeIndex
    if not isinstance(price_df.index, pd.DatetimeIndex):
        price_df.index = pd.to_datetime(price_df.index, errors='coerce')
    price_df = price_df[~price_df.index.isna()]  # Drop rows where index couldn't be converted

    features = {}
    # Normalize each token's price to start at 100
    norm = price_df.apply(lambda x: (x / x.iloc[0]) * 100 if x.iloc[0] != 0 else x, axis=0)
    features['trend_index'] = norm.mean(axis=1)
    # Daily returns
    returns = features['trend_index'].pct_change(fill_method=None).fillna(0)
    # Volatility
    features['volatility_30d'] = returns.rolling(30).std()
    features['volatility_90d'] = returns.rolling(90).std()
    # Rolling averages
    features['rolling_avg_30d'] = features['trend_index'].rolling(30).mean()
    features['rolling_avg_90d'] = features['trend_index'].rolling(90).mean()
    # Drawdown
    running_max = features['trend_index'].cummax()
    features['drawdown'] = (features['trend_index'] - running_max) / running_max
    # Regime labeling (bull: >+5% 30d, bear: <-5% 30d, else sideways)
    regime = []
    for i in range(len(features['trend_index'])):
        if i < 30:
            regime.append('sideways')
        else:
            change = (features['trend_index'].iloc[i] - features['trend_index'].iloc[i-30]) / features['trend_index'].iloc[i-30]
            if change > 0.05:
                regime.append('bull')
            elif change < -0.05:
                regime.append('bear')
            else:
                regime.append('sideways')
    features['regime'] = regime
    # Extreme event flag (>10% monthly drop/gain)
    monthly = features['trend_index'].resample('MS').last().pct_change(fill_method=None).fillna(0)
    extreme = monthly.abs() > 0.10
    extreme_event = pd.Series(False, index=features['trend_index'].index)
    for month, is_extreme in extreme.items():
        if is_extreme:
            # Set all days in this month to True
            mask = (features['trend_index'].index.to_period('M') == month)
            extreme_event[mask] = True
    features['extreme_event'] = extreme_event
    # Combine
    features_df = pd.DataFrame(features)
    return features_df

# --- Correlation Calculation ---
def calculate_trend_correlation(df1, df2):
    """Returns rolling 30d and 90d correlation between two trend indices (Series)."""
    corr_30d = df1['trend_index'].rolling(30).corr(df2['trend_index'])
    corr_90d = df1['trend_index'].rolling(90).corr(df2['trend_index'])
    return corr_30d, corr_90d

# --- Plotting Utilities for Scenario Analysis ---
def plot_final_price_distributions(results_df):
    # Histogram
    plt.figure(figsize=(10,6))
    plt.hist(results_df['Sim1_final_price'], bins=30, alpha=0.5, label='Original')
    plt.hist(results_df['Sim2_final_price'], bins=30, alpha=0.5, label='Proposal')
    plt.hist(results_df['Sim3_final_price'], bins=30, alpha=0.5, label='BME')
    plt.xlabel('Final Price')
    plt.ylabel('Frequency')
    plt.title('Distribution of Final Price Across All Scenarios')
    plt.legend()
    plt.grid(True)
    plt.savefig('output/final_price_histogram.png', bbox_inches='tight')
    plt.close()
    # Boxplot
    melted = pd.melt(results_df, value_vars=['Sim1_final_price', 'Sim2_final_price', 'Sim3_final_price'], var_name='Model', value_name='Final Price')
    plt.figure(figsize=(8,6))
    sns.boxplot(x='Model', y='Final Price', data=melted)
    plt.title('Final Price Distribution by Model')
    plt.grid(True)
    plt.savefig('output/final_price_boxplot.png', bbox_inches='tight')
    plt.close()

def plot_robustness_consistency(results_df):
    # Calculate std dev and IQR for each model
    models = ['Sim1_final_price', 'Sim2_final_price', 'Sim3_final_price']
    stats = {}
    for model in models:
        data = results_df[model].dropna()
        stats[model] = {
            'mean': data.mean(),
            'std': data.std(),
            'min': data.min(),
            'max': data.max(),
            'iqr': data.quantile(0.75) - data.quantile(0.25)
        }
    # Bar plot of std dev
    plt.figure(figsize=(8,5))
    plt.bar([m.replace('_final_price','') for m in models], [stats[m]['std'] for m in models], color=['C0','C1','C2'])
    plt.ylabel('Standard Deviation of Final Price')
    plt.title('Robustness: Std Dev of Final Price by Model')
    plt.grid(True, axis='y')
    plt.savefig('output/robustness_stddev.png', bbox_inches='tight')
    plt.close()
    # Bar plot of IQR
    plt.figure(figsize=(8,5))
    plt.bar([m.replace('_final_price','') for m in models], [stats[m]['iqr'] for m in models], color=['C0','C1','C2'])
    plt.ylabel('Interquartile Range (IQR) of Final Price')
    plt.title('Robustness: IQR of Final Price by Model')
    plt.grid(True, axis='y')
    plt.savefig('output/robustness_iqr.png', bbox_inches='tight')
    plt.close()
    # Print and save summary stats
    stats_df = pd.DataFrame(stats).T
    stats_df.to_csv('output/final_price_summary_stats.csv')
    print('\n--- Final Price Summary Stats by Model ---')
    print(stats_df)

def plot_scenario_comparison(results_df):
    # Boxplot: Final price by model and scenario
    melted = pd.melt(
        results_df,
        id_vars=['market_scenario'],
        value_vars=['Sim1_final_price', 'Sim2_final_price', 'Sim3_final_price'],
        var_name='Model', value_name='Final Price'
    )
    plt.figure(figsize=(10,6))
    sns.boxplot(x='market_scenario', y='Final Price', hue='Model', data=melted)
    plt.title('Final Price Distribution by Model and Market Scenario')
    plt.grid(True)
    plt.savefig('output/scenario_comparison_boxplot.png', bbox_inches='tight')
    plt.close()
    # Grouped bar plot: Mean final price by model and scenario
    grouped = melted.groupby(['market_scenario', 'Model'])['Final Price'].mean().unstack()
    grouped.plot(kind='bar', figsize=(10,6))
    plt.ylabel('Mean Final Price')
    plt.title('Mean Final Price by Model and Market Scenario')
    plt.grid(True, axis='y')
    plt.savefig('output/scenario_comparison_barplot.png', bbox_inches='tight')
    plt.close()

def plot_parameter_sensitivity(results_df, param_sweep_config):
    key_params = [k for k in param_sweep_config.keys() if k != 'market_scenario']
    models = ['Sim1_final_price', 'Sim2_final_price', 'Sim3_final_price']
    for param in key_params:
        if param not in results_df.columns:
            continue
        plt.figure(figsize=(10,6))
        for model in models:
            grouped = results_df.groupby(param)[model].mean()
            plt.plot(grouped.index, grouped.values, marker='o', label=model.replace('_final_price',''))
        plt.xlabel(param)
        plt.ylabel('Mean Final Price')
        plt.title(f'Parameter Sensitivity: {param} vs. Final Price')
        plt.legend()
        plt.grid(True)
        plt.savefig(f'output/parameter_sensitivity_{param}.png', bbox_inches='tight')
        plt.close()

def plot_pairwise_scatter(results_df):
    models = [
        ('Sim1_final_price', 'Sim1_avg_apy', 'Original'),
        ('Sim2_final_price', 'Sim2_avg_apy', 'Proposal'),
        ('Sim3_final_price', 'Sim3_avg_apy', 'BME'),
    ]
    for price_col, apy_col, label in models:
        if price_col in results_df.columns and apy_col in results_df.columns:
            plt.figure(figsize=(8,6))
            sns.scatterplot(x=apy_col, y=price_col, hue='market_scenario', data=results_df, alpha=0.7)
            plt.xlabel('Average APY')
            plt.ylabel('Final Price')
            plt.title(f'{label}: Final Price vs. Average APY')
            plt.grid(True)
            plt.savefig(f'output/pairwise_scatter_{label}_apy.png', bbox_inches='tight')
            plt.close()
    models_util = [
        ('Sim1_final_price', 'Sim1_avg_utilization', 'Original'),
        ('Sim2_final_price', 'Sim2_avg_utilization', 'Proposal'),
        ('Sim3_final_price', 'Sim3_avg_utilization', 'BME'),
    ]
    for price_col, util_col, label in models_util:
        if price_col in results_df.columns and util_col in results_df.columns:
            plt.figure(figsize=(8,6))
            sns.scatterplot(x=util_col, y=price_col, hue='market_scenario', data=results_df, alpha=0.7)
            plt.xlabel('Average Utilization')
            plt.ylabel('Final Price')
            plt.title(f'{label}: Final Price vs. Average Utilization')
            plt.grid(True)
            plt.savefig(f'output/pairwise_scatter_{label}_utilization.png', bbox_inches='tight')
            plt.close()

def plot_failure_case_analysis(results_df, price_threshold=0.1, node_threshold=100):
    models = [
        ('Sim1_final_price', 'Sim1_final_node_count', 'Original'),
        ('Sim2_final_price', 'Sim2_final_node_count', 'Proposal'),
        ('Sim3_final_price', 'Sim3_final_node_count', 'BME'),
    ]
    failure_counts = {}
    failure_tables = {}
    for price_col, node_col, label in models:
        fail_price = results_df[price_col] < price_threshold
        fail_node = results_df[node_col] < node_threshold
        failure = fail_price | fail_node
        failure_counts[label] = failure.sum()
        if failure.any():
            fail_table = results_df.loc[failure, ['market_scenario', price_col, node_col] + [c for c in results_df.columns if c in PARAM_SWEEP_CONFIG.keys()]]
            fail_table.to_csv(f'output/failure_cases_{label}.csv', index=False)
            failure_tables[label] = fail_table
    plt.figure(figsize=(7,5))
    plt.bar(list(failure_counts.keys()), list(failure_counts.values()), color=['C0','C1','C2'])
    plt.ylabel('Number of Failure Cases')
    plt.title(f'Frequency of Failure Cases (final price < {price_threshold} or node count < {node_threshold})')
    plt.grid(True, axis='y')
    plt.savefig('output/failure_case_frequency.png', bbox_inches='tight')
    plt.close()

def plot_comparative_bars(results_df, scenario='Baseline', max_sets=10):
    df = results_df[results_df['market_scenario'] == scenario]
    if len(df) > max_sets:
        df = df.sample(max_sets, random_state=42)
    models = ['Sim1_final_price', 'Sim2_final_price', 'Sim3_final_price']
    df_plot = df[models]
    df_plot.index = [f'Set {i+1}' for i in range(len(df_plot))]
    df_plot.plot(kind='bar', figsize=(12,6))
    plt.ylabel('Final Price')
    plt.title(f'Final Price by Model for {scenario} Scenario (Sampled Sets)')
    plt.grid(True, axis='y')
    plt.savefig(f'output/comparative_bar_final_price_{scenario}.png', bbox_inches='tight')
    plt.close()
    models_nodes = ['Sim1_final_node_count', 'Sim2_final_node_count', 'Sim3_final_node_count']
    df_plot_nodes = df[models_nodes]
    df_plot_nodes.index = [f'Set {i+1}' for i in range(len(df_plot_nodes))]
    df_plot_nodes.plot(kind='bar', figsize=(12,6))
    plt.ylabel('Final Node Count')
    plt.title(f'Final Node Count by Model for {scenario} Scenario (Sampled Sets)')
    plt.grid(True, axis='y')
    plt.savefig(f'output/comparative_bar_final_node_count_{scenario}.png', bbox_inches='tight')
    plt.close()
    models_apy = ['Sim1_avg_apy', 'Sim2_avg_apy', 'Sim3_avg_apy']
    if all(col in df.columns for col in models_apy):
        df_plot_apy = df[models_apy]
        df_plot_apy.index = [f'Set {i+1}' for i in range(len(df_plot_apy))]
        df_plot_apy.plot(kind='bar', figsize=(12,6))
        plt.ylabel('Average APY')
        plt.title(f'Average APY by Model for {scenario} Scenario (Sampled Sets)')
        plt.grid(True, axis='y')
        plt.savefig(f'output/comparative_bar_avg_apy_{scenario}.png', bbox_inches='tight')
        plt.close()

def plot_time_series_snapshots(all_run_results, scenario='Baseline'):
    import numpy as np
    models = [
        ('sim1_metrics', 'Sim1', 'sim1_history'),
        ('sim2_metrics', 'Sim2', 'sim2_history'),
        ('sim3_metrics', 'Sim3', 'sim3_history'),
    ]
    for metrics_key, label, history_key in models:
        filtered = [r for r in all_run_results if r['market_scenario'] == scenario and metrics_key in r and r[metrics_key] and history_key in r and r[history_key]]
        if not filtered:
            continue
        final_prices = np.array([r[metrics_key].get('final_price', np.nan) for r in filtered])
        best_idx = np.nanargmax(final_prices)
        worst_idx = np.nanargmin(final_prices)
        median_idx = np.argsort(final_prices)[len(final_prices)//2]
        for idx, desc in zip([best_idx, worst_idx, median_idx], ['Best', 'Worst', 'Median']):
            run = filtered[idx]
            history = run[history_key]
            if not history:
                continue
            df = pd.DataFrame(history)
            plt.figure(figsize=(12,6))
            if f'{label.lower()}_price_usd' in df.columns:
                plt.plot(df[f'{label.lower()}_price_usd'], label='Price')
            elif 'simulated_dria_price_usd' in df.columns:
                plt.plot(df['simulated_dria_price_usd'], label='Price')
            elif 'simulated_dria_price_usd_proposal' in df.columns:
                plt.plot(df['simulated_dria_price_usd_proposal'], label='Price')
            elif 'dria_price_usd' in df.columns:
                plt.plot(df['dria_price_usd'], label='Price')
            if 'current_node_count' in df.columns:
                plt.plot(df['current_node_count'], label='Node Count')
            elif 'current_contributor_nodes' in df.columns:
                plt.plot(df['current_contributor_nodes'], label='Node Count')
            elif 'node_count' in df.columns:
                plt.plot(df['node_count'], label='Node Count')
            if 'actual_node_apy_monthly_percentage' in df.columns:
                plt.plot(df['actual_node_apy_monthly_percentage'], label='APY')
            elif 'avg_apy' in df.columns:
                plt.plot(df['avg_apy'], label='APY')
            elif 'validator_staking_rewards_monthly_proposal' in df.columns:
                plt.plot(df['validator_staking_rewards_monthly_proposal'], label='APY')
            plt.title(f'{label} {desc} Run: Price, Node Count, APY over Time')
            plt.xlabel('Timestep (Month)')
            plt.legend()
            plt.grid(True)
            plt.savefig(f'output/timeseries_{label}_{desc}_{scenario}.png', bbox_inches='tight')
            plt.close()

# --- Main Execution ---
if __name__ == "__main__":
    print("Starting market-aware simulation comparison...")

    # 1. Fetch and process market data (with caching)
    general_price_df = fetch_or_load_market_data(GENERAL_TOKEN_IDS, MARKET_DATA_DAYS, 'general_market_data.csv')
    depin_price_df = fetch_or_load_market_data(DEPIN_TOKEN_IDS, MARKET_DATA_DAYS, 'depin_market_data.csv')

    # 2. Feature extraction
    general_features = extract_market_features(general_price_df)
    depin_features = extract_market_features(depin_price_df)
    # Correlation
    corr_30d, corr_90d = calculate_trend_correlation(general_features, depin_features)
    print(f"General/DePIN 30d rolling correlation (last 5):\n{corr_30d.dropna().tail()}")
    print(f"General/DePIN 90d rolling correlation (last 5):\n{corr_90d.dropna().tail()}")

    # 3. Use trend_index and volatility for simulation as before
    # Ensure DatetimeIndex for resampling before calculating monthly pct change
    if not isinstance(general_features.index, pd.DatetimeIndex):
        general_features.index = pd.to_datetime(general_features.index, errors='coerce')
    if not isinstance(depin_features.index, pd.DatetimeIndex):
        depin_features.index = pd.to_datetime(depin_features.index, errors='coerce')

    general_trend_monthly_pct_change = general_features['trend_index'].resample('MS').mean().pct_change(fill_method=None).fillna(0)
    depin_trend_monthly_pct_change = depin_features['trend_index'].resample('MS').mean().pct_change(fill_method=None).fillna(0)

    # 4. Run simulations with market trends
    # Ensure engines are modified to accept and use market_trend_series from initial_state
    print("\nEnsure your simulation engines (simulation_engine.py, etc.) are updated to:")
    print("1. Accept 'market_trend_monthly_pct_change', 'base_usd_demand_growth_rate', 'market_trend_impact_factor' in initial_state.")
    print("2. In their monthly loop, get the current month's trend value from 'market_trend_monthly_pct_change'.")
    print("3. Modulate the demand growth: new_growth = base_growth * (1 + trend_value_for_month * impact_factor).")
    print("   (Ensure trend_value_for_month is correctly indexed from the series based on simulation month).")

    # Placeholder: Actual run needs engine modifications
    # For now, we'll pass dummy trends if real ones are empty to avoid crashing the batch runner structure.
    num_sim_months = BASE_SHARED_PARAMS['SIMULATION_YEARS'] * 12
    if general_trend_monthly_pct_change.empty:
        print("Using DUMMY general trend for simulation structure.")
        dummy_dates = pd.date_range(start=pd.Timestamp.today().replace(day=1), periods=num_sim_months, freq='MS')
        general_trend_monthly_pct_change = pd.Series(np.zeros(num_sim_months), index=pd.PeriodIndex(dummy_dates, freq='M'))
        general_trend_monthly_pct_change = general_trend_monthly_pct_change.sort_index()

    if depin_trend_monthly_pct_change.empty:
        print("Using DUMMY DePIN trend for simulation structure.")
        dummy_dates = pd.date_range(start=pd.Timestamp.today().replace(day=1), periods=num_sim_months, freq='MS')
        depin_trend_monthly_pct_change = pd.Series(np.zeros(num_sim_months), index=pd.PeriodIndex(dummy_dates, freq='M'))
        depin_trend_monthly_pct_change = depin_trend_monthly_pct_change.sort_index()

    # Check alignment of trends with simulation duration
    if len(general_trend_monthly_pct_change) < num_sim_months:
        print(f"Padding general trend (len {len(general_trend_monthly_pct_change)}) to {num_sim_months} months.")
        
        # Get the last timestamp in the index
        last_ts = general_trend_monthly_pct_change.index[-1]
        # Calculate the start of the next month
        start_next_month = last_ts + pd.offsets.MonthBegin(1)
        # Create a date range for the padding periods
        next_dates = pd.date_range(
            start=start_next_month,
            periods=num_sim_months - len(general_trend_monthly_pct_change), 
            freq='MS' # Use Month Start frequency
        )
        
        padding = pd.Series(np.zeros(len(next_dates)), index=next_dates)
        general_trend_monthly_pct_change = pd.concat([general_trend_monthly_pct_change, padding])

    if len(depin_trend_monthly_pct_change) < num_sim_months:
        print(f"Padding DePIN trend (len {len(depin_trend_monthly_pct_change)}) to {num_sim_months} months.")

        # Get the last timestamp in the index
        last_ts = depin_trend_monthly_pct_change.index[-1]
        # Calculate the start of the next month
        start_next_month = last_ts + pd.offsets.MonthBegin(1)
        # Create a date range for the padding periods
        next_dates = pd.date_range(
            start=start_next_month,
            periods=num_sim_months - len(depin_trend_monthly_pct_change), 
            freq='MS' # Use Month Start frequency
        )
        
        padding = pd.Series(np.zeros(len(next_dates)), index=next_dates)
        depin_trend_monthly_pct_change = pd.concat([depin_trend_monthly_pct_change, padding])

    # Truncate if trends are longer than simulation period
    general_trend_monthly_pct_change = general_trend_monthly_pct_change.iloc[:num_sim_months]
    depin_trend_monthly_pct_change = depin_trend_monthly_pct_change.iloc[:num_sim_months]

    all_run_results = run_batch_with_market_trends(general_trend_monthly_pct_change, depin_trend_monthly_pct_change)
    # 5. Print results
    print_market_results_table(all_run_results)

    print("\nMarket-aware simulation comparison script finished.")
    print("Reminder: Ensure simulation engines are adapted to use the market trend data passed in initial_state.")

    # --- PLOTTING: Step 1 ---
    # Convert all_run_results to DataFrame if not already
    results_df = pd.DataFrame(flat_results) if 'flat_results' in locals() else None
    if results_df is None or results_df.empty:
        # Try to reconstruct from all_run_results
        flat_results = []
        for res_item in all_run_results:
            row = {}
            row.update(res_item['params_set'])
            row['market_scenario'] = res_item['market_scenario']
            for sim_name, metrics_dict in [('Sim1', res_item['sim1_metrics']), ('Sim2', res_item['sim2_metrics']), ('Sim3', res_item['sim3_metrics'])]:
                if metrics_dict:
                    for k, v in metrics_dict.items():
                        row[f'{sim_name}_{k}'] = v
            flat_results.append(row)
        results_df = pd.DataFrame(flat_results)
    if not results_df.empty:
        plot_final_price_distributions(results_df)
        plot_robustness_consistency(results_df)
        plot_scenario_comparison(results_df)
        plot_parameter_sensitivity(results_df, PARAM_SWEEP_CONFIG)
        plot_pairwise_scatter(results_df)
        plot_failure_case_analysis(results_df)
        plot_comparative_bars(results_df, scenario='Baseline', max_sets=10)
        plot_time_series_snapshots(all_run_results, scenario='Baseline')
    # --- Next: Add more plots in sequence ---

    # --- Add more plotting functions here step by step ---
    # def plot_robustness(...):
    # def plot_scenario_comparison(...):
    # def plot_parameter_sensitivity(...):
    # ... 