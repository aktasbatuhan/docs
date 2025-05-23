import streamlit as st
from sim import model_parameters as p_orig
from sim import model_parameters_proposal as p_prop
from sim import simulation_engine as engine_orig
from sim import simulation_engine_proposal as engine_prop
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# Brand colors
PRIMARY = '#0D9373'
LIGHT = '#07C983'
DARK = '#000000'
ANCHOR = '#00695C'

matplotlib.rcParams['axes.prop_cycle'] = matplotlib.cycler(color=[PRIMARY, LIGHT, ANCHOR, '#e67e22', '#e74c3c'])
matplotlib.rcParams['axes.facecolor'] = DARK
matplotlib.rcParams['figure.facecolor'] = DARK
matplotlib.rcParams['savefig.facecolor'] = DARK
matplotlib.rcParams['text.color'] = '#eaeaea'
matplotlib.rcParams['axes.labelcolor'] = '#eaeaea'
matplotlib.rcParams['xtick.color'] = '#eaeaea'
matplotlib.rcParams['ytick.color'] = '#eaeaea'

st.set_page_config(page_title="Dria Tokenomics Simulator", layout="wide")
st.title("Dria Tokenomics Simulator")
st.markdown("<style>body { background-color: #000000; color: #eaeaea; } .stApp { background-color: #000000; } </style>", unsafe_allow_html=True)

# Format y-axis for plots
def format_y_axis_for_plot(ax):
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()

# Create parameter dictionaries
def get_module_params(module):
    params = {}
    for name in dir(module):
        if name.isupper() and not name.startswith('__'):
            val = getattr(module, name)
            if isinstance(val, (int, float, bool, dict)):  # Added dict to supported types
                params[name] = {'value': val, 'type': type(val)}
    return params

# Initialize parameters
if 'params1' not in st.session_state:
    st.session_state.params1 = get_module_params(p_orig)
if 'params2' not in st.session_state:
    st.session_state.params2 = get_module_params(p_prop)
if 'df1' not in st.session_state:
    st.session_state.df1 = None
if 'df2' not in st.session_state:
    st.session_state.df2 = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# --- Navigation --- 
st.sidebar.header("Navigation")
current_page = st.sidebar.radio(
    "Go to",
    ("Dashboard", "Parameters"),
    key="navigation_choice"
)
st.session_state.current_page = current_page

# --- Parameter Input Rendering Function (Moved from sidebar) ---
def render_parameter_input_widget(name, param_info, prefix, context_key):
    """Render appropriate input widget based on parameter type"""
    val = param_info['value']
    param_type = param_info['type']
    widget_key = f"{context_key}_{prefix.lower().replace(' ', '_')}_{name}"

    if param_type is bool:
        return st.checkbox(
            f"{name.replace('_', ' ').title()}", 
            value=val,
            key=widget_key
        )
    elif param_type in (int, float):
        step = 1 if param_type is int else 0.0001
        # Ensure min_value is appropriate, especially for floats that can be small
        min_val = 0.0 if param_type is float and val >= 0 else None 
        return st.number_input(
            f"{name.replace('_', ' ').title()}", 
            value=val,
            min_value=min_val,
            step=step,
            key=widget_key,
            format="%.4f" if param_type is float else "%d"
        )
    elif param_type is dict:
        st.text(f"{name.replace('_', ' ').title()}:")
        st.json(val) # Display dicts as JSON, non-editable for now in this view
        return val # Return the original value as it's not edited here
    return val

# Create parameter objects that mimic the original modules
class ParamObject:
    def __init__(self, param_dict):
        for key, param_info in param_dict.items():
            setattr(self, key, param_info['value'])

p1 = ParamObject(st.session_state.params1)
p2 = ParamObject(st.session_state.params2)

