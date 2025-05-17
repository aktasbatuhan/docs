# Dria Tokenomics Simulation Plan

## Goal
To build a comprehensive simulation model of Dria's tokenomics to backtest its mechanics, understand its sensitivities, and project its behavior under various scenarios, including historically-informed demand patterns.

## Phases & Tasks

---

### Phase 1: Model Definition & Parameterization
*(Goal: Create a detailed mathematical and logical model of Dria's tokenomics.)*

*   [ ] **1.1. Deep Dive into Dria's Mechanics:**
    *   [ ] **Map Core Levers:** Explicitly define every mechanism affecting token supply and demand.
        *   [ ] **Emission:**
            *   [x] Max supply (1 Billion `$DRIA`).
            *   [x] Node Runner Rewards Pool size (35% of total supply).
            *   [x] Detailed 10-year disinflationary schedule (14% down to 2% of remaining rewards pool annually).
            *   [~] Compute-linked issuance rule (tokens minted *only* for verified FLOPS). (V1 implemented based on network utilization)
        *   [ ] **Burn Mechanisms:**
            *   [x] USD-to-Credit: USD buys `$DRIA` from market -> `$DRIA` is burned. (Define conversion efficiency/fees).
            *   [x] On-Prem Conversion: `$DRIA` earned from idle compute -> converted to credits (Define portion burned).
            *   [x] Oracle Node Usage: Direct `$DRIA` payment -> credits consumed -> (Define portion of `$DRIA` burned).
        *   [ ] **Staking:**
            *   [x] Minimum stake requirements per node/tier.
            *   [x] Staking yield rates/calculation. (Base yield in params, but not yet affecting node decisions)
            *   [~] Impact on node participation and token lock-up. (V1 implemented: node growth, staked DRIA affects liquid supply & price pressure)
        *   [x] **Allocations & Vesting:** (Variable, use current doc values as baseline)
            *   [x] Team (9%): 12-month cliff, then 36-month linear monthly vesting.
            *   [x] Advisors (5%): 12-month cliff, then 24-month linear monthly vesting.
            *   [x] Private Round Investors (16%): Define vesting.
            *   [x] Current Investment Round (5%): Define vesting.
            *   [x] Ecosystem Fund & Community (30%): Model release schedule/triggers.
            *   [x] Treasury & Foundation: Model usage/disbursement. (Covered by Ecosystem Fund)
    *   [~] **Quantify Relationships:** For each lever, define the mathematical relationship.
        *   Vesting schedules implemented.
        *   Base emission schedule (non-compute-linked) implemented.
        *   Ecosystem fund release implemented.
        *   Basic burn mechanisms (USD, On-Prem, Oracle) with static demand drivers implemented.
        *   Simplified dynamic price mechanism implemented.
        *   Still to do: Compute-linked issuance, staking impact, more dynamic demand drivers.

*   [ ] **1.2. Identify Key Input Variables:**
    *   [~] **Demand-Side Drivers:**
        *   [x] `USD_CreditPurchase_Rate`: Volume/frequency of credits bought with USD. (Implemented with growth rate)
        *   [ ] `DRIA_CreditPurchase_Rate`: Volume/frequency of credits bought with `$DRIA`. (Placeholder exists, not fully dynamic yet)
        *   [x] `OnPrem_Compute_Contribution_Rate`: Rate of idle compute (FLOPS) provided by on-prem users. (Simplified as `DRIA_EARNED_BY_ON_PREM_USERS_PER_MONTH` with growth)
        *   [x] `OnPrem_Credit_Conversion_Rate`: Rate at which earned `$DRIA` is converted to credits by on-prem users.
        *   [x] `Oracle_Usage_Rate`: Volume/frequency of oracle node service requests. (Implemented with growth rate)
        *   [x] `Overall_Compute_Demand_Growth_Rate`: Projected growth in total network compute (FLOPS) demanded. (Implemented)
    *   [~] **Supply-Side Drivers (Node Ecosystem):**
        *   [x] Initial Node Distribution (35,000 total, categorized): (Using `INITIAL_NODE_COUNT`)
            *   [ ] `Nodes_Cat_A` (up to 1.5B models): Define count & avg FLOPS.
            *   [ ] `Nodes_Cat_B` (up to 3B models): Define count & avg FLOPS.
            *   [ ] `Nodes_Cat_C` (up to 12B models): Define count & avg FLOPS.
            *   [ ] `Nodes_Cat_D` (up to 70B models): Define count & avg FLOPS.
            *   [ ] Assume 24/7 uptime initially.
        *   [x] `Total_Initial_FLOPS_Capacity`: Calculated from initial node distribution. (Simplified as `INITIAL_NETWORK_CAPACITY_GFLOPS_PER_MONTH` with growth)
        *   [~] `Node_Adoption_Rate_Function`: Model how new nodes (and FLOPS) join based on profitability/incentives. (Simplified as `NODE_COUNT_GROWTH_RATE_MONTHLY` and `NETWORK_CAPACITY_GROWTH_RATE_MONTHLY`)
        *   [ ] `Node_Churn_Rate_Function`: Model how nodes leave based on profitability/other factors.
        *   [x] `Avg_DRIA_Staked_Per_Node`: Average stake, potentially varying by node tier. (Using `MINIMUM_NODE_STAKE_DRIA`)
        *   [ ] `Node_Operating_Costs`: (To be researched/estimated)
            *   [ ] Cloud Servers: Cost per FLOP/hour (e.g., from AWS/GCP/Azure typical instances).
            *   [ ] Existing Devices: Electricity cost per FLOP/hour (estimate based on typical hardware).
            *   [ ] New Devices (e.g., RTX 4090): Amortized hardware cost + electricity per FLOP/hour.
    *   [ ] **External Market Factors (for advanced scenarios/backtesting):**
        *   [ ] Overall crypto market sentiment proxy (e.g., index, BTC dominance).
        *   [ ] Price/activity of broadly comparable DePIN projects.

*   [ ] **1.3. Define Output Metrics & Key Performance Indicators (KPIs):**
    *   [ ] `Circulating_Supply_Over_Time`
    *   [ ] `Total_DRIA_Burned_Over_Time` (and by each mechanism)
    *   [ ] `Net_Inflation_Rate` (Emissions - Burns as % of circ. supply)
    *   [ ] `Node_Runner_Profitability` (Revenue from Rewards - Operating Costs)
    *   [ ] `Node_Runner_APY_Effective` (Staking + Compute Rewards relative to stake & costs)
    *   [ ] `Total_Network_Capacity_FLOPS`
    *   [ ] `Network_Utilization_Rate` (Demand FLOPS / Capacity FLOPS)
    *   [ ] `Treasury_Balance_Over_Time` (If applicable)
    *   [ ] `Token_Velocity_Proxy` (Simulated, e.g., ratio of transacted volume to circulating supply within the model)
    *   [ ] `Ecosystem_Demand_Supply_Ratio_Credits`
    *   [ ] `Simulated_Buy_Sell_Pressure_Ratio`: (e.g., ratio of tokens entering buy-side demand like USD burns, staking vs. tokens potentially sold like unlocked rewards).
    *   [ ] `Token_Price_Stability_Proxy`: (e.g., volatility of the simulated buy/sell pressure ratio, or stability of node profitability under different demand shocks. Direct price simulation is complex and secondary to mechanism robustness).

*   [ ] **1.4. Explicitly Document Initial Assumptions:**
    *   [ ] Starting values for all input variables based on current data and best estimates.
    *   [ ] Projected growth rates for demand drivers (e.g., user adoption, new services).
    *   [ ] User behavior assumptions (e.g., % of USD vs. `$DRIA` payments).
    *   [ ] Node runner behavior assumptions (e.g., staking behavior, sensitivity to APY).

---

### Phase 2: Data Collection & Preparation
*(Goal: Gather all necessary data to power the simulation and benchmark scenarios.)*

*   [ ] **2.1. Dria's Internal Data & Parameters:**
    *   [ ] Current node runner statistics (35k nodes, categorized by capacity, initial FLOPS estimates per category).
    *   [ ] Finalized (or baseline for variability) token allocation percentages and vesting schedules.
    *   [ ] Node operating cost estimates (requires initial research for cloud, electricity, hardware).
        *   [ ] *Action: Perform web search for typical cloud GPU costs, electricity rates, consumer GPU (e.g., RTX 4090) prices.*
*   [ ] **2.2. Historical Data for Comparable Projects (e.g., RNDR, FIL, AKT, TAO, IO.net):**
    *   [ ] Daily/weekly token price.
    *   [ ] Circulating supply over time.
    *   [ ] Network activity metrics (active nodes, compute jobs, revenue).
    *   [ ] Staking data (TVL, APY variations).
    *   [ ] Major protocol events or market-moving news.
    *   *Sources: User-provided APIs, CoinGecko/CoinMarketCap APIs, Messari, TokenTerminal, Dune Analytics, project explorers.*
*   [ ] **2.3. General Crypto Market Data:**
    *   [ ] BTC/ETH price history.
    *   [ ] Total crypto market capitalization.
    *   [ ] Relevant sector indices (e.g., DePIN).
*   [ ] **2.4. Data Cleaning & Preparation:**
    *   [ ] Normalize data frequencies.
    *   [ ] Handle missing data.
    *   [ ] Align time series for comparative analysis.

---

### Phase 3: Baseline Simulation & Scenario Modeling
*(Goal: Simulate Dria's tokenomics under Dria's own projections and test sensitivities.)*

*   [ ] **3.1. Build the Simulation Engine:**
    *   [ ] Choose environment (Python with Pandas/NumPy/Matplotlib/Seaborn recommended).
    *   [ ] Implement core logic based on Dria's mechanics (Phase 1.1).
    *   [ ] Structure for modularity to easily change parameters and scenarios.
*   [ ] **3.2. Simulate Baseline Scenario:**
    *   [ ] Initialize with Dria's current node stats & FLOPS, team's demand-side assumptions.
    *   [ ] Run simulation over a defined period (e.g., 1, 3, 5 years).
    *   [ ] Track all defined KPIs.
*   [ ] **3.3. Develop & Test Multiple Scenarios:**
    *   [ ] **Optimistic Case:** High demand, rapid node adoption, high platform usage.
    *   [ ] **Pessimistic Case:** Slow demand, low node participation, low platform usage.
    *   [ ] **Specific Stress Tests:**
        *   [ ] Sudden drop in node count/network capacity.
        *   [ ] Extreme market volatility impacting USD-to-`$DRIA` conversion rates for burns.
        *   [ ] Changes in major comparable project performance.
    *   [ ] **Sensitivity Analysis:** Systematically vary key input parameters (e.g., USD purchase rate by +/- 10%, oracle burn percentage by +/- 0.1%, node adoption elasticity) to observe impact on KPIs. Identify most critical levers.

---

### Phase 4: Historically-Informed Scenario Simulation
*(Goal: Understand how Dria's unique mechanics might have performed under past market conditions/demand patterns experienced by other tokens.)*

*   [ ] **4.1. Identify Key Historical Periods & Demand Proxies:**
    *   [ ] From comparable project data (Phase 2.2), identify periods of high growth, stagnation, high/low staking, etc.
    *   [ ] Extract *patterns of demand for compute/network services* or *investor sentiment shifts* (e.g., "Compute demand in DePIN sector grew X% monthly during period Y," or "Staking participation dropped Z% during market crash Q").
*   [ ] **4.2. Translate Historical Patterns to Dria's Demand Inputs:**
    *   [ ] Hypothesize how these historical demand/sentiment patterns would translate into specific values or shocks for Dria's demand input variables (e.g., `Overall_Compute_Demand_Growth_Rate`, `Node_Adoption_Rate_Function` parameters).
*   [ ] **4.3. Simulate Dria with Historical Demand Patterns:**
    *   [ ] Run Dria's simulation model using its unique emission, burn, and staking rules, but driven by these historically-informed demand inputs.
    *   [ ] Focus on observing how Dria's internal metrics (circulating supply, burn volumes, node incentives, network utilization) react and self-regulate.

---

### Phase 5: Analysis, Insights & Iteration
*(Goal: Extract actionable insights, refine the model, and communicate findings.)*

*   [ ] **5.1. Analyze Simulation Outputs:**
    *   [ ] Compare KPIs across all scenarios.
    *   [ ] Identify potential bottlenecks, risks, or areas of over/under-supply.
    *   [ ] Assess the long-term sustainability of deflationary mechanisms vs. emissions.
    *   [ ] Evaluate the conditions under which node profitability remains attractive.
*   [ ] **5.2. Visualize Results:**
    *   [ ] Create clear charts, dashboards, and summaries for each scenario and KPI.
*   [ ] **5.3. Refine Dria's Tokenomics (If Necessary):**
    *   [ ] Based on simulation insights, discuss potential adjustments to parameters (e.g., emission rates, burn percentages, staking rewards, vesting schedules) to better achieve strategic goals.
*   [ ] **5.4. Document Everything:**
    *   [ ] Maintain comprehensive documentation of assumptions, data sources, model logic, scenarios, results, and conclusions for each iteration.
*   [ ] **5.5. Iterative Process:**
    *   [ ] Plan for ongoing updates to the model as Dria launches, real-world data becomes available, and the market evolves. Regularly re-validate assumptions.

--- 