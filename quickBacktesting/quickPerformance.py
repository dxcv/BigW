
from itertools import groupby
import numpy as np
import pandas as pd
from scipy.stats import linregress


def aggregate_returns(returns, convert_to):
    def cumulate_returns(x):
        return np.exp(np.log(1 + x).cumsum())[-1] - 1

    if convert_to == 'weekly':
        return returns.groupby(
            [lambda x: x.year,
             lambda x: x.month,
             lambda x: x.isocalendar()[1]]).apply(cumulate_returns)
    elif convert_to == 'monthly':
        return returns.groupby(
            [lambda x: x.year, lambda x: x.month]).apply(cumulate_returns)
    elif convert_to == 'yearly':
        return returns.groupby(
            [lambda x: x.year]).apply(cumulate_returns)
    else:
        ValueError('convert_to must be weekly, monthly or yearly')


def create_cagr(equity, periods=252):
    years = len(equity) / float(periods)
    return (equity[-1] ** (1.0 / years)) - 1.0


def create_sharpe_ratio(returns, periods=252):
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)


def create_sortino_ratio(returns, periods=252):
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns[returns < 0])


def create_drawdowns(returns):
    """
    Calculate the largest peak-to-trough drawdown of the equity curve
    as well as the duration of the drawdown. Requires that the
    pnl_returns is a pandas Series.

    Parameters:
    equity - A pandas Series representing period percentage returns.

    Returns:
    drawdown, drawdown_max, duration
    """
    # Calculate the cumulative returns curve
    # and set up the High Water Mark
    idx = returns.index
    hwm = np.zeros(len(idx))

    return_list = list(returns)

    # Create the high water mark
    for t in range(1, len(idx)):
        hwm[t] = max(hwm[t - 1], return_list[t])

    # Calculate the drawdown and duration statistics
    perf = pd.DataFrame(index=idx)
    hwm_s = pd.Series(hwm, index=idx)
    perf["Drawdown"] = (hwm_s - returns) / hwm_s
    perf.iloc[0]['Drawdown'] = 0.0
    perf["DurationCheck"] = np.where(perf["Drawdown"] == 0, 0, 1)
    duration = max(sum(1 for i in g if i == 1) for k, g in groupby(perf["DurationCheck"]))
    return perf["Drawdown"], np.max(perf["Drawdown"]), duration

def rsquared(x, y):
    """
    Return R^2 where x and y are array-like.
    """
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    return r_value**2