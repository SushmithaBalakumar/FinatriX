"""
Main Orchestration for Risk Analytics Platform
Industry-ready: integrates risk, stress, and reporting modules
Enhanced for Dashboard Integration with Daily Time-Series Metrics
"""

import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root / "src"))

import logging
from datetime import datetime
import pandas as pd
import numpy as np

# Local imports
from risk_analytics.utils import load_config, ensure_dirs, try_git_commit_hash, sha256
from risk_analytics.risk_models import calculate_var_es, calculate_drawdowns, calculate_performance
from risk_analytics.stress import sector_shock_impact, rates_shock_impact, volatility_shock_impact
from risk_analytics.reporting import (
    save_var_results,
    save_drawdowns,
    save_performance,
    save_stress_summary,
    save_strategy_results,
    save_exposures,
    save_audit_log,
    save_csvs,
    save_plots,
)

# ... rest of the code stays the same
# --------------------------------------
# Logging Setup
# --------------------------------------
logger = logging.getLogger("risk_analytics.main")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def calculate_rolling_var_es(pnl_series, window=30, levels=None):
    """
    Calculate rolling VaR and ES metrics using a sliding window.
    
    Args:
        pnl_series: pandas Series of P&L values
        window: rolling window size (default 30 days)
        levels: confidence levels (default [0.95, 0.99])
    
    Returns:
        DataFrame with rolling VaR and ES metrics
    """
    if levels is None:
        levels = [0.95, 0.99]
    
    results = []
    
    # Ensure we have enough data
    if len(pnl_series) < window:
        logger.warning(f"Insufficient data for rolling VaR calculation. Need {window}, have {len(pnl_series)}")
        return pd.DataFrame()
    
    for i in range(window, len(pnl_series) + 1):
        window_data = pnl_series.iloc[i-window:i]
        
        var_es = calculate_var_es(window_data, levels=levels)
        results.append(var_es)
    
    return pd.DataFrame(results)


def calculate_daily_stress_scenarios(df, date, nav_today, config):
    """
    Calculate stress test scenarios for a specific date.
    
    Args:
        df: DataFrame with trading data
        date: specific date to analyze
        nav_today: NAV value for this date
        config: configuration dictionary
    
    Returns:
        Dictionary with stress test results
    """
    stress_results = {}
    
    # Filter data for this specific date
    day_df = df[df['date'] == date].copy()
    
    if day_df.empty:
        return {
            'Rate_Shock': 0.0,
            'Volatility_Spike': 0.0,
            'Sector_Drawdown': 0.0
        }
    
    # Create single-value NAV series for stress calculations
    nav_series = pd.Series([nav_today], index=[date])
    
    # Calculate each stress scenario
    for name, s in config["stress_scenarios"]["scenarios"].items():
        try:
            if s["type"] == "sector":
                result = sector_shock_impact(
                    day_df,
                    s["sector_col"],
                    s["target_sector"],
                    s["shock_pct"],
                    nav_series,
                )
                stress_results[name] = result.get('impact_pct', 0.0)
                
            elif s["type"] == "rates":
                result = rates_shock_impact(
                    day_df,
                    s["delta_bps"],
                    s["proxy_duration_col"],
                    nav_series,
                    config["mappings"]["duration_from_credit_rating"],
                    config["mappings"]["default_duration"],
                )
                stress_results[name] = result.get('impact_pct', 0.0)
                
            elif s["type"] == "vol":
                result = volatility_shock_impact(
                    day_df,
                    s["vol_col"],
                    s["vol_mult"],
                    nav_series,
                )
                stress_results[name] = result.get('impact_pct', 0.0)
                
        except Exception as e:
            logger.warning(f"Stress scenario '{name}' failed for date {date}: {e}")
            stress_results[name] = 0.0
    
    return stress_results


