# sim/simulation_engine_proposal.py
import math
import random
# import model_parameters_proposal as p # This will be passed as an argument

def calculate_monthly_unlock(total_tokens, cliff_months, linear_vesting_months, current_simulation_month, vested_to_date):
    """Calculates tokens unlocked for a single category in the current month."""
    if linear_vesting_months <= 0:
        if current_simulation_month > cliff_months and vested_to_date == 0:
             return total_tokens
        return 0

    monthly_unlock_amount = total_tokens / linear_vesting_months
    tokens_unlocked_this_month = 0
    if current_simulation_month > cliff_months and current_simulation_month <= (cliff_months + linear_vesting_months):
        if vested_to_date + monthly_unlock_amount > total_tokens:
            tokens_unlocked_this_month = total_tokens - vested_to_date
        else:
            tokens_unlocked_this_month = monthly_unlock_amount
    return tokens_unlocked_this_month

def handle_vesting_proposal(state, p):
    current_sim_month = (state["current_year"] -1) * 12 + state["current_month"]
    newly_vested_total = 0
    state['newly_vested_total_monthly_proposal'] = 0

    # Team Vesting
    team_unlocked = calculate_monthly_unlock(
        p.TEAM_TOKENS_TOTAL_PROPOSAL,
        p.TEAM_VESTING_PROPOSAL["cliff"],
        p.TEAM_VESTING_PROPOSAL["linear_months"],
        current_sim_month,
        state["vested_team_tokens_proposal"]
    )
    state["vested_team_tokens_proposal"] += team_unlocked
    newly_vested_total += team_unlocked

    # Advisors Vesting
    advisors_unlocked = calculate_monthly_unlock(
        p.ADVISORS_TOKENS_TOTAL_PROPOSAL,
        p.ADVISORS_VESTING_PROPOSAL["cliff"],
        p.ADVISORS_VESTING_PROPOSAL["linear_months"],
        current_sim_month,
        state["vested_advisors_tokens_proposal"]
    )
    state["vested_advisors_tokens_proposal"] += advisors_unlocked
    newly_vested_total += advisors_unlocked

    # Investors Vesting
    investors_unlocked = calculate_monthly_unlock(
        p.INVESTORS_TOKENS_TOTAL_PROPOSAL,
        p.INVESTORS_VESTING_PROPOSAL["cliff"],
        p.INVESTORS_VESTING_PROPOSAL["linear_months"],
        current_sim_month,
        state["vested_investors_tokens_proposal"]
    )
    state["vested_investors_tokens_proposal"] += investors_unlocked
    newly_vested_total += investors_unlocked
    
    # Ecosystem Fund Monthly Release
    ecosystem_released_this_month = 0
    if state["remaining_ecosystem_fund_tokens_proposal"] > 0:
        ecosystem_released_this_month = min(p.ECOSYSTEM_FUND_MONTHLY_RELEASE_PROPOSAL, state["remaining_ecosystem_fund_tokens_proposal"])
        state["remaining_ecosystem_fund_tokens_proposal"] -= ecosystem_released_this_month
        state["ecosystem_fund_released_monthly_proposal"] = ecosystem_released_this_month
        newly_vested_total += ecosystem_released_this_month

    state["circulating_supply_proposal"] += newly_vested_total
    state['newly_vested_total_monthly_proposal'] = newly_vested_total
    return state

