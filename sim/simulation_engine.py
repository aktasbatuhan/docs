# sim/simulation_engine.py

import model_parameters as params

def calculate_monthly_unlock(total_tokens, cliff_months, linear_vesting_months, current_simulation_month, vested_to_date):
    """Calculates tokens unlocked for a single category in the current month."""
    if linear_vesting_months == 0: # Avoid division by zero if vesting is immediate or not applicable
        if current_simulation_month > cliff_months and vested_to_date == 0: # Immediate unlock after cliff
             # Ensure only total_tokens are unlocked if cliff is 0 and linear_vesting_months is 0 (e.g. fully vested at TGE)
            return total_tokens 
        return 0

    monthly_unlock_amount = total_tokens / linear_vesting_months
    
    tokens_unlocked_this_month = 0
    if current_simulation_month > cliff_months and current_simulation_month <= (cliff_months + linear_vesting_months):
        # Check if we are about to vest more than the total
        if vested_to_date + monthly_unlock_amount > total_tokens:
            tokens_unlocked_this_month = total_tokens - vested_to_date # Vest the remainder
        else:
            tokens_unlocked_this_month = monthly_unlock_amount
            
    return tokens_unlocked_this_month

def handle_vesting(state, p):
    """Handles token vesting for all categories for the current month."""
    current_sim_month = (state["current_year"] -1) * 12 + state["current_month"]
    
    newly_vested_total = 0
    state['newly_vested_total_monthly'] = 0 # Initialize for the month

    # Team Vesting
    team_unlocked_this_month = calculate_monthly_unlock(
        p.TEAM_TOKENS_TOTAL, 
        p.TEAM_VESTING["cliff"], 
        p.TEAM_VESTING["linear_months"], 
        current_sim_month,
        state["vested_team_tokens"]
    )
    state["vested_team_tokens"] += team_unlocked_this_month
    newly_vested_total += team_unlocked_this_month

    # Advisors Vesting
    advisors_unlocked_this_month = calculate_monthly_unlock(
        p.ADVISORS_TOKENS_TOTAL,
        p.ADVISORS_VESTING["cliff"],
        p.ADVISORS_VESTING["linear_months"],
        current_sim_month,
        state["vested_advisors_tokens"]
    )
    state["vested_advisors_tokens"] += advisors_unlocked_this_month
    newly_vested_total += advisors_unlocked_this_month

    # Private Round Investors Vesting
    private_investors_unlocked_this_month = calculate_monthly_unlock(
        p.PRIVATE_ROUND_INVESTORS_TOKENS_TOTAL,
        p.PRIVATE_ROUND_VESTING["cliff"],
        p.PRIVATE_ROUND_VESTING["linear_months"],
        current_sim_month,
        state["vested_private_round_tokens"]
    )
    state["vested_private_round_tokens"] += private_investors_unlocked_this_month
    newly_vested_total += private_investors_unlocked_this_month
    
    # Current Investment Round Vesting
    current_round_investors_unlocked_this_month = calculate_monthly_unlock(
        p.CURRENT_INVESTMENT_ROUND_TOKENS_TOTAL,
        p.CURRENT_ROUND_VESTING["cliff"],
        p.CURRENT_ROUND_VESTING["linear_months"],
        current_sim_month,
        state["vested_current_round_tokens"]
    )
    state["vested_current_round_tokens"] += current_round_investors_unlocked_this_month
    newly_vested_total += current_round_investors_unlocked_this_month

    state["circulating_supply"] += newly_vested_total
    state['newly_vested_total_monthly'] = newly_vested_total
    # print(f"Month {current_sim_month}: Newly Vested: {newly_vested_total}, Circulating Supply: {state['circulating_supply']}")
    return state

