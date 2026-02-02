import pandas as pd
import numpy as np

def compute_metrics(equity_curve):
    returns = equity_curve.pct_change().dropna()

    sharpe = (
        np.sqrt(252) * returns.mean() / returns.std()
        if returns.std() > 0 else 0
    )

    drawdown = (equity_curve.cummax() - equity_curve) / equity_curve.cummax()
    max_dd = drawdown.max()

    return {
        "Sharpe": round(sharpe, 2),
        "MaxDrawdown": round(max_dd, 2)
    }