def handle_emissions_proposal(state, p):
    """Handles monthly emissions based on a halving schedule."""
    absolute_month_index = (state["current_year"] - 1) * 12 + (state["current_month"] -1) 

    num_halvings = 0
    if p.PROPOSAL_HALVING_PERIOD_MONTHS > 0:
        num_halvings = absolute_month_index // p.PROPOSAL_HALVING_PERIOD_MONTHS
    
    base_monthly_emission_target = p.PROPOSAL_INITIAL_MONTHLY_EMISSION / (2**num_halvings)
    state["halvings_occurred"] = num_halvings

    # Add buffer
    buffered_monthly_emission_target = base_monthly_emission_target * (1 + p.EMISSION_BUFFER_PERCENT)

    emitted_this_timestep = 0
    if state["remaining_emission_pool_proposal"] > 0:
        # Ensure we don't emit more than what's left, even with the buffer
        actual_emission_this_month = min(buffered_monthly_emission_target, state["remaining_emission_pool_proposal"])
        emitted_this_timestep = actual_emission_this_month
        # We will subtract the *actually distributed* amount later, after demand scaling
        # state["remaining_emission_pool_proposal"] -= actual_emission_this_month # Deferred
    else:
        emitted_this_timestep = 0

    # Treasury tax from emissions
    treasury_cut_emissions = emitted_this_timestep * p.PROPOSAL_TREASURY_TAX_RATE_FROM_EMISSIONS
    # state["treasury_balance_proposal"] += treasury_cut_emissions # Will be added in main loop after actual emission
    
    reward_pool_for_distribution_potential = emitted_this_timestep - treasury_cut_emissions
    # state["emitted_rewards_monthly_proposal"] = reward_pool_for_distribution_potential # This will be the *actual* distributed
    # state["circulating_supply_proposal"] += reward_pool_for_distribution_potential # Adjusted later

    state["current_epoch_reward_after_halving"] = base_monthly_emission_target # Store the base target for logging
    state["total_emitted_this_timestep_before_treasury"] = emitted_this_timestep # Potential emission

    # Return the potential pool and the treasury cut; actual distribution and circulation impact handled in main loop
    return state, reward_pool_for_distribution_potential, treasury_cut_emissions, emitted_this_timestep

def distribute_epoch_rewards_proposal(state, p, monthly_reward_pool_potential):
    """Distributes the monthly_reward_pool_potential to contributors based on Uptime and FLOPs, scaled by demand."""
    total_performance_score = 0
    performance_scores = []
    total_simulated_utilized_gflops_this_month = 0

    for i in range(state["current_contributor_nodes"]):
        uptime_i = max(0, min(1, random.gauss(p.PROPOSAL_AVG_UPTIME_PER_CONTRIBUTOR, 0.05)))
        # Simulate GFLOPs provided by this node for the month
        # This can be thought of as "utilized" GFLOPs based on current (implicit) demand
        gflops_i_monthly = max(0, random.gauss(p.PROPOSAL_AVG_GFLOPS_PER_CONTRIBUTOR_MONTHLY, 
                                   p.PROPOSAL_AVG_GFLOPS_PER_CONTRIBUTOR_MONTHLY * 0.1))
        total_simulated_utilized_gflops_this_month += gflops_i_monthly

        # Performance score calculation (as before)
        score_i = uptime_i * math.log(1 + gflops_i_monthly) if gflops_i_monthly > 0 else uptime_i * 0.001 
        performance_scores.append(score_i)
        total_performance_score += score_i

    # Calculate demand scaling factor
    # Total available GFLOPs = num_nodes * avg_gflops_potential_per_node
    # We use PROPOSAL_AVG_GFLOPS_PER_CONTRIBUTOR_MONTHLY as the potential per node.
    total_available_gflops = state["current_contributor_nodes"] * p.PROPOSAL_AVG_GFLOPS_PER_CONTRIBUTOR_MONTHLY
    state["total_available_gflops_monthly"] = total_available_gflops # Log this
    state["total_utilized_gflops_monthly"] = total_simulated_utilized_gflops_this_month # Log this

    demand_supply_ratio = 0
    if total_available_gflops > 0:
        demand_supply_ratio = total_simulated_utilized_gflops_this_month / total_available_gflops
    state["demand_supply_ratio_monthly"] = demand_supply_ratio # Log this

    reward_scaling_factor = 1.0
    if p.TARGET_UTILIZATION_FOR_FULL_REWARDS > 0:
        reward_scaling_factor = min(1.0, demand_supply_ratio / p.TARGET_UTILIZATION_FOR_FULL_REWARDS)
    else: # If target utilization is 0 or less, assume full rewards (or handle as error/edge case)
        reward_scaling_factor = 1.0 
    state["reward_scaling_factor_monthly"] = reward_scaling_factor # Log this

    # Scale the potential reward pool by the demand factor
    rewards_to_distribute_after_scaling = monthly_reward_pool_potential * reward_scaling_factor
    state["rewards_to_distribute_after_scaling_monthly"] = rewards_to_distribute_after_scaling # Log this

    actual_distributed_to_contributors = 0
    if total_performance_score > 0 and rewards_to_distribute_after_scaling > 0:
        for score_i in performance_scores:
            node_reward = (score_i / total_performance_score) * rewards_to_distribute_after_scaling
            actual_distributed_to_contributors += node_reward
    
    state["total_distributed_to_contributors_monthly"] = actual_distributed_to_contributors
    # This amount will be added to circulating supply in the main loop.

    return state, actual_distributed_to_contributors