def handle_emissions(state, p):
    """Handles the monthly release of tokens from the Node Runner Rewards Pool, 
       balancing scheduled emissions with direct usage-driven rewards."""
    current_year = state["current_year"]
    potential_monthly_emission_from_schedule = 0
    state['emitted_node_rewards_monthly'] = 0
    state['network_utilization_rate'] = 0

    if current_year in p.YEARLY_EMISSION_SCHEDULE_ABSOLUTE:
        annual_emission_for_current_year = p.YEARLY_EMISSION_SCHEDULE_ABSOLUTE[current_year]
        potential_monthly_emission_from_schedule = annual_emission_for_current_year / 12
    
    # Ensure potential emission doesn't exceed remaining pool initially
    max_emission_this_month = min(potential_monthly_emission_from_schedule, state["remaining_node_rewards_pool_tokens"])

    # Calculate Network Utilization
    if state["current_network_capacity_gflops_monthly"] > 0:
        network_utilization = state["current_compute_demand_gflops_monthly"] / state["current_network_capacity_gflops_monthly"]
        state['network_utilization_rate'] = min(network_utilization, 1.0) # Cap at 100%
    else:
        state['network_utilization_rate'] = 0

    # 1. Scheduled Portion (scaled by utilization)
    scheduled_budget_share = max_emission_this_month * p.SCHEDULE_DRIVEN_EMISSION_FACTOR
    emitted_from_schedule = scheduled_budget_share * state['network_utilization_rate']

    # 2. Usage-Driven Portion (direct GFLOP payment, capped by its budget share)
    usage_driven_budget_share = max_emission_this_month * p.USAGE_DRIVEN_EMISSION_FACTOR
    calculated_usage_driven_rewards = state["current_compute_demand_gflops_monthly"] * p.EMISSION_RATE_PER_GFLOP_DRIA
    emitted_from_usage = min(calculated_usage_driven_rewards, usage_driven_budget_share)
    
    # Total actual tokens to emit
    actual_tokens_to_emit_for_compute = emitted_from_schedule + emitted_from_usage
    
    # Final check against overall remaining pool and monthly max (should be redundant if logic is correct but safe)
    final_emission = min(actual_tokens_to_emit_for_compute, state["remaining_node_rewards_pool_tokens"])
    final_emission = min(final_emission, max_emission_this_month) # Cannot emit more than the total monthly budget from schedule

    if final_emission > 0:
        state["remaining_node_rewards_pool_tokens"] -= final_emission
        state["circulating_supply"] += final_emission
        state['emitted_node_rewards_monthly'] = final_emission
        # print(f"Node Rewards: PotentialMonthSched={potential_monthly_emission_from_schedule:.2f}, MaxMonth={max_emission_this_month:.2f}, Util={state['network_utilization_rate']:.2%}, FromSched={emitted_from_schedule:.2f}, FromUsage={emitted_from_usage:.2f}, FinalEmit={final_emission:.2f}")

    return state

def handle_ecosystem_fund_release(state, p, month_index):
    """Handles the monthly release of tokens from the Ecosystem Fund."""
    released_this_month = 0
    # month_index is 0-indexed (0 to 119 for 10 years)
    # Start of a quarter: month_index 0, 3, 6, 9, ... (which are months 1, 4, 7, 10 of the year)

    # At the START of each quarter, calculate the total for that quarter
    if month_index % 3 == 0:
        current_year = state["current_year"]
        quarterly_release_percent = p.ECOSYSTEM_FUND_QUARTERLY_RELEASE_SCHEDULE_YEARLY.get(current_year, p.DEFAULT_ECOSYSTEM_FUND_QUARTERLY_RELEASE_PERCENT)
        
        quarterly_release_target = state['remaining_ecosystem_fund_tokens'] * quarterly_release_percent
        # Store this target to be used for the 3 months of this quarter
        state['current_quarter_ecosystem_release_pool'] = quarterly_release_target
        # Also store how much of this pool has been released so far this quarter
        state['current_quarter_ecosystem_released_so_far'] = 0

    # Each month, release a fraction of the pool calculated at the start of the quarter
    if 'current_quarter_ecosystem_release_pool' in state and state['current_quarter_ecosystem_release_pool'] > 0:
        # Amount to release this month is 1/3 of the pool for the quarter
        # unless it's the last month of the quarter, then release remaining to hit the target precisely
        
        # Check how many months are left in this quarter's release cycle (1, 2, or 3)
        # month_in_quarter_cycle = (month_index % 3) + 1

        # Intended release this month
        target_monthly_release = state['current_quarter_ecosystem_release_pool'] * p.ECOSYSTEM_FUND_MONTHLY_RELEASE_FRACTION_OF_QUARTERLY

        # Ensure we don't release more than what's left in the pool for this quarter
        remaining_in_quarter_pool = state['current_quarter_ecosystem_release_pool'] - state['current_quarter_ecosystem_released_so_far']
        
        if target_monthly_release > remaining_in_quarter_pool:
             actual_release_this_month = remaining_in_quarter_pool # Release what's left
        else:
            actual_release_this_month = target_monthly_release

        # Additionally, ensure we don't release more than actually available in the total fund
        if actual_release_this_month > state['remaining_ecosystem_fund_tokens']:
            actual_release_this_month = state['remaining_ecosystem_fund_tokens']

        state['circulating_supply'] += actual_release_this_month
        state['remaining_ecosystem_fund_tokens'] -= actual_release_this_month
        state['current_quarter_ecosystem_released_so_far'] += actual_release_this_month
        released_this_month = actual_release_this_month
    
    state['ecosystem_fund_released_monthly'] = released_this_month

    # Clean up at the end of the quarter
    if (month_index + 1) % 3 == 0:
        state['current_quarter_ecosystem_release_pool'] = 0
        state['current_quarter_ecosystem_released_so_far'] = 0
        
    return state