# Run Sim 1
def run_sim1():
    """Runs the original simulation and returns its history."""
    initial_state_orig = {
        "current_year": 1,
        "current_month": 0,
        "circulating_supply": p1.INITIAL_CIRCULATING_SUPPLY,
        "total_tokens_burned": 0,
        "total_dria_staked": 0, # Initial stake will be calculated in handle_staking
        "current_node_count": p1.MIN_NODES, # Start with min nodes
        "simulated_dria_price_usd": p1.INITIAL_SIMULATED_DRIA_PRICE_USD,
        "remaining_node_rewards_pool_tokens": p1.NODE_RUNNER_REWARDS_POOL_TOTAL,
        "remaining_ecosystem_fund_tokens": p1.ECOSYSTEM_FUND_TOKENS_TOTAL, # Corrected name
        "vested_team_tokens": 0,
        "vested_advisors_tokens": 0,
        "vested_private_round_tokens": 0,
        "vested_current_round_tokens": 0,
        "current_usd_credit_purchase_per_month": p1.INITIAL_USD_CREDIT_PURCHASE_PER_MONTH,
        "current_dria_earned_by_on_prem_users_per_month": p1.DRIA_EARNED_BY_ON_PREM_USERS_PER_MONTH,
        "current_oracle_requests_per_month": p1.INITIAL_ORACLE_REQUESTS_PER_MONTH,
        "current_compute_demand_gflops_monthly": p1.INITIAL_SERVICE_DEMAND_GFLOPS_MONTHLY, # Corrected name
        "current_network_capacity_gflops_monthly": p1.INITIAL_NETWORK_CAPACITY_GFLOPS_PER_MONTH,
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
        'current_adjusted_base_staking_yield_annual': p1.BASE_STAKING_YIELD_RATE_ANNUAL,
        'network_utilization_rate': 0,
        'current_quarter_ecosystem_release_pool': 0,
        'current_quarter_ecosystem_released_so_far': 0,
    }
    history = engine_orig.run_simulation(initial_state_orig, p1.SIMULATION_YEARS)
    return pd.DataFrame(history)

def run_sim2():
    # Ensure node counts are always int (fixes bug where dict could be used)
    contributor_nodes = p2.PROPOSAL_INITIAL_CONTRIBUTOR_NODES
    if isinstance(contributor_nodes, dict):
        contributor_nodes = 30000  # fallback default
    validator_nodes = p2.PROPOSAL_INITIAL_VALIDATOR_NODES
    if isinstance(validator_nodes, dict):
        validator_nodes = 50  # fallback default

    initial_state_prop = {
        "current_year": 1,
        "current_month": 0,
        "circulating_supply_proposal": p2.PROPOSAL_INITIAL_CIRCULATING_SUPPLY,
        "total_tokens_burned_proposal": 0,
        "simulated_dria_price_usd_proposal": p2.INITIAL_SIMULATED_DRIA_PRICE_USD_PROPOSAL,
        "remaining_emission_pool_proposal": p2.EMISSION_SUPPLY_POOL_PROPOSAL,
        "remaining_ecosystem_fund_tokens_proposal": p2.ECOSYSTEM_FUND_TOKENS_TOTAL_PROPOSAL,
        "vested_team_tokens_proposal": 0,
        "vested_advisors_tokens_proposal": 0,
        "vested_investors_tokens_proposal": 0,
        "current_usd_demand_per_month_proposal": p2.INITIAL_USD_CREDIT_PURCHASE_PER_MONTH_PROPOSAL,
        "current_dria_demand_per_month_proposal": p2.INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH,
        "current_validator_nodes": int(validator_nodes),
        "current_contributor_nodes": int(contributor_nodes),
        "total_dria_staked_proposal": 0,
        "treasury_balance_proposal": 0,
        "total_tokens_slashed_proposal": 0,
        "burned_from_fees_monthly_proposal": 0,
        "ecosystem_fund_released_monthly_proposal": 0,
        "total_distributed_to_contributors_monthly": 0,
        "validator_staking_rewards_monthly_proposal": 0,
        "monthly_profit_per_node_usd": 0,
        "node_growth_rate": 0
    }
    history = engine_prop.run_simulation_proposal(initial_state_prop, p2, p2.SIMULATION_YEARS)
    return pd.DataFrame(history)