def handle_staking_and_slashing_proposal(state, p):
    """Handles staking by validators and contributors, and potential slashing."""
    # Simplified: Assume fixed number of validators and contributors who stake the minimum.
    # Can be made dynamic based on profitability.
    
    # Validator Staking
    total_validator_stake = state["current_validator_nodes"] * p.PROPOSAL_MIN_VALIDATOR_STAKE_DRIA
    
    # Contributor Staking (if required by the model)
    total_contributor_stake = state["current_contributor_nodes"] * p.PROPOSAL_MIN_CONTRIBUTOR_STAKE_DRIA
    
    total_staked_now = total_validator_stake + total_contributor_stake
    
    # Net change in staked DRIA (if nodes join/leave or stake amounts change)
    # For this simplified version, assume stable node counts for now.
    # If node counts change, then:
    # newly_staked_this_month = total_staked_now - state["total_dria_staked_proposal"]
    # state["circulating_supply_proposal"] -= newly_staked_this_month # if positive, reduces; if negative, increases
    # state["total_dria_staked_proposal"] = total_staked_now

    state["total_dria_staked_proposal"] = total_staked_now # For now, just set it based on current nodes
    # Assume initial staking happened at T0 and is subtracted from circulating supply there.
    # Or, if we want to model dynamic staking's impact on circ supply each month:
    # Calculate change_in_stake = total_staked_now - state.get("previous_total_dria_staked_proposal", 0)
    # state["circulating_supply_proposal"] -= change_in_stake
    # state["previous_total_dria_staked_proposal"] = total_staked_now


    # Slashing
    slashed_this_month = 0
    # Validator Slashing (example: 1% chance of downtime event for a validator per month)
    for _ in range(state["current_validator_nodes"]):
        if random.random() < 0.01: # 1% chance of downtime slash event for a validator
            slash_amount = p.PROPOSAL_MIN_VALIDATOR_STAKE_DRIA * p.PROPOSAL_SLASHING_PERCENTAGE_VALIDATOR_DOWNTIME
            slashed_this_month += slash_amount
        if random.random() < 0.001: # 0.1% chance of malfeasance slash
            slash_amount = p.PROPOSAL_MIN_VALIDATOR_STAKE_DRIA * p.PROPOSAL_SLASHING_PERCENTAGE_VALIDATOR_MALFEASANCE
            slashed_this_month += slash_amount

    # Contributor Slashing (example: 0.5% chance of major failure for a contributor)
    for _ in range(state["current_contributor_nodes"]):
        if random.random() < 0.005:
            slash_amount = p.PROPOSAL_MIN_CONTRIBUTOR_STAKE_DRIA * p.PROPOSAL_SLASHING_PERCENTAGE_CONTRIBUTOR_FAILURE
            slashed_this_month += slash_amount
            
    if slashed_this_month > 0:
        state["circulating_supply_proposal"] -= slashed_this_month # Slashed tokens removed from circ
        state["total_tokens_slashed_proposal"] += slashed_this_month
        state["total_dria_staked_proposal"] -= slashed_this_month # Also remove from total stake pool
        # Slashed tokens could go to treasury or be burned. Assuming burned (removed from circ).

    state["slashed_dria_monthly_proposal"] = slashed_this_month
    
    # Validator Staking Rewards (Placeholder - can be a simple APY or share of emissions)
    # For now, let's assume validators get a base APY on their stake, funded by the overall ecosystem
    # This could come from a portion of the `monthly_reward_pool` or from fees.
    # If it's from general circulating supply (like an interest rate):
    validator_staking_rewards_apy = 0.05 # Example: 5% annual
    monthly_validator_rewards = (total_validator_stake * validator_staking_rewards_apy) / 12
    state["circulating_supply_proposal"] += monthly_validator_rewards # Added to circulation
    state["validator_staking_rewards_monthly_proposal"] = monthly_validator_rewards
    
    return state

