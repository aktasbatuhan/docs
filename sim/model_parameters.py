# sim/model_parameters.py

# --- Core Token Supply ---
MAX_SUPPLY_DRIA = 1_000_000_000

# --- Initial State ---
# Placeholder: Assume a small initial circulating supply from e.g. a portion of private sales TGE unlock
INITIAL_CIRCULATING_SUPPLY = 1_000_000 # Placeholder - PLEASE VERIFY/ADJUST

# --- Allocations (as percentages of MAX_SUPPLY_DRIA) ---
# From docs/token-supply-distribution.mdx
NODE_RUNNER_REWARDS_POOL_PERCENT = 0.35  # 35%
ECOSYSTEM_FUND_PERCENT = 0.19             # 19%
PRIVATE_ROUND_INVESTORS_PERCENT = 0.16    # 16%
CURRENT_INVESTMENT_ROUND_PERCENT = 0.10   # 10%
TEAM_ADVISORS_PERCENT = 0.20              # 20% (Combined Team & Advisors)

# --- Calculated Total Tokens per Category ---
NODE_RUNNER_REWARDS_POOL_TOTAL = MAX_SUPPLY_DRIA * NODE_RUNNER_REWARDS_POOL_PERCENT
ECOSYSTEM_FUND_TOKENS_TOTAL = MAX_SUPPLY_DRIA * ECOSYSTEM_FUND_PERCENT
# Assuming Team & Advisors are combined as per docs, let's split them for vesting if needed, or keep combined.
# For simplicity, let's assume the TEAM_ADVISORS_PERCENT is for a combined "Team & Advisors" vesting schedule.
# If separate, these would need to be broken down.
# Let's assume: Team 15%, Advisors 5% of the 20% for vesting details, or use a single vesting schedule.
# Sticking to the combined TEAM_ADVISORS_PERCENT from docs for now.
TEAM_ADVISORS_TOKENS_TOTAL = MAX_SUPPLY_DRIA * TEAM_ADVISORS_PERCENT
# Individual breakdown for vesting if needed by simulation_engine.py (which it does)
TEAM_PERCENT = 0.15 # Example if Team is 15% of total
ADVISORS_PERCENT = 0.05 # Example if Advisors is 5% of total
TEAM_TOKENS_TOTAL = MAX_SUPPLY_DRIA * TEAM_PERCENT
ADVISORS_TOKENS_TOTAL = MAX_SUPPLY_DRIA * ADVISORS_PERCENT

PRIVATE_ROUND_INVESTORS_TOKENS_TOTAL = 160_000_000 # Placeholder
CURRENT_INVESTMENT_ROUND_TOKENS_TOTAL = 100_000_000 # Placeholder


# --- Vesting Schedules (in months) ---
# From docs/token-supply-distribution.mdx for Team & Advisors
TEAM_VESTING = {"cliff": 12, "linear_months": 36}
ADVISORS_VESTING = {"cliff": 12, "linear_months": 36} # Assuming same as team based on docs

# Placeholders for investor vesting - these need to be defined based on original model's assumptions
PRIVATE_ROUND_VESTING = {"cliff": 6, "linear_months": 24} # Placeholder
CURRENT_ROUND_VESTING = {"cliff": 6, "linear_months": 30} # Placeholder

# --- Emission Schedule for Node Runner Rewards Pool ---
# From docs/core-economic-engine.mdx (annual percentages of the POOL)
YEARLY_EMISSION_SCHEDULE_PERCENT_OF_POOL = {
    1: 0.14, 2: 0.12, 3: 0.10, 4: 0.08, 5: 0.07,
    6: 0.06, 7: 0.05, 8: 0.04, 9: 0.03, 10: 0.02,
}
# Convert to absolute values per year
YEARLY_EMISSION_SCHEDULE_ABSOLUTE = {
    year: NODE_RUNNER_REWARDS_POOL_TOTAL * percent
    for year, percent in YEARLY_EMISSION_SCHEDULE_PERCENT_OF_POOL.items()
}
# For years beyond 10, the doc mentions "remaining 101.5M tokens (29% of the pool) held for potential future emissions"
# For simplicity in a 10-year simulation, this might not be hit, or could be a flat rate after.
# Let's assume 0 for years > 10 unless specified otherwise.

# Emission Factors (from simulation_engine.py usage) - Placeholders
SCHEDULE_DRIVEN_EMISSION_FACTOR = 0.7 # Placeholder: 70% of monthly budget from schedule, scaled by util
USAGE_DRIVEN_EMISSION_FACTOR = 0.3    # Placeholder: 30% of monthly budget for direct GFLOP payment
EMISSION_RATE_PER_GFLOP_DRIA = 0.0001 # Placeholder: DRIA per GFLOP for usage-driven part

# --- Ecosystem Fund Release ---
# From simulation_engine.py logic, seems like a quarterly release based on annual percentages
# Placeholder values - these need actuals
ECOSYSTEM_FUND_QUARTERLY_RELEASE_SCHEDULE_YEARLY = { # Percentage of REMAINING fund to target for release over the year, split quarterly
    1: 0.10, 2: 0.10, 3: 0.08, 4: 0.08, 5: 0.05,
    6: 0.05, 7: 0.05, 8: 0.05, 9: 0.05, 10: 0.05,
}
DEFAULT_ECOSYSTEM_FUND_QUARTERLY_RELEASE_PERCENT = 0.025 # Fallback: 2.5% of remaining fund per quarter (10% annually)
ECOSYSTEM_FUND_MONTHLY_RELEASE_FRACTION_OF_QUARTERLY = 1/3 # Release 1/3 of quarterly target each month

