# Quant Trading Simulator

A modular quantitative trading simulator written in Python, designed to
demonstrate signal generation, portfolio accounting, and Monte Carlo-based
price simulation.

This repository is structured to reflect professional quant research code
rather than ad-hoc scripts.

## Project Structure
```text
.
├── src/
│   ├── config.py           # Global simulation parameters
│   ├── data_loader.py      # Market data ingestion
│   ├── signals.py          # Buy / Sell / Hold logic
│   ├── portfolio.py        # Position and PnL tracking
│   ├── monte_carlo.py      # Stochastic price simulation
│   └── run_simulation.py   # Main simulation entry point
├── trade_simulator.py      # Legacy prototype
├── portfolio_view.py       # Result visualization
├── universe.csv            # Asset universe
└── README.md