def generate_daily_risk_metrics(df, pnl_col, nav_series, config, window=30):
    """
    Generate daily risk metrics including VaR, ES, and stress tests.
    This creates the time-series data required by the dashboard.
    
    Args:
        df: merged trading DataFrame
        pnl_col: column name for P&L
        nav_series: pandas Series of NAV values by date
        config: configuration dictionary
        window: rolling window for VaR/ES calculation
    
    Returns:
        DataFrame with daily risk metrics
    """
    logger.info(f"Calculating daily risk metrics with {window}-day rolling window...")
    
    # Get sorted dates
    dates = sorted(df['date'].unique())
    
    if len(dates) < window:
        logger.error(f"Insufficient dates for risk calculation. Need {window}, have {len(dates)}")
        return pd.DataFrame()
    
    # Calculate daily P&L series
    daily_pnl = df.groupby('date')[pnl_col].sum().sort_index()
    
    # Calculate rolling VaR/ES
    rolling_var_es = calculate_rolling_var_es(daily_pnl, window=window, levels=config["risk"]["var_levels"])
    
    # Initialize results list
    risk_metrics_list = []
    
    # Start from window date onwards
    for idx, date in enumerate(dates[window-1:], start=window-1):
        # Get VaR/ES for this date
        var_es_idx = idx - (window - 1)
        if var_es_idx < len(rolling_var_es):
            var_es = rolling_var_es.iloc[var_es_idx]
        else:
            var_es = {}
        
        # Get NAV for this date
        nav_today = nav_series[nav_series.index == date]
        if len(nav_today) > 0:
            nav_value = float(nav_today.iloc[0])
        else:
            nav_value = float(nav_series.iloc[-1])
        
        # Calculate stress scenarios for this date
        stress = calculate_daily_stress_scenarios(df, date, nav_value, config)
        
        # Combine all metrics
        daily_metrics = {
            'date': date,
            'VaR_95': var_es.get('VaR_95', 0.0),
            'ES_95': var_es.get('ES_95', 0.0),
            'VaR_99': var_es.get('VaR_99', 0.0),
            'ES_99': var_es.get('ES_99', 0.0),
            'Rate_Shock': stress.get('Rate_Shock', 0.0),
            'Volatility_Spike': stress.get('Volatility_Spike', 0.0),
            'Sector_Drawdown': stress.get('Sector_Drawdown', 0.0),
        }
        
        risk_metrics_list.append(daily_metrics)
    
    daily_risk_metrics = pd.DataFrame(risk_metrics_list)
    
    logger.info(f"Generated {len(daily_risk_metrics)} days of risk metrics")
    logger.info(f"VaR_95 range: [{daily_risk_metrics['VaR_95'].min():.2f}, {daily_risk_metrics['VaR_95'].max():.2f}]")
    
    return daily_risk_metrics


def calculate_sector_exposure(df, config):
    """
    Calculate sector exposure as percentage of total portfolio value.
    Uses all positions, not just latest date.
    """
    if 'sector' not in df.columns or 'market_cap_usd' not in df.columns:
        logger.warning("Sector or market_cap_usd column missing. Skipping sector exposure.")
        return pd.DataFrame(columns=['sector', 'portfolio_weight'])
    
    # Aggregate all positions by sector
    sector_totals = df.groupby('sector')['market_cap_usd'].sum().reset_index()
    
    # Calculate total portfolio value
    total_value = sector_totals['market_cap_usd'].sum()
    
    if total_value == 0:
        logger.warning("Total portfolio value is zero. Cannot calculate sector exposure.")
        return pd.DataFrame(columns=['sector', 'portfolio_weight'])
    
    # Calculate sector exposures
    sector_totals['portfolio_weight'] = sector_totals['market_cap_usd'] / total_value
    
    # Keep only sector and portfolio_weight columns
    sector_exposure = sector_totals[['sector', 'portfolio_weight']].copy()
    
    logger.info(f"Calculated exposure for {len(sector_exposure)} sectors")
    logger.info(f"Sector breakdown:\n{sector_exposure.to_string()}")
    
    return sector_exposure


def calculate_portfolio_risk_return(nav_series, config):
    """
    Calculate portfolio-level risk and return metrics.
    
    Args:
        nav_series: pandas Series of NAV values
        config: configuration dictionary
    
    Returns:
        DataFrame with portfolio metrics
    """
    # Calculate returns
    returns = nav_series.pct_change().dropna()
    
    if len(returns) == 0:
        logger.warning("No returns data available for portfolio metrics")
        return pd.DataFrame([{
            'Expected Return': 0.0,
            'Expected Volatility': 0.0,
            'Sharpe Ratio': 0.0
        }])
    
    # Annualization factor (252 trading days)
    ann_factor = 252
    
    # Calculate metrics
    expected_return = returns.mean() * ann_factor
    expected_volatility = returns.std() * np.sqrt(ann_factor)
    
    # Sharpe ratio
    risk_free_rate = config["performance"]["risk_free_rate"]
    sharpe_ratio = (expected_return - risk_free_rate) / expected_volatility if expected_volatility != 0 else 0.0
    
    portfolio_metrics = pd.DataFrame([{
        'Expected Return': expected_return,
        'Expected Volatility': expected_volatility,
        'Sharpe Ratio': sharpe_ratio
    }])
    
    logger.info(f"Portfolio Metrics - Return: {expected_return:.4f}, Vol: {expected_volatility:.4f}, Sharpe: {sharpe_ratio:.4f}")
    
    return portfolio_metrics


