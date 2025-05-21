# sim/model_parameters_proposal.py

# --- Core Token Supply & Emission Parameters (Proposal Based) ---
PROPOSAL_MAX_SUPPLY_DRIA = 100_000_000 # Example from proposal, adjustable

# --- Allocations & Vesting (Still relevant for pre-mined/locked tokens outside of ongoing emissions) ---
TEAM_PERCENT_PROPOSAL = 0.15 # Example: 15% for team
ADVISORS_PERCENT_PROPOSAL = 0.05 # Example: 5% for advisors
INVESTORS_PERCENT_PROPOSAL = 0.20 # Example: 20% for investors (combining rounds)
ECOSYSTEM_FUND_PERCENT_PROPOSAL = 0.10 # Example: 10% for ecosystem, potentially funded also by treasury tax

TEAM_TOKENS_TOTAL_PROPOSAL = PROPOSAL_MAX_SUPPLY_DRIA * TEAM_PERCENT_PROPOSAL
ADVISORS_TOKENS_TOTAL_PROPOSAL = PROPOSAL_MAX_SUPPLY_DRIA * ADVISORS_PERCENT_PROPOSAL
INVESTORS_TOKENS_TOTAL_PROPOSAL = PROPOSAL_MAX_SUPPLY_DRIA * INVESTORS_PERCENT_PROPOSAL
ECOSYSTEM_FUND_TOKENS_TOTAL_PROPOSAL = PROPOSAL_MAX_SUPPLY_DRIA * ECOSYSTEM_FUND_PERCENT_PROPOSAL

# Amount of PROPOSAL_MAX_SUPPLY_DRIA available for emission via halving schedule
EMISSION_SUPPLY_POOL_PROPOSAL = PROPOSAL_MAX_SUPPLY_DRIA - (TEAM_TOKENS_TOTAL_PROPOSAL + ADVISORS_TOKENS_TOTAL_PROPOSAL + INVESTORS_TOKENS_TOTAL_PROPOSAL + ECOSYSTEM_FUND_TOKENS_TOTAL_PROPOSAL)

# --- New Emission Schedule Parameters ---
PROPOSAL_HALVING_PERIOD_MONTHS = 4 * 12 # 4 years in months

# Calculate the initial monthly emission rate.
# The sum of emissions over infinite halving periods is 2 * (tokens_in_first_period).
# So, tokens_in_first_period = EMISSION_SUPPLY_POOL_PROPOSAL / 2.
TOKENS_IN_FIRST_HALVING_PERIOD = EMISSION_SUPPLY_POOL_PROPOSAL / 2
PROPOSAL_INITIAL_MONTHLY_EMISSION = TOKENS_IN_FIRST_HALVING_PERIOD / PROPOSAL_HALVING_PERIOD_MONTHS if PROPOSAL_HALVING_PERIOD_MONTHS > 0 else 0

# --- Emission Buffer and Demand Scaling ---
# Buffer to add to monthly emissions to ensure tokens are not depleted too quickly due to rounding or minor fluctuations
# This buffer will be a small percentage of the monthly emission.
EMISSION_BUFFER_PERCENT = 0.01 # 1% buffer

# Demand scaling factor for rewards.
# If demand_supply_ratio is low, rewards are reduced.
# demand_supply_ratio = utilized_gflops / total_available_gflops
# reward_scaling_factor = min(1, demand_supply_ratio / TARGET_UTILIZATION_FOR_FULL_REWARDS)
# Example: If TARGET_UTILIZATION_FOR_FULL_REWARDS is 0.8, and actual utilization is 0.4,
# then reward_scaling_factor = 0.4 / 0.8 = 0.5, so only 50% of potential emissions are distributed.
TARGET_UTILIZATION_FOR_FULL_REWARDS = 0.8 # Target utilization (e.g. 80%) to distribute full rewards

