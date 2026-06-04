"""
AlphaLab AI — Statistical Analysis Engine
Regression, inference, probability, and correlation utilities.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from typing import Optional


# ─── Regression ──────────────────────────────────────────────────────────────

def run_ols_regression(y: pd.Series, X: pd.DataFrame, add_constant: bool = True) -> dict:
    """
    Fit an OLS regression and return a structured results dictionary.

    Parameters
    ----------
    y : pd.Series          Dependent variable
    X : pd.DataFrame       Independent variable(s)
    add_constant : bool    Whether to prepend an intercept term

    Returns a dict with coefficients, statistics, residuals, etc.
    """
    X_model = sm.add_constant(X) if add_constant else X.copy()

    # Align on shared index
    combined = pd.concat([y, X_model], axis=1).dropna()
    y_clean = combined.iloc[:, 0]
    X_clean = combined.iloc[:, 1:]

    model = sm.OLS(y_clean, X_clean)
    result = model.fit()

    coef_df = pd.DataFrame({
        "Coefficient": result.params,
        "Std Error":   result.bse,
        "t-Statistic": result.tvalues,
        "P-Value":     result.pvalues,
        "95% CI Lower": result.conf_int()[0],
        "95% CI Upper": result.conf_int()[1],
    })

    return {
        "summary": result.summary(),
        "coef_df": coef_df,
        "r_squared": result.rsquared,
        "adj_r_squared": result.rsquared_adj,
        "f_statistic": result.fvalue,
        "f_pvalue": result.f_pvalue,
        "aic": result.aic,
        "bic": result.bic,
        "n_obs": int(result.nobs),
        "residuals": result.resid,
        "fitted": result.fittedvalues,
        "y": y_clean,
        "X": X_clean,
        "result_obj": result,
        "dw_statistic": sm.stats.stattools.durbin_watson(result.resid),
    }


def interpret_regression(results: dict) -> str:
    """Generate a plain-English narrative for OLS results."""
    r2 = results["r_squared"]
    adj_r2 = results["adj_r_squared"]
    f_pval = results["f_pvalue"]
    coefs = results["coef_df"]

    sig_vars = coefs[coefs["P-Value"] < 0.05].index.tolist()
    sig_vars = [v for v in sig_vars if v != "const"]

    significance = "statistically significant" if f_pval < 0.05 else "not statistically significant"

    lines = [
        f"The model explains **{r2:.1%}** of the variance in the dependent variable "
        f"(Adjusted R² = {adj_r2:.1%}).",
        f"The overall model is **{significance}** (F-test p-value = {f_pval:.4f}).",
    ]

    if sig_vars:
        lines.append(
            f"Statistically significant predictors (p < 0.05): **{', '.join(sig_vars)}**."
        )
    else:
        lines.append(
            "No individual predictors are statistically significant at the 5% level."
        )

    dw = results.get("dw_statistic")
    if dw is not None:
        if dw < 1.5:
            lines.append(
                f"Durbin-Watson statistic = {dw:.3f} — possible positive autocorrelation in residuals."
            )
        elif dw > 2.5:
            lines.append(
                f"Durbin-Watson statistic = {dw:.3f} — possible negative autocorrelation in residuals."
            )

    lines.append(
        "_Disclaimer: Statistical relationships do not imply causation. "
        "Results should be interpreted with caution and are for research purposes only._"
    )
    return "\n\n".join(lines)


# ─── Statistical Inference ───────────────────────────────────────────────────

def one_sample_ttest(data: pd.Series, popmean: float, alpha: float = 0.05) -> dict:
    """One-sample t-test against a hypothesized population mean."""
    data = data.dropna()
    t_stat, p_value = stats.ttest_1samp(data, popmean=popmean)
    n = len(data)
    se = data.std() / np.sqrt(n)
    ci = stats.t.interval(1 - alpha, df=n - 1, loc=data.mean(), scale=se)
    reject = p_value < alpha
    return {
        "test": "One-Sample t-Test",
        "n": n,
        "sample_mean": data.mean(),
        "sample_std": data.std(),
        "hypothesized_mean": popmean,
        "t_statistic": t_stat,
        "p_value": p_value,
        "ci_lower": ci[0],
        "ci_upper": ci[1],
        "alpha": alpha,
        "reject_null": reject,
        "interpretation": (
            f"With t({n-1}) = {t_stat:.4f}, p = {p_value:.4f}, we "
            + ("**reject**" if reject else "**fail to reject**")
            + f" the null hypothesis that the population mean equals {popmean} "
            f"at the {alpha:.0%} significance level. "
            f"The {(1-alpha):.0%} confidence interval for the mean is "
            f"[{ci[0]:.4f}, {ci[1]:.4f}]."
        ),
    }


def two_sample_ttest(a: pd.Series, b: pd.Series, equal_var: bool = False, alpha: float = 0.05) -> dict:
    """Independent two-sample t-test (Welch's by default)."""
    a, b = a.dropna(), b.dropna()
    t_stat, p_value = stats.ttest_ind(a, b, equal_var=equal_var)
    reject = p_value < alpha
    diff = a.mean() - b.mean()
    test_name = "Two-Sample t-Test (Equal Variance)" if equal_var else "Welch's Two-Sample t-Test"
    return {
        "test": test_name,
        "n_a": len(a),
        "n_b": len(b),
        "mean_a": a.mean(),
        "mean_b": b.mean(),
        "std_a": a.std(),
        "std_b": b.std(),
        "mean_difference": diff,
        "t_statistic": t_stat,
        "p_value": p_value,
        "alpha": alpha,
        "reject_null": reject,
        "interpretation": (
            f"Mean difference = {diff:.4f}. "
            f"With t = {t_stat:.4f}, p = {p_value:.4f}, we "
            + ("**reject**" if reject else "**fail to reject**")
            + f" the null hypothesis of equal means at the {alpha:.0%} level."
        ),
    }


def compute_confidence_interval(data: pd.Series, confidence: float = 0.95) -> dict:
    """Compute a t-distribution based confidence interval for the mean."""
    data = data.dropna()
    n = len(data)
    mean = data.mean()
    se = data.std() / np.sqrt(n)
    ci = stats.t.interval(confidence, df=n - 1, loc=mean, scale=se)
    return {
        "n": n,
        "mean": mean,
        "std": data.std(),
        "se": se,
        "confidence": confidence,
        "ci_lower": ci[0],
        "ci_upper": ci[1],
        "margin_of_error": ci[1] - mean,
    }


# ─── Probability ─────────────────────────────────────────────────────────────

def return_distribution_stats(returns: pd.Series) -> dict:
    """Compute distributional statistics for a return series."""
    returns = returns.dropna()
    skew = float(stats.skew(returns))
    kurt = float(stats.kurtosis(returns))  # excess kurtosis
    jb_stat, jb_p = stats.jarque_bera(returns)
    return {
        "count": len(returns),
        "mean_daily": returns.mean(),
        "std_daily": returns.std(),
        "mean_annual": returns.mean() * 252,
        "std_annual": returns.std() * np.sqrt(252),
        "skewness": skew,
        "excess_kurtosis": kurt,
        "min": returns.min(),
        "max": returns.max(),
        "percentile_5": returns.quantile(0.05),
        "percentile_95": returns.quantile(0.95),
        "jarque_bera_stat": jb_stat,
        "jarque_bera_pvalue": jb_p,
        "is_normal": jb_p > 0.05,
    }


def prob_drawdown_parametric(returns: pd.Series, threshold: float, horizon: int = 1) -> dict:
    """
    Estimate P(cumulative return < threshold) over `horizon` trading days
    using a Normal approximation.

    threshold: e.g. -0.05 for a 5% loss
    """
    returns = returns.dropna()
    mu_d = returns.mean()
    sigma_d = returns.std()
    mu_h = mu_d * horizon
    sigma_h = sigma_d * np.sqrt(horizon)
    z = (threshold - mu_h) / sigma_h
    prob = float(stats.norm.cdf(z))
    return {
        "threshold": threshold,
        "horizon_days": horizon,
        "mu_horizon": mu_h,
        "sigma_horizon": sigma_h,
        "z_score": z,
        "probability": prob,
        "note": (
            "This estimate assumes normally distributed, i.i.d. returns. "
            "In practice, return distributions have fat tails and autocorrelation, "
            "which means tail probabilities may be underestimated."
        ),
    }


def historical_var(returns: pd.Series, confidence: float = 0.95) -> float:
    """Historical Value at Risk at a given confidence level."""
    return float(returns.dropna().quantile(1 - confidence))


def historical_cvar(returns: pd.Series, confidence: float = 0.95) -> float:
    """Historical Conditional VaR (Expected Shortfall)."""
    r = returns.dropna()
    var = historical_var(r, confidence)
    return float(r[r <= var].mean())


# ─── Correlation ─────────────────────────────────────────────────────────────

def compute_correlation_matrix(returns: pd.DataFrame, method: str = "pearson") -> pd.DataFrame:
    """Compute a correlation matrix using pearson, spearman, or kendall."""
    return returns.corr(method=method)


def correlation_pairs(corr_matrix: pd.DataFrame) -> pd.DataFrame:
    """Extract unique (i, j) correlation pairs sorted by absolute value."""
    rows = []
    cols = corr_matrix.columns.tolist()
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            rows.append({
                "Asset A": cols[i],
                "Asset B": cols[j],
                "Correlation": corr_matrix.iloc[i, j],
            })
    df = pd.DataFrame(rows).sort_values("Correlation", key=abs, ascending=False)
    return df.reset_index(drop=True)


def diversification_ratio(weights: np.ndarray, cov_matrix: np.ndarray) -> float:
    """
    Diversification ratio = weighted avg vol / portfolio vol.
    Higher ratio = more diversification benefit.
    """
    vols = np.sqrt(np.diag(cov_matrix))
    weighted_avg_vol = float(weights @ vols)
    port_vol = float(np.sqrt(weights @ cov_matrix @ weights))
    if port_vol == 0:
        return 1.0
    return weighted_avg_vol / port_vol
