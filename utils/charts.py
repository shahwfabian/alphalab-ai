"""
AlphaLab AI — Chart Library
Consistent dark-themed Plotly visualizations for all AlphaLab modules.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats


# ─── Theme Constants ─────────────────────────────────────────────────────────

NAVY_BG     = "#0A0E1A"
PANEL_BG    = "#0F1628"
ACCENT_BLUE = "#00D4FF"
ACCENT_CYAN = "#00FFD4"
ACCENT_GOLD = "#FFD700"
ACCENT_RED  = "#FF4B6E"
GRID_COLOR  = "#1E2D4A"
TEXT_COLOR  = "#E8F4FD"
MUTED_TEXT  = "#6B8CAE"

CHART_PALETTE = [
    "#00D4FF", "#00FFD4", "#FFD700", "#FF4B6E",
    "#A855F7", "#F97316", "#22D3EE", "#4ADE80",
]

BASE_LAYOUT = dict(
    paper_bgcolor=NAVY_BG,
    plot_bgcolor=PANEL_BG,
    font=dict(color=TEXT_COLOR, family="monospace", size=12),
    xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, linecolor=GRID_COLOR),
    yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, linecolor=GRID_COLOR),
    legend=dict(bgcolor=PANEL_BG, bordercolor=GRID_COLOR, borderwidth=1),
    margin=dict(l=50, r=30, t=60, b=50),
)


def apply_base(fig: go.Figure, title: str = "", height: int = 420) -> go.Figure:
    fig.update_layout(**BASE_LAYOUT, title=dict(text=title, font=dict(size=15, color=ACCENT_BLUE)),
                      height=height)
    return fig


# ─── Price & Return Charts ────────────────────────────────────────────────────

def price_chart(prices: pd.DataFrame, title: str = "Price History") -> go.Figure:
    fig = go.Figure()
    for i, col in enumerate(prices.columns):
        normalized = prices[col] / prices[col].iloc[0] * 100
        fig.add_trace(go.Scatter(
            x=prices.index, y=normalized,
            name=col, mode="lines",
            line=dict(color=CHART_PALETTE[i % len(CHART_PALETTE)], width=1.8),
        ))
    fig.update_layout(yaxis_title="Indexed (Base=100)")
    return apply_base(fig, title)


def returns_histogram(returns: pd.Series, ticker: str = "", bins: int = 60) -> go.Figure:
    r = returns.dropna()
    mu, sigma = r.mean(), r.std()
    x_range = np.linspace(r.min(), r.max(), 300)
    normal_pdf = stats.norm.pdf(x_range, mu, sigma) * (r.max() - r.min()) / bins * len(r)

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=r, nbinsx=bins, name="Returns",
        marker_color=ACCENT_BLUE, opacity=0.75,
    ))
    fig.add_trace(go.Scatter(
        x=x_range, y=normal_pdf, name="Normal Fit",
        mode="lines", line=dict(color=ACCENT_GOLD, width=2, dash="dash"),
    ))
    # VaR line at 5%
    var_5 = r.quantile(0.05)
    fig.add_vline(x=var_5, line_dash="dot", line_color=ACCENT_RED,
                  annotation_text=f"5% VaR: {var_5:.2%}", annotation_font_color=ACCENT_RED)
    fig.update_layout(xaxis_title="Daily Return", yaxis_title="Frequency", bargap=0.05)
    return apply_base(fig, f"{ticker} Return Distribution")


def cumulative_return_chart(returns: pd.DataFrame, title: str = "Cumulative Returns") -> go.Figure:
    fig = go.Figure()
    for i, col in enumerate(returns.columns):
        cum = (1 + returns[col].dropna()).cumprod() - 1
        fig.add_trace(go.Scatter(
            x=cum.index, y=cum * 100,
            name=col, mode="lines",
            line=dict(color=CHART_PALETTE[i % len(CHART_PALETTE)], width=1.8),
        ))
    fig.update_layout(yaxis_title="Cumulative Return (%)", xaxis_title="Date")
    return apply_base(fig, title)


# ─── Regression Charts ────────────────────────────────────────────────────────

def scatter_regression(x: pd.Series, y: pd.Series, x_label: str, y_label: str,
                       slope: float, intercept: float) -> go.Figure:
    x_line = np.linspace(x.min(), x.max(), 200)
    y_line = slope * x_line + intercept

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=y, mode="markers", name="Observations",
        marker=dict(color=ACCENT_BLUE, size=5, opacity=0.6),
    ))
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line, mode="lines", name="Regression Line",
        line=dict(color=ACCENT_GOLD, width=2.5),
    ))
    fig.update_layout(xaxis_title=x_label, yaxis_title=y_label)
    return apply_base(fig, f"{y_label} ~ {x_label}")


def residual_plot(fitted: pd.Series, residuals: pd.Series) -> go.Figure:
    fig = make_subplots(rows=1, cols=2, subplot_titles=["Residuals vs Fitted", "Q-Q Plot"])

    # Residuals vs Fitted
    fig.add_trace(go.Scatter(
        x=fitted, y=residuals, mode="markers",
        marker=dict(color=ACCENT_CYAN, size=4, opacity=0.6),
        name="Residuals",
    ), row=1, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color=ACCENT_GOLD, row=1, col=1)

    # Q-Q Plot
    sorted_res = np.sort(residuals)
    theoretical_q = stats.norm.ppf(np.linspace(0.01, 0.99, len(sorted_res)))
    fig.add_trace(go.Scatter(
        x=theoretical_q, y=sorted_res, mode="markers",
        marker=dict(color=ACCENT_BLUE, size=4, opacity=0.6),
        name="Q-Q",
    ), row=1, col=2)
    diag_min = min(theoretical_q.min(), sorted_res.min())
    diag_max = max(theoretical_q.max(), sorted_res.max())
    fig.add_trace(go.Scatter(
        x=[diag_min, diag_max], y=[diag_min, diag_max],
        mode="lines", line=dict(color=ACCENT_GOLD, dash="dash"), name="Normal",
    ), row=1, col=2)

    fig.update_layout(**BASE_LAYOUT, height=380,
                      title=dict(text="Regression Diagnostics", font=dict(color=ACCENT_BLUE, size=15)))
    fig.update_xaxes(gridcolor=GRID_COLOR)
    fig.update_yaxes(gridcolor=GRID_COLOR)
    return fig


# ─── Correlation Heatmap ──────────────────────────────────────────────────────

def correlation_heatmap(corr_matrix: pd.DataFrame, title: str = "Correlation Matrix") -> go.Figure:
    labels = list(corr_matrix.columns)
    z = corr_matrix.values.round(3)

    fig = go.Figure(go.Heatmap(
        z=z, x=labels, y=labels,
        colorscale=[
            [0.0,  ACCENT_RED],
            [0.5,  PANEL_BG],
            [1.0,  ACCENT_BLUE],
        ],
        zmin=-1, zmax=1,
        text=z, texttemplate="%{text:.2f}",
        textfont=dict(size=11, color=TEXT_COLOR),
        colorbar=dict(title="r", tickfont=dict(color=TEXT_COLOR)),
    ))
    fig.update_layout(
        **BASE_LAYOUT,
        height=max(400, 80 * len(labels)),
        title=dict(text=title, font=dict(size=15, color=ACCENT_BLUE)),
    )
    return fig


# ─── Portfolio Charts ─────────────────────────────────────────────────────────

def efficient_frontier_chart(frontier_df: pd.DataFrame, random_df: pd.DataFrame,
                              portfolios: dict, tickers: list[str]) -> go.Figure:
    fig = go.Figure()

    # Random portfolios (scatter cloud)
    if not random_df.empty:
        fig.add_trace(go.Scatter(
            x=random_df["Volatility"] * 100,
            y=random_df["Return"] * 100,
            mode="markers",
            marker=dict(color=random_df["Sharpe"], colorscale="Blues",
                        size=3, opacity=0.3, showscale=False),
            name="Random Portfolios",
            hovertemplate="Vol: %{x:.2f}%<br>Ret: %{y:.2f}%<extra></extra>",
        ))

    # Efficient frontier curve
    if not frontier_df.empty:
        fig.add_trace(go.Scatter(
            x=frontier_df["Volatility"] * 100,
            y=frontier_df["Return"] * 100,
            mode="lines",
            line=dict(color=ACCENT_BLUE, width=3),
            name="Efficient Frontier",
        ))

    colors = {"Max Sharpe": ACCENT_GOLD, "Min Variance": ACCENT_CYAN, "Equal Weight": ACCENT_RED}
    symbols = {"Max Sharpe": "star", "Min Variance": "diamond", "Equal Weight": "circle"}

    for label, p in portfolios.items():
        fig.add_trace(go.Scatter(
            x=[p["volatility"] * 100],
            y=[p["return"] * 100],
            mode="markers+text",
            marker=dict(color=colors.get(label, ACCENT_BLUE), size=16, symbol=symbols.get(label, "circle"),
                        line=dict(color="white", width=1.5)),
            text=[label],
            textposition="top center",
            textfont=dict(color=colors.get(label, ACCENT_BLUE), size=11),
            name=label,
            hovertemplate=f"{label}<br>Vol: %{{x:.2f}}%<br>Ret: %{{y:.2f}}%<extra></extra>",
        ))

    fig.update_layout(
        xaxis_title="Annualized Volatility (%)",
        yaxis_title="Annualized Return (%)",
    )
    return apply_base(fig, "Efficient Frontier", height=500)


def portfolio_weights_bar(tickers: list[str], weights: np.ndarray, title: str) -> go.Figure:
    colors = [CHART_PALETTE[i % len(CHART_PALETTE)] for i in range(len(tickers))]
    fig = go.Figure(go.Bar(
        x=tickers,
        y=(weights * 100).round(2),
        marker_color=colors,
        text=[f"{w:.1f}%" for w in weights * 100],
        textposition="outside",
    ))
    fig.update_layout(yaxis_title="Weight (%)", xaxis_title="Asset", showlegend=False)
    return apply_base(fig, title, height=380)


# ─── Probability Charts ───────────────────────────────────────────────────────

def probability_density_chart(returns: pd.Series, ticker: str,
                               highlight_threshold: float = None) -> go.Figure:
    r = returns.dropna()
    mu, sigma = r.mean(), r.std()
    x = np.linspace(r.min() * 1.5, r.max() * 1.5, 400)
    pdf_normal = stats.norm.pdf(x, mu, sigma)

    # KDE
    kde = stats.gaussian_kde(r)
    pdf_kde = kde(x)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=pdf_kde, mode="lines", name="KDE (Historical)",
        line=dict(color=ACCENT_BLUE, width=2.5),
        fill="tozeroy", fillcolor=f"rgba(0,212,255,0.08)",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=pdf_normal, mode="lines", name="Normal Fit",
        line=dict(color=ACCENT_GOLD, width=2, dash="dash"),
    ))

    if highlight_threshold is not None:
        mask = x <= highlight_threshold
        fig.add_trace(go.Scatter(
            x=x[mask], y=pdf_kde[mask], mode="lines",
            fill="tozeroy", fillcolor=f"rgba(255,75,110,0.25)",
            line=dict(color=ACCENT_RED, width=0), name=f"P(return ≤ {highlight_threshold:.1%})",
        ))
        fig.add_vline(x=highlight_threshold, line_dash="dot", line_color=ACCENT_RED,
                      annotation_text=f"{highlight_threshold:.1%}", annotation_font_color=ACCENT_RED)

    fig.update_layout(xaxis_title="Return", yaxis_title="Density")
    return apply_base(fig, f"{ticker} Return Density", height=420)


def drawdown_chart(prices: pd.Series, title: str = "Drawdown") -> go.Figure:
    roll_max = prices.cummax()
    drawdown = (prices - roll_max) / roll_max * 100
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=drawdown.index, y=drawdown,
        mode="lines", fill="tozeroy",
        line=dict(color=ACCENT_RED, width=1.5),
        fillcolor="rgba(255,75,110,0.15)",
        name="Drawdown (%)",
    ))
    fig.update_layout(yaxis_title="Drawdown (%)", xaxis_title="Date")
    return apply_base(fig, title, height=350)
