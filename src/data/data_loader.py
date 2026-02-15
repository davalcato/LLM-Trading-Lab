# src/data/data_loader.py

import os
import pandas as pd
import yfinance as yf
from tqdm import tqdm

# ---------------------------
# Paths (robust, module-based)
# ---------------------------
# Data folder is the same folder as this file
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
UNIVERSE_CSV = os.path.join(DATA_DIR, "universe.csv")
PRICE_CACHE_CSV = os.path.join(DATA_DIR, "price_data.csv")


# ---------------------------
# Load Universe
# ---------------------------
def load_universe():
    """
    Load the master ticker universe from CSV.

    - Normalizes column names to lowercase
    - Accepts 'ticker' or 'symbol'
    - Removes duplicates
    - Drops null or empty tickers
    """
    if not os.path.exists(UNIVERSE_CSV):
        raise FileNotFoundError(
            f"{UNIVERSE_CSV} not found. Please place your universe CSV in this folder."
        )

    df = pd.read_csv(UNIVERSE_CSV)

    # Normalize column names
    df.columns = df.columns.str.lower()

    # Flexible column handling
    if "ticker" not in df.columns:
        if "symbol" in df.columns:
            df = df.rename(columns={"symbol": "ticker"})
        else:
            raise KeyError("Universe CSV must contain a 'ticker' column")

    # Clean data
    df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()
    df = df.drop_duplicates(subset="ticker").reset_index(drop=True)
    df = df[df["ticker"].notna() & (df["ticker"] != "")]

    return df


# ---------------------------
# Load Price Data
# ---------------------------
def load_universe_prices(df_universe, start="2023-01-01", end=None, parallel=True):
    """
    Download adjusted close prices for tickers.

    - Uses caching
    - Handles delisted tickers
    - Merges new downloads with existing cache
    """

    tickers = df_universe["ticker"].tolist()

    # Load cache if exists
    if os.path.exists(PRICE_CACHE_CSV):
        print(f"Loading cached price data from {PRICE_CACHE_CSV}")
        price_data = pd.read_csv(PRICE_CACHE_CSV, index_col=0, parse_dates=True)
        missing_tickers = [t for t in tickers if t not in price_data.columns]
    else:
        price_data = pd.DataFrame()
        missing_tickers = tickers

    if not missing_tickers:
        return price_data

    print(f"Downloading {len(missing_tickers)} missing tickers (parallel={parallel})...")

    try:
        yf_data = yf.download(
            tickers=missing_tickers,
            start=start,
            end=end,
            group_by="ticker",
            auto_adjust=True,
            threads=parallel,
            progress=False,
        )
    except Exception as e:
        print("Error downloading price data:", e)
        return price_data

    adj_close = pd.DataFrame()

    for t in missing_tickers:
        try:
            if isinstance(yf_data.columns, pd.MultiIndex):
                if t in yf_data.columns.get_level_values(0):
                    adj_close[t] = yf_data[t]["Close"]
            else:
                # Single ticker case
                if "Close" in yf_data.columns:
                    adj_close[t] = yf_data["Close"]
        except Exception as e:
            print(f"Ticker {t} failed download: {e}")

    adj_close = adj_close.dropna(axis=1, how="all")

    # Merge with cache
    if not price_data.empty:
        price_data = pd.concat([price_data, adj_close], axis=1)
    else:
        price_data = adj_close

    # Ensure sorted index
    price_data = price_data.sort_index()

    # Save cache
    os.makedirs(DATA_DIR, exist_ok=True)
    price_data.to_csv(PRICE_CACHE_CSV)

    failed = [t for t in tickers if t not in price_data.columns]
    if failed:
        print(f"Failed downloads: {failed}")

    return price_data

