import yfinance as yf
import pandas as pd

def load_price_data(tickers, hist_days):
    """
    Downloads adjusted close price data for a list of tickers.
    Returns a dict: { ticker: pd.Series }
    """
    data = yf.download(
        tickers,
        period=f"{hist_days}d",
        auto_adjust=True,
        group_by="ticker",
        progress=False
    )

    prices = {}
    for t in tickers:
        prices[t] = data[t]["Close"].dropna()

    return prices