def save_dashboard_csvs(daily_risk_metrics, sector_exposure, portfolio_risk_return, output_dir):
    """
    Save CSV files in the format required by the dashboard.
    
    Args:
        daily_risk_metrics: DataFrame with daily risk metrics
        sector_exposure: DataFrame with sector exposures
        portfolio_risk_return: DataFrame with portfolio metrics
        output_dir: output directory path
    """
    # Create subdirectories
    risk_dir = output_dir / "Risk Analytics Module"
    portfolio_dir = output_dir / "Portfolio Optimization Module"
    
    ensure_dirs(risk_dir)
    ensure_dirs(portfolio_dir)
    
    # Save daily risk metrics (without date index)
    if not daily_risk_metrics.empty:
        # Drop date column for the format expected by dashboard
        risk_output = daily_risk_metrics[['VaR_95', 'ES_95', 'VaR_99', 'ES_99', 
                                          'Rate_Shock', 'Volatility_Spike', 'Sector_Drawdown']].copy()
        risk_output.to_csv(risk_dir / "daily_risk_metrics.csv", index=False)
        logger.info(f"Saved daily_risk_metrics.csv with {len(risk_output)} rows")
    
    # Save sector exposure
    if not sector_exposure.empty:
        sector_exposure.to_csv(risk_dir / "sector_exposure.csv", index=False)
        logger.info(f"Saved sector_exposure.csv with {len(sector_exposure)} sectors")
    
    # Save portfolio risk/return
    if not portfolio_risk_return.empty:
        portfolio_risk_return.to_csv(portfolio_dir / "portfolio_risk_return.csv", index=False)
        logger.info(f"Saved portfolio_risk_return.csv")


