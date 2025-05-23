import pandas as pd
import yfinance as yf
import requests
import time
from datetime import datetime

# Token lists (Yahoo tickers and CoinLore symbols)
YAHOO_TICKERS = {
    'BTC': 'BTC-USD',
    'ETH': 'ETH-USD',
    'BNB': 'BNB-USD',
    'XRP': 'XRP-USD',
    'SOL': 'SOL-USD',
    'DOGE': 'DOGE-USD',
    'ADA': 'ADA-USD',
    'AVAX': 'AVAX-USD',
    'TRX': 'TRX-USD',
    'DOT': 'DOT-USD',
    'MATIC': 'MATIC-USD',
    'LINK': 'LINK-USD',
    'NEAR': 'NEAR-USD',
    'OP': 'OP-USD',
    'ARB': 'ARB-USD',
    'APT': 'APT-USD',
    'STX': 'STX-USD',
    'ICP': 'ICP-USD',
    # Add more if available
}
COINLORE_SYMBOLS = [
    'TON', 'TAO', 'RNDR', 'AKT', 'FIL', 'HNT', 'FET', 'GLM', 'STORJ', 'LPT', 'OCEAN', 'SUI',
    # Add more if needed
]

ALL_TOKENS = list(YAHOO_TICKERS.keys()) + COINLORE_SYMBOLS

# --- Fetch from Yahoo Finance ---
def fetch_yahoo_price(ticker, max_retries=3):
    for attempt in range(max_retries):
        try:
            df = yf.download(ticker, period='max', interval='1d', progress=False)
            if not df.empty:
                df = df[['Close']].rename(columns={'Close': ticker})
                return df
        except Exception as e:
            print(f"Yahoo fetch error for {ticker}: {e}")
        time.sleep(1)
    print(f"Failed to fetch {ticker} from Yahoo after {max_retries} attempts.")
    return None

# --- Fetch from CoinLore ---
def get_coinlore_id(symbol):
    # Paginate through CoinLore tickers to find the coin ID
    for start in range(0, 12000, 100):
        url = f"https://api.coinlore.net/api/tickers/?start={start}&limit=100"
        try:
            resp = requests.get(url)
            data = resp.json()['data']
            for coin in data:
                if coin['symbol'].upper() == symbol.upper():
                    return coin['id']
        except Exception as e:
            print(f"CoinLore ID fetch error for {symbol}: {e}")
        time.sleep(0.2)
    print(f"CoinLore ID not found for {symbol}")
    return None

def fetch_coinlore_market_data(coin_id, max_retries=3):
    url = f"https://api.coinlore.net/api/coin/markets/?id={coin_id}"
    for attempt in range(max_retries):
        try:
            resp = requests.get(url)
            if resp.status_code != 200:
                continue
            data = resp.json()
            # Filter out rows with invalid or missing 'time'
            clean_data = [row for row in data if isinstance(row.get('time', None), int)]
            if not clean_data:
                continue
            df = pd.DataFrame(clean_data)
            if not df.empty:
                df['datetime'] = pd.to_datetime(df['time'], unit='s')
                df = df.sort_values('datetime')
                df = df.set_index('datetime')
                # Use price_usd as 'Close' equivalent
                df = df[['price_usd']].rename(columns={'price_usd': 'Close'})
                # Drop duplicate index values
                df = df.loc[~df.index.duplicated(keep='first')]
                return df
        except Exception as e:
            print(f"CoinLore market fetch error for {coin_id}: {e}")
        time.sleep(1)
    print(f"Failed to fetch market data for CoinLore ID {coin_id} after {max_retries} attempts.")
    return None

# --- Main Data Collection ---
def main():
    all_dfs = []
    # Yahoo tokens
    for symbol, ticker in YAHOO_TICKERS.items():
        print(f"Fetching {symbol} from Yahoo Finance ({ticker})...")
        df = fetch_yahoo_price(ticker)
        if df is not None:
            df = df.rename(columns={ticker: symbol})
            # Drop duplicate index values
            df = df.loc[~df.index.duplicated(keep='first')]
            all_dfs.append(df)
        else:
            print(f"No data for {symbol} from Yahoo.")
    # CoinLore tokens
    for symbol in COINLORE_SYMBOLS:
        print(f"Fetching {symbol} from CoinLore...")
        coin_id = get_coinlore_id(symbol)
        if coin_id:
            df = fetch_coinlore_market_data(coin_id)
            if df is not None:
                df = df.rename(columns={'Close': symbol})
                # Drop duplicate index values
                df = df.loc[~df.index.duplicated(keep='first')]
                all_dfs.append(df)
            else:
                print(f"No market data for {symbol} from CoinLore.")
        else:
            print(f"No CoinLore ID for {symbol}.")
    # Combine all
    if all_dfs:
        try:
            combined = pd.concat(all_dfs, axis=1)
            combined = combined.sort_index()
            combined.to_csv('all_crypto_prices.csv')
            print("Saved all_crypto_prices.csv with columns:", combined.columns.tolist())
        except Exception as e:
            print(f"Error during concatenation or saving: {e}")
            # Try to save each DataFrame separately for debugging
            for i, df in enumerate(all_dfs):
                df.to_csv(f'debug_crypto_prices_{i}.csv')
            print("Saved partial data for debugging.")
    else:
        print("No data fetched for any token.")

def save_yahoo_only_csv():
    yahoo_cols = [col for col in pd.read_csv('all_crypto_prices.csv', nrows=1).columns if 'BTC' in col or 'ETH' in col or 'BNB' in col or 'XRP' in col or 'SOL' in col or 'DOGE' in col or 'ADA' in col or 'AVAX' in col or 'TRX' in col or 'DOT' in col or 'MATIC' in col or 'LINK' in col or 'NEAR' in col or 'OP' in col or 'ARB' in col or 'APT' in col or 'STX' in col or 'ICP' in col]
    df = pd.read_csv('all_crypto_prices.csv', index_col=0, parse_dates=True)
    yahoo_df = df[yahoo_cols]
    yahoo_df.to_csv('yahoo_crypto_prices.csv')
    print('Saved yahoo_crypto_prices.csv with columns:', yahoo_df.columns.tolist())

if __name__ == "__main__":
    main()
    save_yahoo_only_csv() 