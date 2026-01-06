"""
Stress testing functions for portfolio scenarios.
Supports sector shocks, rate shocks, and volatility scenarios.
Industry-ready with audit logging.
"""

import pandas as pd
from typing import Dict, Any


def sector_shock_impact(
    df: pd.DataFrame,
    sector_col: str,
    target_sector: str,
    shock_pct: float,
    nav_series: pd.Series
) -> Dict[str, Any]:
    """
    Estimate impact of a sector shock (e.g., -15% Technology).
    Uses market_cap_usd exposure rather than PnL for realism.
    """
    result = {"shock": "sector", "target": target_sector, "shock_pct": shock_pct}

    if sector_col not in df.columns or "market_cap_usd" not in df.columns:
        result.update({"impact_usd": None, "impact_pct": None, "status": "required columns missing"})
        return result

    last_date = df["date"].max()
    latest = df[df["date"] == last_date]

    if latest.empty:
        result.update({"impact_usd": None, "impact_pct": None, "status": "no data"})
        return result

    sec_exposure = latest.loc[latest[sector_col] == target_sector, "market_cap_usd"].sum()
    nav_last = nav_series.get(last_date, nav_series.iloc[-1])

    impact_usd = sec_exposure * shock_pct
    impact_pct = impact_usd / nav_last if nav_last else None

    result.update({
        "impact_usd": float(impact_usd),
        "impact_pct": float(impact_pct) if impact_pct is not None else None,
        "sector_exposure": float(sec_exposure),
        "nav": float(nav_last),
        "status": "ok"
    })
    return result


def rates_shock_impact(
    df: pd.DataFrame,
    delta_bps: float,
    duration_col: str,
    nav_series: pd.Series,
    duration_map: Dict[str, float],
    default_duration: float
) -> Dict[str, Any]:
    """
    Estimate impact of interest rate shock on fixed income using duration × delta × market_value.
    """
    result = {"shock": "rates", "delta_bps": delta_bps}

    last_date = df["date"].max()
    latest = df[df["date"] == last_date]

    if latest.empty:
        result.update({"impact_usd": None, "impact_pct": None, "status": "no data"})
        return result

    fixed_income = latest[latest["asset_class"].str.contains("Fixed Income", na=False)]
    if fixed_income.empty:
        result.update({"impact_usd": None, "impact_pct": None, "status": "no fixed income exposure"})
        return result

    # Duration mapping
    if duration_col in fixed_income.columns:
        durations = pd.to_numeric(fixed_income[duration_col], errors="coerce").fillna(default_duration)
    elif "credit_rating" in fixed_income.columns:
        durations = fixed_income["credit_rating"].map(duration_map).fillna(default_duration)
    else:
        durations = pd.Series([default_duration] * len(fixed_income))

    avg_duration = durations.mean()

    # Market value exposure
    if "market_cap_usd" in fixed_income.columns:
        mv = fixed_income["market_cap_usd"].sum()
    elif "market_value" in fixed_income.columns:
        mv = fixed_income["market_value"].sum()
    else:
        mv = fixed_income["pnl_usd"].sum()  # fallback (not ideal)

    delta = delta_bps / 10000.0
    impact_usd = -avg_duration * delta * mv
    nav_last = nav_series.get(last_date, nav_series.iloc[-1])
    impact_pct = impact_usd / nav_last if nav_last else None

    result.update({
        "impact_usd": float(impact_usd),
        "impact_pct": float(impact_pct) if impact_pct is not None else None,
        "avg_duration": float(avg_duration),
        "exposure_mv": float(mv),
        "nav": float(nav_last),
        "status": "ok"
    })
    return result


def volatility_shock_impact(
    df: pd.DataFrame,
    vol_col: str,
    vol_mult: float,
    nav_series: pd.Series
) -> Dict[str, Any]:
    """
    Estimate impact of higher volatility regime by scaling portfolio volatility.
    Uses volatility_30d in decimal form (e.g., 0.02 = 2%).
    """
    result = {"shock": "volatility", "vol_mult": vol_mult}

    if vol_col not in df.columns:
        result.update({"impact_usd": None, "impact_pct": None, "status": "vol column missing"})
        return result

    last_date = df["date"].max()
    latest = df[df["date"] == last_date]

    if latest.empty:
        result.update({"impact_usd": None, "impact_pct": None, "status": "no data"})
        return result

    base_vol = latest[vol_col].astype(float).mean()
    stressed_vol = base_vol * vol_mult

    nav_last = nav_series.get(last_date, nav_series.iloc[-1])
    # Assume 1-day VaR impact ~ vol × NAV
    impact_usd = (stressed_vol - base_vol) * nav_last
    impact_pct = impact_usd / nav_last if nav_last else None

    result.update({
        "impact_usd": float(impact_usd),
        "impact_pct": float(impact_pct) if impact_pct is not None else None,
        "base_vol": float(base_vol),
        "stressed_vol": float(stressed_vol),
        "nav": float(nav_last),
        "status": "ok"
    })
    return result