# --- REMOVED/REPLACED PARAMETERS ---
# PROPOSAL_INITIAL_EPOCH_REWARD (replaced by PROPOSAL_INITIAL_MONTHLY_EMISSION)
# PROPOSAL_HALVING_INTERVAL_EPOCHS (replaced by PROPOSAL_HALVING_PERIOD_MONTHS)
# PROPOSAL_EPOCHS_PER_MONTH (concept no longer used for emission calculation)
# PROPOSAL_TOTAL_SIMULATION_EPOCHS (concept no longer used)
# PROPOSAL_EPOCHS_PER_TIMESTEP (concept no longer used for emission calculation)
# PROPOSAL_HALVING_INTERVAL_MONTHS_APPROX (now directly PROPOSAL_HALVING_PERIOD_MONTHS)

# Vesting Schedules (in months) - Can reuse structure
TEAM_VESTING_PROPOSAL = {"cliff": 12, "linear_months": 36}
ADVISORS_VESTING_PROPOSAL = {"cliff": 12, "linear_months": 24}
INVESTORS_VESTING_PROPOSAL = {"cliff": 6, "linear_months": 30} # Example

# Ecosystem Fund Release (Can be simpler or tied to governance in proposal)
ECOSYSTEM_FUND_MONTHLY_RELEASE_PROPOSAL = ECOSYSTEM_FUND_TOKENS_TOTAL_PROPOSAL / (10*12) # Example: 10 year linear

# --- Performance-Based Reward Parameters (Proposal) ---
PROPOSAL_UPTIME_THRESHOLD_FOR_FULL_REWARDS = 0.95 # 95% uptime for full eligibility multiplier

# --- Staking & Slashing Parameters (Proposal) ---
PROPOSAL_MIN_VALIDATOR_STAKE_DRIA = 5000 # Example min stake for a validator
PROPOSAL_MIN_CONTRIBUTOR_STAKE_DRIA = 100 # Example min stake for a FLOPs/Uptime contributor (if required)
PROPOSAL_SLASHING_PERCENTAGE_VALIDATOR_DOWNTIME = 0.005 # Small slash for validator downtime
PROPOSAL_SLASHING_PERCENTAGE_VALIDATOR_MALFEASANCE = 0.05 # Major slash for cheating
PROPOSAL_SLASHING_PERCENTAGE_CONTRIBUTOR_FAILURE = 0.01 # Slash for consistently failing to provide promised Uptime/FLOPs

# --- Token Utility & Fees (Proposal) ---
PROPOSAL_AVG_TX_FEE_DRIA = 0.01 # Average transaction fee in DRIA
PROPOSAL_SERVICE_FEE_PERCENT_OF_VALUE = 0.01 # 1% of service value converted to DRIA fees
USD_TO_DRIA_BURN_ACTIVE_PROPOSAL = True # Set to False to disable
USD_TO_CREDIT_FX_FEE_PROPOSAL = 0.015

# --- Treasury (Proposal) ---
PROPOSAL_TREASURY_TAX_RATE_FROM_EMISSIONS = 0.05 # 5% of new emissions go to treasury
PROPOSAL_TREASURY_TAX_RATE_FROM_FEES = 0.10 # 10% of service/tx fees go to treasury

# --- Node Ecosystem Parameters (Proposal) ---
PROPOSAL_INITIAL_CONTRIBUTOR_NODES = 30000  # Starting with current 30K+ nodes
PROPOSAL_INITIAL_VALIDATOR_NODES = 50
PROPOSAL_AVG_UPTIME_PER_CONTRIBUTOR = 0.98 # Initial average
PROPOSAL_AVG_GFLOPS_PER_CONTRIBUTOR_MONTHLY = 5000 # Initial average GFLOPs per month for a contributor node

# Node Growth Parameters
NODE_GROWTH_SENSITIVITY = 0.1  # How quickly nodes join/leave based on profitability
MIN_MONTHLY_PROFIT_USD_FOR_GROWTH = 100  # Minimum monthly profit in USD to attract new nodes
MAX_MONTHLY_NODE_GROWTH_RATE = 0.2  # Maximum 20% monthly growth rate
MAX_MONTHLY_NODE_DECLINE_RATE = 0.1  # Maximum 10% monthly decline rate
NODE_COUNT_ADJUSTMENT_LAG_MONTHS = 3  # Nodes take time to join/leave based on profitability

AVG_NODE_OPERATING_COST_USD_MONTHLY = 50  # Average monthly cost to run a node

