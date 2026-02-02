import numpy as np

def signal_engine(price_series, position, lookback, low_pctl, high_pctl):
    if len(price_series) < lookback:
        return "HOLD"

    window = price_series.iloc[-lookback:]
    current = window.iloc[-1]

    p_low = np.percentile(window, low_pctl)
    p_high = np.percentile(window, high_pctl)

    if current <= p_low and position == 0:
        return "BUY"

    if current >= p_high and position > 0:
        return "SELL"

    if position > 0:
        return "SELL"

    return "HOLD"