# Generate plots for Sim 1
def generate_plots_sim1(df):
    fig, axs = plt.subplots(5, 2, figsize=(15, 25))
    fig.patch.set_facecolor(DARK)
    
    # Plot 1: Circulating Supply
    axs[0, 0].plot(df['circulating_supply'], label='Circulating Supply', color=PRIMARY)
    axs[0, 0].plot(df['remaining_node_rewards_pool_tokens'], label='Remaining Node Rewards', color=LIGHT, linestyle=':')
    axs[0, 0].set_title('Circulating Supply & Rewards Pool')
    format_y_axis_for_plot(axs[0, 0])
    
    # Plot 2: Token Burns
    axs[0, 1].plot(df['total_tokens_burned'], label='Total Burned', color='red')
    axs[0, 1].plot(df['burned_from_usd_monthly'].cumsum(), label='From USD Payments', color='orange', linestyle='--')
    axs[0, 1].plot(df['burned_from_onprem_monthly'].cumsum(), label='From On-Prem', color='yellow', linestyle=':')
    axs[0, 1].plot(df['burned_from_oracle_monthly'].cumsum(), label='From Oracle', color='pink', linestyle='-.')
    axs[0, 1].set_title('Cumulative Token Burns')
    format_y_axis_for_plot(axs[0, 1])
    
    # Plot 3: DRIA Price
    axs[1, 0].plot(df['simulated_dria_price_usd'], label='DRIA Price (USD)', color='green')
    axs[1, 0].set_title('Simulated DRIA Price (USD)')
    format_y_axis_for_plot(axs[1, 0])
    
    # Plot 4: Monthly Inflows
    axs[1, 1].plot(df['newly_vested_total_monthly'], label='Newly Vested', color=LIGHT)
    axs[1, 1].plot(df['emitted_node_rewards_monthly'], label='Node Rewards', linestyle='--')
    axs[1, 1].plot(df['ecosystem_fund_released_monthly'], label='Ecosystem Fund')
    axs[1, 1].set_title('Monthly Token Inflows')
    format_y_axis_for_plot(axs[1, 1])
    
    # Plot 5: Node Count and Staking
    axs[2, 0].plot(df['current_node_count'], label='Node Count', color=PRIMARY)
    axs[2, 0].set_title('Node Count (with Lag)')
    format_y_axis_for_plot(axs[2, 0])
    
    # Plot 6: Total Staked
    axs[2, 1].plot(df['total_dria_staked'], label='Total DRIA Staked', color='brown')
    axs[2, 1].set_title('Total DRIA Staked')
    format_y_axis_for_plot(axs[2, 1])
    
    # Plot 7: Network Utilization
    axs[3, 0].plot(df['network_utilization_rate'] * 100, label='Network Utilization (%)', color='purple')
    axs[3, 0].set_title('Network Utilization (%)')
    axs[3, 0].set_ylim(0, 110)
    format_y_axis_for_plot(axs[3, 0])
    
    # Plot 8: Staking Yield
    axs[3, 1].plot(df['actual_node_apy_monthly_percentage'] * 12 * 100, label='Annual Staking Yield (%)', color='cyan')
    axs[3, 1].set_title('Annual Staking Yield (%)')
    format_y_axis_for_plot(axs[3, 1])
    
    # Plot 9: Treasury Balance
    if 'treasury_balance' in df.columns:
        axs[4, 0].plot(df['treasury_balance'], label='Treasury Balance', color='magenta')
        axs[4, 0].set_title('Treasury Balance (from Emissions)')
        format_y_axis_for_plot(axs[4, 0])
    else:
        axs[4, 0].set_title('Treasury Balance (N/A)')
    
    # Plot 10: Node Count Smoothing (Lag Visualization)
    axs[4, 1].plot(df['current_node_count'], label='Node Count (Lagged)', color=PRIMARY)
    axs[4, 1].set_title('Node Join/Leave Lag (Smoothed Node Count)')
    format_y_axis_for_plot(axs[4, 1])
    
    plt.tight_layout()
    return fig

