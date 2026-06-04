"""
AlphaLab AI — Module Definitions
Each module has a name, description, system prompt, welcome message, and analysis handler.
"""

import re
import pandas as pd
import numpy as np
import streamlit as st


# ── Module registry ───────────────────────────────────────────────────────────

MODULES = [
    {
        "id":      "research",
        "name":    "Research Assistant",
        "desc":    "Ask any statistical or finance question in plain English.",
        "prompt":  "You are AlphaLab AI, a rigorous quantitative research assistant. You help users understand statistical methods, interpret results, and design analyses. Be concise, precise, and always highlight uncertainty, assumptions, and limitations. Never claim certainty about future outcomes. Format responses clearly with structure when helpful.",
        "welcome": "I'm your research assistant. Ask me anything — statistical methods, how to interpret results, what analysis fits your question, or how financial models work. What would you like to explore?",
        "starters": [
            "What's the difference between R² and Adjusted R²?",
            "When should I use log returns vs simple returns?",
            "How do I test if a strategy has alpha?",
            "Explain Value at Risk in plain English.",
        ],
    },
    {
        "id":      "regression",
        "name":    "Regression Lab",
        "desc":    "OLS regression with full diagnostics and interpretation.",
        "prompt":  "You are a regression analysis expert. Help users run OLS regressions, interpret coefficients, R², p-values, and diagnostics. When users mention tickers and want regression, ask for any missing info (dependent variable, independent variables, date range) then confirm before analysis. Always explain assumptions and limitations.",
        "welcome": "I can run OLS regression on any market data or uploaded dataset.\n\nTell me what you'd like to analyze — for example:\n- *\"Does QQQ explain NVDA returns better than SPY?\"*\n- *\"Run a regression of AAPL on the S&P 500 from 2020 to 2024\"*\n\nWhat would you like to test?",
        "starters": [
            "Does QQQ explain NVDA returns better than SPY?",
            "Run regression of TSLA on SPY from 2021 to 2024",
            "What does beta mean in regression?",
            "How do I interpret a p-value of 0.03?",
        ],
    },
    {
        "id":      "inference",
        "name":    "Statistical Inference",
        "desc":    "Hypothesis testing, t-tests, and confidence intervals.",
        "prompt":  "You are a statistical inference expert. Help users design and interpret hypothesis tests, t-tests, confidence intervals. When users want a test run, identify the right test, explain the null/alternative hypotheses, then run it. Always explain what the p-value means in context and warn about the distinction between statistical and practical significance.",
        "welcome": "I can run hypothesis tests and build confidence intervals on market return data.\n\nFor example:\n- *\"Test whether SPY's mean daily return is significantly different from zero\"*\n- *\"Compare the mean returns of QQQ vs SPY\"*\n- *\"Give me a 95% confidence interval for AAPL returns\"*\n\nWhat would you like to test?",
        "starters": [
            "Is SPY's mean daily return significantly different from zero?",
            "Compare average returns of QQQ vs SPY",
            "Build a 95% confidence interval for NVDA daily returns",
            "What's the difference between Type I and Type II error?",
        ],
    },
    {
        "id":      "probability",
        "name":    "Probability Lab",
        "desc":    "Return distributions, VaR, CVaR, drawdown probability.",
        "prompt":  "You are a probability and risk modeling expert. Help users model return distributions, estimate tail risk, compute VaR and CVaR, and calculate drawdown probabilities. When users ask probability questions with a ticker, run the analysis. Always explain the assumptions behind Normal approximations and warn about fat tails.",
        "welcome": "I can model return distributions and estimate the probability of specific outcomes.\n\nFor example:\n- *\"What is the probability of SPY dropping more than 5% in the next 30 days?\"*\n- *\"Show me the return distribution and VaR for NVDA\"*\n- *\"What's the historical max drawdown of QQQ?\"*\n\nWhat would you like to model?",
        "starters": [
            "What is the probability of SPY dropping 5% in 30 days?",
            "Show me the return distribution for NVDA",
            "What's the 95% VaR for QQQ?",
            "Explain the difference between VaR and CVaR",
        ],
    },
    {
        "id":      "portfolio",
        "name":    "Portfolio Optimization",
        "desc":    "Max Sharpe, Min Variance, and Efficient Frontier.",
        "prompt":  "You are a portfolio optimization expert specializing in Modern Portfolio Theory. Help users build optimal portfolios, understand the efficient frontier, and interpret Sharpe ratios. When users provide tickers, run the optimization. Always explain MPT's assumptions and limitations prominently.",
        "welcome": "I can optimize a portfolio using Modern Portfolio Theory.\n\nFor example:\n- *\"Build the highest Sharpe portfolio from SPY, QQQ, GLD, TLT, VNQ\"*\n- *\"What's the minimum variance portfolio for these 5 assets?\"*\n- *\"Show me the efficient frontier for tech stocks\"*\n\nWhich assets would you like to optimize?",
        "starters": [
            "Build the highest Sharpe portfolio from SPY, QQQ, GLD, TLT, VNQ",
            "What's the minimum variance portfolio for AAPL, MSFT, GOOGL?",
            "Explain the efficient frontier",
            "How sensitive is MPT to input assumptions?",
        ],
    },
    {
        "id":      "correlation",
        "name":    "Correlation Explorer",
        "desc":    "Correlation matrices, heatmaps, rolling correlation.",
        "prompt":  "You are a correlation and diversification analysis expert. Help users understand co-movement between assets, identify diversification opportunities, and interpret correlation matrices. When users provide tickers, run the analysis. Always warn that correlations are not stable over time and tend to increase during market stress.",
        "welcome": "I can analyze correlations and co-movement across any set of assets.\n\nFor example:\n- *\"Show me the correlation matrix for SPY, QQQ, GLD, TLT, BTC\"*\n- *\"Which assets in my portfolio are most correlated?\"*\n- *\"How has the rolling correlation between SPY and GLD changed?\"*\n\nWhich assets would you like to analyze?",
        "starters": [
            "Show me the correlation matrix for SPY, QQQ, GLD, TLT, BTC-USD",
            "Which pairs in SPY, AAPL, MSFT, NVDA are most correlated?",
            "How has SPY vs GLD correlation changed over time?",
            "What is a good diversification ratio?",
        ],
    },
    {
        "id":      "data",
        "name":    "Data Upload",
        "desc":    "Upload a CSV and explore it automatically.",
        "prompt":  "You are a data exploration and analysis expert. Help users understand their uploaded datasets, identify data quality issues, and recommend appropriate analyses. Be specific about what you observe in the data and give actionable recommendations.",
        "welcome": "Upload a CSV file and I'll automatically explore it — detect column types, flag missing values, show summary statistics, and recommend which AlphaLab analyses fit your data best.\n\nYou can upload any tabular dataset: price data, returns, financial metrics, or anything numeric.",
        "starters": [
            "What analyses can I run on my uploaded data?",
            "How do I handle missing values in my dataset?",
            "What does skewness tell me about my return series?",
            "How many data points do I need for reliable regression?",
        ],
    },
    {
        "id":      "reports",
        "name":    "Research Reports",
        "desc":    "Generate and export a professional research report.",
        "prompt":  "You are a research report specialist. Help users structure their quantitative research findings into professional reports. Guide them through defining their research question, methodology, assumptions, and conclusions. Always emphasize that reports are for research purposes only.",
        "welcome": "I can generate a professional research report — regression analysis, portfolio optimization, correlation study, or a custom report.\n\nTell me what analysis you want to document and I'll guide you through it. The final report exports as a clean HTML file.\n\nWhat would you like to report on?",
        "starters": [
            "Generate a regression report for NVDA vs QQQ and SPY",
            "Create a portfolio optimization report for SPY, QQQ, GLD, TLT",
            "Build a correlation analysis report for tech stocks",
            "What sections should a good quant research report have?",
        ],
    },
]