def handle_service_fees_proposal(state, p):
    """Handles service fees paid by users, their distribution, and potential burns."""
    total_service_value_usd_this_month = state["current_usd_demand_per_month_proposal"]
    total_service_value_dria_this_month = state["current_dria_demand_per_month_proposal"]

    # Convert USD demand to DRIA equivalent for fee calculation
    if state['simulated_dria_price_usd_proposal'] > 0:
        service_value_from_usd_in_dria = total_service_value_usd_this_month / state['simulated_dria_price_usd_proposal']
    else:
        service_value_from_usd_in_dria = 0
        
    total_service_value_in_dria_equivalent = service_value_from_usd_in_dria + total_service_value_dria_this_month
    
    # Calculate total fees in DRIA
    total_fees_generated_dria = total_service_value_in_dria_equivalent * p.PROPOSAL_SERVICE_FEE_PERCENT_OF_VALUE
    
    # Add average transaction fees (simplified: based on number of nodes as proxy for activity)
    num_transactions_proxy = (state["current_contributor_nodes"] + state["current_validator_nodes"]) * 10 # Example: 10 tx per node
    total_tx_fees_dria = num_transactions_proxy * p.PROPOSAL_AVG_TX_FEE_DRIA
    total_fees_generated_dria += total_tx_fees_dria
    
    state["total_fees_generated_dria_monthly"] = total_fees_generated_dria

    # Distribute fees
    # 1. Treasury Cut from Fees
    treasury_cut_fees = total_fees_generated_dria * p.PROPOSAL_TREASURY_TAX_RATE_FROM_FEES
    state["treasury_balance_proposal"] += treasury_cut_fees
    
    fees_after_treasury = total_fees_generated_dria - treasury_cut_fees
    
    # Fees can be distributed to contributors/validators, or burned.
    # For now, let's assume a portion is burned and rest goes to contributors/validators (similar to emission rewards)
    fees_to_burn = fees_after_treasury * 0.5 # Example: 50% of remaining fees burned
    fees_for_rewards = fees_after_treasury - fees_to_burn
    
    state["circulating_supply_proposal"] -= fees_to_burn # Burning reduces circ supply
    state["total_tokens_burned_proposal"] += fees_to_burn
    state["burned_from_fees_monthly_proposal"] = fees_to_burn
    
    # Add fees_for_rewards to the pool to be distributed, similar to monthly_reward_pool
    # This could be added to the next month's reward pool or distributed immediately.
    # For simplicity, let's assume it's available for immediate distribution via the same mechanism as monthly rewards.
    # This part needs careful design: are fees distributed by performance score too? Or to stakers?
    # Let's add it to a general pool that could be paid to stakers (validators primarily).
    state["fee_rewards_for_validators_monthly_proposal"] = fees_for_rewards
    state["circulating_supply_proposal"] += fees_for_rewards # These are re-circulated
                                                            # if not already accounted for (e.g. paid from user to network)
                                                            # This needs care: fees are paid by users, so they are already part of supply.
                                                            # The burning reduces supply. The part for rewards is a transfer.
                                                            # If users pay in DRIA, that DRIA moves. If USD, new DRIA might be involved if not burned.

    # If USD payments for services also trigger a buy-and-burn (optional feature)
    if p.USD_TO_DRIA_BURN_ACTIVE_PROPOSAL and state['simulated_dria_price_usd_proposal'] > 0:
        usd_value_to_buy_burn = state["current_usd_demand_per_month_proposal"] * (1 - p.USD_TO_CREDIT_FX_FEE_PROPOSAL)
        dria_bought_for_burn = usd_value_to_buy_burn / state['simulated_dria_price_usd_proposal']
        
        actual_burn_from_usd = min(dria_bought_for_burn, state["circulating_supply_proposal"] - state.get("burned_from_fees_monthly_proposal",0) - state.get("slashed_dria_monthly_proposal",0) ) # Avoid burning more than available after other burns
        state["circulating_supply_proposal"] -= actual_burn_from_usd
        state["total_tokens_burned_proposal"] += actual_burn_from_usd
        state["burned_from_usd_payments_monthly_proposal"] = actual_burn_from_usd
        
    return state

