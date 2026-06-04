# ⬡ AlphaLab AI

**AI-Powered Statistical Research Copilot**

> Convert natural-language research questions into quantitative analysis, visualizations, statistical interpretation, and professional research reports.

AlphaLab AI is not a stock prediction app. It is not a generic chatbot.  
It is a rigorous, evidence-based research tool for quantitative analysts, portfolio managers, students, and data scientists who want to reason with evidence.

---

## Screenshots

> Bloomberg Terminal meets AI Research Workstation — deep navy, electric blue, professional.

---

## Core Modules

| # | Module | Description |
|---|--------|-------------|
| 01 | **Research Assistant** | Natural-language question → method identification → structured analysis guidance |
| 02 | **Regression Lab** | OLS regression with full diagnostics (R², coefficients, residuals, Q-Q plot) |
| 03 | **Statistical Inference Lab** | One-sample & two-sample t-tests, confidence intervals, hypothesis testing |
| 04 | **Probability Lab** | Return distributions, VaR, CVaR, drawdown probability modeling |
| 05 | **Portfolio Optimization** | Modern Portfolio Theory — Max Sharpe, Min Variance, Efficient Frontier |
| 06 | **Correlation Explorer** | Correlation matrices, heatmaps, rolling correlation, diversification analysis |
| 07 | **Data Upload Lab** | CSV upload, auto-exploration, missing value analysis, analysis recommendations |
| 08 | **Research Reports** | Professional HTML report generation and export |
| 09 | **Settings** | API keys, risk parameters, date defaults |

---

## Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python 3.11+
- **Statistical Engine:** statsmodels, scipy, scikit-learn
- **Data:** pandas, numpy, yfinance
- **Visualization:** Plotly
- **AI Layer:** OpenAI GPT-4o Mini (optional — mock fallback included)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/alphalab-ai.git
cd alphalab-ai
```

### 2. Create a virtual environment (recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `kaleido` is required for chart-to-PNG export in Research Reports.  
> If you encounter install issues with kaleido: `pip install kaleido==0.2.1`

### 4. Run locally

```bash
streamlit run app.py
```

AlphaLab will open at `http://localhost:8501`

---

## Configuration

### OpenAI API Key (Optional)

AlphaLab works fully without an API key using structured mock responses.  
To enable live AI-powered explanations:

1. Open the app → **Settings** → **AI Engine** tab
2. Paste your OpenAI API key (`sk-...`)
3. Click **Save API Key**

The key is stored only in Streamlit session state — never logged or persisted to disk.

### Risk-Free Rate

Default: **5.00%** (approximate US 3M T-Bill rate)  
Adjust in **Settings → Risk Parameters** to match current market conditions.

---

## Project Structure

```
alphalab-ai/
│
├── app.py                          # Home page + global session state + navigation
│
├── pages/
│   ├── 1_Research_Assistant.py     # AI-powered research question interface
│   ├── 2_Regression_Lab.py         # OLS regression with full diagnostics
│   ├── 3_Statistical_Inference_Lab.py  # T-tests and confidence intervals
│   ├── 4_Probability_Lab.py        # Distribution, VaR, drawdown probability
│   ├── 5_Portfolio_Optimization_Lab.py # MPT / Efficient Frontier
│   ├── 6_Correlation_Explorer.py   # Heatmaps, rolling correlation
│   ├── 7_Data_Upload_Lab.py        # CSV upload + auto-exploration
│   ├── 8_Research_Reports.py       # HTML report builder + exporter
│   └── 9_Settings.py               # Configuration + system info
│
├── utils/
│   ├── __init__.py
│   ├── data_loader.py              # yfinance + CSV loading + return calculations
│   ├── statistics.py               # OLS, t-tests, correlation, probability functions
│   ├── portfolio.py                # MPT optimization engine (scipy)
│   ├── charts.py                   # Plotly dark-theme chart library
│   ├── ai_explainer.py             # OpenAI integration + mock response system
│   └── report_generator.py         # HTML report assembler
│
├── .streamlit/
│   └── config.toml                 # Dark theme + server config
│
├── requirements.txt
└── README.md
```

---

## Example Questions

Ask these in the **Research Assistant** module:

