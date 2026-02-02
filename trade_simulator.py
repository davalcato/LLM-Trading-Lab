import pandas as pd
import numpy as np
import yfinance as yf

# =========================
# CONFIG
# =========================
STARTING_CASH = 272.0
cash = STARTING_CASH
positions = {}
trade_log = []

HIST_DAYS = 90
FORECAST_DAYS = 60
MC_SIMULATIONS = 800

LOOKBACK = 20

BUY_Z = -1.0     # buy when price is statistically cheap
SELL_Z = 1.0     # sell when price is statistically expensive
EXIT_Z = 0.2

TRANSACTION_COST = 0.001  # 10 bps

# =========================
# LOAD TICKERS
# =========================
try:
    tickers = pd.read_csv("universe.csv")["Ticker"].dropna().tolist()
except FileNotFoundError:
    tickers = [
        "BURU","CRBP","KITT","SRRK","RIO","LMND","RKLB","OKLO",
        "DRUG","SOXL","RGTI","FJET","IBIO","RR"
    ]

print("\nLoaded tickers:", tickers)

# =========================
# DOWNLOAD DATA
# =========================
data = yf.download(
    tickers,
    period=f"{HIST_DAYS}d",
    auto_adjust=True,
    group_by="ticker",
    progress=False
)

# =========================
# MONTE CARLO
# =========================
def monte_carlo_paths(series, days, sims):
    returns = series.pct_change().dropna()

    mu = returns.mean()
    sigma = returns.std()

    shocks = np.random.normal(mu, sigma, (days, sims))
    paths = np.zeros((days, sims))
    paths[0] = series.iloc[-1] * (1 + shocks[0])

    for i in range(1, days):
        paths[i] = paths[i - 1] * (1 + shocks[i])

    return pd.DataFrame(paths)

# =========================
# SIGNAL ENGINE (FIXED)
# =========================
def signal_engine(prices, position):
    if len(prices) < LOOKBACK:
        return "HOLD"

    window = prices.iloc[-LOOKBACK:]
    mean_price = window.mean()
    std_price = window.std()

    if std_price == 0 or np.isnan(std_price):
        return "HOLD"

    z = (prices.iloc[-1] - mean_price) / std_price

    if z < BUY_Z and position == 0:
        return "BUY"

    if z > SELL_Z and position > 0:
        return "SELL"

    if abs(z) < EXIT_Z and position > 0:
        return "SELL"

    return "HOLD"

# =========================
# BUILD PRICE SERIES
# =========================
extended_prices = {}

for t in tickers:
    try:
        close = data[t]["Close"].dropna()

        mc = monte_carlo_paths(close, FORECAST_DAYS, MC_SIMULATIONS)
        forecast = mc.mean(axis=1)

        future_dates = pd.bdate_range(
            start=close.index[-1] + pd.Timedelta(days=1),
            periods=FORECAST_DAYS
        )
        forecast.index = future_dates

        extended_prices[t] = pd.concat([close, forecast])
        positions[t] = 0

    except Exception as e:
        print(f"Skipping {t}: {e}")

# =========================
# SIMULATION LOOP
# =========================
total_days = len(next(iter(extended_prices.values())))
peak_equity = STARTING_CASH

for day in range(total_days):
    date = next(iter(extended_prices.values())).index[day]
    label = "FORECAST" if day >= HIST_DAYS else "HIST"

    print(f"\n=== {label} DAY {day+1} ({date.date()}) ===")

    for t in tickers:
        series = extended_prices[t].iloc[:day + 1]
        price = series.iloc[-1]
        position = positions[t]

        signal = signal_engine(series, position)
        print(f"{t}: price={price:.2f}, signal={signal}")

        # BUY
        if signal == "BUY" and cash > price:
            qty = int(cash // price)
            if qty > 0:
                cost = qty * price * (1 + TRANSACTION_COST)
                cash -= cost
                positions[t] += qty

        # SELL
        elif signal == "SELL" and position > 0:
            proceeds = position * price * (1 - TRANSACTION_COST)
            cash += proceeds
            positions[t] = 0

    equity = cash + sum(
        positions[t] * extended_prices[t].iloc[day]
        for t in tickers
    )

    peak_equity = max(peak_equity, equity)
    drawdown = (peak_equity - equity) / peak_equity

    print(f"Total Equity: {equity:.2f}")
    print(f"Drawdown: {drawdown:.2%}")

# =========================
# FINAL REPORT
# =========================
print("\n--- FINAL PORTFOLIO ---")
print("Cash:", round(cash, 2))
print("Positions:", {k: v for k, v in positions.items() if v > 0})