def handle_staking(state, p):
    """Handles changes in node count based on APY, total staked DRIA, and its impact on circulating supply and network capacity."""
    previous_total_staked_dria = state["total_dria_staked"]
    previous_node_count = state["current_node_count"]

    # APY Moving Average Calculation
    state['apy_history'].append(state.get("actual_node_apy_monthly_percentage", 0))
    if len(state['apy_history']) > p.APY_MOVING_AVERAGE_MONTHS:
        state['apy_history'].pop(0) # Keep list to size of moving average window
    
    average_apy_for_decision = 0
    if state['apy_history']:
        average_apy_for_decision = sum(state['apy_history']) / len(state['apy_history'])
    state['average_apy_for_decision'] = average_apy_for_decision # Store for logging/history

    # Calculate node growth based on APY difference (using moving average APY)
    if previous_node_count > 0: # Avoid division by zero or extreme changes if starting from 0 nodes and APY is high
        apy_difference_percentage_points = average_apy_for_decision - p.TARGET_NODE_APY_PERCENTAGE
        # Convert APY difference (e.g. 5 for 5%) to a decimal factor for sensitivity (e.g. 0.05)
        # Sensitivity is how much 1 percentage point of APY diff influences growth rate (e.g. 0.002 means 1% APY diff -> 0.2% growth)
        node_growth_factor_monthly = (apy_difference_percentage_points) * p.NODE_ADOPTION_CHURN_SENSITIVITY 
        
        # Apply growth/churn to node count
        # Ensure node count doesn't go below a certain minimum if desired (e.g. 1, or 0 if allowed)
        # Add a cap to growth/churn rate to prevent extreme swings, e.g. +/- 20% per month
        max_monthly_change = 0.20 
        node_growth_factor_monthly = max(min(node_growth_factor_monthly, max_monthly_change), -max_monthly_change)
        
        state["current_node_count"] = previous_node_count * (1 + node_growth_factor_monthly)
        state["current_node_count"] = max(state["current_node_count"], 0) # Ensure node count doesn't go negative
    else: # If starting with 0 nodes, a fixed small initial growth if APY is positive, or stays 0
        if average_apy_for_decision > p.TARGET_NODE_APY_PERCENTAGE:
            state["current_node_count"] = 1 # Start with 1 node if attractive
        else:
            state["current_node_count"] = 0
            
    # Update total DRIA staked based on new node count
    current_total_dria_staked = state["current_node_count"] * p.MINIMUM_NODE_STAKE_DRIA
    state["total_dria_staked"] = current_total_dria_staked

    # Calculate net change in staked DRIA this month
    newly_staked_this_month = current_total_dria_staked - previous_total_staked_dria
    state["newly_staked_dria_monthly"] = newly_staked_this_month

    # Update circulating supply: staking removes tokens, unstaking adds them back
    if newly_staked_this_month > 0: # Staking
        state["circulating_supply"] -= min(newly_staked_this_month, state["circulating_supply"])
    elif newly_staked_this_month < 0: # Unstaking
        state["circulating_supply"] -= newly_staked_this_month # Subtracting a negative = adding
    
    # Update network capacity based on new node count
    state["current_network_capacity_gflops_monthly"] = state["current_node_count"] * p.AVG_GFLOPS_PER_NODE

    # print(f"Staking: Nodes={state['current_node_count']:.2f}, TargetAPY={p.TARGET_NODE_APY_PERCENTAGE:.2f}, AvgDecisionAPY={average_apy_for_decision:.2f}, ActualAPYThisMonth={state.get('actual_node_apy_monthly_percentage',0):.2f}, GrowthFactor={node_growth_factor_monthly if previous_node_count > 0 else 'N/A'}, Capacity={state['current_network_capacity_gflops_monthly']:.2f}")
    return state

