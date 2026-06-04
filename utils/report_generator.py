"""
AlphaLab AI — Research Report Generator
Assembles structured HTML research reports from analysis results.
"""

import base64
import datetime
import io
import plotly.graph_objects as go


REPORT_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;600;700&display=swap');
  :root {
    --navy: #0A0E1A;
    --panel: #0F1628;
    --blue: #00D4FF;
    --cyan: #00FFD4;
    --gold: #FFD700;
    --red:  #FF4B6E;
    --text: #E8F4FD;
    --muted: #6B8CAE;
    --border: #1E2D4A;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: var(--navy);
    color: var(--text);
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    line-height: 1.7;
    padding: 40px;
    max-width: 1100px;
    margin: 0 auto;
  }
  .header {
    border-bottom: 2px solid var(--blue);
    padding-bottom: 24px;
    margin-bottom: 40px;
  }
  .header h1 {
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    color: var(--blue);
    letter-spacing: 2px;
  }
  .header .subtitle { color: var(--muted); font-size: 13px; margin-top: 6px; }
  .badge {
    display: inline-block;
    background: rgba(0,212,255,0.12);
    color: var(--blue);
    border: 1px solid var(--blue);
    padding: 2px 10px;
    border-radius: 4px;
    font-size: 11px;
    font-family: 'JetBrains Mono', monospace;
    margin-right: 8px;
    margin-top: 8px;
  }
  .section {
    margin-bottom: 36px;
    padding: 24px;
    background: var(--panel);
    border-radius: 8px;
    border-left: 3px solid var(--blue);
  }
  .section h2 {
    font-size: 16px;
    color: var(--blue);
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 1px;
    margin-bottom: 14px;
    text-transform: uppercase;
  }
  .section p, .section li { color: var(--text); margin-bottom: 8px; }
  .section ul { padding-left: 20px; }
  .metric-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 14px;
    margin-top: 14px;
  }
  .metric-card {
    background: rgba(0,212,255,0.05);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px 16px;
  }
  .metric-card .label { color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }
  .metric-card .value { font-family: 'JetBrains Mono', monospace; font-size: 22px; color: var(--blue); margin-top: 4px; }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    margin-top: 12px;
  }
  th {
    background: rgba(0,212,255,0.1);
    color: var(--blue);
    font-family: 'JetBrains Mono', monospace;
    text-align: left;
    padding: 8px 12px;
    border-bottom: 1px solid var(--border);
  }
  td {
    padding: 7px 12px;
    border-bottom: 1px solid var(--border);
    color: var(--text);
  }
  tr:nth-child(even) td { background: rgba(255,255,255,0.02); }
  .warning-box {
    background: rgba(255,215,0,0.06);
    border: 1px solid var(--gold);
    border-radius: 6px;
    padding: 14px 18px;
    color: var(--gold);
    font-size: 13px;
    margin-top: 14px;
  }
  .footer {
    border-top: 1px solid var(--border);
    padding-top: 20px;
    margin-top: 50px;
    color: var(--muted);
    font-size: 12px;
    text-align: center;
  }
  img { max-width: 100%; border-radius: 6px; margin-top: 12px; }
