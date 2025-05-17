# sim/model_parameters.py

# --- Core Token Supply & Emission Parameters ---
MAX_SUPPLY_DRIA = 1_000_000_000

# Allocations (as percentages of MAX_SUPPLY_DRIA)
NODE_RUNNER_REWARDS_POOL_PERCENT = 0.35
ECOSYSTEM_FUND_COMMUNITY_PERCENT = 0.30
PRIVATE_ROUND_INVESTORS_PERCENT = 0.16
CURRENT_INVESTMENT_ROUND_PERCENT = 0.05
TEAM_PERCENT = 0.09
ADVISORS_PERCENT = 0.05

# Calculated Token Amounts
NODE_RUNNER_REWARDS_POOL_TOTAL = MAX_SUPPLY_DRIA * NODE_RUNNER_REWARDS_POOL_PERCENT
TEAM_TOKENS_TOTAL = MAX_SUPPLY_DRIA * TEAM_PERCENT
ADVISORS_TOKENS_TOTAL = MAX_SUPPLY_DRIA * ADVISORS_PERCENT
PRIVATE_ROUND_INVESTORS_TOKENS_TOTAL = MAX_SUPPLY_DRIA * PRIVATE_ROUND_INVESTORS_PERCENT
CURRENT_INVESTMENT_ROUND_TOKENS_TOTAL = MAX_SUPPLY_DRIA * CURRENT_INVESTMENT_ROUND_PERCENT
ECOSYSTEM_FUND_COMMUNITY_TOKENS_TOTAL = MAX_SUPPLY_DRIA * ECOSYSTEM_FUND_COMMUNITY_PERCENT

# Emission Schedule (Annual percentage of the *remaining* rewards pool or a fixed portion of the initial pool based on docs)
# Docs: "10-year disinflationary schedule (14% down to 2% of remaining rewards pool annually)"
# Docs also show absolute token amounts per year. We'll use the absolute amounts as per the table for predictability.
# Annual emission from the Node Runner Rewards Pool (absolute values from docs)
YEARLY_EMISSION_SCHEDULE_ABSOLUTE = {
    1: 49_000_000,  # 14% of 350M
    2: 42_000_000,  # 12% of 350M (This implies % of *initial* pool, not remaining)
    3: 35_000_000,  # 10%
    4: 28_000_000,  # 8%
    5: 24_500_000,  # 7%
    6: 21_000_000,  # 6%
    7: 17_500_000,  # 5%
    8: 14_000_000,  # 4%
    9: 10_500_000,  # 3%
    10: 7_000_000, # 2%
}
# The docs table has a "Remaining 101,500,000" after year 10 for the 350M pool.
# Let's clarify if this remainder is also subject to a schedule or held indefinitely.
# For now, sum of above is 248.5M. The pool is 350M.

# Vesting Schedules (in months)
TEAM_VESTING = {"cliff": 12, "linear_months": 36}
ADVISORS_VESTING = {"cliff": 12, "linear_months": 24}
# TODO: Add vesting for Private Round Investors (16%) and Current Investment Round (5%)
PRIVATE_ROUND_VESTING = {"cliff": 6, "linear_months": 36} # Updated: Added 6-month cliff
CURRENT_ROUND_VESTING = {"cliff": 6, "linear_months": 36} # Updated: Added 6-month cliff

# Ecosystem Fund & Community Release
ECOSYSTEM_FUND_QUARTERLY_RELEASE_SCHEDULE_YEARLY = {
    1: 0.001, # Updated: 0.1% of remaining fund released quarterly in Year 1 (was 0.01)
    2: 0.005, # Updated: 0.5% of remaining fund released quarterly in Year 2 (was 0.02)
    # Years not specified will use the default rate
}
DEFAULT_ECOSYSTEM_FUND_QUARTERLY_RELEASE_PERCENT = 0.05 # Default: 5% of remaining fund released quarterly
ECOSYSTEM_FUND_MONTHLY_RELEASE_FRACTION_OF_QUARTERLY = 1/3 # Release 1/3 of the calculated quarterly amount each month

# --- Burn Mechanism Parameters ---
# Placeholder - these need precise definitions or to be functions of market conditions
USD_TO_CREDIT_FX_FEE = 0.015 # Example: 1.5% (docs say ~1-2%)
# Burn for USD-to-Credit: Is it 100% of the DRIA bought after FX fee?
ON_PREM_CONVERSION_BURN_RATE = 0.02 # Example: 2% (docs say ~1-3%)
ORACLE_USAGE_BURN_RATE = 0.0075    # Example: 0.75% (docs say ~0.5-1%)

# --- Staking Parameters ---
MINIMUM_NODE_STAKE_DRIA = 100 # Example from docs (e.g., 100)
# TODO: Define Staking Yield Rate (or make it dynamic based on network conditions)
BASE_STAKING_YIELD_RATE_ANNUAL = 0.10 # Example: 10% APY as a baseline

# --- Node Ecosystem Parameters ---
INITIAL_NODE_COUNT = 35_000 # Reverted from 10_000, was 35_000
# TODO: Define node categories, counts per category, and avg FLOPS per category
NODE_CATEGORIES = {
    "cat_A_1.5B": {"count": 0, "avg_flops": 0}, # Placeholder
    "cat_B_3B":   {"count": 0, "avg_flops": 0}, # Placeholder
    "cat_C_12B":  {"count": 0, "avg_flops": 0}, # Placeholder
    "cat_D_70B":  {"count": 0, "avg_flops": 0}, # Placeholder
}
# TODO: Define Node Operating Costs (can be complex, maybe start with averages)
AVG_NODE_OPERATING_COST_USD_MONTHLY = 50 # Highly variable placeholder

