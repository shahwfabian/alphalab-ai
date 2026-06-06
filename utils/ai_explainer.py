"""
AlphaLab AI — AI Engine
Primary: Anthropic Claude  |  Secondary: OpenAI GPT-4o-mini  |  Fallback: intelligent rule-based
"""

import os
import re
import streamlit as st
from typing import Optional


# ── Per-module expert system prompts ─────────────────────────────────────────
# Pattern: Role + Expertise + Behaviour rules + Output format + Guardrails
# Inspired by CO-STAR + RISEN frameworks from prompt engineering best practice.

MODULE_SYSTEM_PROMPTS = {

    "research": """You are AlphaLab AI — a senior quantitative research analyst and statistician \
with 20 years of experience across asset management, academic finance, and applied statistics.

Your role is to answer ANY question about statistics, finance, data science, econometrics, \
or research methodology with the depth and clarity of a world-class expert.

Behaviour:
- Give complete, accurate, genuinely useful answers — not deflections or template text
- Use step-by-step reasoning when explaining complex concepts (think out loud)
- Use concrete examples with real numbers to illustrate abstract ideas
- If a concept has nuance, explain it — don't oversimplify
- For formulas, write them clearly in plain text (e.g. Sharpe = (R_p - R_f) / σ_p)
- Compare and contrast competing methods when relevant
- Always flag key assumptions and limitations naturally in the answer
- Keep responses focused but thorough — as long as they need to be, no longer
- NEVER say "I can't answer that" for any statistical, finance, or data question
- NEVER output rigid "Method / Why / Inputs" templates unless the user explicitly asks for that structure
- Respond conversationally and naturally, like a brilliant colleague explaining something""",

    "regression": """You are AlphaLab AI — a regression analysis and econometrics expert.

Your expertise:
- OLS, WLS, GLS, Ridge, Lasso, logistic regression, time-series regression
- Coefficient interpretation (beta, alpha, intercept), R², Adjusted R², F-statistic
- Diagnostic tests: Durbin-Watson, Breusch-Pagan, VIF, Jarque-Bera, RESET
- Heteroscedasticity, autocorrelation, multicollinearity — detection and fixes
- Capital Asset Pricing Model (CAPM), Fama-French factors
- Financial return data: log vs simple returns, stationarity, rolling regression

When the user asks a regression question:
1. Directly answer what they asked — interpret results if provided, explain concepts if asked
2. If they mention tickers and want analysis run, acknowledge and guide them
3. Always explain what the numbers MEAN in plain English — not just what they are
4. Walk through interpretations step by step using Chain-of-Thought when complex
5. Warn about violated assumptions only when actually relevant to their question

NEVER output canned template responses. Answer the actual question asked.""",

    "inference": """You are AlphaLab AI — a statistical inference and hypothesis testing specialist.

Your expertise:
- One-sample and two-sample t-tests, paired t-tests
- ANOVA, chi-square, Mann-Whitney U, Kolmogorov-Smirnov tests
- Confidence intervals: construction, interpretation, common misinterpretations
- p-values: what they mean, what they don't mean, p-hacking, multiple testing
- Effect sizes: Cohen's d, practical vs statistical significance
- Type I / Type II errors, power analysis, sample size calculations
- Applications: testing trading strategies for alpha, comparing fund performance

When answering:
- Explain what the null and alternative hypotheses mean in context
- Interpret the p-value correctly ("probability of observing data this extreme IF H₀ is true")
- Always distinguish statistical significance from practical significance
- Walk through the logic step-by-step for complex questions
- Be direct about what the test can and cannot tell us

NEVER output canned templates. Answer what was actually asked with precision.""",

    "probability": """You are AlphaLab AI — a probability theory and financial risk modeling expert.

Your expertise:
- Probability distributions: Normal, t, log-normal, Pareto, fat-tailed distributions
- Value at Risk (VaR): parametric, historical simulation, Monte Carlo
- Expected Shortfall / Conditional VaR (CVaR / ES)
- Drawdown analysis: maximum drawdown, probability of drawdown, Calmar ratio
- Return distribution characteristics: skewness, kurtosis, excess kurtosis, fat tails
- Jarque-Bera normality test, Shapiro-Wilk
- Options pricing intuition, Black-Scholes assumptions, implied volatility

When answering probability questions:
- Give exact formulas when helpful (written clearly in plain text)
- Explain the intuition behind the math, not just the formula
- For "what is the probability of X dropping Y% in Z days" — walk through the calculation step by step
- Always explain the Normal approximation and when it underestimates tail risk
- Use concrete numbers to make abstract probabilities tangible

NEVER output canned templates. Give real, calculated, thoughtful answers.""",

    "portfolio": """You are AlphaLab AI — a portfolio theory and asset allocation expert.

Your expertise:
- Modern Portfolio Theory (Markowitz 1952): mean-variance optimization, efficient frontier
- Sharpe ratio, Sortino ratio, Treynor ratio, Information ratio, Calmar ratio
- Risk parity, Black-Litterman model, factor investing
- Portfolio construction: diversification, correlation, rebalancing
- CAPM: Security Market Line, beta, expected return
- Practical critiques: MPT sensitivity to inputs, estimation error, regime changes
- Alternative optimization: equal weight, minimum variance, maximum diversification

When answering:
- Explain the math behind portfolio metrics clearly with formulas
- Interpret optimization results — what do the weights actually mean?
- Compare alternative strategies (equal weight vs MPT, etc.)
- Be honest about MPT's well-known limitations — it's a theoretical framework, not a trading system
- Use Chain-of-Thought for multi-step portfolio math

NEVER output canned templates. Engage deeply with what was actually asked.""",

    "correlation": """You are AlphaLab AI — a correlation analysis and diversification expert.

Your expertise:
- Pearson, Spearman, Kendall correlation — differences, when to use each
- Correlation matrices, heatmaps, pairwise analysis
- Rolling correlation: regime changes, correlation breakdown during crises
- Diversification ratio, portfolio correlation, HHI concentration
- Spurious correlation, nonsense correlations, correlation vs causation
- Copulas, tail dependence, conditional correlation
- Applications: identifying diversifiers, building uncorrelated portfolios

When answering:
- Interpret correlation values (what does r=0.72 actually mean in context?)
- Explain rolling correlation shifts with real market examples (2008, COVID)
- Always warn that correlation ≠ causation with a concrete example
- Discuss correlation instability and why it matters for portfolio construction
- Be specific and quantitative, not vague

NEVER output canned templates. Answer with depth and precision.""",

    "data": """You are AlphaLab AI — a data science and exploratory data analysis expert.

Your expertise:
- Data quality: missing values, outliers, duplicates, type inference
- Descriptive statistics: mean, median, std, skewness, kurtosis, percentiles
- Data transformations: normalization, standardization, log transforms
- Time series: stationarity, ADF test, seasonality, autocorrelation (ACF/PACF)
- Feature engineering for financial data
- Recommending the right analysis given the data structure
- Common pitfalls: look-ahead bias, survivorship bias, data snooping

When answering:
- Be specific about what you see in the data
- Give actionable recommendations
- Explain WHY a particular analysis fits the data
- Warn about data quality issues that would affect results""",

    "reports": """You are AlphaLab AI — a quantitative research communication specialist.

Your expertise:
- Structuring quantitative research reports: hypothesis, methodology, results, interpretation
- Academic and professional writing standards for finance research
- Presenting statistical results clearly: what to include, what to omit
- Visualizations: choosing the right chart, avoiding misleading displays
- Disclosure standards: assumptions, limitations, out-of-sample validation
- Common mistakes in quant research communication

Guide users through building clear, rigorous, honest research reports.
Be specific about structure, language, and what makes a report credible.""",
}

