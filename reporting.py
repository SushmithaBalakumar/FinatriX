"""
Reporting utilities for Risk Analytics Platform
Handles saving risk metrics, exposures, stress tests, plots, and audit logs.
Industry-ready with JSON, CSV, and PNG outputs for reproducibility.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any

import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------
# Logging Setup
# ---------------------------------
logger = logging.getLogger("risk_analytics.reporting")
logger.setLevel(logging.INFO)


# ---------------------------------
# Core Utilities
# ---------------------------------
def ensure_dir(path: Path):
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)


# ---------------------------------
# Save Functions
# ---------------------------------
def save_var_results(var_results: Dict[str, Any], out_dir: Path):
    """Save portfolio-level VaR/ES results to JSON."""
    ensure_dir(out_dir)
    filepath = out_dir / "var_results.json"
    try:
        with open(filepath, "w") as f:
            json.dump(var_results, f, indent=2, default=str)
        logger.info(f"✅ VaR/ES results saved at {filepath}")
    except Exception as e:
        logger.error(f"❌ Failed to save VaR/ES results: {e}")


def save_strategy_results(strategy_results: Dict[str, Dict[str, Any]], out_dir: Path):
    """Save strategy-level performance metrics."""
    ensure_dir(out_dir)
    filepath = out_dir / "strategy_results.json"
    try:
        with open(filepath, "w") as f:
            json.dump(strategy_results, f, indent=2, default=str)
        logger.info(f"✅ Strategy results saved at {filepath}")
    except Exception as e:
        logger.error(f"❌ Failed to save strategy results: {e}")


def save_exposures(exposures: Dict[str, Any], out_dir: Path):
    """Save exposures (sector/instrument level)."""
    ensure_dir(out_dir)
    filepath = out_dir / "exposures.json"
    try:
        with open(filepath, "w") as f:
            json.dump(exposures, f, indent=2, default=str)
        logger.info(f"✅ Exposures saved at {filepath}")
    except Exception as e:
        logger.error(f"❌ Failed to save exposures: {e}")


def save_drawdowns(drawdowns: pd.DataFrame, out_dir: Path):
    """Save drawdown series to CSV."""
    ensure_dir(out_dir)
    filepath = out_dir / "drawdowns.csv"
    try:
        drawdowns.to_csv(filepath, index=False)
        logger.info(f"✅ Drawdowns saved at {filepath}")
    except Exception as e:
        logger.error(f"❌ Failed to save drawdowns: {e}")


def save_performance(performance: Dict[str, Any], out_dir: Path):
    """Save performance metrics to JSON."""
    ensure_dir(out_dir)
    filepath = out_dir / "performance.json"
    try:
        with open(filepath, "w") as f:
            json.dump(performance, f, indent=2, default=str)
        logger.info(f"✅ Performance metrics saved at {filepath}")
    except Exception as e:
        logger.error(f"❌ Failed to save performance metrics: {e}")


def save_stress_summary(stress_results: Dict[str, Any], out_dir: Path):
    """Save stress testing results to JSON."""
    ensure_dir(out_dir)
    filepath = out_dir / "stress_summary.json"
    try:
        with open(filepath, "w") as f:
            json.dump(stress_results, f, indent=2, default=str)
        logger.info(f"✅ Stress test summary saved at {filepath}")
    except Exception as e:
        logger.error(f"❌ Failed to save stress test summary: {e}")


def save_audit_log(audit_dict: Dict[str, Any], out_dir: Path):
    """Save full audit metadata as JSON."""
    ensure_dir(out_dir)
    filepath = out_dir / "audit.json"
    try:
        with open(filepath, "w") as f:
            json.dump(audit_dict, f, indent=2, default=str)
        logger.info(f"✅ Audit log saved at {filepath}")
    except Exception as e:
        logger.error(f"❌ Failed to save audit log: {e}")


def save_csvs(
    daily_pnl: pd.Series,
    daily_return: pd.Series,
    strat_returns: Dict[str, pd.Series],
    out_dir: Path,
):
    """Save PnL and returns to CSVs."""
    ensure_dir(out_dir)
    try:
        daily_pnl.to_csv(out_dir / "daily_pnl.csv", index=True)
        daily_return.to_csv(out_dir / "daily_returns.csv", index=True)

        for strat, series in strat_returns.items():
            series.to_csv(out_dir / f"strategy_returns_{strat}.csv", index=True)

        logger.info(f"📊 CSV outputs saved under: {out_dir}")
    except Exception as e:
        logger.error(f"❌ Failed to save CSV outputs: {e}")


def save_plots(
    daily_pnl: pd.Series,
    cum_returns: pd.Series,
    rolling_sharpe: pd.Series,
    drawdown: pd.Series,
    out_dir: Path,
    sharpe_window: int,
):
    """Save key performance plots for visualization."""
    ensure_dir(out_dir)
    try:
        # Daily PnL
        daily_pnl.plot(title="Daily PnL", figsize=(10, 4))
        plt.tight_layout()
        plt.savefig(out_dir / "daily_pnl.png")
        plt.close()

        # Cumulative Returns
        cum_returns.plot(title="Cumulative Returns", figsize=(10, 4))
        plt.tight_layout()
        plt.savefig(out_dir / "cumulative_returns.png")
        plt.close()

        # Rolling Sharpe
        rolling_sharpe.plot(title=f"Rolling Sharpe Ratio ({sharpe_window}-day)", figsize=(10, 4))
        plt.axhline(0, color="red", linestyle="--", linewidth=1)
        plt.tight_layout()
        plt.savefig(out_dir / "rolling_sharpe.png")
        plt.close()

        # Drawdowns
        drawdown.plot(title="Drawdowns", figsize=(10, 4))
        plt.axhline(0, color="black", linestyle="--", linewidth=1)
        plt.tight_layout()
        plt.savefig(out_dir / "drawdowns.png")
        plt.close()

        logger.info(f"📈 Plots saved under: {out_dir}")
    except Exception as e:
        logger.error(f"❌ Failed to save plots: {e}")
