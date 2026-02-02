import pandas as pd
from config import *
from data_loader import load_price_data
from monte_carlo import monte_carlo_paths
from signals import signal_engine
from portfolio import compute_metrics

# Load universe
tickers = pd.read_csv("data/universe.csv")["Ticker"].dropna().tolist()
prices = load_price_data(tickers, HIST_DAYS)

cash = STARTING_CASH
positions = {t: 0 for t in tickers}

equity_curve = []
trade_log = []

# Precompute forecasts
forecasts = {
    t: monte_carlo_paths(prices[t], FORECAST_DAYS, MC_SIMULATIONS).mean(axis=1)
    for t in tickers
}

total_days = HIST_DAYS + FORECAST_DAYS

for day in range(total_days):
    for t in tickers:
        hist_series = prices[t].iloc[:min(day + 1, HIST_DAYS)]

        price = (
            hist_series.iloc[-1]
            if day < HIST_DAYS
            else forecasts[t].iloc[day - HIST_DAYS]
        )

        signal = signal_engine(
            hist_series,
            positions[t],
            LOOKBACK,
            LOW_PCTL,
            HIGH_PCTL
        )

        if signal == "BUY" and cash > price:
            qty = int(cash // price)
            cost = qty * price * (1 + TRANSACTION_COST)
            cash -= cost
            positions[t] += qty
            trade_log.append([t, "BUY", qty, price])

        elif signal == "SELL" and positions[t] > 0:
            proceeds = positions[t] * price * (1 - TRANSACTION_COST)
            cash += proceeds
            trade_log.append([t, "SELL", positions[t], price])
            positions[t] = 0

    equity = cash + sum(
        positions[t] * (
            prices[t].iloc[-1]
            if day < HIST_DAYS
            else forecasts[t].iloc[day - HIST_DAYS]
        )
        for t in tickers
    )

    equity_curve.append(equity)

# Save outputs
pd.DataFrame(trade_log, columns=["Ticker","Side","Qty","Price"]).to_csv(
    "output/trades.csv", index=False
)

pd.Series(equity_curve).to_csv(
    "output/equity_curve.csv", index=False
)

metrics = compute_metrics(pd.Series(equity_curve))
print("Metrics:", metrics)

