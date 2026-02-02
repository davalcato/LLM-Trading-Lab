import numpy as np
import pandas as pd

def monte_carlo_paths(series, days, sims):
    log_returns = np.log(series / series.shift(1)).dropna()
    mu, sigma = log_returns.mean(), log_returns.std()

    shocks = np.random.normal(mu, sigma, (days, sims))

    paths = np.zeros((days, sims))
    paths[0] = series.iloc[-1] * np.exp(shocks[0])

    for i in range(1, days):
        paths[i] = paths[i - 1] * np.exp(shocks[i])

    return pd.DataFrame(paths)