# --- Demand-Side Driver Assumptions (Initial Baselines - will be varied in scenarios) ---
INITIAL_USD_CREDIT_PURCHASE_PER_MONTH = 100_000 # Example: $100k USD worth of credits bought monthly
INITIAL_DRIA_CREDIT_PURCHASE_PER_MONTH = 500_000 # Example: 500k DRIA used for credits monthly
INITIAL_ON_PREM_COMPUTE_GFLOPS_PER_MONTH = 1_000_000 # Example
INITIAL_ON_PREM_CREDIT_CONVERSION_RATE = 0.5 # 50% of earned DRIA converted
INITIAL_ORACLE_REQUESTS_PER_MONTH = 10_000 # Example

# --- V1 Burn Mechanism Specific Parameters (Simplifications) ---
INITIAL_SIMULATED_DRIA_PRICE_USD = 0.431 # Placeholder: Initial $DRIA price in USD for simulation. Was 0.43
DRIA_EARNED_BY_ON_PREM_USERS_PER_MONTH = 200_000 # Placeholder: Total DRIA earned by on-prem users monthly
DRIA_COST_PER_ORACLE_REQUEST = 0.5 # Placeholder: Cost in DRIA per oracle request

# --- V1 Demand Driver Growth Rates (Monthly) ---
USD_CREDIT_PURCHASE_GROWTH_RATE_MONTHLY = 0.01  # Placeholder: 1% monthly growth
ON_PREM_USER_EARNINGS_GROWTH_RATE_MONTHLY = 0.005 # Placeholder: 0.5% monthly growth
ORACLE_REQUESTS_GROWTH_RATE_MONTHLY = 0.01 # Placeholder: 1% monthly growth

# --- V1 Compute-Linked Emission Parameters ---
SCHEDULE_DRIVEN_EMISSION_FACTOR = 0.5 # Portion of monthly budget via schedule * utilization
USAGE_DRIVEN_EMISSION_FACTOR = 0.5    # Portion of monthly budget capping direct GFLOP rewards
EMISSION_RATE_PER_GFLOP_DRIA = 0.0001 # Placeholder: DRIA per GFLOP for usage-driven part
INITIAL_COMPUTE_DEMAND_GFLOPS_PER_MONTH = 1_000_000 # Placeholder: e.g., 500k GFLOPS/month. Increased from 500_000 to match capacity
COMPUTE_DEMAND_GROWTH_RATE_MONTHLY = 0.015 # Placeholder: 1.5% monthly growth
INITIAL_NETWORK_CAPACITY_GFLOPS_PER_MONTH = 1_000_000 # Placeholder: e.g. 1M GFLOPS/month total capacity
# NETWORK_CAPACITY_GROWTH_RATE_MONTHLY = 0.005 # Placeholder: 0.5% monthly growth for network capacity (simplification for now) -> To be replaced by dynamic node capacity

# --- V1 Staking & Node Participation Parameters ---
# NODE_COUNT_GROWTH_RATE_MONTHLY = 0.01 # Placeholder: 1% monthly growth in active nodes -> To be replaced by dynamic node growth
# MINIMUM_NODE_STAKE_DRIA is already defined under Staking Parameters
# INITIAL_NODE_COUNT is already defined under Node Ecosystem Parameters

# --- V1 Node Economics Parameters ---
APY_MOVING_AVERAGE_MONTHS = 3 # Number of months to average APY for node decisions
# AVG_NODE_OPERATING_COST_USD_MONTHLY is already defined under Node Ecosystem Parameters (e.g., 50 USD)
TARGET_NODE_APY_PERCENTAGE = 15.0 # Placeholder: Target APY for node runners (e.g., 15%)
NODE_ADOPTION_CHURN_SENSITIVITY = 0.002 # Placeholder: e.g., 1% APY diff results in 0.2% node count change factor
AVG_GFLOPS_PER_NODE = INITIAL_NETWORK_CAPACITY_GFLOPS_PER_MONTH / INITIAL_NODE_COUNT if INITIAL_NODE_COUNT > 0 else 0 # Calculate based on initial values, assuming homogeneity for V1

# Adaptive Base Yield Parameters
ADAPTIVE_YIELD_PRICE_THRESHOLD_LOW = 0.20  # If price below this, boost base yield
ADAPTIVE_YIELD_PRICE_THRESHOLD_HIGH = 0.60 # If price above this, reduce base yield
BASE_YIELD_BOOST_FACTOR = 1.5              # Factor to multiply base yield by if price is low
BASE_YIELD_REDUCTION_FACTOR = 0.8          # Factor to multiply base yield by if price is high
MIN_ADAPTIVE_BASE_YIELD_ANNUAL = 0.05      # Minimum 5% APY for adaptive base yield
MAX_ADAPTIVE_BASE_YIELD_ANNUAL = 0.15      # Maximum 15% APY for adaptive base yield

# --- V1 Dynamic Price Parameters ---
PRICE_ADJUSTMENT_SENSITIVITY = 0.01 # Placeholder: How much price reacts to S/D imbalance. Was 0.05
MIN_SIMULATED_DRIA_PRICE_USD = 0.001 # Placeholder: Floor for the simulated price

# --- Simulation Control ---
SIMULATION_YEARS = 10
SIMULATION_TIMESTEP_MONTHS = 1 # Simulate month by month

# --- Derived Parameters (Placeholders, to be calculated in main or engine) ---
INITIAL_CIRCULATING_SUPPLY = 0 # This needs to be carefully calculated based on who gets tokens at TGE (e.g., Binance Launchpool if applicable from IO example, initial part of private sales, etc.)

print("Model parameters loaded.") 