def update_demand_drivers_proposal(state, p):
    state["current_usd_demand_per_month_proposal"] *= (1 + p.USD_DEMAND_GROWTH_RATE_MONTHLY_PROPOSAL)
    state["current_dria_demand_per_month_proposal"] *= (1 + p.DRIA_DEMAND_GROWTH_RATE_MONTHLY_PROPOSAL)
    # Add growth for node counts if desired (or make it dynamic based on APY)
    # state["current_contributor_nodes"] *= (1 + 0.005) # Example fixed growth
    # state["current_validator_nodes"] *= (1 + 0.002)   # Example fixed growth
    return state
    
def update_simulated_price_proposal(state, p):
    # Simplified price model: Reacts to net change in circulating supply vs. demand proxies
    # More sophisticated models could use order book depth, velocity, etc.

    # Factors increasing demand / reducing effective supply:
    # - DRIA paid for services (removed from immediate circulation for a time)
    # - DRIA staked (removed from circulation)
    # - DRIA burned (permanently removed)
    # - USD demand converted to DRIA buy pressure
    
    # Factors increasing supply / sell pressure:
    # - Newly vested tokens
    # - Newly emitted tokens (rewards)

    # Proxy for net buy pressure this month:
    buy_pressure = state.get("burned_from_fees_monthly_proposal", 0) + \
                   state.get("burned_from_usd_payments_monthly_proposal", 0) + \
                   state.get("slashed_dria_monthly_proposal", 0) + \
                   (state["current_dria_demand_per_month_proposal"] * 0.1) # Small fraction of DRIA service payments acting as buy pressure

    # Proxy for net sell pressure this month:
    sell_pressure = state.get("newly_vested_total_monthly_proposal", 0) + \
                    state.get("emitted_rewards_monthly_proposal", 0) # Net rewards after treasury cut

    # Simple ratio - can be refined
    if buy_pressure > 0: # Avoid division by zero if no buy pressure
        price_change_factor = (buy_pressure / (sell_pressure + 1)) -1 # +1 to avoid div by zero if no sell pressure
    elif sell_pressure > 0: # Only sell pressure
        price_change_factor = - (sell_pressure / (buy_pressure + 1)) # +1 to avoid div by zero
    else: # No pressure
        price_change_factor = 0

    # Dampen the change
    price_adjustment = price_change_factor * p.PRICE_ADJUSTMENT_SENSITIVITY_PROPOSAL
    
    # Cap adjustment to prevent extreme swings, e.g. +/- 20% per month from this factor
    price_adjustment = max(min(price_adjustment, 0.2), -0.2)

    state["simulated_dria_price_usd_proposal"] *= (1 + price_adjustment)
    state["simulated_dria_price_usd_proposal"] = max(state["simulated_dria_price_usd_proposal"], p.MIN_SIMULATED_DRIA_PRICE_USD_PROPOSAL)
    
    return state

