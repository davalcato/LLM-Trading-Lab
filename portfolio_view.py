import pandas as pd
import yfinance as yf

# Load portfolio
portfolio = pd.read_csv("my_portfolio.csv")

# Dynamically get tickers from CSV
tickers = portfolio["Ticker"].tolist()

# Fetch prices
prices = yf.download(tickers, period="1d", group_by="ticker", auto_adjust=True)

def get_price(prices, ticker):
    # Handle single vs multiple tickers
    if len(tickers) == 1:
        return prices["Close"].iloc[-1]
    return prices[ticker]["Close"].iloc[-1]

# Update portfolio with latest prices
portfolio["Price"] = portfolio["Ticker"].apply(lambda t: get_price(prices, t))
portfolio["PositionValue"] = portfolio["Shares"] * portfolio["Price"]

# Calculate total equity
total_equity = portfolio["PositionValue"].sum()

# Print portfolio
print("\nTicker  Shares  Price   PositionValue")
for _, row in portfolio.iterrows():
    print(f"{row['Ticker']:<6}  {int(row['Shares']):<6}  {row['Price']:<7.2f}  {row['PositionValue']:<.2f}")

print(f"\nTotal Portfolio Value: ${total_equity:,.2f}")