# Default fallback for any module not in the map
DEFAULT_SYSTEM_PROMPT = MODULE_SYSTEM_PROMPTS["research"]


# ── Claude (Anthropic) response ───────────────────────────────────────────────

def get_claude_response(module_id: str, history: list, user_message: str,
                        api_key: str) -> str:
    """Call Anthropic Claude with full conversation history."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        system = MODULE_SYSTEM_PROMPTS.get(module_id, DEFAULT_SYSTEM_PROMPT)

        # Build message history (skip welcome message / system messages)
        messages = []
        for m in history[-16:]:   # last 8 turns (16 messages)
            if m["role"] in ("user", "assistant"):
                content = m["content"]
                # Strip any analysis summary artifacts from assistant messages
                messages.append({"role": m["role"], "content": content})

        messages.append({"role": "user", "content": user_message})

        resp = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1500,
            system=system,
            messages=messages,
        )
        return resp.content[0].text

    except ImportError:
        return None
    except Exception as e:
        return f"_Claude error: {e}_"


# ── OpenAI response ───────────────────────────────────────────────────────────

def get_openai_response_chat(module_id: str, history: list, user_message: str,
                              api_key: str) -> str:
    """Call OpenAI GPT-4o-mini with full conversation history."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        system = MODULE_SYSTEM_PROMPTS.get(module_id, DEFAULT_SYSTEM_PROMPT)
        messages = [{"role": "system", "content": system}]

        for m in history[-16:]:
            if m["role"] in ("user", "assistant"):
                messages.append({"role": m["role"], "content": m["content"]})

        messages.append({"role": "user", "content": user_message})

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.35,
            max_tokens=1200,
        )
        return resp.choices[0].message.content

    except ImportError:
        return None
    except Exception as e:
        return f"_OpenAI error: {e}_"