- *"Does QQQ explain NVDA returns better than SPY?"* → Regression Lab
- *"Is momentum statistically significant in this dataset?"* → Statistical Inference Lab
- *"What is the probability of a 10% drawdown in 30 days?"* → Probability Lab
- *"Build the highest Sharpe portfolio from SPY, QQQ, GLD, TLT, VNQ"* → Portfolio Optimization
- *"Which assets are most correlated in my portfolio?"* → Correlation Explorer

---

## Module Explanations

### `utils/data_loader.py`
Central data access layer. Wraps `yfinance` for market data retrieval with `@st.cache_data` caching to avoid redundant API calls. Handles CSV parsing, return calculation (simple and log), and DataFrame summarization.

### `utils/statistics.py`
Pure statistical functions:
- `run_ols_regression()` — wraps `statsmodels.OLS` and returns structured results dict
- `one_sample_ttest()`, `two_sample_ttest()` — scipy t-tests with full interpretation
- `return_distribution_stats()` — skewness, kurtosis, Jarque-Bera normality test
- `prob_drawdown_parametric()` — Normal-distribution tail probability estimate
- `historical_var()`, `historical_cvar()` — empirical risk measures
- `compute_correlation_matrix()`, `correlation_pairs()` — correlation analytics

### `utils/portfolio.py`
Modern Portfolio Theory engine:
- `optimize_max_sharpe()` — SLSQP maximization of Sharpe ratio
- `optimize_min_variance()` — SLSQP minimization of portfolio variance
- `generate_efficient_frontier()` — sweeps target returns to trace the frontier
- `generate_random_portfolios()` — Monte Carlo portfolio cloud for visualization

### `utils/charts.py`
Consistent Plotly dark-theme chart factory:
- All charts share the navy/electric-blue palette
- `correlation_heatmap()`, `efficient_frontier_chart()`, `residual_plot()`, `returns_histogram()`, `drawdown_chart()`, etc.

### `utils/ai_explainer.py`
Two-mode AI layer:
- **Live mode:** Sends structured prompts to OpenAI GPT-4o Mini, parses structured response sections
- **Mock mode:** Rule-based question classifier maps to pre-written expert responses for 5 statistical categories

### `utils/report_generator.py`
HTML report assembler:
- Embeds charts as base64-encoded PNG images
- Renders DataFrames as styled HTML tables
- Full professional CSS with AlphaLab dark theme
- Self-contained single-file HTML output (no external dependencies)

---

## Core Design Principles

1. **Never claim certainty.** Every output emphasizes evidence, confidence, uncertainty, and limitations.
2. **Research-first UX.** Every module explains the method, assumptions, and limitations — not just the numbers.
3. **Modular architecture.** Each utility function can be imported and used independently.
4. **Fallback by default.** No API key required. Mock responses are high-quality structured outputs.
5. **Educational disclaimers.** Every module includes a persistent disclaimer about research vs. financial advice.

---

## Recommended Next Features

### Near-term
- [ ] **Fama-French Factor Analysis** — 3-factor and 5-factor model regression
- [ ] **Rolling Regression** — time-varying beta estimation
- [ ] **Backtesting Engine** — strategy performance vs benchmark
- [ ] **PDF Export** — via WeasyPrint or pdfkit

### Medium-term
- [ ] **Time Series Lab** — ADF stationarity test, ARIMA, autocorrelation (ACF/PACF)
- [ ] **Monte Carlo Simulator** — portfolio return path simulation
- [ ] **Options Pricing** — Black-Scholes model with Greeks
- [ ] **Macro Data Integration** — FRED API for economic indicators

### Advanced
- [ ] **SQLite persistence** — save analysis sessions and reports
- [ ] **Multi-user auth** — per-user API keys and report history
- [ ] **Local LLM support** — Ollama integration for offline AI
- [ ] **Streaming AI responses** — real-time token streaming in Research Assistant
- [ ] **Alert system** — email/Slack notifications for threshold breaches

---

## Disclaimer

> AlphaLab AI is an educational and research tool. It does not constitute financial advice,  
> investment recommendations, or guarantees of future performance. All statistical outputs  
> carry uncertainty. Past performance does not imply future results. Consult a qualified  
> financial professional before making investment decisions.

---

## License

MIT License — free to use, modify, and distribute.

---

*Built with Python · Streamlit · statsmodels · scipy · plotly · yfinance · OpenAI*