def handle_burns(state, p):
    """Handles all token burn mechanisms for the current month."""
    total_burned_this_month = 0
    
    # Reset monthly burn trackers
    state["burned_from_usd_monthly"] = 0
    state["burned_from_onprem_monthly"] = 0
    state["burned_from_oracle_monthly"] = 0

    # A. USD-to-Credit Burn
    if state['simulated_dria_price_usd'] > 0: # Use dynamic price from state
        dria_bought_for_burn_usd = state["current_usd_credit_purchase_per_month"] / state['simulated_dria_price_usd']
        # Ensure burn does not exceed circulating supply (edge case, but good practice)
        actual_burn_usd = min(dria_bought_for_burn_usd, state["circulating_supply"] - total_burned_this_month)
        state["burned_from_usd_monthly"] = actual_burn_usd
        total_burned_this_month += actual_burn_usd
    
    # B. On-Prem Conversion Burn
    dria_converted_to_credits_on_prem = state["current_dria_earned_by_on_prem_users_per_month"] * p.INITIAL_ON_PREM_CREDIT_CONVERSION_RATE
    dria_burned_from_on_prem_potential = dria_converted_to_credits_on_prem * p.ON_PREM_CONVERSION_BURN_RATE
    actual_burn_onprem = min(dria_burned_from_on_prem_potential, state["circulating_supply"] - total_burned_this_month)
    state["burned_from_onprem_monthly"] = actual_burn_onprem
    total_burned_this_month += actual_burn_onprem

    # C. Oracle Node Usage Burn
    total_dria_spent_on_oracle = state["current_oracle_requests_per_month"] * p.DRIA_COST_PER_ORACLE_REQUEST
    dria_burned_from_oracle_potential = total_dria_spent_on_oracle * p.ORACLE_USAGE_BURN_RATE
    actual_burn_oracle = min(dria_burned_from_oracle_potential, state["circulating_supply"] - total_burned_this_month)
    state["burned_from_oracle_monthly"] = actual_burn_oracle
    total_burned_this_month += actual_burn_oracle

    state["circulating_supply"] -= total_burned_this_month
    state["total_tokens_burned"] += total_burned_this_month # Cumulative total burns
    
    # print(f"Burns this month: USD={state['burned_from_usd_monthly']}, OnPrem={state['burned_from_onprem_monthly']}, Oracle={state['burned_from_oracle_monthly']}. Total: {total_burned_this_month}")
    # print(f"Circulating Supply after burns: {state['circulating_supply']}, Total Burned Ever: {state['total_tokens_burned']}")
    return state

def update_simulated_price(state, p):
    """Updates the simulated DRIA price based on monthly token flows."""
    
    # Demand Pressure Calculation
    # USD burns are already in DRIA terms (state['burned_from_usd_monthly'])
    demand_from_usd_burns = state.get('burned_from_usd_monthly', 0)
    
    # Oracle usage: total DRIA spent, not just burned portion
    # (assuming DRIA_COST_PER_ORACLE_REQUEST and INITIAL_ORACLE_REQUESTS_PER_MONTH are constant for now)
    total_dria_spent_on_oracle = p.INITIAL_ORACLE_REQUESTS_PER_MONTH * p.DRIA_COST_PER_ORACLE_REQUEST
    demand_from_oracle_usage = total_dria_spent_on_oracle # This is a proxy for DRIA locked/used
    
    effective_demand_pressure = demand_from_usd_burns + demand_from_oracle_usage
    
    # Supply Pressure Calculation
    supply_from_vesting = state.get('newly_vested_total_monthly', 0)
    supply_from_emissions = state.get('emitted_node_rewards_monthly', 0)
    supply_from_ecosystem_fund = state.get('ecosystem_fund_released_monthly', 0)
    
    # Net change in staked tokens: positive means more staked (less supply pressure), negative means unstaked (more supply pressure)
    net_newly_staked = state.get('newly_staked_dria_monthly', 0)

    effective_supply_pressure = (supply_from_vesting + supply_from_emissions + supply_from_ecosystem_fund) - net_newly_staked
    
    # Calculate Price Change
    current_price = state.get('simulated_dria_price_usd', p.INITIAL_SIMULATED_DRIA_PRICE_USD)
    new_price = current_price

    if effective_supply_pressure > 0: # Avoid division by zero if no new supply
        demand_supply_ratio = effective_demand_pressure / effective_supply_pressure
        # Simple linear adjustment: 
        # ratio > 1 (demand > supply) -> price increases
        # ratio < 1 (demand < supply) -> price decreases
        price_change_percentage = (demand_supply_ratio - 1) * p.PRICE_ADJUSTMENT_SENSITIVITY
        new_price = current_price * (1 + price_change_percentage)
    elif effective_demand_pressure > 0: # No new supply, but there is demand pressure
        # If no new supply but there's demand, price increases (e.g. by sensitivity factor)
        new_price = current_price * (1 + p.PRICE_ADJUSTMENT_SENSITIVITY) 
        
    # Apply price floor
    new_price = max(new_price, p.MIN_SIMULATED_DRIA_PRICE_USD)
    
    state['simulated_dria_price_usd'] = new_price
    
    # print(f"Price Update: D/S Ratio: {demand_supply_ratio if effective_supply_pressure > 0 else 'N/A'}, Old Price: {current_price:.4f}, New Price: {new_price:.4f}")
    return state

