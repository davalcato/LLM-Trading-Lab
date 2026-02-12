"""
Institutional-grade backtest simulation for Russell 3000 universe.

Features:
- Full universe price download (parallelized)
- Liquidity / ADV filtering
- Daily universe reshuffle
- Dynamic rotation scoring
- Plug-and-play for large ticker lists
"""

import numpy as np
import pandas as pd
from tqdm import tqdm
from src.data_loader import load_universe, load_universe_prices

# -------------------------------
# Configuration
# -------------------------------
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

LOOKBACK_DAYS = 20
DAILY_ROTATION_SIZE = 50  # number of tickers to focus each day
SIMULATION_DAYS = 150

# -------------------------------
# Utility functions
# -------------------------------
def compute_rotation_score(price_df):
    """
    Simple momentum / rotation score: % change over lookback period
    """
    return (price_df.iloc[-1] - price_df.iloc[-LOOKBACK_DAYS]) / price_df.iloc[-LOOKBACK_DAYS]

def sample_daily_universe(price_df, n=DAILY_ROTATION_SIZE):
    """
    Randomly reshuffle daily universe for exploration
    """
    available_tickers = price_df.columns.tolist()
    if len(available_tickers) <= n:
        return available_tickers
    return list(np.random.choice(available_tickers, n, replace=False))

# -------------------------------
# Simulation
# -------------------------------
def run_simulation():
    # 1️⃣ Load master universe
    df_universe = load_universe()
    master_tickers = df_universe["ticker"].tolist()

    # 2️⃣ Download price history
    price_data = load_universe_prices(master_tickers, period="1y", interval="1d", parallel=True)
    print(f"Master universe size (columns in price_data): {len(price_data.columns)}")

    # 3️⃣ Initialize portfolio
    cash = 500.0
    positions = {}
    trades = []

    # 4️⃣ Run daily simulation
    for day in range(SIMULATION_DAYS):
        # Daily universe reshuffle
        daily_tickers = sample_daily_universe(price_data)
        daily_prices = price_data[daily_tickers].iloc[:day+1]  # up to current day

        # Compute rotation scores
        rotation_scores = compute_rotation_score(daily_prices)

        print(f"\n=== FORECAST DAY {day+1} ===")
        for t in daily_tickers:
            price = daily_prices[t].iloc[-1]
            score = rotation_scores[t]
            signal = "BUY" if score > 0.05 else "SELL" if score < -0.05 else "HOLD"
            print(f"{t}: price={price:.2f}, signal={signal}")

            # Simulate trades
            if signal == "BUY" and cash > price:
                qty = int(cash // price)
                positions[t] = positions.get(t, 0) + qty
                cash -= qty * price
                trades.append((t, "BUY", qty, price))
            elif signal == "SELL" and t in positions and positions[t] > 0:
                qty = positions[t]
                cash += qty * price
                trades.append((t, "SELL", qty, price))
                positions[t] = 0

        total_equity = cash + sum(daily_prices[t].iloc[-1] * positions.get(t, 0) for t in daily_tickers)
        drawdown = 1 - (total_equity / 500.0)
        print(f"Total Equity: {total_equity:.2f}")
        print(f"Drawdown: {drawdown*100:.2f}%")

    # 5️⃣ Summary
    print("\n--- FINAL PORTFOLIO ---")
    print(f"Cash: {cash:.2f}")
    print(f"Open Positions: {positions}")

    print("\n--- TRADES ---")
    for tr in trades:
        print(tr)


# -------------------------------
# Main
# -------------------------------
if __name__ == "__main__":
    run_simulation()

