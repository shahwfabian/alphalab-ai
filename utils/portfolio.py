"""
AlphaLab AI — Portfolio Optimization Engine
Modern Portfolio Theory via scipy.optimize.
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Optional


TRADING_DAYS = 252


def compute_portfolio_stats(weights: np.ndarray, mean_returns: np.ndarray, cov_matrix: np.ndarray) -> tuple:
    """
    Compute annualized portfolio return, volatility, and Sharpe ratio.

    Returns (return, volatility, sharpe)
    """
    port_return = float(np.dot(weights, mean_returns) * TRADING_DAYS)
    port_vol = float(np.sqrt(weights @ cov_matrix @ weights) * np.sqrt(TRADING_DAYS))
    return port_return, port_vol


def sharpe_ratio(weights: np.ndarray, mean_returns: np.ndarray, cov_matrix: np.ndarray, rf: float = 0.0) -> float:
    """Annualized Sharpe ratio."""
    ret, vol = compute_portfolio_stats(weights, mean_returns, cov_matrix)
    if vol == 0:
        return 0.0
    return (ret - rf) / vol


def negative_sharpe(weights, mean_returns, cov_matrix, rf):
    """Negative Sharpe for minimization."""
    return -sharpe_ratio(weights, mean_returns, cov_matrix, rf)


def portfolio_volatility(weights, mean_returns, cov_matrix):
    _, vol = compute_portfolio_stats(weights, mean_returns, cov_matrix)
    return vol


def optimize_max_sharpe(mean_returns: np.ndarray, cov_matrix: np.ndarray, rf: float = 0.0,
                        weight_bounds: tuple = (0.0, 1.0)) -> dict:
    """Find the Maximum Sharpe Ratio portfolio."""
    n = len(mean_returns)
    x0 = np.ones(n) / n
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    bounds = [weight_bounds] * n

    result = minimize(
        negative_sharpe,
        x0,
        args=(mean_returns, cov_matrix, rf),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000, "ftol": 1e-12},
    )
    weights = result.x
    ret, vol = compute_portfolio_stats(weights, mean_returns, cov_matrix)
    sr = sharpe_ratio(weights, mean_returns, cov_matrix, rf)
    return {"weights": weights, "return": ret, "volatility": vol, "sharpe": sr, "success": result.success}


def optimize_min_variance(mean_returns: np.ndarray, cov_matrix: np.ndarray,
                          weight_bounds: tuple = (0.0, 1.0)) -> dict:
    """Find the Minimum Variance portfolio."""
    n = len(mean_returns)
    x0 = np.ones(n) / n
    constraints = [{"type": "eq", "fun": lambda w: np.sum(w) - 1}]
    bounds = [weight_bounds] * n

    result = minimize(
        portfolio_volatility,
        x0,
        args=(mean_returns, cov_matrix),
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={"maxiter": 1000, "ftol": 1e-12},
    )
    weights = result.x
    ret, vol = compute_portfolio_stats(weights, mean_returns, cov_matrix)
    rf = 0.0
    sr = sharpe_ratio(weights, mean_returns, cov_matrix, rf)
    return {"weights": weights, "return": ret, "volatility": vol, "sharpe": sr, "success": result.success}


def equal_weight_portfolio(mean_returns: np.ndarray, cov_matrix: np.ndarray, rf: float = 0.0) -> dict:
    """Equal weight portfolio."""
    n = len(mean_returns)
    weights = np.ones(n) / n
    ret, vol = compute_portfolio_stats(weights, mean_returns, cov_matrix)
    sr = sharpe_ratio(weights, mean_returns, cov_matrix, rf)
    return {"weights": weights, "return": ret, "volatility": vol, "sharpe": sr}


def generate_efficient_frontier(mean_returns: np.ndarray, cov_matrix: np.ndarray,
                                rf: float = 0.0, n_points: int = 100,
                                weight_bounds: tuple = (0.0, 1.0)) -> pd.DataFrame:
    """
    Generate the efficient frontier by sweeping target returns from
    min-variance to max-return.
    """
    n = len(mean_returns)
    max_ret = float(mean_returns.max() * TRADING_DAYS)
    min_port = optimize_min_variance(mean_returns, cov_matrix, weight_bounds)
    min_ret = min_port["return"]

    target_returns = np.linspace(min_ret, max_ret * 0.95, n_points)
    results = []

    for target in target_returns:
        constraints = [
            {"type": "eq", "fun": lambda w: np.sum(w) - 1},
            {"type": "eq", "fun": lambda w, t=target: compute_portfolio_stats(w, mean_returns, cov_matrix)[0] - t},
        ]
        bounds = [weight_bounds] * n
        x0 = np.ones(n) / n
        res = minimize(
            portfolio_volatility,
            x0,
            args=(mean_returns, cov_matrix),
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
            options={"maxiter": 500, "ftol": 1e-10},
        )
        if res.success:
            ret, vol = compute_portfolio_stats(res.x, mean_returns, cov_matrix)
            sr = (ret - rf) / vol if vol > 0 else 0.0
            results.append({"Return": ret, "Volatility": vol, "Sharpe": sr})

    return pd.DataFrame(results)


def generate_random_portfolios(mean_returns: np.ndarray, cov_matrix: np.ndarray,
                               rf: float = 0.0, n: int = 3000) -> pd.DataFrame:
    """Monte Carlo sample of random portfolio allocations for visualization."""
    n_assets = len(mean_returns)
    records = []
    rng = np.random.default_rng(42)
    for _ in range(n):
        w = rng.dirichlet(np.ones(n_assets))
        ret, vol = compute_portfolio_stats(w, mean_returns, cov_matrix)
        sr = (ret - rf) / vol if vol > 0 else 0.0
        records.append({"Return": ret, "Volatility": vol, "Sharpe": sr, "Weights": w.tolist()})
    return pd.DataFrame(records)


def build_portfolio_summary(tickers: list[str], weights: np.ndarray,
                            mean_returns: np.ndarray, cov_matrix: np.ndarray,
                            rf: float = 0.0) -> pd.DataFrame:
    """Return a formatted DataFrame of portfolio weights and contribution stats."""
    ret, vol = compute_portfolio_stats(weights, mean_returns, cov_matrix)
    indiv_vols = np.sqrt(np.diag(cov_matrix)) * np.sqrt(TRADING_DAYS)
    indiv_rets = mean_returns * TRADING_DAYS

    df = pd.DataFrame({
        "Ticker": tickers,
        "Weight (%)": (weights * 100).round(2),
        "Asset Return (%)": (indiv_rets * 100).round(2),
        "Asset Volatility (%)": (indiv_vols * 100).round(2),
    })
    df["Weighted Return (%)"] = (df["Weight (%)"] / 100 * df["Asset Return (%)"]).round(2)
    return df
