# sim/main_bme.py

import model_parameters_bme as p
import simulation_engine_bme as engine
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def main_bme():
    initial_state_bme = {
        "current_year": 1,
        "current_month": 0,
        "circulating_supply": p.BME_INITIAL_CIRCULATING_SUPPLY,
        "total_tokens_burned": 0,
        "total_tokens_emitted": 0,
        "dria_price_usd": p.BME_INITIAL_DRIA_PRICE_USD,
        "node_count": p.BME_INITIAL_NODE_COUNT,
        "usd_demand_per_month": p.BME_INITIAL_USD_CREDIT_PURCHASE_PER_MONTH,
        "dria_demand_per_month": p.BME_INITIAL_DRIA_PAYMENTS_FOR_SERVICES_PER_MONTH,
        "burned_from_usd_monthly": 0,
        "burned_from_dria_fees_monthly": 0,
        "emitted_rewards_monthly": 0,
        "monthly_profit_per_node_usd": 0,
        "node_growth_rate": 0,
    }

    print("--- Starting Dria Tokenomics Simulation (BME Model) ---\n")
    print(f"Initial State: {initial_state_bme}\n")
    print(f"Simulating for {p.BME_SIMULATION_YEARS} years with monthly timesteps.\n")

    simulation_history = engine.run_simulation_bme(initial_state_bme, p, p.BME_SIMULATION_YEARS)

    print("--- BME Simulation Complete ---\n")
    print(f"Total simulation steps (months): {len(simulation_history)}\n")

    if not simulation_history:
        print("No simulation history recorded. Exiting.")
        return

    df = pd.DataFrame(simulation_history)
    if df.empty:
        print ("DataFrame is empty, skipping plots.")
        return
    df['simulation_month_abs'] = range(1, len(df) + 1)

    num_plots_y = 4
    num_plots_x = 2
    plt.figure(figsize=(16, num_plots_y * 4))

    def format_y_axis(ax):
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M' if x >= 1e6 else (f'{x/1e3:.1f}K' if x >= 1e3 else f'{x:.1f}')))
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()

    plt.subplot(num_plots_y, num_plots_x, 1)
    plt.plot(df['simulation_month_abs'], df['circulating_supply'], label='Circulating Supply')
    plt.title('Circulating Supply')
    format_y_axis(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 2)
    plt.plot(df['simulation_month_abs'], df['total_tokens_burned'], label='Total Burned', color='red')
    plt.plot(df['simulation_month_abs'], df['total_tokens_emitted'], label='Total Emitted', color='green')
    plt.title('Cumulative Burned & Emitted')
    format_y_axis(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 3)
    plt.plot(df['simulation_month_abs'], df['dria_price_usd'], label='DRIA Price (USD)', color='blue')
    plt.title('Simulated DRIA Price (USD)')
    plt.gca().grid(True, linestyle='--', alpha=0.7); plt.gca().legend()

    plt.subplot(num_plots_y, num_plots_x, 4)
    plt.plot(df['simulation_month_abs'], df['node_count'], label='Node Count', color='purple')
    plt.title('Node Count')
    format_y_axis(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 5)
    plt.plot(df['simulation_month_abs'], df['burned_from_usd_monthly'], label='Burned from USD', color='orange')
    plt.plot(df['simulation_month_abs'], df['burned_from_dria_fees_monthly'], label='Burned from DRIA Fees', color='pink')
    plt.title('Monthly Token Burns')
    format_y_axis(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 6)
    plt.plot(df['simulation_month_abs'], df['emitted_rewards_monthly'], label='Emitted Rewards', color='green')
    plt.title('Monthly Emissions')
    format_y_axis(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 7)
    plt.plot(df['simulation_month_abs'], df['monthly_profit_per_node_usd'], label='Profit per Node (USD)', color='brown')
    plt.title('Monthly Profit per Node')
    format_y_axis(plt.gca())

    plt.subplot(num_plots_y, num_plots_x, 8)
    plt.plot(df['simulation_month_abs'], df['node_growth_rate'], label='Node Growth Rate', color='gray')
    plt.title('Node Growth Rate')
    format_y_axis(plt.gca())

    plt.tight_layout(pad=3.0)
    plt.show()

if __name__ == "__main__":
    main_bme() 