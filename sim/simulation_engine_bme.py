# sim/simulation_engine_bme.py
import math
import random
import numpy as np

def run_simulation_bme(initial_state, p, num_years):
    state = initial_state.copy()
    history = []
    for year in range(1, num_years + 1):
        state["current_year"] = year
        for month in range(1, 13):
            state["current_month"] = month
            # --- Market Feature Extraction ---
            market_trend_series = state.get('market_trend_monthly_pct_change')
            base_growth_rate = state.get('base_usd_demand_growth_rate', p.BME_USD_DEMAND_GROWTH_RATE_MONTHLY)
            impact_factor = state.get('market_trend_impact_factor', 0.5)
            market_features_df = state.get('market_features_df')
            current_sim_month_index = (state["current_year"] - 1) * 12 + (state["current_month"] - 1)
            trend_influence = 0.0
            volatility_30d = 0.0
            drawdown = 0.0
            regime = 'sideways'
            extreme_event = False
            if market_features_df is not None and len(market_features_df) > current_sim_month_index:
                features_row = market_features_df.iloc[current_sim_month_index]
                trend_influence = features_row.get('trend_index', 0.0)
                volatility_30d = features_row.get('volatility_30d', 0.0)
                drawdown = features_row.get('drawdown', 0.0)
                regime = features_row.get('regime', 'sideways')
                extreme_event = features_row.get('extreme_event', False)
            else:
                if market_trend_series is not None and not isinstance(market_trend_series, type(None)) and len(market_trend_series) > current_sim_month_index:
                    trend_influence = market_trend_series.iloc[current_sim_month_index]
            # --- Trend: modulate growth rate ---
            effective_growth_rate = base_growth_rate * (1 + trend_influence * impact_factor)
            # --- Regime: switch between optimistic/pessimistic growth ---
            if regime == 'bull':
                effective_growth_rate *= 1.2
            elif regime == 'bear':
                effective_growth_rate *= 0.8
            # --- Volatility: modulate churn/staking (example: increase churn if high volatility) ---
            churn_multiplier = 1.0
            if volatility_30d > 0.08:
                churn_multiplier += 0.05
            # --- Drawdown: trigger panic events ---
            if drawdown < -0.3:
                effective_growth_rate *= 0.5
                churn_multiplier += 0.10
            # --- Extreme event: apply random demand shock ---
            if extreme_event:
                effective_growth_rate *= np.random.uniform(0.7, 1.3)
            # --- Apply to demand drivers ---
            state["usd_demand_per_month"] *= (1 + effective_growth_rate)
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
            profit_per_node = avg_rewards_per_node - p.BME_AVG_NODE_OPERATING_COST_USD_MONTHLY
            if profit_per_node > p.BME_MIN_MONTHLY_PROFIT_USD_FOR_GROWTH:
                growth_rate = min(p.BME_MAX_MONTHLY_NODE_GROWTH_RATE * (profit_per_node / p.BME_MIN_MONTHLY_PROFIT_USD_FOR_GROWTH), p.BME_MAX_MONTHLY_NODE_GROWTH_RATE)
            else:
                growth_rate = max(-p.BME_MAX_MONTHLY_NODE_DECLINE_RATE * (abs(profit_per_node) / p.BME_MIN_MONTHLY_PROFIT_USD_FOR_GROWTH), -p.BME_MAX_MONTHLY_NODE_DECLINE_RATE)
            # Optionally, modulate node churn by churn_multiplier
            growth_rate *= (1 - 0.5 * (churn_multiplier - 1))
            target_node_count = state["node_count"] * (1 + growth_rate)
            lag = max(p.BME_NODE_COUNT_ADJUSTMENT_LAG_MONTHS, 1)
            new_node_count = state["node_count"] + (target_node_count - state["node_count"]) / lag
            state["node_count"] = max(int(round(new_node_count)), 1)

            # --- Price Update Based on Supply/Demand ---
            # Simple price model: price reacts to burns vs emissions
            total_burned_this_month = burned_from_usd + burned_from_dria_fees
            net_supply_change = emission_this_month - total_burned_this_month
            
            # Price pressure calculation
            if state["circulating_supply"] > 0:
                supply_pressure = net_supply_change / state["circulating_supply"]
            else:
                supply_pressure = 0
                
            # Demand pressure from growth
            demand_pressure = effective_growth_rate * 0.5  # Growth translates to some price pressure
            
            # Net price change
            price_change_factor = demand_pressure - supply_pressure
            price_adjustment = price_change_factor * p.BME_PRICE_ADJUSTMENT_SENSITIVITY
            
            # Apply price change with bounds
            price_adjustment = max(min(price_adjustment, 0.2), -0.2)  # Cap at +/- 20% per month
            state["dria_price_usd"] *= (1 + price_adjustment)
            state["dria_price_usd"] = max(state["dria_price_usd"], p.BME_MIN_DRIA_PRICE_USD)
            
            # Store monthly metrics
            state["monthly_profit_per_node_usd"] = profit_per_node
            state["node_growth_rate"] = growth_rate

            history.append(state.copy())
    return history 