def calculate_node_profitability_and_growth(state, p):
    """Calculates node profitability and adjusts node counts based on economic incentives."""
    
    # Calculate average rewards per node
    total_monthly_rewards = state.get("total_distributed_to_contributors_monthly", 0)
    current_nodes = state["current_contributor_nodes"]
    
    if current_nodes > 0:
        avg_rewards_per_node_dria = total_monthly_rewards / current_nodes
        # Convert to USD using current price
        avg_rewards_per_node_usd = avg_rewards_per_node_dria * state["simulated_dria_price_usd_proposal"]
        
        # Calculate profit/loss
        monthly_profit_usd = avg_rewards_per_node_usd - p.AVG_NODE_OPERATING_COST_USD_MONTHLY
        
        # Calculate target growth rate based on profitability
        if monthly_profit_usd > p.MIN_MONTHLY_PROFIT_USD_FOR_GROWTH:
            # Positive growth - more nodes want to join
            profit_ratio = monthly_profit_usd / p.MIN_MONTHLY_PROFIT_USD_FOR_GROWTH
            growth_rate = min(p.NODE_GROWTH_SENSITIVITY * profit_ratio, p.MAX_MONTHLY_NODE_GROWTH_RATE)
        else:
            # Negative growth - nodes may leave
            loss_ratio = monthly_profit_usd / p.MIN_MONTHLY_PROFIT_USD_FOR_GROWTH
            growth_rate = max(p.NODE_GROWTH_SENSITIVITY * loss_ratio, -p.MAX_MONTHLY_NODE_DECLINE_RATE)
            
        # Apply growth with lag effect
        target_nodes = current_nodes * (1 + growth_rate)
        # Move current_nodes some percentage of the way toward target_nodes
        adjustment_factor = 1 / p.NODE_COUNT_ADJUSTMENT_LAG_MONTHS
        new_node_count = int(current_nodes + (target_nodes - current_nodes) * adjustment_factor)
        
        # Ensure we don't go below a minimum threshold
        new_node_count = max(new_node_count, 100)  # Maintain at least 100 nodes
        
        state["current_contributor_nodes"] = new_node_count
        state["monthly_profit_per_node_usd"] = monthly_profit_usd
        state["node_growth_rate"] = growth_rate
    
    return state

def run_simulation_proposal(initial_state_proposal, p, num_years):
    """Runs the proposal-based simulation for the specified number of years."""
    history = []
    state = initial_state_proposal.copy()

    # Initial staking setup
    initial_total_stake = (state["current_validator_nodes"] * p.PROPOSAL_MIN_VALIDATOR_STAKE_DRIA) + \
                         (state["current_contributor_nodes"] * p.PROPOSAL_MIN_CONTRIBUTOR_STAKE_DRIA)
    state["total_dria_staked_proposal"] = initial_total_stake
    state["circulating_supply_proposal"] -= initial_total_stake
    state["circulating_supply_proposal"] = max(0, state["circulating_supply_proposal"])

    for year in range(1, num_years + 1):
        state["current_year"] = year
        
        for month in range(1, 13):
            state["current_month"] = month
            
            # --- Monthly Updates ---
            state = handle_vesting_proposal(state, p)
            
            # Handle emissions and get reward pool
            # emitted_this_timestep is the raw amount (base+buffer) potentially taken from the emission pool this month
            state, monthly_reward_pool_potential, treasury_cut_emissions, emitted_this_timestep = handle_emissions_proposal(state, p)
            
            # Distribute rewards to nodes, scaled by demand
            # actual_distributed_to_contributors is the amount that actually goes to nodes
            state, actual_distributed_to_contributors = distribute_epoch_rewards_proposal(state, p, monthly_reward_pool_potential)

            # Update treasury and circulating supply based on actual distributions
            state["treasury_balance_proposal"] += treasury_cut_emissions
            state["circulating_supply_proposal"] += actual_distributed_to_contributors + treasury_cut_emissions
            
            # Update the remaining emission pool by what was actually paid out (to nodes + treasury)
            # The initial `emitted_this_timestep` was a potential draw, including buffer and before demand scaling.
            # The actual reduction from the pool is the sum of what went to contributors and what went to treasury.
            amount_deducted_from_pool = actual_distributed_to_contributors + treasury_cut_emissions
            state["remaining_emission_pool_proposal"] -= amount_deducted_from_pool
            
            # Log the actual emissions that were distributed to nodes for this month
            state["emitted_rewards_monthly_proposal"] = actual_distributed_to_contributors
            # Log the portion of emissions that went to treasury
            state["emissions_to_treasury_monthly_proposal"] = treasury_cut_emissions

            state = handle_staking_and_slashing_proposal(state, p)
            
            # Process service fees
            state = handle_service_fees_proposal(state, p)
            
            # Update demand drivers
            state = update_demand_drivers_proposal(state, p)
            
            # Update simulated price
            state = update_simulated_price_proposal(state, p)
            
            # Calculate profitability and adjust node counts
            state = calculate_node_profitability_and_growth(state, p)
            
            # Record state for this timestep
            history.append(state.copy())
            
    return history