def run_simulation(initial_state, num_years):
    """Main simulation loop."""
    timesteps = num_years * 12 # Assuming monthly timesteps
    current_state = initial_state.copy()
    history = []

    for t in range(timesteps):
        # 0. Update Demand Drivers based on growth rates
        current_state = update_demand_drivers(current_state, params)

        # Update time
        current_state["current_month"] += 1
        if current_state["current_month"] > 12:
            current_state["current_month"] = 0 # Month 0 will become 1 in next step
            current_state["current_year"] += 1
            current_state["current_month"] +=1 # Corrected: month should be 1 after year increment
        
        # 1. Handle Vesting & Unlocks
        current_state = handle_vesting(current_state, params)
        
        # 2. Handle Emissions (Calculates new tokens minted from rewards pool for compute)
        current_state = handle_emissions(current_state, params)

        # 2.b. Handle Ecosystem Fund Release (Quarterly)
        current_state = handle_ecosystem_fund_release(current_state, params, t)
        
        # 2.c. Calculate Node Economics (Revenue, Cost, APY)
        current_state = calculate_node_economics(current_state, params)

        # 2.d. Handle Staking and Node Count Update (Now uses APY)
        current_state = handle_staking(current_state, params)

        # 3. Handle Demand & Credit Purchases (This will be a separate function later)
        # current_state = handle_demand(current_state, params)
        
        # 4. Handle Burn Mechanisms
        current_state = handle_burns(current_state, params)

        # 4.b. Update Simulated DRIA Price
        current_state = update_simulated_price(current_state, params)

        # 5. Update Circulating Supply (Done by individual handlers now)
        
        # Store history for this timestep
        history.append(current_state.copy())
        
        # print(f"Simulated Year: {current_state['current_year']}, Month: {current_state['current_month']}")
        # if t > 50: # Stopper for initial development
        #     break
            

    return history

def update_demand_drivers(state, p):
    """Updates demand driver values in the state based on their monthly growth rates."""
    state["current_usd_credit_purchase_per_month"] *= (1 + p.USD_CREDIT_PURCHASE_GROWTH_RATE_MONTHLY)
    state["current_dria_earned_by_on_prem_users_per_month"] *= (1 + p.ON_PREM_USER_EARNINGS_GROWTH_RATE_MONTHLY)
    state["current_oracle_requests_per_month"] *= (1 + p.ORACLE_REQUESTS_GROWTH_RATE_MONTHLY)
    
    # Update compute demand and capacity
    state["current_compute_demand_gflops_monthly"] *= (1 + p.COMPUTE_DEMAND_GROWTH_RATE_MONTHLY)
    # state["current_network_capacity_gflops_monthly"] *= (1 + p.NETWORK_CAPACITY_GROWTH_RATE_MONTHLY) # Replaced by dynamic capacity calculation in handle_staking
    return state