# Generate plots for Sim 2
def generate_plots_sim2(df):
    fig, axs = plt.subplots(6, 2, figsize=(16, 28))
    fig.patch.set_facecolor(DARK)
    # 1. Circulating Supply & Emission Pool
    axs[0, 0].plot(df['circulating_supply_proposal'], label='Circulating Supply', color=PRIMARY)
    axs[0, 0].plot(df['remaining_emission_pool_proposal'], label='Emission Pool', color=LIGHT, linestyle=':')
    axs[0, 0].set_title('Circulating Supply & Emission Pool')
    format_y_axis_for_plot(axs[0, 0])
    # 2. Token Burns
    axs[0, 1].plot(df['total_tokens_burned_proposal'], label='Total Burned', color='red')
    axs[0, 1].plot(df['burned_from_usd_payments_monthly_proposal'].cumsum(), label='From USD Payments', color='orange', linestyle='--')
    axs[0, 1].plot(df['burned_from_fees_monthly_proposal'].cumsum(), label='From Fees', color='yellow', linestyle=':')
    axs[0, 1].set_title('Token Burns (Cumulative)')
    format_y_axis_for_plot(axs[0, 1])
    # 3. Treasury Balance & Outflows
    axs[1, 0].plot(df['treasury_balance_proposal'], label='Treasury Balance', color='purple')
    axs[1, 0].plot(df['treasury_outflow_monthly_proposal'].cumsum(), label='Cumulative Outflows', color='pink', linestyle='--')
    axs[1, 0].set_title('Treasury Balance & Outflows')
    format_y_axis_for_plot(axs[1, 0])
    # 4. Validator & Contributor Node Counts
    axs[1, 1].plot(df['current_validator_nodes'], label='Validators', color='blue')
    axs[1, 1].plot(df['current_contributor_nodes'], label='Contributors', color='green')
    axs[1, 1].set_title('Validator & Contributor Node Counts')
    format_y_axis_for_plot(axs[1, 1])
    # 5. Validator Rewards & Fee Share
    axs[2, 0].plot(df['validator_staking_rewards_monthly_proposal'], label='Validator Staking Rewards', color='navy')
    axs[2, 0].plot(df['fee_rewards_for_validators_monthly_proposal'], label='Validator Fee Rewards', color='teal', linestyle='--')
    axs[2, 0].set_title('Validator Rewards (Staking & Fees)')
    format_y_axis_for_plot(axs[2, 0])
    # 6. Demand Shocks & User Churn Events
    axs[2, 1].plot(df['demand_shock_event'], label='Demand Shock Multiplier', color='orange')
    axs[2, 1].plot(df['user_churn_event'].astype(int), label='User Churn Event', color='red', linestyle=':')
    axs[2, 1].set_title('Demand Shocks & User Churn Events')
    format_y_axis_for_plot(axs[2, 1])
    # 7. Node Growth Rates
    axs[3, 0].plot(df['validator_growth_rate'], label='Validator Growth Rate', color='blue')
    axs[3, 0].plot(df['contributor_growth_rate'], label='Contributor Growth Rate', color='green', linestyle='--')
    axs[3, 0].set_title('Node Growth Rates')
    # 8. Monthly Profits
    axs[3, 1].plot(df['monthly_profit_per_validator_usd'], label='Validator Profit (USD)', color='blue')
    axs[3, 1].plot(df['monthly_profit_per_contributor_usd'], label='Contributor Profit (USD)', color='green', linestyle='--')
    axs[3, 1].set_title('Monthly Profits per Node')
    # 9. Demand (USD & DRIA)
    axs[4, 0].plot(df['current_usd_demand_per_month_proposal'], label='USD Demand', color='black')
    axs[4, 0].plot(df['current_dria_demand_per_month_proposal'], label='DRIA Demand', color='gray', linestyle='--')
    axs[4, 0].set_title('User Demand (USD & DRIA)')
    format_y_axis_for_plot(axs[4, 0])
    # 10. Simulated DRIA Price
    axs[4, 1].plot(df['simulated_dria_price_usd_proposal'], label='Simulated DRIA Price (USD)', color='gold')
    axs[4, 1].set_title('Simulated DRIA Price (USD)')
    format_y_axis_for_plot(axs[4, 1])
    # 11. Emissions to Treasury & Contributors
    axs[5, 0].plot(df['emissions_to_treasury_monthly_proposal'].cumsum(), label='Emissions to Treasury', color='purple')
    axs[5, 0].plot(df['emitted_rewards_monthly_proposal'].cumsum(), label='Emissions to Contributors', color='green', linestyle='--')
    axs[5, 0].set_title('Emissions to Treasury & Contributors (Cumulative)')
    format_y_axis_for_plot(axs[5, 0])
    # 12. Total Distributed to Contributors (Cumulative)
    axs[5, 1].plot(df['total_distributed_to_contributors_monthly'].cumsum(), label='Total to Contributors', color='green')
    axs[5, 1].set_title('Total Distributed to Contributors (Cumulative)')
    format_y_axis_for_plot(axs[5, 1])
    for ax in axs.flat:
        ax.legend()
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig

# --- Screens ---
def render_dashboard_screen():
    st.header("Simulation Dashboard")
    # --- Main layout for dashboard ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sim 1: Original Model")
        run_sim1_button = st.button("Run Simulation 1", key="run_sim1_dashboard")
        
        if run_sim1_button:
            with st.spinner("Running Simulation 1..."):
                st.session_state.df1 = run_sim1() # Assumes run_sim1 uses p1 from session_state
            st.success("Simulation 1 complete!")
        
        if st.session_state.df1 is not None:
            st.text("Data Preview (Sim 1)")
            st.dataframe(st.session_state.df1.head(10))
            st.text("Visualizations (Sim 1)")
            fig1 = generate_plots_sim1(st.session_state.df1)
            st.pyplot(fig1)

    with col2:
        st.subheader("Sim 2: Proposal Model")
        run_sim2_button = st.button("Run Simulation 2", key="run_sim2_dashboard")
        
        if run_sim2_button:
            with st.spinner("Running Simulation 2..."):
                st.session_state.df2 = run_sim2() # Assumes run_sim2 uses p2 from session_state
            st.success("Simulation 2 complete!")
        
        if st.session_state.df2 is not None:
            st.text("Data Preview (Sim 2)")
            st.dataframe(st.session_state.df2.head(10))
            st.text("Visualizations (Sim 2)")
            fig2 = generate_plots_sim2(st.session_state.df2)
            st.pyplot(fig2)

def render_parameters_screen():
    st.header("Configure Simulation Parameters")
    
    # Create parameter objects from session state for current values
    # This ensures that changes made on this screen are reflected when simulations are run
    p1_current = ParamObject(st.session_state.params1)
    p2_current = ParamObject(st.session_state.params2)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sim 1: Original Model Parameters")
        for name, param_info in st.session_state.params1.items():
            # Use a unique context key for this screen to avoid conflicts with potential sidebar widgets if any remained
            new_val = render_parameter_input_widget(name, param_info, "Sim 1", "params_screen_s1")
            if new_val != param_info['value']: # Update session state only if value changed
                 st.session_state.params1[name]['value'] = param_info['type'](new_val)
                 st.experimental_rerun() # Rerun to reflect change immediately and update p1_current

    with col2:
        st.subheader("Sim 2: Proposal Model Parameters")
        for name, param_info in st.session_state.params2.items():
            new_val = render_parameter_input_widget(name, param_info, "Sim 2", "params_screen_s2")
            if new_val != param_info['value']: # Update session state only if value changed
                st.session_state.params2[name]['value'] = param_info['type'](new_val)
                st.experimental_rerun()

    # Update the global p1 and p2 objects that run_sim functions use
    # This is crucial for the simulation functions to pick up changes made on this screen.
    # Need to re-instantiate them based on potentially updated session state.
    global p1, p2
    p1 = ParamObject(st.session_state.params1)
    p2 = ParamObject(st.session_state.params2)

    st.markdown("---_Note: Changes are saved automatically. Navigate to Dashboard to run simulations._---")

# --- Main App Logic --- 
if st.session_state.current_page == "Dashboard":
    # Ensure p1 and p2 are up-to-date before rendering dashboard or running sims
    p1 = ParamObject(st.session_state.params1)
    p2 = ParamObject(st.session_state.params2)
    render_dashboard_screen()
elif st.session_state.current_page == "Parameters":
    render_parameters_screen()