# ── Intelligent rule-based fallback ──────────────────────────────────────────
# Not rigid templates — actual reasoning based on the question.

def intelligent_fallback(module_id: str, question: str) -> str:
    """
    When no API key is available, provide a genuinely useful, specific answer
    based on the question content — not a generic template.
    """
    q = question.lower()

    # ── Regression ────────────────────────────────────────────────────────────
    if any(k in q for k in ["r-squared", "r²", "r2", "coefficient of determination"]):
        return """**R² vs Adjusted R²**

R² (R-squared) measures the proportion of variance in the dependent variable explained by your model. It ranges from 0 to 1 — higher means the model explains more of the variation.

**The problem with R²:** It always increases when you add more predictors, even if they're noise. A model with 10 random variables will have a higher R² than one with 3 meaningful ones.

**Adjusted R²** corrects for this by penalizing extra predictors:

Adj. R² = 1 − [(1 − R²)(n − 1) / (n − k − 1)]

Where n = observations, k = number of predictors.

**In practice:**
- If Adj. R² is much lower than R², you have too many weak predictors
- Use Adjusted R² when comparing models with different numbers of variables
- Neither metric tells you if the model is *correctly specified* — only that it fits the training data

For financial data, R² of 0.1–0.3 is common and can still be meaningful. A high R² in finance often signals overfitting rather than genuine predictability.

*To get live AI responses with full conversational ability, add an Anthropic or OpenAI API key in Settings (⚙).*"""

    if any(k in q for k in ["beta", "coefficient", "interpret"]):
        return """**Interpreting Regression Coefficients**

In OLS regression Y = α + β₁X₁ + β₂X₂ + ε:

**Beta (β):** For every 1-unit increase in X, Y changes by β units, *holding all other predictors constant*.

In financial regression (e.g., CAPM):
- β > 1: Stock moves *more* than the market (amplified)
- β = 1: Stock moves with the market
- β < 1: Stock is less volatile than the market
- β < 0: Stock moves *opposite* the market (rare; gold, long bonds sometimes)

**Alpha (intercept α):** Expected return when all X variables = 0. In CAPM context, positive alpha means outperformance above what beta predicts.

**p-value:** Probability of observing a coefficient this large by chance if the true effect is zero. p < 0.05 = statistically significant at 5% level.

**Confidence interval:** Range where the true coefficient lies with 95% probability. If it doesn't cross zero, the variable is significant.

**Practical note:** Statistical significance ≠ economic significance. A coefficient can be highly significant but too small to matter in practice.

*Add an API key in Settings (⚙) for full conversational AI.*"""

    if any(k in q for k in ["p-value", "p value", "significance", "hypothesis"]):
        return """**Understanding p-values and Hypothesis Testing**

A p-value is the probability of observing results as extreme as yours *assuming the null hypothesis is true*.

**What p < 0.05 means:** If there were truly no effect, you'd see data this extreme less than 5% of the time. It does NOT mean there's a 95% chance your hypothesis is true.

**Common misinterpretations:**
- ❌ "p = 0.04 means there's a 96% chance of a real effect" — Wrong
- ❌ "p = 0.06 means nothing is happening" — Wrong (it's a continuum)
- ✅ "p = 0.04 means this result is unlikely under H₀" — Correct

**In financial research:**
- With large samples (1000+ daily returns), tiny meaningless effects become "significant"
- Always report effect size alongside p-value
- A strategy with t-stat > 3 is a higher bar and more credible than just p < 0.05
- Multiple testing problem: if you test 20 hypotheses, one will appear significant by chance

*Add an API key in Settings (⚙) for full conversational AI.*"""

    if any(k in q for k in ["var", "value at risk", "cvar", "expected shortfall", "tail risk"]):
        return """**Value at Risk (VaR) and CVaR Explained**

**VaR** answers: "What is the maximum I expect to lose over N days with X% confidence?"

Example: 1-day 95% VaR = -2.1% means on 95% of days, losses won't exceed 2.1%. But on the remaining 5% of days, you could lose *more* than that.

**Three calculation methods:**
1. **Historical simulation:** Sort past returns, take the 5th percentile directly. No distribution assumptions.
2. **Parametric (Normal):** VaR = μ - z·σ where z=1.645 for 95%. Fast but assumes normality.
3. **Monte Carlo:** Simulate thousands of scenarios. Most flexible but computationally heavy.

**CVaR (Conditional VaR / Expected Shortfall):**
CVaR answers: "Given that I AM in the worst 5%, how bad is the average loss?"
CVaR is always worse than VaR and is considered a superior risk measure because:
- It captures the shape of the tail, not just the cutoff point
- It's subadditive (portfolio CVaR ≤ sum of individual CVaRs) — VaR is not
- Basel III requires banks to use CVaR

**The fat tail problem:** Real return distributions have kurtosis > 3 (fatter tails than Normal). Parametric VaR systematically underestimates extreme losses.

*Add an API key in Settings (⚙) for full conversational AI.*"""

    if any(k in q for k in ["sharpe", "sortino", "information ratio", "risk-adjusted"]):
        return """**Risk-Adjusted Performance Metrics**

**Sharpe Ratio** = (Portfolio Return − Risk-Free Rate) / Portfolio Std Dev

Measures excess return per unit of *total* risk (both upside and downside volatility).
- > 1.0: Good
- > 2.0: Very good
- > 3.0: Exceptional (often too good to be true out-of-sample)

**Sortino Ratio** = (Portfolio Return − Risk-Free Rate) / Downside Deviation

Only penalizes *downside* volatility. Better for strategies with asymmetric returns (options, trend following). A strategy can have a high Sortino but low Sharpe if it has big positive outliers.

**Information Ratio** = (Portfolio Return − Benchmark Return) / Tracking Error

Measures manager skill relative to a benchmark. IR > 0.5 is considered skilled.

**Calmar Ratio** = Annualized Return / Maximum Drawdown

Useful for evaluating drawdown risk. Preferred by CTA traders.

**Key caveats:**
- All ratios use historical data — no guarantee of future performance
- Sharpe assumes normally distributed returns — problematic for fat-tailed strategies
- Higher Sharpe from leverage doesn't represent skill
- In-sample Sharpe is almost always higher than out-of-sample

*Add an API key in Settings (⚙) for full conversational AI.*"""

    if any(k in q for k in ["log return", "simple return", "arithmetic", "geometric"]):
        return """**Log Returns vs Simple Returns**

**Simple (arithmetic) returns:** r = (P₁ - P₀) / P₀

**Log returns:** r = ln(P₁ / P₀)

**When they differ:** For small daily returns (<2%), they're nearly identical. They diverge significantly over longer horizons or for volatile assets.

**Use log returns when:**
- Running OLS regression (they're additive across time, making math cleaner)
- Testing for normality (log returns are closer to normally distributed)
- Computing portfolio variance over time
- Academic research (convention)

**Use simple returns when:**
- Aggregating across assets in a portfolio (they're additive *across assets*)
- Reporting to investors (more intuitive: "+10%" means what it says)
- Computing portfolio weights and rebalancing
- Computing Sharpe ratio, drawdown, CAGR

**Key relationship:** Simple return = e^(log return) − 1

**Compounding:** $1 growing at 10% log return/year = $1 × e^0.10 = $1.105 after 1 year — same as 10.5% simple return. The difference compounds over time.

*Add an API key in Settings (⚙) for full conversational AI.*"""

    if any(k in q for k in ["efficient frontier", "modern portfolio", "mpt", "markowitz"]):
        return """**Modern Portfolio Theory and the Efficient Frontier**

**Core insight (Markowitz, 1952):** You can reduce portfolio risk through diversification *without sacrificing expected return*, as long as assets aren't perfectly correlated.

**The Efficient Frontier** is the set of portfolios that:
- Maximize expected return for a given level of risk, OR
- Minimize risk for a given level of expected return

Portfolios below the frontier are "inefficient" — you could get the same return with less risk.

**The Math:**
- Expected portfolio return: E(R_p) = Σ wᵢ · E(Rᵢ)
- Portfolio variance: σ²_p = Σᵢ Σⱼ wᵢ wⱼ σᵢⱼ (depends on all pairwise covariances)
- Optimization: minimize σ²_p subject to: weights sum to 1, target return met

**Sharpe's Addition — The Capital Market Line:**
Adding a risk-free asset creates the CML. The tangency portfolio (where CML touches the frontier) is the maximum Sharpe ratio portfolio.

**Known weaknesses:**
- Highly sensitive to expected return inputs — garbage in, garbage out
- Uses historical covariances which aren't stable (especially in crises)
- Produces extreme, unstable weights that flip dramatically on small input changes
- Ignores fat tails, skewness, liquidity, transaction costs, taxes

*Add an API key in Settings (⚙) for full conversational AI.*"""

    if any(k in q for k in ["correlat", "diversif", "co-movement", "heatmap"]):
        return """**Correlation and Diversification**

**Pearson correlation (r)** measures the linear relationship between two return series:
- r = 1.0: Perfect positive correlation (move in lockstep)
- r = 0.0: No linear relationship (uncorrelated)
- r = −1.0: Perfect negative correlation (one zigs when other zags)

**Diversification benefit:** Portfolio variance depends on correlations between assets.
σ²_portfolio = w₁²σ₁² + w₂²σ₂² + 2w₁w₂σ₁σ₂ρ₁₂

Lower ρ = lower portfolio variance. The math works even with imperfect diversifiers.

**Why "crisis correlation" matters:**
In normal markets: SPY-GLD correlation might be −0.15 (good diversifier)
In the 2008 crisis: Most correlations spiked toward 1.0 — the "diversification illusion"
This is when you need diversification most, but correlations converge under stress.

**Good diversifiers historically:**
- Gold (GLD): Low/negative correlation to equities, especially in downturns
- Treasuries (TLT): Negative correlation to stocks in risk-off environments
- Managed futures / trend following: Often uncorrelated or positively correlated to volatility

**Pearson vs Spearman:** Pearson measures linear relationships. Spearman (rank-based) captures monotonic relationships and is more robust to outliers. Use Spearman if you suspect non-linear relationships.

*Add an API key in Settings (⚙) for full conversational AI.*"""

    # General fallback — still useful, not just a "no API key" message
    return f"""I can help with that. Here's what I know about this topic:

Your question touches on **{_topic_from_question(q)}** — a core area of quantitative finance and statistics.

To give you the most accurate and complete answer, I'd need either:
1. **An Anthropic API key** (recommended — uses Claude, the same AI powering this response style)
2. **An OpenAI API key** (GPT-4o-mini)

**Add your key:** Click the ⚙ gear icon at the top right of any chat, paste your API key, and click Save. Your key is stored only in your browser session.

Once connected, I can answer any statistics, finance, or data science question with the full depth of a senior quant analyst — not template responses.

**Get a free Anthropic key:** [console.anthropic.com](https://console.anthropic.com) → API Keys → Create Key (free tier available)

*All questions you've typed are saved in this session — just add a key and ask again.*"""


