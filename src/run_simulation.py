# =========================
# src/run_simulation.py
# Canonical simulation entry point for Portfolio
# =========================

import numpy as np
import pandas as pd
from pathlib import Path

from src.config import (
    INITIAL_CAPITAL,
    MAX_POSITION_PCT,
    BUY_ZSCORE,
    SELL_ZSCORE,
    HIST_DAYS,
    FORECAST_DAYS,
    RANDOM_SEED
)
from src.data_loader import load_universe_prices
from src.portfolio import Portfolio, compute_metrics

# ----------------------------
# Signal Generation
# ----------------------------
def generate_signal(price, history, buy_z=BUY_ZSCORE, sell_z=SELL_ZSCORE):
    """
    Compute z-score and generate BUY / SELL / HOLD signal
    """
    mean = history.mean()
    std = history.std()

    if std == 0:
        return "HOLD"

    z = (price - mean) / std

    if z <= buy_z:
        return "BUY"
    elif z >= sell_z:
        return "SELL"
    else:
        return "HOLD"

# ----------------------------
# Simulation Loop
# ----------------------------
def run_simulation():
    np.random.seed(RANDOM_SEED)

    # Load price data
    price_data = load_universe_prices(HIST_DAYS + FORECAST_DAYS)

    # Initialize portfolio
    portfolio = Portfolio(INITIAL_CAPITAL)

    # Track peak equity for drawdown calculation
    peak_equity = INITIAL_CAPITAL

    # Loop over each day starting after lookback
    lookback = 20
    for day in range(lookback, len(price_data)):
        today_prices = price_data.iloc[day]
        history = price_data.iloc[day - lookback:day]

        print(f"\n=== DAY {day} ({price_data.index[day].date()}) ===")

        # Loop through tickers
        for symbol in price_data.columns:
            price = today_prices[symbol]
            hist = history[symbol]

            signal = generate_signal(price, hist)
            portfolio.execute(symbol, price, signal)

            print(f"{symbol}: price={price:.2f}, signal={signal}")

        # Update equity
        equity = portfolio.total_equity(today_prices.to_dict())
        portfolio.equity_curve.append(equity)

        peak_equity = max(peak_equity, equity)
        drawdown = (peak_equity - equity) / peak_equity * 100

        print(f"Total Equity: {equity:.2f}")
        print(f"Drawdown: {drawdown:.2f}%")

    # ----------------------------
    # Export Trades & Equity
    # ----------------------------
    Path("output").mkdir(exist_ok=True)

    trades_df = pd.DataFrame(
        portfolio.trade_log,
        columns=["Ticker", "Side", "Qty", "Price"]
    )
    trades_df.to_csv("output/trades.csv", index=False)

    equity_df = pd.Series(portfolio.equity_curve)
    equity_df.to_csv("output/equity_curve.csv", index=False)

    # ----------------------------
    # Compute Metrics
    # ----------------------------
    metrics = compute_metrics(equity_df)
    print("\n--- Metrics ---")
    print(metrics)

    return portfolio

# ----------------------------
# Entry Point
# ----------------------------
if __name__ == "__main__":
    run_simulation()

