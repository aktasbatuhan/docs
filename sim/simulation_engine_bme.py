# sim/simulation_engine_bme.py
import math
import random

def run_simulation_bme(initial_state, p, num_years):
    state = initial_state.copy()
    history = []
    for year in range(1, num_years + 1):
        state["current_year"] = year
        for month in range(1, 13):
            state["current_month"] = month
            # --- Demand Growth ---
            state["usd_demand_per_month"] *= (1 + p.BME_USD_DEMAND_GROWTH_RATE_MONTHLY)
            state["dria_demand_per_month"] *= (1 + p.BME_DRIA_DEMAND_GROWTH_RATE_MONTHLY)

            # --- Burn USD Income (Buy-and-Burn) ---
            if state["dria_price_usd"] > 0:
                dria_bought_for_burn = state["usd_demand_per_month"] / state["dria_price_usd"]
            else:
                dria_bought_for_burn = 0
            burned_from_usd = dria_bought_for_burn * p.BME_BURN_PERCENT_OF_USD_INCOME
            state["circulating_supply"] -= burned_from_usd
            state["total_tokens_burned"] += burned_from_usd
            state["burned_from_usd_monthly"] = burned_from_usd

            # --- Burn DRIA Service Fees ---
            burned_from_dria_fees = state["dria_demand_per_month"] * p.BME_BURN_PERCENT_OF_DRIA_FEES
            state["circulating_supply"] -= burned_from_dria_fees
            state["total_tokens_burned"] += burned_from_dria_fees
            state["burned_from_dria_fees_monthly"] = burned_from_dria_fees

            # --- Emit Fixed Rewards ---
            emission_this_month = p.BME_FIXED_EMISSION_PER_MONTH
            state["circulating_supply"] += emission_this_month
            state["total_tokens_emitted"] += emission_this_month
            state["emitted_rewards_monthly"] = emission_this_month

            # --- Node Economics (Growth/Churn) ---
            # Simple profitability-based node count adjustment
            avg_rewards_per_node = emission_this_month / state["node_count"] if state["node_count"] > 0 else 0
            avg_rewards_per_node_usd = avg_rewards_per_node * state["dria_price_usd"]
            monthly_profit_usd = avg_rewards_per_node_usd - p.BME_AVG_NODE_OPERATING_COST_USD_MONTHLY
            if monthly_profit_usd > p.BME_MIN_MONTHLY_PROFIT_USD_FOR_GROWTH:
                profit_ratio = monthly_profit_usd / p.BME_MIN_MONTHLY_PROFIT_USD_FOR_GROWTH
                growth_rate = min(profit_ratio * p.BME_MAX_MONTHLY_NODE_GROWTH_RATE, p.BME_MAX_MONTHLY_NODE_GROWTH_RATE)
            else:
                loss_ratio = monthly_profit_usd / p.BME_MIN_MONTHLY_PROFIT_USD_FOR_GROWTH
                growth_rate = max(loss_ratio * p.BME_MAX_MONTHLY_NODE_DECLINE_RATE, -p.BME_MAX_MONTHLY_NODE_DECLINE_RATE)
            target_node_count = state["node_count"] * (1 + growth_rate)
            adjustment_factor = 1 / p.BME_NODE_COUNT_ADJUSTMENT_LAG_MONTHS
            new_node_count = int(state["node_count"] + (target_node_count - state["node_count"]) * adjustment_factor)
            new_node_count = max(new_node_count, 100)
            state["node_count"] = new_node_count
            state["monthly_profit_per_node_usd"] = monthly_profit_usd
            state["node_growth_rate"] = growth_rate

            # --- Price Simulation (Simple Supply/Demand) ---
            buy_pressure = burned_from_usd + burned_from_dria_fees + (state["dria_demand_per_month"] * 0.1)
            sell_pressure = emission_this_month
            if buy_pressure > 0:
                price_change_factor = (buy_pressure / (sell_pressure + 1)) - 1
            elif sell_pressure > 0:
                price_change_factor = - (sell_pressure / (buy_pressure + 1))
            else:
                price_change_factor = 0
            price_adjustment = price_change_factor * p.BME_PRICE_ADJUSTMENT_SENSITIVITY
            price_adjustment = max(min(price_adjustment, 0.2), -0.2)
            state["dria_price_usd"] *= (1 + price_adjustment)
            state["dria_price_usd"] = max(state["dria_price_usd"], p.BME_MIN_DRIA_PRICE_USD)

            # --- Record State ---
            history.append(state.copy())
    return history 