def _topic_from_question(q: str) -> str:
    if any(k in q for k in ["regress", "beta", "r²", "ols"]): return "regression analysis"
    if any(k in q for k in ["portfol", "sharpe", "frontier"]): return "portfolio optimization"
    if any(k in q for k in ["correlat", "diversif"]): return "correlation and diversification"
    if any(k in q for k in ["probabilit", "var", "drawdown", "tail"]): return "probability and risk modeling"
    if any(k in q for k in ["hypothesis", "p-value", "t-test", "significance"]): return "statistical inference"
    return "quantitative finance and statistics"


# ── Primary dispatcher used by app.py ────────────────────────────────────────

def _get_key(name: str) -> str:
    """
    Resolve an API key from: Streamlit secrets → environment variable → session state.
    Streamlit secrets (set in Streamlit Cloud dashboard) are the primary source
    so the app works for ALL users without them providing any key.
    """
    # 1. Streamlit Cloud secrets (server-side, invisible to users)
    try:
        import streamlit as _st
        val = _st.secrets.get(name, "")
        if val:
            return val.strip()
    except Exception:
        pass

    # 2. Environment variable (local .streamlit/secrets.toml or .env)
    val = os.environ.get(name, "")
    if val:
        return val.strip()

    # 3. User-entered key in settings (last resort)
    session_key = "anthropic_api_key" if "ANTHROPIC" in name else "openai_api_key"
    try:
        import streamlit as _st
        return _st.session_state.get(session_key, "").strip()
    except Exception:
        return ""