# --- Staking & Node Economics ---
APY_MOVING_AVERAGE_MONTHS = 3              # Placeholder
TARGET_NODE_APY_PERCENTAGE = 15.0          # Placeholder: Target APY for nodes (e.g., 15%)
NODE_GROWTH_SENSITIVITY_TO_APY = 0.01      # Placeholder: How much 1% APY diff from target affects monthly growth rate (0.01 = 1% growth per 1% APY diff)
MAX_MONTHLY_NODE_GROWTH_RATE = 0.20        # Placeholder: Max 20% node growth per month
MAX_MONTHLY_NODE_DECLINE_RATE = 0.10       # Placeholder: Max 10% node decline per month
MIN_NODES = 50                             # Placeholder
MAX_NODES = 100000                         # Placeholder
GFLOPS_PER_NODE_MONTHLY_BASE = 1000        # Placeholder: Base GFLOPs per node
GFLOPS_PER_NODE_MONTHLY_MAX_SCALING = 3.0  # Placeholder: Max scaling factor for GFLOPs based on demand/price
STAKE_PER_NODE_DRIA = 1000                 # Placeholder: Required stake per node
BASE_STAKING_YIELD_RATE_ANNUAL = 0.05      # Placeholder: Base annual staking yield if not adaptive (e.g., 5%)

# --- Burn Mechanisms ---
ON_PREM_CONVERSION_BURN_RATE = 0.01 # Placeholder: 1% burn on converting earned DRIA to credits
ORACLE_USAGE_BURN_RATE = 0.005      # Placeholder: 0.5% burn from Oracle fees

# --- Demand Drivers ---
INITIAL_SERVICE_DEMAND_GFLOPS_MONTHLY = 50_000_000 # Placeholder
SERVICE_DEMAND_GROWTH_RATE_MONTHLY = 0.02          # Placeholder: 2% monthly growth

# Additional demand/state parameters expected by main_combined.py for initial_state_orig
INITIAL_USD_CREDIT_PURCHASE_PER_MONTH = 50000  # Placeholder for USD demand
DRIA_EARNED_BY_ON_PREM_USERS_PER_MONTH = 100000 # Placeholder for DRIA earned by on-prem users
INITIAL_ORACLE_REQUESTS_PER_MONTH = 1000000    # Placeholder for oracle requests
INITIAL_NETWORK_CAPACITY_GFLOPS_PER_MONTH = INITIAL_SERVICE_DEMAND_GFLOPS_MONTHLY * 2 # Placeholder, e.g. 2x initial demand

# --- Simulation Control ---
SIMULATION_YEARS = 10
SIMULATION_TIMESTEP_MONTHS = 1 # Monthly

# --- Price Simulation ---
INITIAL_SIMULATED_DRIA_PRICE_USD = 0.10 # Placeholder
PRICE_ADJUSTMENT_SENSITIVITY = 0.05     # Placeholder
MIN_SIMULATED_DRIA_PRICE_USD = 0.001    # Placeholder

# --- Additional Parameters Required by simulation_engine.py ---
# Vesting & Allocations
PRIVATE_ROUND_INVESTORS_TOKENS_TOTAL = 160_000_000 # Placeholder
PRIVATE_ROUND_VESTING = {"cliff": 6, "linear_months": 24} # Placeholder
CURRENT_INVESTMENT_ROUND_TOKENS_TOTAL = 100_000_000 # Placeholder
CURRENT_ROUND_VESTING = {"cliff": 6, "linear_months": 30} # Placeholder

# Staking & Node Economics
NODE_ADOPTION_CHURN_SENSITIVITY = 0.01 # Placeholder
MINIMUM_NODE_STAKE_DRIA = 1000 # Placeholder
AVG_GFLOPS_PER_NODE = 1000 # Placeholder

# Burns & Fees
INITIAL_ON_PREM_CREDIT_CONVERSION_RATE = 1.0 # Placeholder (100% conversion)
DRIA_COST_PER_ORACLE_REQUEST = 0.01 # Placeholder

# Demand & Growth
USD_CREDIT_PURCHASE_GROWTH_RATE_MONTHLY = 0.01 # Placeholder
ON_PREM_USER_EARNINGS_GROWTH_RATE_MONTHLY = 0.01 # Placeholder
ORACLE_REQUESTS_GROWTH_RATE_MONTHLY = 0.01 # Placeholder
COMPUTE_DEMAND_GROWTH_RATE_MONTHLY = 0.01 # Placeholder
AVG_NODE_OPERATING_COST_USD_MONTHLY = 50 # Placeholder

# Price Simulation
ADAPTIVE_YIELD_PRICE_THRESHOLD_LOW = 0.05 # Placeholder
BASE_YIELD_BOOST_FACTOR = 1.2 # Placeholder
MAX_ADAPTIVE_BASE_YIELD_ANNUAL = 0.10 # Placeholder
ADAPTIVE_YIELD_PRICE_THRESHOLD_HIGH = 0.5 # Placeholder
BASE_YIELD_REDUCTION_FACTOR = 0.8 # Placeholder
MIN_ADAPTIVE_BASE_YIELD_ANNUAL = 0.01 # Placeholder

print("Original model parameters loaded.")