MODULE_MAP = {m["id"]: m for m in MODULES}


# ── Ticker extraction ─────────────────────────────────────────────────────────

COMMON_WORDS = {
    "I", "A", "AN", "THE", "AND", "OR", "IN", "ON", "AT", "TO", "FOR",
    "OF", "IS", "IT", "AS", "BE", "MY", "ME", "DO", "NO", "UP", "SO",
    "BY", "IF", "VS", "TO", "FROM", "CAN", "GET", "RUN", "USE", "ALL",
    "OLS", "MPT", "VaR", "ETF", "USD", "API", "CSV", "ML", "AI", "RF",
}

def extract_tickers(text: str) -> list[str]:
    """Extract likely ticker symbols from user message."""
    candidates = re.findall(r'\b[A-Z]{2,5}(?:-[A-Z]{2,3})?\b', text.upper())
    return [c for c in candidates if c not in COMMON_WORDS]


def extract_years(text: str) -> tuple[str | None, str | None]:
    """Extract start/end years from a message like 'from 2020 to 2024'."""
    years = re.findall(r'\b(20\d{2})\b', text)
    if len(years) >= 2:
        return f"{years[0]}-01-01", f"{years[-1]}-12-31"
    if len(years) == 1:
        return f"{years[0]}-01-01", "2024-12-31"
    return None, None