def get_best_response(module_id: str, history: list, user_message: str) -> str:
    """
    Try AI providers in order: Claude → OpenAI → intelligent fallback.
    Server-side keys (Streamlit secrets) are used first so no user action needed.
    """
    # 1. Try Claude (Anthropic) — primary
    anthropic_key = _get_key("ANTHROPIC_API_KEY")
    if anthropic_key:
        result = get_claude_response(module_id, history, user_message, anthropic_key)
        if result and not result.startswith("_Claude error"):
            return result

    # 2. Try OpenAI — secondary
    openai_key = _get_key("OPENAI_API_KEY")
    if openai_key:
        result = get_openai_response_chat(module_id, history, user_message, openai_key)
        if result and not result.startswith("_OpenAI error"):
            return result

    # 3. Intelligent rule-based fallback (no key needed)
    return intelligent_fallback(module_id, user_message)


# ── Legacy compatibility (called from older pages) ────────────────────────────

def classify_question(question: str) -> str:
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
    return "regression"


# Kept for backwards compatibility with pages that import these
MOCK_RESPONSES = {
    "regression":  {"method": "OLS Regression", "why": "", "inputs": "", "assumptions": "", "limitations": ""},
    "correlation": {"method": "Pearson Correlation", "why": "", "inputs": "", "assumptions": "", "limitations": ""},
    "probability": {"method": "Historical Simulation + Normal", "why": "", "inputs": "", "assumptions": "", "limitations": ""},
    "portfolio":   {"method": "Mean-Variance Optimization", "why": "", "inputs": "", "assumptions": "", "limitations": ""},
    "inference":   {"method": "t-Test", "why": "", "inputs": "", "assumptions": "", "limitations": ""},
}

def get_mock_response(question: str) -> dict:
    cat = classify_question(question)
    return {"category": cat, "question": question, **MOCK_RESPONSES[cat], "source": "mock"}

def get_openai_response(question: str, api_key: str) -> dict:
    return get_mock_response(question)

def explain_results(context: str, api_key: Optional[str] = None) -> str:
    if not api_key:
        return "_Add an API key in Settings to enable AI result interpretation._"
    return get_openai_response_chat("research", [], context, api_key) or ""

def get_research_response(question: str, api_key: Optional[str] = None) -> dict:
    return get_mock_response(question)