</style>
"""


def fig_to_base64(fig: go.Figure) -> str:
    """Convert a Plotly figure to a base64-encoded PNG string."""
    try:
        img_bytes = fig.to_image(format="png", width=900, height=420, scale=2)
        return base64.b64encode(img_bytes).decode("utf-8")
    except Exception:
        return ""


def df_to_html_table(df) -> str:
    """Convert a DataFrame to a styled HTML table string."""
    try:
        import pandas as pd
        if isinstance(df, pd.DataFrame):
            rows = "".join(
                f"<tr>{''.join(f'<td>{v}</td>' for v in row)}</tr>"
                for row in df.itertuples(index=False)
            )
            headers = "".join(f"<th>{c}</th>" for c in df.columns)
            return f"<table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>"
    except Exception:
        pass
    return ""


def build_report(
    title: str,
    question: str,
    methodology: str,
    assumptions: list[str],
    data_description: str,
    results_text: str,
    interpretation: str,
    limitations: list[str],
    conclusion: str,
    metrics: dict = None,
    tables: list = None,
    figures: list = None,
    tickers: list[str] = None,
    date_range: tuple = None,
) -> str:
    """
    Assemble a complete HTML research report.

    Parameters
    ----------
    title : str            Report title
    question : str         Research question
    methodology : str      Methodology description
    assumptions : list     List of assumption strings
    data_description : str Dataset description
    results_text : str     Summary of results
    interpretation : str   Plain-English interpretation
    limitations : list     List of limitation strings
    conclusion : str       Concluding remarks
    metrics : dict         Key metrics {label: value} for the metric grid
    tables : list          List of DataFrames to include
    figures : list         List of Plotly figures to embed
    tickers : list         Ticker symbols used
    date_range : tuple     (start, end) date strings

    Returns HTML string.
    """
    generated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M UTC")

    # Badges
    badge_html = ""
    if tickers:
        badge_html += "".join(f'<span class="badge">{t}</span>' for t in tickers)
    if date_range:
        badge_html += f'<span class="badge">{date_range[0]} → {date_range[1]}</span>'
    badge_html += '<span class="badge">AlphaLab AI</span>'

    # Metric grid
    metric_html = ""
    if metrics:
        cards = "".join(
            f'<div class="metric-card"><div class="label">{k}</div>'
            f'<div class="value">{v}</div></div>'
            for k, v in metrics.items()
        )
        metric_html = f'<div class="metric-grid">{cards}</div>'

    # Assumptions
    assump_html = "<ul>" + "".join(f"<li>{a}</li>" for a in assumptions) + "</ul>"

    # Limitations
    limit_html = "<ul>" + "".join(f"<li>{l}</li>" for l in limitations) + "</ul>"

    # Tables
    tables_html = ""
    if tables:
        for df in tables:
            tables_html += df_to_html_table(df)

    # Figures
    figures_html = ""
    if figures:
        for fig in figures:
            b64 = fig_to_base64(fig)
            if b64:
                figures_html += f'<img src="data:image/png;base64,{b64}" />'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — AlphaLab AI</title>
  {REPORT_CSS}
</head>
<body>

<div class="header">
  <h1>⬡ ALPHALAB AI</h1>
  <div class="subtitle">AI-Powered Statistical Research Copilot &nbsp;|&nbsp; Generated: {generated_at}</div>
  <div style="margin-top:14px">{badge_html}</div>
  <h2 style="font-size:20px; color:#E8F4FD; margin-top:20px; font-family:Inter,sans-serif; font-weight:700;">{title}</h2>
</div>

<div class="section">
  <h2>01 — Research Question</h2>
  <p>{question}</p>
</div>

<div class="section">
  <h2>02 — Data Used</h2>
  <p>{data_description}</p>
</div>

<div class="section">
  <h2>03 — Methodology</h2>
  <p>{methodology}</p>
</div>

<div class="section">
  <h2>04 — Assumptions</h2>
  {assump_html}
</div>

<div class="section">
  <h2>05 — Results</h2>
  {metric_html}
  <p style="margin-top:16px">{results_text}</p>
  {tables_html}
</div>

<div class="section">
  <h2>06 — Visualizations</h2>
  {figures_html if figures_html else "<p>No visualizations included in this report.</p>"}
</div>

<div class="section">
  <h2>07 — Interpretation</h2>
  <p>{interpretation}</p>
</div>

<div class="section">
  <h2>08 — Limitations</h2>
  {limit_html}
</div>

<div class="section">
  <h2>09 — Conclusion</h2>
  <p>{conclusion}</p>
</div>

<div class="warning-box">
  ⚠ <strong>Disclaimer:</strong> This report was generated by AlphaLab AI for research and educational purposes only.
  It does not constitute financial advice, investment recommendations, or guarantees of future performance.
  All statistical results carry uncertainty and should be interpreted by qualified professionals.
  Past performance is not indicative of future results.
</div>

<div class="footer">
  AlphaLab AI &nbsp;|&nbsp; Statistical Research Copilot &nbsp;|&nbsp; {generated_at}
</div>

</body>
</html>"""

    return html