def main():
    try:
        # ==========================
        # 1. Load Config
        # ==========================
        project_root = Path(__file__).resolve().parents[2]
        cfg_path = project_root / "configs" / "risk_config.yaml"
        config = load_config(str(cfg_path))

        output_dir = project_root / config["reporting"]["output_dir"]
        ensure_dirs(output_dir)

        logger.info(f"Config loaded from {cfg_path}")

        # ==========================
        # 2. Load Data
        # ==========================
        trading_file = project_root / config["data"]["trading_file"]
        instruments_file = project_root / config["data"]["instruments_file"]

        trades = pd.read_csv(trading_file, parse_dates=[config["data"]["timestamp_column"]])
        instruments = pd.read_csv(instruments_file)

        # Merge enriched dataset
        df = pd.merge(trades, instruments, on=config["data"]["instrument_column"], how="left")
        df.sort_values(config["data"]["timestamp_column"], inplace=True)
        df["date"] = pd.to_datetime(df[config["data"]["timestamp_column"]]).dt.date

        # Fix volatility scaling: ensure it's in decimal form
        if "volatility_30d" in df.columns:
            df["volatility_30d"] = df["volatility_30d"] / 100.0

        logger.info(f"Trading shape={trades.shape} | Instruments shape={instruments.shape}")
        logger.info(f"Merged shape={df.shape}")

        # Save merged dataset for debugging / validation
        df.to_csv(output_dir / "merged_dataset.csv", index=False)

        # ==========================
        # 3. Portfolio NAV Series
        # ==========================
        initial_nav = config["portfolio"]["initial_nav"]
        pnl_col = config["data"]["pnl_column"]
        daily_pnl = df.groupby("date")[pnl_col].sum()
        nav_series = initial_nav + daily_pnl.cumsum()

        logger.info(f"Initial NAV: ${initial_nav:,.2f}")
        logger.info(f"Final NAV: ${nav_series.iloc[-1]:,.2f}")
        logger.info(f"Total Return: {((nav_series.iloc[-1] - initial_nav) / initial_nav * 100):.2f}%")

        # ==========================
        # 4. Daily Risk Metrics (Time Series)
        # ==========================
        risk_window = config.get("risk", {}).get("rolling_window", 30)
        daily_risk_metrics = generate_daily_risk_metrics(
            df, 
            pnl_col, 
            nav_series, 
            config, 
            window=risk_window
        )

        # ==========================
        # 5. Portfolio-Level Risk Metrics (Summary)
        # ==========================
        var_results = calculate_var_es(df[pnl_col], levels=config["risk"]["var_levels"])
        drawdowns = calculate_drawdowns(nav_series)
        performance = calculate_performance(
            nav_series,
            risk_free_rate=config["performance"]["risk_free_rate"],
        )

        # Add % of NAV to VaR/ES results
        latest_nav = nav_series.iloc[-1]
        for k in list(var_results.keys()):
            if var_results[k] is not None:
                var_results[f"{k}_pctNAV"] = var_results[k] / latest_nav

        logger.info(f"Portfolio Risk Metrics: {var_results}")

        # ==========================
        # 6. Strategy-Level Performance
        # ==========================
        strategy_col = config["data"]["strategy_column"]
        strategy_results = {}
        for strat, strat_df in df.groupby(strategy_col):
            strat_pnl = strat_df.groupby("date")[pnl_col].sum()
            strat_nav = initial_nav + strat_pnl.cumsum()
            strategy_results[strat] = calculate_performance(
                strat_nav,
                risk_free_rate=config["performance"]["risk_free_rate"],
            )
        logger.info(f"Strategy-level performance computed: {list(strategy_results.keys())}")

        # ==========================
        # 7. Sector Exposure
        # ==========================
        sector_exposure = calculate_sector_exposure(df, config)

        # ==========================
        # 8. Portfolio Risk/Return Metrics
        # ==========================
        portfolio_risk_return = calculate_portfolio_risk_return(nav_series, config)

        # ==========================
        # 9. Asset Class Exposures (Legacy)
        # ==========================
        exposures = {
            "sector": df.groupby("sector")["market_cap_usd"].sum().to_dict()
            if "sector" in df.columns else {},
            "asset_class": df.groupby("asset_class")["market_cap_usd"].sum().to_dict()
            if "asset_class" in df.columns else {}
        }

        # ==========================
        # 10. Daily Returns
        # ==========================
        daily_return = nav_series.pct_change().fillna(0.0)

        # ==========================
        # 11. Stress Testing (Portfolio-Level Summary)
        # ==========================
        stress_results = {}
        if config["stress_scenarios"]["enabled"]:
            for name, s in config["stress_scenarios"]["scenarios"].items():
                if s["type"] == "sector":
                    stress_results[name] = sector_shock_impact(
                        df,
                        s["sector_col"],
                        s["target_sector"],
                        s["shock_pct"],
                        nav_series,
                    )
                elif s["type"] == "rates":
                    stress_results[name] = rates_shock_impact(
                        df,
                        s["delta_bps"],
                        s["proxy_duration_col"],
                        nav_series,
                        config["mappings"]["duration_from_credit_rating"],
                        config["mappings"]["default_duration"],
                    )
                elif s["type"] == "vol":
                    stress_results[name] = volatility_shock_impact(
                        df,
                        s["vol_col"],
                        s["vol_mult"],
                        nav_series,
                    )

        logger.info(f"Stress Test Results: {stress_results}")

        # ==========================
        # 12. Save Dashboard-Compatible CSV Files
        # ==========================
        save_dashboard_csvs(
            daily_risk_metrics,
            sector_exposure,
            portfolio_risk_return,
            output_dir
        )

        # ==========================
        # 13. Legacy Reporting (Keep existing reports)
        # ==========================
        save_var_results(var_results, output_dir)
        save_drawdowns(drawdowns, output_dir)
        save_performance(performance, output_dir)
        save_strategy_results(strategy_results, output_dir)
        save_exposures(exposures, output_dir)
        save_stress_summary(stress_results, output_dir)

        # Save CSV + plots
        save_csvs(daily_pnl, daily_return, {}, output_dir)
        sharpe_window = config["performance"]["sharpe_window"]
        drawdown_series = drawdowns.set_index("date")["drawdown"]
        save_plots(daily_pnl, nav_series, daily_return, drawdown_series, output_dir, sharpe_window)

        # ==========================
        # 14. Audit Log
        # ==========================
        audit_data = {
            "run_time": datetime.utcnow().isoformat() + "Z",
            "git_commit": try_git_commit_hash(),
            "snapshots": {
                "trading_csv": sha256(str(trading_file)),
                "instruments_csv": sha256(str(instruments_file)),
            },
            "config": config,
            "var_results": var_results,
            "performance": performance,
            "strategy_results": strategy_results,
            "exposures": exposures,
            "stress_results": stress_results,
            "latest_nav": float(latest_nav),
            "daily_risk_metrics_count": len(daily_risk_metrics),
            "portfolio_metrics": portfolio_risk_return.to_dict('records')[0] if not portfolio_risk_return.empty else {}
        }
        save_audit_log(audit_data, output_dir)

        logger.info("=" * 80)
        logger.info("Risk Analytics Pipeline Completed Successfully")
        logger.info("=" * 80)
        logger.info(f"Dashboard files saved to: {output_dir}")
        logger.info(f"  - daily_risk_metrics.csv: {len(daily_risk_metrics)} rows")
        logger.info(f"  - sector_exposure.csv: {len(sector_exposure)} sectors")
        logger.info(f"  - portfolio_risk_return.csv: 1 row")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()