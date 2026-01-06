import numpy as np
import pandas as pd


def historical_var_es(return_series: pd.Series, level: float = 0.95) -> tuple[float, float] | tuple[None, None]:
    """
    Compute Historical Value-at-Risk (VaR) and Expected Shortfall (ES).

    Parameters
    ----------
    return_series : pd.Series
        Daily returns in decimal form (e.g., 0.01 = 1%).
    level : float, optional
        Confidence level, default = 0.95.

    Returns
    -------
    tuple
        (VaR, ES) as fractions of NAV. None values if no data available.
    """
    arr = np.array(return_series.dropna())
    if arr.size == 0:
        return None, None

    cutoff = np.percentile(arr, (1 - level) * 100)
    var = abs(cutoff)

    tail = arr[arr <= cutoff]
    es = abs(tail.mean()) if tail.size > 0 else var

    return var, es


def compute_drawdown(cum_returns: pd.Series) -> tuple[pd.Series, float]:
    """
    Compute drawdown series and max drawdown.

    Parameters
    ----------
    cum_returns : pd.Series
        Cumulative returns (growth of $1 NAV).

    Returns
    -------
    tuple
        (drawdown_series, max_drawdown)
    """
    running_max = cum_returns.cummax()
    drawdown = (cum_returns - running_max) / running_max
    return drawdown, float(drawdown.min())


def rolling_sharpe_ratio(
    daily_return: pd.Series, 
    rf_daily: float, 
    window: int = 30, 
    ann_factor: int = 252
) -> pd.Series:
    """
    Compute rolling Sharpe ratio (annualized).

    Parameters
    ----------
    daily_return : pd.Series
        Daily returns in decimal form.
    rf_daily : float
        Daily risk-free rate.
    window : int, optional
        Rolling window length in days, default = 30.
    ann_factor : int, optional
        Annualization factor, default = 252 (trading days).

    Returns
    -------
    pd.Series
        Rolling Sharpe ratio.
    """
    excess = daily_return - rf_daily
    mean = excess.rolling(window).mean()
    std = daily_return.rolling(window).std().replace(0, 1e-12)
    return (mean / std) * np.sqrt(ann_factor)
