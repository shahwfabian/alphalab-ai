"""
AlphaLab AI — AI Explainer
OpenAI-powered research assistant with structured outputs and mock fallback.
"""

import os
import re
import streamlit as st
from typing import Optional


SYSTEM_PROMPT = """You are AlphaLab AI, a quantitative research assistant.
You help users understand statistical methods, financial data analysis, and
research design. You are rigorous, evidence-based, and always emphasize uncertainty,
assumptions, and limitations. You never claim certainty about future outcomes.
You structure every response with:
- Method Selected
- Why This Method Fits
- Inputs Needed
- Assumptions
- Expected Output
- Limitations

You use clear, professional language appropriate for a quantitative research context.
You never provide financial advice. This is a research and educational tool."""


MOCK_RESPONSES = {
    "regression": {
        "method": "Ordinary Least Squares (OLS) Regression",
        "why": "OLS is the standard approach for estimating linear relationships between a dependent variable and one or more independent variables. It minimizes the sum of squared residuals.",
        "inputs": "Dependent variable (e.g., NVDA daily returns), independent variable(s) (e.g., QQQ returns, SPY returns), historical price data for your chosen time window.",
        "assumptions": "1. Linear relationship between variables\n2. Errors are normally distributed\n3. Homoscedasticity (constant variance of errors)\n4. No perfect multicollinearity among predictors\n5. Independence of observations",
        "output": "Regression coefficients (Beta), R², Adjusted R², p-values for each predictor, confidence intervals, residual plots, and a plain-English interpretation of explanatory power.",
        "limitations": "OLS assumes stationarity and linear relationships. Financial returns often exhibit autocorrelation, heteroscedasticity, and fat tails — all of which violate OLS assumptions. Results should be interpreted cautiously and validated with diagnostics.",
    },
    "correlation": {
        "method": "Pearson Correlation Analysis",
        "why": "Pearson correlation measures the linear association between two variables. For financial assets, it quantifies co-movement and diversification potential.",
        "inputs": "Return series for two or more assets over the same time period. Minimum 30 data points recommended for reliability.",
        "assumptions": "1. Linear relationship between variables\n2. Variables are approximately normally distributed\n3. No significant outliers\n4. Stationarity (stable correlation over time)",
        "output": "Correlation matrix, heatmap, ranked correlation pairs (highest to lowest), and interpretation of diversification implications.",
        "limitations": "Correlation is not causation. Correlations are unstable over time and often increase during market stress — exactly when diversification is most needed. Pearson correlation only captures linear relationships.",
    },
    "probability": {
        "method": "Historical Simulation + Parametric Normal Approximation",
        "why": "Combining historical simulation with a parametric model gives both empirically-grounded estimates and analytical tractability. The normal approximation enables quick probability calculations.",
        "inputs": "Historical daily return series for the asset, time horizon (days), threshold level (e.g., -5% drawdown).",
        "assumptions": "1. Returns are i.i.d. (independently and identically distributed)\n2. Historical distribution is representative of future behavior\n3. Normal approximation may underestimate tail risk",
        "output": "Probability estimate of the threshold event, historical VaR, CVaR (Expected Shortfall), return distribution chart with highlighted tail region.",
        "limitations": "Financial returns have fat tails and autocorrelation, violating i.i.d. assumptions. Normal distribution systematically underestimates extreme event probabilities. These are statistical estimates, not predictions.",
    },
    "portfolio": {
        "method": "Mean-Variance Optimization (Modern Portfolio Theory)",
        "why": "MPT finds the portfolio allocation that maximizes expected return for a given level of risk (or minimizes risk for a given return), tracing the efficient frontier.",
        "inputs": "List of asset tickers, historical returns for expected return estimates, covariance matrix estimation, risk-free rate.",
        "assumptions": "1. Returns are normally distributed\n2. Investors are risk-averse and rational\n3. Historical covariances are representative of future covariances\n4. No transaction costs, taxes, or short-selling constraints (unless specified)",
        "output": "Optimal portfolio weights, annualized return, volatility, Sharpe ratio, efficient frontier chart, comparison of equal-weight vs optimal portfolios.",
        "limitations": "MPT is highly sensitive to input estimates — especially expected returns. Small changes in assumptions can produce dramatically different allocations. In-sample optimization tends to overfit. This is a theoretical framework, not a trading strategy.",
    },
    "inference": {
        "method": "Hypothesis Testing (t-Test)",
        "why": "T-tests allow us to assess whether an observed difference or mean is statistically distinguishable from a null hypothesis, accounting for sample size and variance.",
        "inputs": "Sample data series (e.g., strategy returns), hypothesized population mean (e.g., 0 for 'no alpha'), significance level α.",
        "assumptions": "1. Data is approximately normally distributed (or n > 30 by CLT)\n2. Observations are independent\n3. Sample is representative of the population",
        "output": "T-statistic, p-value, confidence interval, decision to reject or fail to reject the null hypothesis, and plain-English interpretation.",
        "limitations": "Statistical significance ≠ practical significance. With large sample sizes, trivially small effects become 'significant.' Multiple testing inflates false positive rates. Failing to reject H₀ does not prove H₀ is true.",
    },
}