# --- Demand-Side Driver Assumptions (Can be adapted from original params) ---
INITIAL_USD_CREDIT_PURCHASE_PER_MONTH_PROPOSAL = 100_000 # Users paying USD for Dria services
INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH = 200_000 # Users paying DRIA directly for services
USD_DEMAND_GROWTH_RATE_MONTHLY_PROPOSAL = 0.01
DRIA_DEMAND_GROWTH_RATE_MONTHLY_PROPOSAL = 0.01

# --- Simulation Control (Can reuse from original params) ---
SIMULATION_YEARS = 10
SIMULATION_TIMESTEP_MONTHS = 1 # Simulate month by month
PROPOSAL_TOTAL_TIMESTEPS = SIMULATION_YEARS * 12
# PROPOSAL_EPOCHS_PER_TIMESTEP is removed, ensure GFLOPs calculation for rewards is monthly.

# --- Price Simulation (Can reuse or adapt) ---
INITIAL_SIMULATED_DRIA_PRICE_USD_PROPOSAL = 0.50 # Initial price for proposal model
PRICE_ADJUSTMENT_SENSITIVITY_PROPOSAL = 0.01
MIN_SIMULATED_DRIA_PRICE_USD_PROPOSAL = 0.001

# --- Initial State Values ---
# Initial circulating supply will be sum of any immediately unlocked portions of pre-allocations
# e.g., if a small % of investor/ecosystem tokens are liquid at TGE. For simplicity, start low.
PROPOSAL_INITIAL_CIRCULATING_SUPPLY = 1_000_000 # Example

print("Proposal model parameters loaded.")
# --- Parameters from original model_parameters.py that might be useful or need careful consideration for removal/adaptation ---
# MAX_SUPPLY_DRIA (replaced by PROPOSAL_MAX_SUPPLY_DRIA)
# NODE_RUNNER_REWARDS_POOL_PERCENT, YEARLY_EMISSION_SCHEDULE_ABSOLUTE (replaced by halving mechanism)
# ON_PREM_CONVERSION_BURN_RATE, ORACLE_USAGE_BURN_RATE (replaced by simpler fee model, or can be added back if desired)
# BASE_STAKING_YIELD_RATE_ANNUAL (staking yield in proposal might come from emission share or fees, not a fixed base rate)
# EMISSION_RATE_PER_GFLOP_DRIA (replaced by composite score P_i)
# ADAPTIVE_YIELD_PRICE_THRESHOLD_LOW etc. (adaptive yield logic can be ported if desired for validator rewards)

# --- Treasury Outflows (Ecosystem Funding) ---
TREASURY_OUTFLOW_RATE_MONTHLY = 0.02  # 2% of treasury spent per month on grants/governance

# --- Validator/Contributor Churn Parameters ---
VALIDATOR_GROWTH_SENSITIVITY = 0.05  # How quickly validators join/leave based on APY
VALIDATOR_MIN_MONTHLY_PROFIT_USD_FOR_GROWTH = 200  # Minimum monthly profit in USD to attract new validators
VALIDATOR_MAX_MONTHLY_GROWTH_RATE = 0.1  # Max 10% monthly growth
VALIDATOR_MAX_MONTHLY_DECLINE_RATE = 0.05  # Max 5% monthly decline
VALIDATOR_COUNT_ADJUSTMENT_LAG_MONTHS = 6  # Validators are slower to join/leave
VALIDATOR_OPERATING_COST_USD_MONTHLY = 100  # Higher cost for validators

# --- Fee Distribution ---
VALIDATOR_FEE_SHARE = 0.3  # 30% of service/tx fees go to validators
# (Treasury and burn shares remain as previously set)

# --- User Churn and Demand Shocks ---
USER_CHURN_PROBABILITY = 0.05  # 5% chance per month of user churn event
USER_CHURN_MAGNITUDE = 0.1     # 10% drop in demand if churn event occurs
DEMAND_SHOCK_PROBABILITY = 0.03 # 3% chance per month of demand shock
DEMAND_SHOCK_MAGNITUDE = 0.2    # 20% up or down (random) if shock occurs 