def calculate_node_economics(state, p):
    """Calculates monthly revenue, costs, profit, and APY for node runners."""
    # Revenue from emitted node rewards
    state["node_runner_revenue_monthly_usd"] = state.get('emitted_node_rewards_monthly', 0) * state['simulated_dria_price_usd']

    # Costs
    if state["current_node_count"] > 0:
        total_network_operating_cost_usd_monthly = state["current_node_count"] * p.AVG_NODE_OPERATING_COST_USD_MONTHLY
        avg_operating_cost_per_node_usd_monthly = p.AVG_NODE_OPERATING_COST_USD_MONTHLY
    else:
        total_network_operating_cost_usd_monthly = 0
        avg_operating_cost_per_node_usd_monthly = 0

    # Profit
    net_profit_all_nodes_usd_monthly = state["node_runner_revenue_monthly_usd"] - total_network_operating_cost_usd_monthly
    
    avg_profit_per_node_usd_monthly = 0
    if state["current_node_count"] > 0:
        avg_profit_per_node_usd_monthly = net_profit_all_nodes_usd_monthly / state["current_node_count"]

    # APY Calculation (Simplified for V1 - based on profit from compute vs. value of stake)
    # More advanced: could include a base staking APY from another source if applicable.
    annualized_profit_per_node_usd = avg_profit_per_node_usd_monthly * 12
    value_staked_per_node_usd = p.MINIMUM_NODE_STAKE_DRIA * state['simulated_dria_price_usd']

    if value_staked_per_node_usd > 0:
        # APY from compute rewards relative to stake value
        compute_apy_percentage = (annualized_profit_per_node_usd / value_staked_per_node_usd) * 100 
    else:
        compute_apy_percentage = 0
    
    # For V1, let's assume the BASE_STAKING_YIELD_RATE_ANNUAL is an additional flat yield on staked DRIA.
    # This yield would theoretically come from another part of the token supply (e.g. ecosystem fund or specific staking rewards pool)
    # For now, we will model it as an additional incentive that nodes perceive.
    # This portion of APY does not directly consume from emitted_node_rewards_monthly.

    # Adaptive Base Yield Calculation
    current_price = state['simulated_dria_price_usd']
    adjusted_base_staking_yield_annual = p.BASE_STAKING_YIELD_RATE_ANNUAL

    if current_price < p.ADAPTIVE_YIELD_PRICE_THRESHOLD_LOW:
        adjusted_base_staking_yield_annual = min(p.BASE_STAKING_YIELD_RATE_ANNUAL * p.BASE_YIELD_BOOST_FACTOR, p.MAX_ADAPTIVE_BASE_YIELD_ANNUAL)
    elif current_price > p.ADAPTIVE_YIELD_PRICE_THRESHOLD_HIGH:
        adjusted_base_staking_yield_annual = max(p.BASE_STAKING_YIELD_RATE_ANNUAL * p.BASE_YIELD_REDUCTION_FACTOR, p.MIN_ADAPTIVE_BASE_YIELD_ANNUAL)
    
    state['current_adjusted_base_staking_yield_annual'] = adjusted_base_staking_yield_annual
    total_effective_apy_percentage = compute_apy_percentage + (adjusted_base_staking_yield_annual * 100)
    state["actual_node_apy_monthly_percentage"] = total_effective_apy_percentage

    # print(f"NodeEcon: RevenueM={state['node_runner_revenue_monthly_usd']:.2f}, ProfitPerNodeM={avg_profit_per_node_usd_monthly:.2f}, StakeValuePerNode={value_staked_per_node_usd:.2f}, CompAPY={compute_apy_percentage:.2f}%, AdjBaseYield={adjusted_base_staking_yield_annual*100:.2f}%, TotalAPY={total_effective_apy_percentage:.2f}%")
    return state

# --- Placeholder functions for other steps ---
# def handle_emissions(state, p):
#     # Logic for tokens emitted to node runners based on compute
#     return state

# def handle_demand(state, p):
#     # Logic for credit purchases (USD & DRIA), on-prem compute, oracle usage
#     return state

# def handle_burns(state, p):
#     # Logic for tokens burned from USD purchases, on-prem, oracle
#     return state

# def calculate_circulating_supply(state, p):
#     # Recalculate based on emissions, burns, vesting
#     # This will be the primary function that sums up all ins and outs.
#     # For now, handle_vesting directly adds to circulating_supply for simplicity.
#     # This function might become more of an aggregator or checker.
#     return state["circulating_supply"]

print("Simulation engine loaded.") 