def classify_question(question: str) -> str:
    """Rule-based classifier to identify the research method from a question."""
    q = question.lower()
    if any(k in q for k in ["regress", "beta", "r-squared", "explain", "predict", "coefficient"]):
        return "regression"
    if any(k in q for k in ["correlat", "co-move", "diversif", "relationship between"]):
        return "correlation"
    if any(k in q for k in ["probabilit", "chance", "drawdown", "loss", "var", "tail risk"]):
        return "probability"
    if any(k in q for k in ["portfolio", "sharpe", "allocat", "frontier", "optimiz", "weight"]):
        return "portfolio"
    if any(k in q for k in ["test", "hypothesis", "significance", "p-value", "confidence interval", "mean"]):
        return "inference"
    return "regression"  # default


MODULE_MAP = {
    "regression":  "Regression Lab",
    "correlation": "Correlation Explorer",
    "probability": "Probability Lab",
    "portfolio":   "Portfolio Optimization Lab",
    "inference":   "Statistical Inference Lab",
}


def get_mock_response(question: str) -> dict:
    """Return a structured mock response based on question classification."""
    category = classify_question(question)
    data = MOCK_RESPONSES[category]
    return {
        "category": category,
        "question": question,
        "method": data["method"],
        "why": data["why"],
        "inputs": data["inputs"],
        "assumptions": data["assumptions"],
        "output": data["output"],
        "limitations": data["limitations"],
        "suggested_module": MODULE_MAP[category],
        "source": "mock",
    }


def get_openai_response(question: str, api_key: str) -> dict:
    """Query OpenAI with a structured prompt and parse the response."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        user_prompt = f"""Research question: "{question}"

Please analyze this question and respond with the following structure (use these exact headers):

**Method Selected:** [name of method]
**Why This Method Fits:** [explanation]
**Inputs Needed:** [data requirements]
**Assumptions:** [numbered list]
**Expected Output:** [what the analysis will produce]
**Limitations:** [constraints and caveats]
**Suggested AlphaLab Module:** [one of: Regression Lab, Statistical Inference Lab, Probability Lab, Portfolio Optimization Lab, Correlation Explorer]"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=900,
        )
        content = response.choices[0].message.content

        def extract(header: str, text: str) -> str:
            pattern = rf"\*\*{re.escape(header)}:\*\*\s*(.*?)(?=\n\*\*|\Z)"
            m = re.search(pattern, text, re.DOTALL)
            return m.group(1).strip() if m else ""

        return {
            "question": question,
            "method": extract("Method Selected", content),
            "why": extract("Why This Method Fits", content),
            "inputs": extract("Inputs Needed", content),
            "assumptions": extract("Assumptions", content),
            "output": extract("Expected Output", content),
            "limitations": extract("Limitations", content),
            "suggested_module": extract("Suggested AlphaLab Module", content),
            "raw": content,
            "source": "openai",
        }

    except ImportError:
        st.warning("openai package not installed. Using mock response.")
        return get_mock_response(question)
    except Exception as e:
        st.warning(f"OpenAI API error: {e}. Using mock response.")
        return get_mock_response(question)


def explain_results(context: str, api_key: Optional[str] = None) -> str:
    """
    Ask the AI to explain a set of statistical results in plain English.
    Falls back to a generic message if no API key is available.
    """
    if not api_key:
        return (
            "_AI explanation unavailable — add your OpenAI API key in Settings "
            "to enable natural-language interpretation of results._"
        )
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": (
                    f"Please explain these statistical results in clear, plain English "
                    f"for a research audience. Emphasize what the numbers mean, "
                    f"uncertainty, and limitations:\n\n{context}"
                )},
            ],
            temperature=0.3,
            max_tokens=600,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"_AI explanation error: {e}_"


def get_research_response(question: str, api_key: Optional[str] = None) -> dict:
    """Top-level dispatcher: use OpenAI if key present, otherwise mock."""
    if api_key and len(api_key.strip()) > 10:
        return get_openai_response(question, api_key.strip())
    return get_mock_response(question)