# ── Intent detection ──────────────────────────────────────────────────────────

def detect_intent(text: str, module_id: str) -> str:
    """Detect whether the message contains an analysis request."""
    t = text.lower()

    run_words = ["run", "show", "compute", "calculate", "give me", "what is", "analyze",
                 "build", "create", "optimize", "regress", "test", "find", "plot", "display"]
    has_run = any(w in t for w in run_words)

    tickers = extract_tickers(text)

    if not has_run or not tickers:
        return "conversational"

    if module_id == "regression"   and len(tickers) >= 2: return "run_regression"
    if module_id == "inference"    and len(tickers) >= 1: return "run_inference"
    if module_id == "probability"  and len(tickers) >= 1: return "run_probability"
    if module_id == "portfolio"    and len(tickers) >= 2: return "run_portfolio"
    if module_id == "correlation"  and len(tickers) >= 2: return "run_correlation"

    return "conversational"


# ── Analysis runners ──────────────────────────────────────────────────────────

def run_analysis_from_chat(module_id: str, user_message: str) -> dict:
    """
    Attempt to run an analysis based on a user message.
    Returns {"ran": bool, "summary": str, "fig": fig or None, "df": df or None}
    """
    from utils.data_loader import fetch_simple_returns, DEFAULT_START, DEFAULT_END
    from utils.statistics import (run_ols_regression, interpret_regression,
                                   return_distribution_stats, prob_drawdown_parametric,
                                   historical_var, historical_cvar,
                                   compute_correlation_matrix, correlation_pairs)
    from utils.portfolio import optimize_max_sharpe, equal_weight_portfolio
    from utils.charts import (scatter_regression, correlation_heatmap,
                               returns_histogram, efficient_frontier_chart,
                               portfolio_weights_bar)

    tickers = extract_tickers(user_message)
    start, end = extract_years(user_message)
    start = start or DEFAULT_START
    end   = end   or DEFAULT_END

    try:
        if module_id == "run_regression" and len(tickers) >= 2:
            rets = fetch_simple_returns(tickers, start, end)
            valid = [t for t in tickers if t in rets.columns]
            if len(valid) < 2:
                return {"ran": False, "summary": f"Could not load data for: {', '.join(tickers)}"}
            y, X = rets[valid[0]], rets[valid[1:]]
            res  = run_ols_regression(y, X)
            coefs = res["coef_df"]["Coefficient"]
            fig  = None
            if len(valid) == 2:
                fig = scatter_regression(res["X"].iloc[:,-1], res["y"], valid[1], valid[0],
                                         float(coefs.iloc[-1]), float(coefs.get("const", 0)))
            return {
                "ran": True,
                "summary": f"**{valid[0]} ~ {' + '.join(valid[1:])}** · R² = {res['r_squared']:.4f} · Adj. R² = {res['adj_r_squared']:.4f} · F p-value = {res['f_pvalue']:.4f} · N = {res['n_obs']}\n\n{interpret_regression(res)}",
                "fig": fig,
                "df":  res["coef_df"].round(6),
            }

        elif module_id == "run_probability" and len(tickers) >= 1:
            ticker = tickers[0]
            rets   = fetch_simple_returns([ticker], start, end)
            if ticker not in rets.columns:
                return {"ran": False, "summary": f"Could not load data for {ticker}."}
            s     = rets[ticker].dropna()
            ds    = return_distribution_stats(s)
            var95 = historical_var(s, 0.95)
            cvar95= historical_cvar(s, 0.95)
            fig   = returns_histogram(s, ticker, bins=60)
            rf    = st.session_state.get("risk_free_rate", 0.05)
            ann_ret = ds["mean_annual"]
            ann_vol = ds["std_annual"]
            sharpe  = (ann_ret - rf) / ann_vol if ann_vol > 0 else 0
            return {
                "ran": True,
                "summary": f"**{ticker} Return Distribution** ({start[:4]}–{end[:4]})\n\n"
                           f"Ann. Return **{ann_ret:.2%}** · Ann. Vol **{ann_vol:.2%}** · Sharpe **{sharpe:.3f}**\n\n"
                           f"95% VaR **{var95:.2%}** · 95% CVaR **{cvar95:.2%}**\n\n"
                           f"Skewness **{ds['skewness']:.3f}** · Excess Kurtosis **{ds['excess_kurtosis']:.3f}** · "
                           f"Normal? **{'Yes' if ds['is_normal'] else 'No'}** (JB p = {ds['jarque_bera_pvalue']:.4f})",
                "fig": fig,
                "df": None,
            }

        elif module_id == "run_portfolio" and len(tickers) >= 2:
            rets  = fetch_simple_returns(tickers, start, end)
            valid = [t for t in tickers if t in rets.columns]
            if len(valid) < 2:
                return {"ran": False, "summary": f"Could not load enough data. Valid: {valid}"}
            rets  = rets[valid].dropna()
            mu, cov = rets.mean().values, rets.cov().values
            rf    = st.session_state.get("risk_free_rate", 0.05)
            ms    = optimize_max_sharpe(mu, cov, rf)
            eq    = equal_weight_portfolio(mu, cov, rf)
            fig   = portfolio_weights_bar(valid, ms["weights"], "Max Sharpe Weights")
            wt_str = " · ".join([f"{t} **{w:.1%}**" for t, w in zip(valid, ms["weights"])])
            return {
                "ran": True,
                "summary": f"**Max Sharpe Portfolio** ({', '.join(valid)}) · RF = {rf:.2%}\n\n"
                           f"Return **{ms['return']:.2%}** · Volatility **{ms['volatility']:.2%}** · Sharpe **{ms['sharpe']:.3f}**\n\n"
                           f"Weights: {wt_str}\n\n"
                           f"vs Equal Weight — Return **{eq['return']:.2%}** · Sharpe **{eq['sharpe']:.3f}**",
                "fig": fig,
                "df": pd.DataFrame({"Ticker": valid, "Weight (%)": (ms["weights"]*100).round(2)}),
            }

        elif module_id == "run_correlation" and len(tickers) >= 2:
            rets  = fetch_simple_returns(tickers, start, end)
            valid = [t for t in tickers if t in rets.columns]
            if len(valid) < 2:
                return {"ran": False, "summary": f"Could not load enough data. Valid: {valid}"}
            rets  = rets[valid].dropna()
            corr  = compute_correlation_matrix(rets)
            pairs = correlation_pairs(corr)
            fig   = correlation_heatmap(corr)
            top   = pairs.iloc[0]
            bot   = pairs.iloc[-1]
            return {
                "ran": True,
                "summary": f"**Correlation Matrix** ({', '.join(valid)}) · Period {start[:4]}–{end[:4]}\n\n"
                           f"Average pairwise correlation: **{pairs['Correlation'].mean():.3f}**\n\n"
                           f"Most correlated: **{top['Asset A']} / {top['Asset B']}** (r = {top['Correlation']:.3f})\n\n"
                           f"Best diversifier: **{bot['Asset A']} / {bot['Asset B']}** (r = {bot['Correlation']:.3f})",
                "fig": fig,
                "df": pairs.round(3),
            }

        elif module_id == "run_inference" and len(tickers) >= 1:
            ticker = tickers[0]
            rets   = fetch_simple_returns([ticker], start, end)
            if ticker not in rets.columns:
                return {"ran": False, "summary": f"Could not load data for {ticker}."}
            from utils.statistics import one_sample_ttest
            res = one_sample_ttest(rets[ticker], popmean=0.0, alpha=0.05)
            return {
                "ran": True,
                "summary": f"**One-Sample t-Test: {ticker} mean daily return = 0**\n\n"
                           f"N = {res['n']} · Mean = {res['sample_mean']:.6f} · t = {res['t_statistic']:.4f} · p = {res['p_value']:.6f}\n\n"
                           f"**{'Reject H₀' if res['reject_null'] else 'Fail to reject H₀'}** at 5% level.\n\n"
                           f"95% CI: [{res['ci_lower']:.6f}, {res['ci_upper']:.6f}]\n\n"
                           f"{res['interpretation']}",
                "fig": None,
                "df": None,
            }

    except Exception as e:
        return {"ran": False, "summary": f"Analysis error: {e}"}

    return {"ran": False, "summary": ""}