# Example of how to initialize and run (would typically be in main_proposal.py)
if __name__ == '__main__':
    # This section is for example/testing only. 
    # Real execution will be from main_proposal.py importing these functions.
    class MockParams:
        PROPOSAL_MAX_SUPPLY_DRIA = 100_000_000
        PROPOSAL_INITIAL_EPOCH_REWARD = 10000 # Adjusted for monthly simulation (e.g. total for month / epochs_in_month)
        PROPOSAL_HALVING_INTERVAL_EPOCHS = 210_000 
        PROPOSAL_EPOCHS_PER_TIMESTEP = (30*24*60)//10 # Approx epochs in a month if epoch is 10 min
        
        TEAM_PERCENT_PROPOSAL = 0.15
        ADVISORS_PERCENT_PROPOSAL = 0.05
        INVESTORS_PERCENT_PROPOSAL = 0.20
        ECOSYSTEM_FUND_PERCENT_PROPOSAL = 0.10
        TEAM_TOKENS_TOTAL_PROPOSAL = PROPOSAL_MAX_SUPPLY_DRIA * TEAM_PERCENT_PROPOSAL
        ADVISORS_TOKENS_TOTAL_PROPOSAL = PROPOSAL_MAX_SUPPLY_DRIA * ADVISORS_PERCENT_PROPOSAL
        INVESTORS_TOKENS_TOTAL_PROPOSAL = PROPOSAL_MAX_SUPPLY_DRIA * INVESTORS_PERCENT_PROPOSAL
        ECOSYSTEM_FUND_TOKENS_TOTAL_PROPOSAL = PROPOSAL_MAX_SUPPLY_DRIA * ECOSYSTEM_FUND_PERCENT_PROPOSAL
        EMISSION_SUPPLY_POOL_PROPOSAL = PROPOSAL_MAX_SUPPLY_DRIA - (TEAM_TOKENS_TOTAL_PROPOSAL + ADVISORS_TOKENS_TOTAL_PROPOSAL + INVESTORS_TOKENS_TOTAL_PROPOSAL + ECOSYSTEM_FUND_TOKENS_TOTAL_PROPOSAL)

        TEAM_VESTING_PROPOSAL = {"cliff": 12, "linear_months": 36}
        ADVISORS_VESTING_PROPOSAL = {"cliff": 12, "linear_months": 24}
        INVESTORS_VESTING_PROPOSAL = {"cliff": 6, "linear_months": 30}
        ECOSYSTEM_FUND_MONTHLY_RELEASE_PROPOSAL = ECOSYSTEM_FUND_TOKENS_TOTAL_PROPOSAL / (10*12)

        PROPOSAL_UPTIME_THRESHOLD_FOR_FULL_REWARDS = 0.95
        PROPOSAL_MIN_VALIDATOR_STAKE_DRIA = 5000
        PROPOSAL_MIN_CONTRIBUTOR_STAKE_DRIA = 100
        PROPOSAL_SLASHING_PERCENTAGE_VALIDATOR_DOWNTIME = 0.005
        PROPOSAL_SLASHING_PERCENTAGE_VALIDATOR_MALFEASANCE = 0.05
        PROPOSAL_SLASHING_PERCENTAGE_CONTRIBUTOR_FAILURE = 0.01
        PROPOSAL_AVG_TX_FEE_DRIA = 0.01
        PROPOSAL_SERVICE_FEE_PERCENT_OF_VALUE = 0.01
        USD_TO_DRIA_BURN_ACTIVE_PROPOSAL = True
        USD_TO_CREDIT_FX_FEE_PROPOSAL = 0.015
        PROPOSAL_TREASURY_TAX_RATE_FROM_EMISSIONS = 0.05
        PROPOSAL_TREASURY_TAX_RATE_FROM_FEES = 0.10
        PROPOSAL_INITIAL_CONTRIBUTOR_NODES = 1000
        PROPOSAL_INITIAL_VALIDATOR_NODES = 50
        PROPOSAL_AVG_UPTIME_PER_CONTRIBUTOR = 0.98
        PROPOSAL_AVG_GFLOPS_PER_CONTRIBUTOR_MONTHLY = 5000 # This is monthly, distribute_epoch_rewards will divide by epochs per month
        
        INITIAL_USD_CREDIT_PURCHASE_PER_MONTH_PROPOSAL = 100_000
        INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH = 200_000
        USD_DEMAND_GROWTH_RATE_MONTHLY_PROPOSAL = 0.01
        DRIA_DEMAND_GROWTH_RATE_MONTHLY_PROPOSAL = 0.01
        
        SIMULATION_YEARS = 1 # Short test
        SIMULATION_TIMESTEP_MONTHS = 1
        PROPOSAL_TOTAL_TIMESTEPS = SIMULATION_YEARS * 12
        # PROPOSAL_EPOCHS_PER_TIMESTEP already set
        PROPOSAL_TOTAL_SIMULATION_EPOCHS = SIMULATION_YEARS * 12 * PROPOSAL_EPOCHS_PER_TIMESTEP


        INITIAL_SIMULATED_DRIA_PRICE_USD_PROPOSAL = 0.50
        PRICE_ADJUSTMENT_SENSITIVITY_PROPOSAL = 0.01
        MIN_SIMULATED_DRIA_PRICE_USD_PROPOSAL = 0.001
        PROPOSAL_INITIAL_CIRCULATING_SUPPLY = 1_000_000
        
    mock_p = MockParams()

    initial_state_proposal_test = {
        "current_year": 1,
        "current_month": 0,
        "circulating_supply_proposal": mock_p.PROPOSAL_INITIAL_CIRCULATING_SUPPLY,
        "total_tokens_burned_proposal": 0,
        "total_tokens_slashed_proposal": 0,
        "simulated_dria_price_usd_proposal": mock_p.INITIAL_SIMULATED_DRIA_PRICE_USD_PROPOSAL,
        "remaining_emission_pool_proposal": mock_p.EMISSION_SUPPLY_POOL_PROPOSAL,
        "remaining_ecosystem_fund_tokens_proposal": mock_p.ECOSYSTEM_FUND_TOKENS_TOTAL_PROPOSAL,
        "treasury_balance_proposal": 0,
        "vested_team_tokens_proposal": 0,
        "vested_advisors_tokens_proposal": 0,
        "vested_investors_tokens_proposal": 0,
        "current_usd_demand_per_month_proposal": mock_p.INITIAL_USD_CREDIT_PURCHASE_PER_MONTH_PROPOSAL,
        "current_dria_demand_per_month_proposal": mock_p.INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH,
        "current_contributor_nodes": mock_p.PROPOSAL_INITIAL_CONTRIBUTOR_NODES,
        "current_validator_nodes": mock_p.PROPOSAL_INITIAL_VALIDATOR_NODES,
        "total_dria_staked_proposal": 0, # Will be initialized in run_simulation
        "current_total_epochs_passed": 0,
        "halvings_occurred": 0,
        # Monthly trackers (will be reset/updated each month in functions)
        "newly_vested_total_monthly_proposal":0,
        "ecosystem_fund_released_monthly_proposal":0,
        "emitted_rewards_monthly_proposal":0,
        "total_distributed_to_contributors_monthly":0,
        "slashed_dria_monthly_proposal":0,
        "validator_staking_rewards_monthly_proposal":0,
        "total_fees_generated_dria_monthly":0,
        "burned_from_fees_monthly_proposal":0,
        "burned_from_usd_payments_monthly_proposal":0,
        "current_epoch_reward_after_halving": 0,
        "total_emitted_this_timestep_before_treasury": 0,
        "fee_rewards_for_validators_monthly_proposal":0,

    }
    print(f"Starting test run with initial state: {initial_state_proposal_test}")
    history_test = run_simulation_proposal(initial_state_proposal_test, mock_p, mock_p.SIMULATION_YEARS)
    print(f"Test run completed. History length: {len(history_test)}")
    if history_test:
        print("Last state:")
        for key, value in history_test[-1].items():
            print(f"  {key}: {value}")