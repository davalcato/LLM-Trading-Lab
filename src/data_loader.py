# =========================
# src/data_loader.py
# Data loading utilities
# =========================

import pandas as pd

UNIVERSE_FILE = "universe.csv"  # repo root

def load_universe_prices(total_days=None):
    """
    Load universe prices as a DataFrame
    total_days: optional, number of business days to fetch
    """
    import pandas as pd
    import yfinance as yf

    try:
        tickers = pd.read_csv("universe.csv")["Ticker"].dropna().tolist()
    except FileNotFoundError:
        tickers = ["BURU","CRBP","KITT","SRRK","RIO"]

    period = f"{total_days}d" if total_days is not None else "180d"

    data = yf.download(
        tickers,
        period=period,
        auto_adjust=True,
        group_by="ticker",
        progress=False
    )

    prices = pd.DataFrame({t: data[t]["Close"] for t in tickers})
    return prices

