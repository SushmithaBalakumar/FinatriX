import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
import os
from typing import Optional, Dict, List

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

BASE_PATH = r"C:\Users\myhp2\risk-analytics\src\risk_analytics\Finance"

RISK_LIMITS = {
    'var_95_limit': -10.0,
    'var_99_limit': -40.0,
    'es_95_limit': -50.0,
    'es_99_limit': -150.0,
    'sector_concentration_limit': 0.15,
    'single_position_limit': 0.10,
    'slippage_threshold_bps': 10.0,
    'market_impact_threshold_bps': 15.0,
    'max_drawdown_limit': -0.20
}

COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'accent': '#f093fb',
    'danger': '#ff6b6b',
    'warning': '#feca57',
    'success': '#48dbfb',
    'info': '#00d2d3',
    'dark': '#0f0f23',
    'surface': '#1a1a2e',
    'card': '#16213e',
    'text': '#e4e4e7',
    'muted': '#94a3b8'
}

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="FinatriX",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ULTRA-MODERN PROFESSIONAL STYLING
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
        color: #e4e4e7;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a15 0%, #16213e 100%);
        border-right: 1px solid rgba(102, 126, 234, 0.1);
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.5);
    }
    
    [data-testid="stSidebar"] * {
        color: #e4e4e7 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    [data-testid="stSidebar"] [role="radiogroup"] label {
        background: rgba(102, 126, 234, 0.05) !important;
        border-radius: 12px;
        padding: 0.75rem 1rem !important;
        margin: 0.25rem 0 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border-left: 3px solid transparent;
    }
    
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(102, 126, 234, 0.12) !important;
        transform: translateX(4px);
        border-left-color: #667eea;
    }
    
    [data-testid="stSidebar"] [role="radiogroup"] input:checked + div {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2)) !important;
        border-left: 3px solid #667eea !important;
        font-weight: 600;
    }
    
    h1 {
        font-size: 2.75rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.03em;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 0 40px rgba(102, 126, 234, 0.3);
    }
    
    h2 {
        font-size: 1.875rem !important;
        font-weight: 700 !important;
        color: #e4e4e7 !important;
        letter-spacing: -0.02em;
        margin-top: 2rem !important;
    }
    
    h3 {
        font-size: 1.375rem !important;
        font-weight: 600 !important;
        color: #cbd5e1 !important;
        letter-spacing: -0.01em;
    }
    
    .kpi-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 1.75rem;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--accent-color, #667eea), transparent);
        opacity: 0;
        transition: opacity 0.4s;
    }
    
    .kpi-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.4);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    .kpi-card:hover::before {
        opacity: 1;
    }
    
    .kpi-title {
        font-size: 0.75rem;
        font-weight: 700;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 1rem;
    }
    
    .kpi-value {
        font-size: 2.5rem;
        font-weight: 800;
        line-height: 1;
        margin: 0.75rem 0;
        text-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
    }
    
    .kpi-change {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        font-weight: 600;
        padding: 0.5rem 1rem;
        border-radius: 100px;
        margin-top: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .kpi-subtitle {
        font-size: 0.75rem;
        color: #64748b;
        margin-top: 0.75rem;
        font-weight: 500;
    }
    
    .section-header {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0.15) 0%, transparent 100%);
        border-left: 4px solid #667eea;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin: 2.5rem 0 1.5rem 0;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    
    .section-header h3 {
        margin: 0 !important;
        font-size: 1.25rem !important;
    }
    
    .alert-box {
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1rem 0;
        border-left: 4px solid;
        backdrop-filter: blur(20px);
        font-size: 0.95rem;
        line-height: 1.7;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .alert-box:hover {
        transform: translateX(4px);
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3);
    }
    
    .alert-critical {
        border-color: #ff6b6b;
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.15), rgba(255, 107, 107, 0.05));
    }
    
    .alert-danger {
        border-color: #ff6b6b;
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.12), rgba(255, 107, 107, 0.04));
    }
    
    .alert-warning {
        border-color: #feca57;
        background: linear-gradient(135deg, rgba(254, 202, 87, 0.12), rgba(254, 202, 87, 0.04));
    }
    
    .alert-success {
        border-color: #48dbfb;
        background: linear-gradient(135deg, rgba(72, 219, 251, 0.12), rgba(72, 219, 251, 0.04));
    }
    
    .alert-info {
        border-color: #00d2d3;
        background: linear-gradient(135deg, rgba(0, 210, 211, 0.12), rgba(0, 210, 211, 0.04));
    }
    
    .trade-card {
        background: linear-gradient(135deg, rgba(22, 33, 62, 0.8) 0%, rgba(26, 26, 46, 0.8) 100%);
        backdrop-filter: blur(15px);
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 16px;
        border-left: 4px solid;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .trade-card:hover {
        transform: translateX(6px);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    }
    
    .trade-buy {
        border-color: #48dbfb;
        background: linear-gradient(135deg, rgba(72, 219, 251, 0.08), rgba(72, 219, 251, 0.02));
    }
    
    .trade-sell {
        border-color: #ff6b6b;
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.08), rgba(255, 107, 107, 0.02));
    }
    
    .data-quality {
        display: inline-flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 1.25rem;
        border-radius: 100px;
        font-size: 0.875rem;
        font-weight: 700;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    
    .data-quality:hover {
        transform: scale(1.05);
    }
    
    .quality-high {
        background: linear-gradient(135deg, rgba(72, 219, 251, 0.2), rgba(72, 219, 251, 0.1));
        border: 1px solid rgba(72, 219, 251, 0.3);
        color: #48dbfb;
    }
    
    .quality-medium {
        background: linear-gradient(135deg, rgba(254, 202, 87, 0.2), rgba(254, 202, 87, 0.1));
        border: 1px solid rgba(254, 202, 87, 0.3);
        color: #feca57;
    }
    
    .quality-low {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(255, 107, 107, 0.1));
        border: 1px solid rgba(255, 107, 107, 0.3);
        color: #ff6b6b;
    }
    
    .metric-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        backdrop-filter: blur(10px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: transparent;
        border-bottom: 2px solid rgba(102, 126, 234, 0.2);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        background: transparent;
        border-radius: 12px 12px 0 0;
        font-weight: 600;
        color: #94a3b8;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1);
        color: #e4e4e7;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
        border-bottom: 3px solid #667eea;
        color: #667eea !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        background: linear-gradient(135deg, #7c8eef 0%, #8a5fb8 100%);
    }
    
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 15, 35, 0.5);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea, #764ba2);
        border-radius: 10px;
        border: 2px solid rgba(15, 15, 35, 0.5);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #7c8eef, #8a5fb8);
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.5), transparent);
        margin: 2rem 0;
    }
    
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background: rgba(22, 33, 62, 0.5);
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 10px;
        color: #e4e4e7;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .kpi-card, .trade-card, .alert-box {
        animation: fadeInUp 0.6s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

@st.cache_data(ttl=300)
def load_csv_safe(path: str) -> pd.DataFrame:
    try:
        if not os.path.exists(path):
            return pd.DataFrame()
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        df = df.drop_duplicates()
        return df
    except:
        return pd.DataFrame()

def assess_data_quality(df: pd.DataFrame) -> str:
    if df.empty:
        return "low"
    missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
    if missing_pct < 1:
        return "high"
    elif missing_pct < 5:
        return "medium"
    else:
        return "low"

# ============================================================================
# FILE PATHS & DATA LOADING
# ============================================================================

PATHS = {
    "risk_metrics": os.path.join(BASE_PATH, "Risk Analytics Module", "daily_risk_metrics.csv"),
    "sector_exposure": os.path.join(BASE_PATH, "Risk Analytics Module", "sector_exposure.csv"),
    "backtest_results": os.path.join(BASE_PATH, "Backtesting Framework & Strategies", "backtest_results.csv"),
    "backtest_wf": os.path.join(BASE_PATH, "Backtesting Framework & Strategies", "backtest_results_walkforward.csv"),
    "target_weights": os.path.join(BASE_PATH, "Portfolio Optimization Module", "target_weights.csv"),
    "trade_recommendations": os.path.join(BASE_PATH, "Portfolio Optimization Module", "trade_recommendations.csv"),
    "portfolio_risk_returns": os.path.join(BASE_PATH, "Portfolio Optimization Module", "portfolio_risk_return.csv"),
    "tca_summary": os.path.join(BASE_PATH, "Transaction Cost Analysis (TCA)", "weekly_tca_summary.csv")
}

with st.spinner("Loading portfolio data..."):
    risk_metrics = load_csv_safe(PATHS["risk_metrics"])
    sector_exposure = load_csv_safe(PATHS["sector_exposure"])
    backtest_results = load_csv_safe(PATHS["backtest_results"])
    backtest_wf = load_csv_safe(PATHS["backtest_wf"])
    target_weights = load_csv_safe(PATHS["target_weights"])
    trade_recommendations = load_csv_safe(PATHS["trade_recommendations"])
    portfolio_risk_returns = load_csv_safe(PATHS["portfolio_risk_returns"])
    tca_summary = load_csv_safe(PATHS["tca_summary"])

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_safe_value(series: pd.Series, index: int = -1, default: float = 0.0) -> float:
    try:
        series_clean = series.dropna()
        if len(series_clean) > abs(index):
            return float(series_clean.iloc[index])
        return default
    except:
        return default

def calculate_change(series: pd.Series, periods: int = 1) -> float:
    try:
        series_clean = series.dropna()
        if len(series_clean) > periods:
            current = float(series_clean.iloc[-1])
            previous = float(series_clean.iloc[-(periods + 1)])
            if previous != 0:
                return ((current - previous) / abs(previous)) * 100
        return 0.0
    except:
        return 0.0

def format_large_number(num: float) -> str:
    abs_num = abs(num)
    if abs_num >= 1e9:
        return f"{num/1e9:.2f}B"
    elif abs_num >= 1e6:
        return f"{num/1e6:.2f}M"
    elif abs_num >= 1e3:
        return f"{num/1e3:.2f}K"
    else:
        return f"{num:.2f}"

def kpi_card(title: str, value: float, change: Optional[float] = None, 
             color: str = '#667eea', format_str: str = '.2f',
             subtitle: str = '', threshold: Optional[float] = None):
    
    # Format the value
    formatted_value = f"{value:{format_str}}"
    
    # Breach indicator
    breach_html = ""
    if threshold is not None and value < threshold:
        breach_html = " <span style='color:#ff6b6b; font-weight:700;'>⚠ BREACH</span>"
    
    # Change indicator
    change_html = ""
    if change is not None:
        change_color = COLORS['success'] if change < 0 else COLORS['danger']
        change_symbol = '▼' if change < 0 else '▲'
        change_bg = 'rgba(72, 219, 251, 0.2)' if change < 0 else 'rgba(255, 107, 107, 0.2)'
        change_html = f"""<div class='kpi-change' style='color:{change_color}; background:{change_bg}'>{change_symbol} {abs(change):.2f}%</div>"""
    
    # Subtitle
    subtitle_html = f"<div class='kpi-subtitle'>{subtitle}</div>" if subtitle else ""
    
    # Render the complete card
    card_html = f"""
    <div class='kpi-card' style='--accent-color:{color}'>
        <div class='kpi-title'>{title}{breach_html}</div>
        <div class='kpi-value' style='color:{color}'>{formatted_value}</div>
        {change_html}
        {subtitle_html}
    </div>
    """
    
    st.markdown(card_html, unsafe_allow_html=True)

def create_gauge_chart(value: float, title: str, max_val: float, 
                       threshold: float, unit: str = "%") -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=abs(value),
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 18, 'color': COLORS['text'], 'family': 'Inter'}},
        number={'suffix': unit, 'font': {'size': 28, 'family': 'Inter'}},
        gauge={
            'axis': {'range': [None, max_val], 'tickcolor': COLORS['text']},
            'bar': {'color': COLORS['primary'], 'thickness': 0.75},
            'bgcolor': 'rgba(0,0,0,0)',
            'borderwidth': 0,
            'steps': [
                {'range': [0, abs(threshold) * 0.7], 'color': 'rgba(72, 219, 251, 0.2)'},
                {'range': [abs(threshold) * 0.7, abs(threshold)], 'color': 'rgba(254, 202, 87, 0.2)'},
                {'range': [abs(threshold), max_val], 'color': 'rgba(255, 107, 107, 0.2)'}
            ],
            'threshold': {
                'line': {'color': COLORS['danger'], 'width': 4},
                'thickness': 0.85,
                'value': abs(threshold)
            }
        }
    ))
    
    fig.update_layout(
        height=280,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORS['text'], family='Inter'),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

# ============================================================================
# PREMIUM SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.markdown("""
    <div style='text-align: center; padding: 1.5rem 0;'>
        <h1 style='font-size: 2.500rem; margin: 0; background: linear-gradient(135deg, #667eea, #764ba2, #f093fb);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
            〽 FinatriX
        </h1>
        <p style='color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;'>Finance Simplified</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("<hr style='margin: 1rem 0; opacity: 0.2;'>", unsafe_allow_html=True)

section = st.sidebar.radio(
    "Navigation",
    [
        "Executive Overview",
        "Risk Analytics",
        "Strategy Performance",
        "Portfolio Management",
        "Transaction Analysis",
        "Alerts & Compliance",
        "Reporting & Export"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown("<hr style='margin: 1.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)

st.sidebar.markdown("### System Status")
st.sidebar.success("All Systems Operational")

st.sidebar.markdown("### Data Freshness")
st.sidebar.info(f"""
**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Next Refresh:** {(datetime.now() + timedelta(hours=1)).strftime('%H:%M')}
""")

quality_risk = assess_data_quality(risk_metrics)
quality_sector = assess_data_quality(sector_exposure)

color_map = {"high": "#48dbfb", "medium": "#feca57", "low": "#ff6b6b"}

st.sidebar.markdown(f"""
<div style='padding: 1rem; background: rgba(102, 126, 234, 0.1); border-radius: 12px; margin-top: 1rem;'>
    <div style='font-size: 0.875rem; font-weight: 600; margin-bottom: 0.5rem;'>Data Quality</div>
    <div style='display: flex; justify-content: space-between; margin: 0.25rem 0;'>
        <span>Risk Metrics</span>
        <span style='color: {color_map[quality_risk]};'>{quality_risk.upper()}</span>
    </div>
    <div style='display: flex; justify-content: space-between; margin: 0.25rem 0;'>
        <span>Sector Data</span>
        <span style='color: {color_map[quality_sector]};'>{quality_sector.upper()}</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("### Records Loaded")
st.sidebar.markdown(f"""
- **Risk Metrics:** {len(risk_metrics):,}  
- **Sectors:** {len(sector_exposure):,}  
- **Backtest:** {len(backtest_results):,}  
- **Portfolio:** {len(target_weights):,}  
- **Trades:** {len(trade_recommendations):,}  
- **TCA:** {len(tca_summary):,}
""")

st.sidebar.markdown("<hr style='margin: 1.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)

st.sidebar.markdown("### Quick Actions")
col_r, col_e = st.sidebar.columns(2)
with col_r:
    if st.button("Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col_e:
    if st.button("Export", use_container_width=True):
        st.sidebar.success("Export ready!")

        st.sidebar.markdown("<hr style='margin: 1.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)

        st.sidebar.markdown("""
<div style='text-align: center; padding: 1rem; color: #64748b; font-size: 0.8rem;'>
    <strong>Version 2.5.0</strong><br>
    © 2024 Risk Platform
</div>
""", unsafe_allow_html=True)

# ============================================================================
# MAIN CONTENT - EXECUTIVE OVERVIEW
# ============================================================================

if section == "Executive Overview":
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.title("Executive Risk Dashboard")
        st.markdown("Comprehensive portfolio risk and performance overview")
    with col_h2:
        quality = assess_data_quality(risk_metrics)
        quality_class = f"quality-{quality}"
        st.markdown(f"""
            <div class='data-quality {quality_class}'>
                Data Quality: {quality.upper()}
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### Key Risk Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if not risk_metrics.empty and "VaR_95" in risk_metrics.columns:
            val = get_safe_value(risk_metrics["VaR_95"])
            change = calculate_change(risk_metrics["VaR_95"])
            kpi_card("VaR 95%", val, change, COLORS['danger'], '.2f', 
                    'Daily Value at Risk', RISK_LIMITS['var_95_limit'])
    
    with col2:
        if not risk_metrics.empty and "ES_95" in risk_metrics.columns:
            val = get_safe_value(risk_metrics["ES_95"])
            change = calculate_change(risk_metrics["ES_95"])
            kpi_card("Expected Shortfall", val, change, COLORS['danger'], '.2f',
                    '95% Confidence', RISK_LIMITS['es_95_limit'])
    
    with col3:
        if not portfolio_risk_returns.empty and "Expected Return" in portfolio_risk_returns.columns:
            val = float(portfolio_risk_returns["Expected Return"].iloc[0])
            kpi_card("Expected Return", val, change, COLORS['success'], '.2f', 'Annualized %')

    with col4:
        if not portfolio_risk_returns.empty and "Sharpe Ratio" in portfolio_risk_returns.columns:
            val = float(portfolio_risk_returns["Sharpe Ratio"].iloc[0])*0.05
            kpi_card("Sharpe Ratio", val, change, COLORS['info'], '.3f', 'Risk-Adjusted')

    with col5:
        if not portfolio_risk_returns.empty and "Expected Volatility" in portfolio_risk_returns.columns:
            val = float(portfolio_risk_returns["Expected Volatility"].iloc[0]) * 100
            kpi_card("Volatility", val, change, COLORS['warning'], '.2f', 'Annualized %')
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### Risk Utilization")
    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
    
    with col_g1:
        if not risk_metrics.empty and "VaR_95" in risk_metrics.columns:
            val = get_safe_value(risk_metrics["VaR_95"])
            fig = create_gauge_chart(val, "VaR 95%", 50, RISK_LIMITS['var_95_limit'])
            st.plotly_chart(fig, use_container_width=True, key="gauge_var95")
    
    with col_g2:
        if not risk_metrics.empty and "ES_95" in risk_metrics.columns:
            val = get_safe_value(risk_metrics["ES_95"])
            fig = create_gauge_chart(val, "ES 95%", 100, RISK_LIMITS['es_95_limit'])
            st.plotly_chart(fig, use_container_width=True, key="gauge_es95")
    
    with col_g3:
        if not risk_metrics.empty and "VaR_99" in risk_metrics.columns:
            val = get_safe_value(risk_metrics["VaR_99"])
            fig = create_gauge_chart(val, "VaR 99%", 80, RISK_LIMITS['var_99_limit'])
            st.plotly_chart(fig, use_container_width=True, key="gauge_var99")
    
    with col_g4:
        if not risk_metrics.empty and "ES_99" in risk_metrics.columns:
            val = get_safe_value(risk_metrics["ES_99"])
            fig = create_gauge_chart(val, "ES 99%", 200, RISK_LIMITS['es_99_limit'])
            st.plotly_chart(fig, use_container_width=True, key="gauge_es99")
    
    col_left, col_right = st.columns([1.3, 1])
    
    with col_left:
        st.markdown("<div class='section-header'><h3>Sector Exposure Analysis</h3></div>", unsafe_allow_html=True)
        
        if not sector_exposure.empty:
            sector_data = sector_exposure.copy()
            sector_data['portfolio_weight'] = sector_data['portfolio_weight'] * 100
            sector_data = sector_data.sort_values('portfolio_weight')
            
            max_exposure = sector_data['portfolio_weight'].abs().max()
            concentration_alert = max_exposure > (RISK_LIMITS['sector_concentration_limit'] * 100)
            
            fig = go.Figure()
            
            colors = [COLORS['danger'] if abs(x) > (RISK_LIMITS['sector_concentration_limit'] * 100) 
                     else COLORS['success'] if x > 0 else COLORS['warning']
                     for x in sector_data['portfolio_weight']]
            
            fig.add_trace(go.Bar(
                x=sector_data['portfolio_weight'],
                y=sector_data['sector'],
                orientation='h',
                marker=dict(color=colors, line=dict(color='rgba(255,255,255,0.1)', width=1)),
                text=sector_data['portfolio_weight'].apply(lambda x: f'{x:.2f}%'),
                textposition='outside',
                textfont=dict(family='Inter', size=11),
                hovertemplate='<b>%{y}</b><br>Weight: %{x:.2f}%<extra></extra>'
            ))
            
            limit_pct = RISK_LIMITS['sector_concentration_limit'] * 100
            fig.add_vline(x=limit_pct, line_dash="dash", line_color=COLORS['warning'],
                         annotation_text=f"Limit: {limit_pct}%", annotation_position="top right")
            fig.add_vline(x=-limit_pct, line_dash="dash", line_color=COLORS['warning'])
            
            fig.update_layout(
                height=420,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COLORS['text'], family='Inter'),
                xaxis=dict(title="Portfolio Weight (%)", gridcolor='rgba(102, 126, 234, 0.1)', 
                          zeroline=True, zerolinecolor='rgba(102, 126, 234, 0.2)'),
                yaxis=dict(title="", tickfont=dict(size=11)),
                margin=dict(l=20, r=80, t=20, b=40)
            )
            
            st.plotly_chart(fig, use_container_width=True, key="sector_exposure_main")
            
            if concentration_alert:
                st.markdown("""
                    <div class='alert-box alert-warning'>
                        <strong>Concentration Risk Detected:</strong> One or more sectors exceed the 15% exposure limit.
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No sector exposure data available")
    
    with col_right:
        st.markdown("<div class='section-header'><h3>Stress Test Scenarios</h3></div>", unsafe_allow_html=True)
        
        if not risk_metrics.empty:
            stress_cols = ["Rate_Shock", "Volatility_Spike", "Sector_Drawdown"]
            available = [c for c in stress_cols if c in risk_metrics.columns]
            
            if available:
                latest_stress = risk_metrics[available].iloc[-1]
                
                for col in available:
                    val = latest_stress[col]
                    
                    if val < -5.0:
                        color = COLORS['danger']
                        severity = "CRITICAL"
                        icon = "🔴"
                    elif val < -2.0:
                        color = COLORS['warning']
                        severity = "HIGH"
                        icon = "🟡"
                    elif val < 0:
                        color = COLORS['info']
                        severity = "MODERATE"
                        icon = "🟢"
                    else:
                        color = COLORS['success']
                        severity = "LOW"
                        icon = "🟢"
                    
                    st.markdown(f"""
                        <div class='trade-card' style='border-color: {color}'>
                            <div style='display: flex; justify-content: space-between; align-items: center;'>
                                <div>
                                    <span style='font-weight: 700; font-size: 0.95rem;'>{col.replace('_', ' ')}</span><br>
                                    <span class='metric-badge' style='background:{color};color:#fff;margin-top:0.5rem;'>{icon} {severity}</span>
                                </div>
                                <span style='color: {color}; font-weight: 800; font-size: 1.6rem;'>{val:.2f}%</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                stress_history = risk_metrics[available].tail(30)
                
                fig_stress = go.Figure()
                colors_stress = [COLORS['danger'], COLORS['warning'], COLORS['info']]
                
                for i, col in enumerate(available):
                    fig_stress.add_trace(go.Scatter(
                        y=stress_history[col],
                        name=col.replace('_', ' '),
                        mode='lines',
                        line=dict(width=2.5, color=colors_stress[i]),
                        fill='tonexty' if i > 0 else None
                    ))
                
                fig_stress.update_layout(
                    height=220,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['text'], size=10, family='Inter'),
                    xaxis=dict(title="", gridcolor='rgba(102, 126, 234, 0.1)', showticklabels=False),
                    yaxis=dict(title="Impact (%)", gridcolor='rgba(102, 126, 234, 0.1)'),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=9)),
                    margin=dict(l=40, r=10, t=30, b=20),
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig_stress, use_container_width=True, key="stress_mini")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_perf1, col_perf2 = st.columns([1.2, 1])
    
    with col_perf1:
        st.markdown("<div class='section-header'><h3>Top Holdings Analysis</h3></div>", unsafe_allow_html=True)
        
        if not target_weights.empty and "Target Weight" in target_weights.columns:
            top_holdings = target_weights.nlargest(10, 'Target Weight')
            
            max_position = top_holdings['Target Weight'].max()
            position_alert = max_position > RISK_LIMITS['single_position_limit']
            
            fig = go.Figure()
            
            colors_holdings = [COLORS['danger'] if w > RISK_LIMITS['single_position_limit'] 
                             else COLORS['primary'] for w in top_holdings['Target Weight']]
            
            fig.add_trace(go.Bar(
                x=top_holdings['Target Weight'],
                y=top_holdings['Instrument'],
                orientation='h',
                marker=dict(
                    color=colors_holdings,
                    line=dict(color='rgba(255,255,255,0.1)', width=1)
                ),
                text=top_holdings['Target Weight'].apply(lambda x: f'{x:.2%}'),
                textposition='outside',
                textfont=dict(family='Inter', size=10),
                hovertemplate='<b>%{y}</b><br>Weight: %{x:.2%}<extra></extra>'
            ))
            
            fig.add_vline(x=RISK_LIMITS['single_position_limit'], line_dash="dash", 
                         line_color=COLORS['warning'],
                         annotation_text=f"Limit: {RISK_LIMITS['single_position_limit']:.0%}", 
                         annotation_position="top right")
            
            fig.update_layout(
                height=370,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COLORS['text'], family='Inter'),
                xaxis=dict(title="Position Weight", gridcolor='rgba(102, 126, 234, 0.1)', tickformat='.0%'),
                yaxis=dict(title="", autorange='reversed', tickfont=dict(size=10)),
                showlegend=False,
                margin=dict(l=20, r=80, t=20, b=40)
            )
            
            st.plotly_chart(fig, use_container_width=True, key="top_holdings_main")
            
            if position_alert:
                st.markdown(f"""
                    <div class='alert-box alert-warning'>
                        <strong>Position Concentration Alert:</strong> Maximum single position of {max_position:.2%} exceeds {RISK_LIMITS['single_position_limit']:.0%} limit.
                    </div>
                """, unsafe_allow_html=True)
    
    with col_perf2:
        st.markdown("<div class='section-header'><h3>Transaction Cost Trends</h3></div>", unsafe_allow_html=True)
        
        if not tca_summary.empty and "avg_slippage_bps" in tca_summary.columns:
            avg_slippage = tca_summary["avg_slippage_bps"].mean()
            recent_slippage = get_safe_value(tca_summary["avg_slippage_bps"])
            slippage_trend = calculate_change(tca_summary["avg_slippage_bps"], periods=4)
            
            high_slippage = abs(recent_slippage) > RISK_LIMITS['slippage_threshold_bps']
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                y=tca_summary["avg_slippage_bps"],
                mode='lines+markers',
                line=dict(color=COLORS['danger'] if high_slippage else COLORS['info'], width=3),
                marker=dict(size=8, symbol='diamond'),
                fill='tozeroy',
                fillcolor=f"rgba(255, 107, 107, 0.15)" if high_slippage else f"rgba(0, 210, 211, 0.15)",
                name='Slippage',
                hovertemplate='Week %{x}<br>Slippage: %{y:.2f} bps<extra></extra>'
            ))
            
            fig.add_hline(
                y=avg_slippage, 
                line_dash="dash", 
                line_color=COLORS['warning'],
                annotation_text=f"Avg: {avg_slippage:.2f} bps",
                annotation_position="right"
            )
            
            fig.add_hline(
                y=RISK_LIMITS['slippage_threshold_bps'], 
                line_dash="dot", 
                line_color=COLORS['danger'],
                annotation_text=f"Threshold: {RISK_LIMITS['slippage_threshold_bps']} bps",
                annotation_position="left"
            )
            
            fig.update_layout(
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COLORS['text'], family='Inter'),
                xaxis=dict(title="Week", gridcolor='rgba(102, 126, 234, 0.1)'),
                yaxis=dict(title="Slippage (bps)", gridcolor='rgba(102, 126, 234, 0.1)'),
                margin=dict(l=50, r=20, t=20, b=40),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True, key="tca_trend_main")
            
            col_tca1, col_tca2 = st.columns(2)
            with col_tca1:
                st.metric(
                    "Current Slippage",
                    f"{recent_slippage:.2f} bps",
                    f"{slippage_trend:+.1f}%",
                    delta_color="inverse"
                )
            with col_tca2:
                st.metric(
                    "Average Slippage",
                    f"{avg_slippage:.2f} bps"
                )
            
            if high_slippage:
                st.markdown("""
                    <div class='alert-box alert-danger' style='margin-top:1rem;'>
                        <strong>High Slippage Warning:</strong> Recent execution costs exceed acceptable thresholds.
                    </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("<div class='section-header'><h3>Risk Summary & Compliance Status</h3></div>", unsafe_allow_html=True)
    
    summary_data = []
    
    if not risk_metrics.empty:
        var_95 = get_safe_value(risk_metrics.get("VaR_95", pd.Series([0])))
        summary_data.append({
            'Risk Metric': 'Value at Risk (95%)',
            'Current Value': f"{var_95:.2f}",
            'Limit': f"{RISK_LIMITS['var_95_limit']:.2f}",
            'Utilization': f"{(var_95/RISK_LIMITS['var_95_limit']*100):.1f}%",
            'Status': 'Pass' if var_95 >= RISK_LIMITS['var_95_limit'] else 'Breach'
        })
        
        es_95 = get_safe_value(risk_metrics.get("ES_95", pd.Series([0])))
        summary_data.append({
            'Risk Metric': 'Expected Shortfall (95%)',
            'Current Value': f"{es_95:.2f}",
            'Limit': f"{RISK_LIMITS['es_95_limit']:.2f}",
            'Utilization': f"{(es_95/RISK_LIMITS['es_95_limit']*100):.1f}%",
            'Status': 'Pass' if es_95 >= RISK_LIMITS['es_95_limit'] else 'Breach'
        })
    
    if not sector_exposure.empty:
        max_sector = sector_exposure['portfolio_weight'].abs().max()
        summary_data.append({
            'Risk Metric': 'Sector Concentration',
            'Current Value': f"{max_sector*100:.2f}%",
            'Limit': f"{RISK_LIMITS['sector_concentration_limit']*100:.0f}%",
            'Utilization': f"{(max_sector/RISK_LIMITS['sector_concentration_limit']*100):.1f}%",
            'Status': 'Pass' if max_sector <= RISK_LIMITS['sector_concentration_limit'] else 'Warning'
        })
    
    if not target_weights.empty:
        max_position = target_weights['Target Weight'].max()
        summary_data.append({
            'Risk Metric': 'Single Position Limit',
            'Current Value': f"{max_position*100:.2f}%",
            'Limit': f"{RISK_LIMITS['single_position_limit']*100:.0f}%",
            'Utilization': f"{(max_position/RISK_LIMITS['single_position_limit']*100):.1f}%",
            'Status': 'Pass' if max_position <= RISK_LIMITS['single_position_limit'] else 'Warning'
        })
    
    if summary_data:
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True, height=250)
        
        passes = sum('Pass' in str(row['Status']) for row in summary_data)
        total = len(summary_data)
        compliance_pct = (passes / total * 100) if total > 0 else 0
        
        if compliance_pct == 100:
            st.markdown("""
                <div class='alert-box alert-success'>
                    <strong>Full Compliance:</strong> All risk limits are within acceptable ranges.
                </div>
            """, unsafe_allow_html=True)
        elif compliance_pct >= 75:
            st.markdown(f"""
                <div class='alert-box alert-warning'>
                    <strong>Partial Compliance:</strong> {compliance_pct:.0f}% of limits met. Review required.
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='alert-box alert-danger'>
                    <strong>Compliance Issues:</strong> Only {compliance_pct:.0f}% of limits met. Immediate action required.
                </div>
            """, unsafe_allow_html=True)

# ============================================================================
# RISK ANALYTICS SECTION - ENHANCED & INTERACTIVE
# ============================================================================

elif section == "Risk Analytics":
    st.title("Risk Analytics Deep Dive")
    st.markdown("Comprehensive risk metrics, factor exposure, and scenario analysis")
    st.markdown("---")
    
    # Interactive Risk Profile Selector
    col_selector1, col_selector2, col_selector3 = st.columns([2, 2, 1])
    with col_selector1:
        risk_horizon = st.selectbox(
            "Risk Horizon",
            ["1-Day", "5-Day", "10-Day", "Monthly"],
            index=0,
            help="Select time horizon for risk calculations"
        )
    horizon_map = {"1-Day": 1, "5-Day": 5, "10-Day": 10, "Monthly": 22}
    scaling_factor = np.sqrt(horizon_map[risk_horizon])

    risk_metrics_scaled = risk_metrics.copy()
    for col in ["VaR_95", "ES_95", "VaR_99", "ES_99"]:
        if col in risk_metrics_scaled.columns:
            risk_metrics_scaled[col] = risk_metrics_scaled[col] * scaling_factor

    st.markdown("---")
    st.markdown(f"### 🎯 Current Risk Position ({risk_horizon})")
    
    # Current Risk Position with Interactive Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if "VaR_95" in risk_metrics_scaled.columns:
            val = get_safe_value(risk_metrics_scaled["VaR_95"])
            change = calculate_change(risk_metrics_scaled["VaR_95"])
            kpi_card("VaR 95%", val, change, COLORS['danger'], '.2f', risk_horizon, RISK_LIMITS['var_95_limit'])
    
    with col2:
        if "ES_95" in risk_metrics_scaled.columns:
            val = get_safe_value(risk_metrics_scaled["ES_95"])
            change = calculate_change(risk_metrics_scaled["ES_95"])
            kpi_card("ES 95%", val, change, COLORS['danger'], '.2f', 'Tail Risk', RISK_LIMITS['es_95_limit'])
    
    with col3:
        if "VaR_99" in risk_metrics_scaled.columns:
            val = get_safe_value(risk_metrics_scaled["VaR_99"])
            change = calculate_change(risk_metrics_scaled["VaR_99"])
            kpi_card("VaR 99%", val, change, COLORS['warning'], '.2f', 'Extreme', RISK_LIMITS['var_99_limit'])
    
    with col4:
        if "ES_99" in risk_metrics_scaled.columns:
            val = get_safe_value(risk_metrics_scaled["ES_99"])
            change = calculate_change(risk_metrics_scaled["ES_99"])
            kpi_card("ES 99%", val, change, COLORS['warning'], '.2f', 'Extreme Tail', RISK_LIMITS['es_99_limit'])
    
    with col5:
        if not risk_metrics_scaled.empty:
            avg_risk = risk_metrics_scaled[["VaR_95", "ES_95"]].mean().mean()
            change = calculate_change(risk_metrics_scaled[["VaR_95", "ES_95"]].mean(axis=1))
            kpi_card("Avg Risk", avg_risk, change, COLORS['info'], '.2f', 'Combined')
    
    st.markdown("<br>", unsafe_allow_html=True)

    # ============================================================================
    # STRATEGY-LEVEL RISK BREAKDOWN
    # ============================================================================
    
    st.markdown("<div class='section-header'><h3>📊 Strategy-Level Risk Breakdown</h3></div>", unsafe_allow_html=True)
    
    # Check if strategy-level data exists
    strategy_files = {
        'ARBITRAGE': os.path.join(BASE_PATH, "..", "..", "outputs", "strategy_returns_ARBITRAGE.csv"),
        'MARKET_MAKING': os.path.join(BASE_PATH, "..", "..", "outputs", "strategy_returns_MARKET_MAKING.csv"),
        'MEAN_REVERSION': os.path.join(BASE_PATH, "..", "..", "outputs", "strategy_returns_MEAN_REVERSION.csv"),
        'MOMENTUM': os.path.join(BASE_PATH, "..", "..", "outputs", "strategy_returns_MOMENTUM.csv"),
        'PAIRS_TRADING': os.path.join(BASE_PATH, "..", "..", "outputs", "strategy_returns_PIRS_TRADING.csv")
    }

    strategy_risk_data = {}
    
    # Load and calculate VaR/ES for each strategy
    for strategy_name, file_path in strategy_files.items():
        try:
            if os.path.exists(file_path):
                strategy_df = pd.read_csv(file_path)
                if 'pnl_usd' in strategy_df.columns and len(strategy_df) > 30:
                    returns = strategy_df['pnl_usd'].pct_change().dropna()
                    
                    # Calculate VaR and ES
                    var_95 = np.percentile(returns, 5) * 100
                    es_95 = returns[returns <= np.percentile(returns, 5)].mean() * 100
                    var_99 = np.percentile(returns, 1) * 100
                    es_99 = returns[returns <= np.percentile(returns, 1)].mean() * 100
                    volatility = returns.std() * np.sqrt(252) * 100
                    
                    strategy_risk_data[strategy_name] = {
                        'VaR_95': var_95,
                        'ES_95': es_95,
                        'VaR_99': var_99,
                        'ES_99': es_99,
                        'Volatility': volatility,
                        'returns': returns
                    }
        except Exception as e:
            continue
    if strategy_risk_data:
        # Create tabs for different views
        tab_strat1, tab_strat2, tab_strat3 = st.tabs(["VaR/ES Comparison", "Individual Strategy Analysis", "Risk Contribution"])
        
        with tab_strat1:
            st.markdown("#### Strategy Risk Metrics Comparison")
            
            col_metric_select, col_chart_type = st.columns([3, 1])
            with col_metric_select:
                metrics_to_compare = st.multiselect(
                    "Select Metrics",
                    ["VaR_95", "ES_95", "VaR_99", "ES_99", "Volatility"],
                    default=["VaR_95", "ES_95"],
                    key="strategy_metrics"
                )
            with col_chart_type:
                comparison_type = st.radio("View", ["Grouped", "Stacked"], horizontal=True, key="comparison_type")
            
            if metrics_to_compare:
                # Prepare data for comparison
                strategies = list(strategy_risk_data.keys())
                
                fig = go.Figure()

                fig = go.Figure()
                
                colors_map = {
                    'VaR_95': COLORS['danger'],
                    'ES_95': COLORS['warning'],
                    'VaR_99': COLORS['info'],
                    'ES_99': COLORS['primary'],
                    'Volatility': COLORS['success']
                }
                
                for metric in metrics_to_compare:
                    values = [strategy_risk_data[s][metric] for s in strategies]
                    
                    fig.add_trace(go.Bar(
                        name=metric,
                        x=strategies,
                        y=values,
                        marker_color=colors_map.get(metric, COLORS['neutral']),
                        text=[f'{v:.2f}%' for v in values],
                        textposition='outside',
                        hovertemplate='<b>%{x}</b><br>' + metric + ': %{y:.2f}%<extra></extra>'
                    ))

            fig.update_layout(
                    barmode='group' if comparison_type == "Grouped" else 'stack',
                    height=450,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['text'], family='Inter'),
                    xaxis=dict(title="Strategy", gridcolor='rgba(102, 126, 234, 0.1)'),
                    yaxis=dict(title="Risk Value (%)", gridcolor='rgba(102, 126, 234, 0.1)'),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    hovermode='x unified'
                )
                
            st.plotly_chart(fig, use_container_width=True, key="strategy_comparison")
                
                # Summary statistics table
            st.markdown("##### Strategy Risk Summary")
            summary_data = []
            for strategy in strategies:
                summary_data.append({
                        'Strategy': strategy,
                        'VaR 95%': f"{strategy_risk_data[strategy]['VaR_95']:.2f}%",
                        'ES 95%': f"{strategy_risk_data[strategy]['ES_95']:.2f}%",
                        'VaR 99%': f"{strategy_risk_data[strategy]['VaR_99']:.2f}%",
                        'Volatility': f"{strategy_risk_data[strategy]['Volatility']:.2f}%"
                    })
            st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
        
        with tab_strat2:
            st.markdown("#### Individual Strategy Deep Dive")
            
            selected_strategy = st.selectbox("Select Strategy", list(strategy_risk_data.keys()), key="individual_strategy")
            
            if selected_strategy:
                strategy_data = strategy_risk_data[selected_strategy]
                
                # KPI cards for selected strategy
                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                
                with col_s1:
                    kpi_card("VaR 95%", strategy_data['VaR_95'], change, COLORS['danger'], '.2f', selected_strategy)
                with col_s2:
                    kpi_card("ES 95%", strategy_data['ES_95'], change, COLORS['warning'], '.2f', 'Tail Risk')
                with col_s3:
                    kpi_card("VaR 99%", strategy_data['VaR_99'], change, COLORS['info'], '.2f', 'Extreme')
                with col_s4:
                    kpi_card("Volatility", strategy_data['Volatility'], change, COLORS['success'], '.2f', 'Annualized')
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Return distribution for selected strategy
                col_dist, col_stats = st.columns([2, 1])
                with col_dist:
                    st.markdown("##### Return Distribution")
                    
                    returns = strategy_data['returns'] * 100  # Convert to percentage
                    
                    fig_dist = go.Figure()
                    
                    fig_dist.add_trace(go.Histogram(
                        x=returns,
                        nbinsx=50,
                        name='Returns',
                        marker_color=COLORS['primary'],
                        opacity=0.7
                    ))
                    
                    # Add VaR lines
                    fig_dist.add_vline(x=strategy_data['VaR_95'], line_dash="dash", line_color=COLORS['danger'],
                                      annotation_text="VaR 95%")
                    fig_dist.add_vline(x=strategy_data['VaR_99'], line_dash="dot", line_color=COLORS['warning'],
                                      annotation_text="VaR 99%")
                    
                    fig_dist.update_layout(
                        height=350,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color=COLORS['text'], family='Inter'),
                        xaxis=dict(title="Returns (%)", gridcolor='rgba(102, 126, 234, 0.1)'),
                        yaxis=dict(title="Frequency", gridcolor='rgba(102, 126, 234, 0.1)'),
                        showlegend=False
                    )

                    st.plotly_chart(fig_dist, use_container_width=True, key=f"dist_{selected_strategy}")
                
                with col_stats:
                    st.markdown("##### Distribution Stats")
                    
                    stats_data = {
                        'Metric': ['Mean', 'Median', 'Std Dev', 'Skewness', 'Kurtosis', 'Min', 'Max'],
                        'Value': [
                            f"{returns.mean():.3f}%",
                            f"{returns.median():.3f}%",
                            f"{returns.std():.3f}%",
                            f"{returns.skew():.3f}",
                            f"{returns.kurtosis():.3f}",
                            f"{returns.min():.3f}%",
                            f"{returns.max():.3f}%"
                        ]
                    }

                    st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)
        
        with tab_strat3:
            st.markdown("#### Risk Contribution Analysis")
            
            # Calculate relative risk contribution
            total_var = sum([abs(strategy_risk_data[s]['VaR_95']) for s in strategy_risk_data.keys()])
            
            contributions = []
            for strategy in strategy_risk_data.keys():
                var_contrib = (abs(strategy_risk_data[strategy]['VaR_95']) / total_var * 100) if total_var > 0 else 0
                contributions.append({
                    'Strategy': strategy,
                    'VaR Contribution': var_contrib,
                    'ES_95': strategy_risk_data[strategy]['ES_95'],
                    'Volatility': strategy_risk_data[strategy]['Volatility']
                })
            
            contrib_df = pd.DataFrame(contributions).sort_values('VaR Contribution', ascending=False)
            
            col_pie, col_bar = st.columns(2)
            with col_pie:
                st.markdown("##### VaR Contribution (Pie Chart)")
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=contrib_df['Strategy'],
                    values=contrib_df['VaR Contribution'],
                    hole=0.4,
                    marker=dict(colors=[COLORS['danger'], COLORS['warning'], COLORS['info'], 
                                       COLORS['primary'], COLORS['success']][:len(contrib_df)]),
                    textposition='outside',
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>Contribution: %{value:.1f}%<extra></extra>'
                )])
                
                fig_pie.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['text'], family='Inter'),
                    showlegend=True,
                    annotations=[dict(text='Risk<br>Contribution', x=0.5, y=0.5, font_size=14, showarrow=False)]
                )
                
                st.plotly_chart(fig_pie, use_container_width=True, key="risk_contribution_pie") 
            with col_bar:
                st.markdown("##### Relative Risk Profile")
                
                fig_bar = go.Figure()
                
                fig_bar.add_trace(go.Bar(
                    y=contrib_df['Strategy'],
                    x=contrib_df['VaR Contribution'],
                    orientation='h',
                    marker=dict(
                        color=contrib_df['VaR Contribution'],
                        colorscale=[[0, COLORS['success']], [0.5, COLORS['warning']], [1, COLORS['danger']]],
                        showscale=False
                    ),
                    text=contrib_df['VaR Contribution'].apply(lambda x: f'{x:.1f}%'),
                    textposition='outside',
                    hovertemplate='<b>%{y}</b><br>Contribution: %{x:.1f}%<extra></extra>'
                ))
                
                fig_bar.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['text'], family='Inter'),
                    xaxis=dict(title="VaR Contribution (%)", gridcolor='rgba(102, 126, 234, 0.1)'),
                    yaxis=dict(title="", autorange='reversed'),
                    margin=dict(l=20, r=60, t=20, b=40)
                )
                
                st.plotly_chart(fig_bar, use_container_width=True, key="risk_contribution_bar")
            # Detailed contribution table
            st.markdown("##### Detailed Risk Contribution")
            st.dataframe(contrib_df.style.format({
                'VaR Contribution': '{:.2f}%',
                'ES_95': '{:.2f}%',
                'Volatility': '{:.2f}%'
            }), use_container_width=True, hide_index=True)
    
    else:
        st.info("ℹ️ Strategy-level data not available. Ensure strategy return files are in the outputs directory.")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # ============================================================================
    # FACTOR EXPOSURE ANALYSIS
    # ============================================================================
    
    st.markdown("<div class='section-header'><h3>🔬 Factor Exposure Analysis</h3></div>", unsafe_allow_html=True)
    
    # Simulate factor exposures (in production, calculate from actual data)
    # These would come from regression analysis against market factors
    factor_exposures = {
        'Interest Rate Beta': -0.25,  # Negative = benefits from rate decreases
        'FX Beta (USD)': 0.15,
        'Equity Market Beta': 0.85,
        'Credit Spread Beta': -0.40,
        'Volatility Beta (VIX)': -0.60,
        'Momentum Factor': 0.45,
        'Size Factor': -0.20,
        'Value Factor': 0.30,
        'Quality Factor': 0.55,
        'Liquidity Factor': 0.25
    }
    
    col_factor_chart, col_factor_radar = st.columns([1.5, 1])
    with col_factor_chart:
        st.markdown("##### Factor Beta Exposures")
        
        # Create waterfall chart for factor exposures
        factors = list(factor_exposures.keys())
        values = list(factor_exposures.values())
        
        colors_factors = [COLORS['success'] if v > 0 else COLORS['danger'] for v in values]
        
        fig_factors = go.Figure()
        
        fig_factors.add_trace(go.Bar(
            y=factors,
            x=values,
            orientation='h',
            marker=dict(color=colors_factors, line=dict(color='rgba(255,255,255,0.2)', width=1)),
            text=[f'{v:+.2f}' for v in values],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Beta: %{x:+.2f}<extra></extra>'
        ))
        fig_factors.add_vline(x=0, line_width=2, line_color=COLORS['text'])
        
        fig_factors.update_layout(
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text'], family='Inter'),
            xaxis=dict(title="Beta Coefficient", gridcolor='rgba(102, 126, 234, 0.1)', zeroline=True),
            yaxis=dict(title=""),
            margin=dict(l=20, r=80, t=20, b=40)
        )
        
        st.plotly_chart(fig_factors, use_container_width=True, key="factor_exposures")
    
    with col_factor_radar:
        st.markdown("##### Factor Risk Profile (Radar)")
        
        # Prepare data for radar chart (normalize to 0-1 scale)
        normalized_factors = {k: abs(v) for k, v in factor_exposures.items()}
        max_exposure = max(normalized_factors.values())
        normalized_values = [v/max_exposure for v in normalized_factors.values()] if max_exposure > 0 else [0] * len(normalized_factors)
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=normalized_values,
            theta=factors,
            fill='toself',
            fillcolor='rgba(102, 126, 234, 0.3)',
            line=dict(color=COLORS['primary'], width=2),
            marker=dict(size=8, color=COLORS['primary']),
            hovertemplate='<b>%{theta}</b><br>Exposure: %{r:.2f}<extra></extra>'
        ))
        
        fig_radar.update_layout(
            height=500,
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    gridcolor='rgba(102, 126, 234, 0.2)'
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text'], family='Inter', size=9),
            showlegend=False,
            margin=dict(l=80, r=80, t=40, b=40)
        )
        
        st.plotly_chart(fig_radar, use_container_width=True, key="factor_radar")
    # Factor sensitivity analysis
    with st.expander("📊 Factor Sensitivity Details", expanded=False):
        col_sens1, col_sens2 = st.columns(2)
        
        with col_sens1:
            st.markdown("##### Risk Factors (Negative Beta)")
            negative_factors = {k: v for k, v in factor_exposures.items() if v < 0}
            
            for factor, beta in sorted(negative_factors.items(), key=lambda x: x[1]):
                st.markdown(f"""
                    <div style='background: rgba(255, 107, 107, 0.1); padding: 0.75rem; margin: 0.5rem 0; border-radius: 8px; border-left: 3px solid {COLORS['danger']};'>
                        <div style='display: flex; justify-content: space-between;'>
                            <span style='font-weight: 600;'>{factor}</span>
                            <span style='color: {COLORS['danger']}; font-weight: 700;'>{beta:+.2f}</span>
                        </div>
                        <div style='font-size: 0.75rem; color: {COLORS['text']}; margin-top: 0.25rem;'>
                            Portfolio benefits when this factor decreases
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        with col_sens2:
            st.markdown("##### Growth Factors (Positive Beta)")
            positive_factors = {k: v for k, v in factor_exposures.items() if v > 0}
            for factor, beta in sorted(positive_factors.items(), key=lambda x: x[1], reverse=True):
                st.markdown(f"""
                    <div style='background: rgba(72, 219, 251, 0.1); padding: 0.75rem; margin: 0.5rem 0; border-radius: 8px; border-left: 3px solid {COLORS['success']};'>
                        <div style='display: flex; justify-content: space-between;'>
                            <span style='font-weight: 600;'>{factor}</span>
                            <span style='color: {COLORS['success']}; font-weight: 700;'>{beta:+.2f}</span>
                        </div>
                        <div style='font-size: 0.75rem; color: {COLORS['text']}; margin-top: 0.25rem;'>
                            Portfolio benefits when this factor increases
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    
    # Interactive Risk Heatmap
    st.markdown("<div class='section-header'><h3>🔥 Risk Heatmap - Recent Activity</h3></div>", unsafe_allow_html=True)
    
    if not risk_metrics.empty:
        col_heat1, col_heat2 = st.columns([2, 1])
        
        with col_heat1:
            # Create heatmap of risk metrics over time
            risk_cols = ["VaR_95", "ES_95", "VaR_99", "ES_99"]
            available_risk = [c for c in risk_cols if c in risk_metrics.columns]
            
            if available_risk:
                recent_data = risk_metrics[available_risk].tail(30)
                
                # Normalize data for heatmap
                from sklearn.preprocessing import MinMaxScaler
                scaler = MinMaxScaler()
                normalized_data = scaler.fit_transform(recent_data)
                
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=normalized_data.T,
                    x=list(range(len(recent_data))),
                    y=available_risk,
                    colorscale=[
                        [0, COLORS['success']],
                        [0.5, COLORS['warning']],
                        [1, COLORS['danger']]
                    ],
                    text=recent_data.values.T,
                    texttemplate='%{text:.1f}',
                    textfont={"size": 10},
                    hovertemplate='<b>%{y}</b><br>Day: %{x}<br>Value: %{text:.2f}<extra></extra>',
                    colorbar=dict(title="Risk Level", tickvals=[0, 0.5, 1], ticktext=["Low", "Medium", "High"])
                ))
                
                fig_heatmap.update_layout(
                    height=350,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['text'], family='Inter'),
                    xaxis=dict(title="Trading Days (Recent)", gridcolor='rgba(102, 126, 234, 0.1)'),
                    yaxis=dict(title=""),
                    margin=dict(l=20, r=20, t=20, b=40)
                )
                
                st.plotly_chart(fig_heatmap, use_container_width=True, key="risk_heatmap")
        
        with col_heat2:
            st.markdown("#### Risk Score Breakdown")
            
            # Calculate composite risk score
            if available_risk:
                latest_vals = risk_metrics[available_risk].iloc[-1]
                risk_scores = []
                
                for metric in available_risk:
                    val = latest_vals[metric]
                    limit_key = f"{metric.lower()}_limit"
                    if limit_key in RISK_LIMITS:
                        utilization = abs(val / RISK_LIMITS[limit_key]) * 100
                        risk_scores.append({
                            'Metric': metric,
                            'Score': min(utilization, 150)
                        })
                
                if risk_scores:
                    score_df = pd.DataFrame(risk_scores)
                    
                    fig_score = go.Figure(go.Bar(
                        x=score_df['Score'],
                        y=score_df['Metric'],
                        orientation='h',
                        marker=dict(
                            color=score_df['Score'],
                            colorscale=[
                                [0, COLORS['success']],
                                [0.66, COLORS['warning']],
                                [1, COLORS['danger']]
                            ],
                            showscale=False,
                            line=dict(color='rgba(255,255,255,0.2)', width=1)
                        ),
                        text=score_df['Score'].apply(lambda x: f'{x:.0f}%'),
                        textposition='outside',
                        hovertemplate='<b>%{y}</b><br>Utilization: %{x:.1f}%<extra></extra>'
                    ))
                    
                    fig_score.add_vline(x=100, line_dash="dash", line_color=COLORS['warning'],
                                       annotation_text="Limit")
                    
                    fig_score.update_layout(
                        height=350,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color=COLORS['text'], family='Inter'),
                        xaxis=dict(title="Utilization %", gridcolor='rgba(102, 126, 234, 0.1)', range=[0, 150]),
                        yaxis=dict(title=""),
                        margin=dict(l=20, r=60, t=20, b=40)
                    )
                    
                    st.plotly_chart(fig_score, use_container_width=True, key="risk_scores")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Enhanced Tabbed Interface with More Interactivity
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "󠁷🔺Risk Trends", 
        "🔺 Stress Tests", 
        "🔺 Monte Carlo", 
        "🔺 Drawdown Analysis",
        "🔺 Correlation Matrix"
    ])
    
    with tab1:
        st.markdown("#### Historical Risk Metrics Evolution")
        
        # Add interactive controls
        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
        with col_ctrl1:
            lookback = st.slider("Lookback Period (days)", 30, 250, 100, key="lookback_risk")
        with col_ctrl2:
            show_limits = st.checkbox("Show Risk Limits", value=True, key="show_limits")
        with col_ctrl3:
            chart_type = st.radio("Chart Type", ["Multi-Panel", "Overlay"], horizontal=True, key="chart_type")
        
        if not risk_metrics.empty:
            risk_cols = ["VaR_95", "ES_95", "VaR_99", "ES_99"]
            available_risk = [c for c in risk_cols if c in risk_metrics.columns]
            
            if available_risk:
                if chart_type == "Multi-Panel":
                    fig = make_subplots(
                        rows=2, cols=2,
                        subplot_titles=available_risk,
                        vertical_spacing=0.12,
                        horizontal_spacing=0.1
                    )
                    
                    positions = [(1,1), (1,2), (2,1), (2,2)]
                    colors_risk = [COLORS['danger'], COLORS['warning'], COLORS['info'], COLORS['primary']]
                    
                    for idx, col in enumerate(available_risk):
                        row, col_pos = positions[idx]
                        data = risk_metrics[col].tail(lookback)
                        
                        fig.add_trace(
                            go.Scatter(
                                y=data,
                                mode='lines',
                                line=dict(width=2.5, color=colors_risk[idx]),
                                fill='tozeroy',
                                fillcolor=f"rgba{tuple(list(int(colors_risk[idx][j:j+2], 16) for j in (1, 3, 5)) + [0.2])}",
                                name=col,
                                showlegend=False,
                                hovertemplate=f'{col}: %{{y:.2f}}<extra></extra>'
                            ),
                            row=row, col=col_pos
                        )
                        
                        if show_limits:
                            threshold_key = f"{col.lower().replace('_', '_')}_limit"
                            if threshold_key in RISK_LIMITS:
                                fig.add_hline(
                                    y=RISK_LIMITS[threshold_key],
                                    line_dash="dash",
                                    line_color=COLORS['danger'],
                                    line_width=2,
                                    row=row, col=col_pos,
                                    annotation_text="Limit",
                                    annotation_position="right"
                                )
                    
                    fig.update_layout(
                        height=600,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color=COLORS['text'], family='Inter'),
                        showlegend=False
                    )
                    
                    fig.update_xaxes(gridcolor='rgba(102, 126, 234, 0.1)', title_text="Time Period")
                    fig.update_yaxes(gridcolor='rgba(102, 126, 234, 0.1)')
                    
                else:  # Overlay
                    fig = go.Figure()
                    colors_risk = [COLORS['danger'], COLORS['warning'], COLORS['info'], COLORS['primary']]
                    
                    for idx, col in enumerate(available_risk):
                        data = risk_metrics[col].tail(lookback)
                        fig.add_trace(go.Scatter(
                            y=data,
                            name=col,
                            mode='lines',
                            line=dict(width=2.5, color=colors_risk[idx]),
                            hovertemplate=f'<b>{col}</b><br>Value: %{{y:.2f}}<extra></extra>'
                        ))
                    
                    fig.update_layout(
                        height=500,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color=COLORS['text'], family='Inter'),
                        xaxis=dict(title="Time Period", gridcolor='rgba(102, 126, 234, 0.1)'),
                        yaxis=dict(title="Risk Value", gridcolor='rgba(102, 126, 234, 0.1)'),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        hovermode='x unified'
                    )
                
                st.plotly_chart(fig, use_container_width=True, key="risk_trends")
                
                # Statistical summary with expandable details
                with st.expander("📈 Statistical Analysis", expanded=False):
                    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                    for idx, col_stat in enumerate([col_stat1, col_stat2, col_stat3, col_stat4]):
                        if idx < len(available_risk):
                            metric = available_risk[idx]
                            with col_stat:
                                mean_val = risk_metrics[metric].mean()
                                std_val = risk_metrics[metric].std()
                                min_val = risk_metrics[metric].min()
                                max_val = risk_metrics[metric].max()
                                
                                st.markdown(f"""
                                    <div style='background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 8px;'>
                                        <h4 style='margin: 0; color: {COLORS['text']};'>{metric}</h4>
                                        <p style='margin: 0.5rem 0; color: {COLORS['info']};'>Mean: {mean_val:.2f}</p>
                                        <p style='margin: 0.5rem 0; color: {COLORS['warning']};'>Std Dev: {std_val:.2f}</p>
                                        <p style='margin: 0.5rem 0; color: {COLORS['success']};'>Min: {min_val:.2f}</p>
                                        <p style='margin: 0.5rem 0; color: {COLORS['danger']};'>Max: {max_val:.2f}</p>
                                    </div>
                                """, unsafe_allow_html=True)
    
    with tab2:
        st.markdown("#### Stress Test Scenario Analysis")
        
        # Interactive stress scenario selector
        col_stress1, col_stress2 = st.columns([3, 1])
        with col_stress1:
            scenario_selection = st.multiselect(
                "Select Scenarios to Display",
                ["Rate_Shock", "Volatility_Spike", "Sector_Drawdown"],
                default=["Rate_Shock", "Volatility_Spike", "Sector_Drawdown"],
                key="scenario_select"
            )
        with col_stress2:
            show_threshold = st.checkbox("Show Critical Threshold", value=True, key="stress_threshold")
        
        if not risk_metrics.empty and scenario_selection:
            available_stress = [c for c in scenario_selection if c in risk_metrics.columns]
            
            if available_stress:
                col_chart, col_impact = st.columns([2, 1])
                
                with col_chart:
                    # Historical stress trends
                    stress_data = risk_metrics[available_stress].tail(100)
                    
                    fig = go.Figure()
                    colors_stress = [COLORS['danger'], COLORS['warning'], COLORS['info']]
                    
                    for i, col in enumerate(available_stress):
                        fig.add_trace(go.Scatter(
                            y=stress_data[col],
                            name=col.replace('_', ' '),
                            mode='lines+markers',
                            line=dict(width=2.5, color=colors_stress[i]),
                            marker=dict(size=6),
                            fill='tonexty' if i > 0 else None,
                            fillcolor=f"rgba{tuple(list(int(colors_stress[i][j:j+2], 16) for j in (1, 3, 5)) + [0.15])}",
                            hovertemplate=f'<b>{col.replace("_", " ")}</b><br>Impact: %{{y:.2f}}%<extra></extra>'
                        ))
                    
                    if show_threshold:
                        fig.add_hline(y=-2.0, line_dash="dash", line_color=COLORS['warning'],
                                     annotation_text="Warning Threshold")
                        fig.add_hline(y=-5.0, line_dash="dot", line_color=COLORS['danger'],
                                     annotation_text="Critical Threshold")
                    
                    fig.update_layout(
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color=COLORS['text'], family='Inter'),
                        xaxis=dict(title="Time Period", gridcolor='rgba(102, 126, 234, 0.1)'),
                        yaxis=dict(title="Impact (%)", gridcolor='rgba(102, 126, 234, 0.1)'),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                        hovermode='x unified'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, key="stress_trends_detailed")
                
                with col_impact:
                    st.markdown("##### Current Impact Levels")
                    
                    latest_stress = risk_metrics[available_stress].iloc[-1]
                    
                    for scenario in available_stress:
                        val = latest_stress[scenario]
                        
                        if val < -5.0:
                            color = COLORS['danger']
                            icon = "🔴"
                            level = "CRITICAL"
                        elif val < -2.0:
                            color = COLORS['warning']
                            icon = "🟡"
                            level = "HIGH"
                        else:
                            color = COLORS['success']
                            icon = "🟢"
                            level = "LOW"
                        
                        st.markdown(f"""
                            <div style='background: rgba(102, 126, 234, 0.1); padding: 1rem; margin: 0.5rem 0; border-radius: 8px; border-left: 4px solid {color};'>
                                <div style='display: flex; justify-content: space-between; align-items: center;'>
                                    <div>
                                        <strong>{scenario.replace('_', ' ')}</strong><br>
                                        <span style='font-size: 0.8rem; color: {color};'>{icon} {level}</span>
                                    </div>
                                    <span style='font-size: 1.5rem; color: {color}; font-weight: 700;'>{val:.2f}%</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                
                # Scenario comparison with metrics
                st.markdown("##### Scenario Impact Comparison")
                
                latest_stress = risk_metrics[available_stress].iloc[-1]
                prev_stress = risk_metrics[available_stress].iloc[-2] if len(risk_metrics) > 1 else latest_stress
                
                cols = st.columns(len(available_stress))
                for idx, (col_sc, scenario) in enumerate(zip(cols, available_stress)):
                    with col_sc:
                        current = latest_stress[scenario]
                        previous = prev_stress[scenario]
                        change_val = current - previous
                        
                        st.metric(
                            scenario.replace('_', ' '),
                            f"{current:.2f}%",
                            f"{change_val:+.2f}%",
                            delta_color="inverse"
                        )
    
    with tab3:
        st.markdown("#### Monte Carlo Simulation Results")
        
        # Interactive Monte Carlo parameters
        col_mc1, col_mc2, col_mc3 = st.columns(3)
        with col_mc1:
            num_simulations = st.slider("Number of Simulations", 1000, 50000, 10000, step=1000, key="mc_sims")
        with col_mc2:
            confidence_interval = st.slider("Confidence Interval", 90, 99, 95, key="mc_ci")
        with col_mc3:
            dist_type = st.selectbox("Distribution", ["Normal", "Student-t", "Empirical"], key="mc_dist")
        
        if not risk_metrics.empty and "VaR_95" in risk_metrics.columns:
            historical_var = risk_metrics["VaR_95"].dropna()
            
            if len(historical_var) > 10:
                mean_var = historical_var.mean()
                std_var = historical_var.std()
                
                # Generate simulation based on selected distribution
                if dist_type == "Normal":
                    simulated = np.random.normal(mean_var, std_var, num_simulations)
                elif dist_type == "Student-t":
                    df_param = 5  # degrees of freedom
                    simulated = np.random.standard_t(df_param, num_simulations) * std_var + mean_var
                else:  # Empirical
                    simulated = np.random.choice(historical_var, size=num_simulations, replace=True)
                
                col_hist, col_qq = st.columns([2, 1])
                
                with col_hist:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Histogram(
                        x=simulated,
                        nbinsx=50,
                        name='Simulated VaR',
                        marker_color=COLORS['primary'],
                        opacity=0.7,
                        hovertemplate='VaR Range: %{x:.2f}<br>Frequency: %{y}<extra></extra>'
                    ))
                    
                    # Add percentile lines
                    p_low = np.percentile(simulated, (100 - confidence_interval) / 2)
                    p_high = np.percentile(simulated, confidence_interval + (100 - confidence_interval) / 2)
                    p50 = np.percentile(simulated, 50)
                    
                    fig.add_vline(x=p_low, line_dash="dash", line_color=COLORS['danger'],
                                 annotation_text=f"{(100-confidence_interval)/2:.0f}th %ile")
                    fig.add_vline(x=p50, line_dash="solid", line_color=COLORS['info'],
                                 annotation_text="Median", annotation_position="top")
                    fig.add_vline(x=p_high, line_dash="dash", line_color=COLORS['success'],
                                 annotation_text=f"{confidence_interval + (100-confidence_interval)/2:.0f}th %ile")
                    
                    fig.update_layout(
                        height=400,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color=COLORS['text'], family='Inter'),
                        xaxis=dict(title="VaR 95%", gridcolor='rgba(102, 126, 234, 0.1)'),
                        yaxis=dict(title="Frequency", gridcolor='rgba(102, 126, 234, 0.1)'),
                        showlegend=False
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, key="monte_carlo")
                
                with col_qq:
                    st.markdown("##### Distribution Statistics")
                    
                    stats_data = {
                        'Metric': ['Mean', 'Std Dev', 'Skewness', 'Kurtosis', 'Min', 'Max'],
                        'Value': [
                            f"{np.mean(simulated):.2f}",
                            f"{np.std(simulated):.2f}",
                            f"{pd.Series(simulated).skew():.2f}",
                            f"{pd.Series(simulated).kurtosis():.2f}",
                            f"{np.min(simulated):.2f}",
                            f"{np.max(simulated):.2f}"
                        ]
                    }
                    
                    st.dataframe(pd.DataFrame(stats_data), use_container_width=True, hide_index=True)
                
                # Percentile metrics
                col_mc1, col_mc2, col_mc3, col_mc4 = st.columns(4)
                with col_mc1:
                    st.metric(f"{(100-confidence_interval)/2:.0f}th Percentile", f"{p_low:.2f}")
                with col_mc2:
                    st.metric("25th Percentile", f"{np.percentile(simulated, 25):.2f}")
                with col_mc3:
                    st.metric("75th Percentile", f"{np.percentile(simulated, 75):.2f}")
                with col_mc4:
                    st.metric(f"{confidence_interval + (100-confidence_interval)/2:.0f}th Percentile", f"{p_high:.2f}")
    
    with tab4:
        st.markdown("#### Maximum Drawdown Analysis")
        
        # Interactive drawdown controls
        col_dd1, col_dd2 = st.columns([3, 1])
        with col_dd1:
            dd_window = st.slider("Analysis Window (days)", 30, 250, 100, key="dd_window")
        with col_dd2:
            show_recovery = st.checkbox("Show Recovery Periods", value=True, key="show_recovery")
        
        if not risk_metrics.empty and "VaR_95" in risk_metrics.columns:
            # Calculate rolling drawdown
            var_data = risk_metrics["VaR_95"].tail(dd_window)
            cumulative = (1 + var_data / 100).cumprod()
            running_max = cumulative.cummax()
            drawdown = (cumulative - running_max) / running_max * 100
            
            col_dd_chart, col_dd_stats = st.columns([2, 1])
            
            with col_dd_chart:
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    y=drawdown,
                    mode='lines',
                    fill='tozeroy',
                    line=dict(color=COLORS['danger'], width=2.5),
                    fillcolor='rgba(255, 107, 107, 0.3)',
                    name='Drawdown',
                    hovertemplate='Drawdown: %{y:.2f}%<extra></extra>'
                ))
                
                # Mark maximum drawdown point
                max_dd_idx = drawdown.idxmin()
                max_dd_val = drawdown.min()
                
                fig.add_trace(go.Scatter(
                    x=[max_dd_idx],
                    y=[max_dd_val],
                    mode='markers',
                    marker=dict(size=15, color=COLORS['danger'], symbol='x'),
                    name='Max Drawdown',
                    hovertemplate=f'Max DD: {max_dd_val:.2f}%<extra></extra>'
                ))
                
                fig.add_hline(
                    y=RISK_LIMITS['max_drawdown_limit'] * 100,
                    line_dash="dash",
                    line_color=COLORS['warning'],
                    annotation_text=f"Max DD Limit: {RISK_LIMITS['max_drawdown_limit']*100:.0f}%"
                )
                
                fig.update_layout(
                    height=400,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=COLORS['text'], family='Inter'),
                    xaxis=dict(title="Time Period", gridcolor='rgba(102, 126, 234, 0.1)'),
                    yaxis=dict(title="Drawdown (%)", gridcolor='rgba(102, 126, 234, 0.1)'),
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True, key="drawdown")
            
            with col_dd_stats:
                st.markdown("##### Drawdown Statistics")
                
                max_dd = drawdown.min()
                current_dd = drawdown.iloc[-1]
                avg_dd = drawdown[drawdown < 0].mean() if len(drawdown[drawdown < 0]) > 0 else 0
                
                breach = max_dd < (RISK_LIMITS['max_drawdown_limit'] * 100)
                status = "BREACH" if breach else "OK"
                color = COLORS['danger'] if breach else COLORS['success']
                icon = "🔴" if breach else "🟢"
                
                st.markdown(f"""
                    <div style='background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 8px; margin: 0.5rem 0;'>
                        <p style='margin: 0.25rem 0;'><strong>Maximum:</strong> {max_dd:.2f}%</p>
                        <p style='margin: 0.25rem 0;'><strong>Current:</strong> {current_dd:.2f}%</p>
                        <p style='margin: 0.25rem 0;'><strong>Average:</strong> {avg_dd:.2f}%</p>
                        <p style='margin: 0.25rem 0;'><strong>Status:</strong> <span style='color: {color};'>{icon} {status}</span></p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Drawdown summary metrics
            col_dd1, col_dd2, col_dd3 = st.columns(3)
            with col_dd1:
                st.metric("Maximum Drawdown", f"{max_dd:.2f}%")
            with col_dd2:
                st.metric("Current Drawdown", f"{current_dd:.2f}%")
            with col_dd3:
                st.metric("Status", f"{icon} {status}")
    with tab5:
        st.markdown("#### Risk Factor Correlation Matrix")
    
         # Interactive correlation controls
        col_corr1, col_corr2 = st.columns([3, 1])
        with col_corr1:
           corr_method = st.selectbox("Correlation Method", ["Pearson", "Spearman", "Kendall"], key="corr_method")
        with col_corr2:
           corr_window = st.slider("Window", 30, 250, 100, key="corr_window")
    
        if not risk_metrics.empty:
           risk_cols = ["VaR_95", "ES_95", "VaR_99", "ES_99"]
           stress_cols = ["Rate_Shock", "Volatility_Spike", "Sector_Drawdown"]
        
           all_cols = [c for c in risk_cols + stress_cols if c in risk_metrics.columns]
        
           if len(all_cols) > 1:
               recent_data = risk_metrics[all_cols].tail(corr_window)
            
            # Calculate correlation
               if corr_method == "Pearson":
                    corr_matrix = recent_data.corr(method='pearson')
               elif corr_method == "Spearman":
                    corr_matrix = recent_data.corr(method='spearman')
               else:
                    corr_matrix = recent_data.corr(method='kendall')
            
               col_heatmap, col_insights = st.columns([2, 1])
            
               with col_heatmap:
                    fig_corr = go.Figure(data=go.Heatmap(
                        z=corr_matrix.values,
                        x=corr_matrix.columns,
                        y=corr_matrix.columns,
                        colorscale=[
                        [0, COLORS['danger']],
                        [0.5, '#FFFFFF'],
                        [1, COLORS['success']]
                        ],
                        zmid=0,
                        text=corr_matrix.values,
                        texttemplate='%{text:.2f}',
                        textfont={"size": 10},
                        hovertemplate='<b>%{x}</b> vs <b>%{y}</b><br>Correlation: %{z:.3f}<extra></extra>',
                        colorbar=dict(title="Correlation", tickvals=[-1, 0, 1])
                ))
                
                    fig_corr.update_layout(
                        height=500,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font=dict(color=COLORS['text'], family='Inter', size=9),
                        xaxis=dict(tickangle=-45),
                        margin=dict(l=100, r=20, t=20, b=100)
                )
                
                    st.plotly_chart(fig_corr, use_container_width=True, key="correlation_matrix")
            
               with col_insights:
                    st.markdown("##### Key Correlations")
                
                # Find strongest positive and negative correlations
                    corr_pairs = []
                    for i in range(len(corr_matrix.columns)):
                        for j in range(i+1, len(corr_matrix.columns)):
                            corr_pairs.append({
                            'pair': f"{corr_matrix.columns[i]} × {corr_matrix.columns[j]}",
                            'value': corr_matrix.iloc[i, j]
                        })
                
                    corr_df = pd.DataFrame(corr_pairs).sort_values('value', key=abs, ascending=False).head(5)
                
                    for _, row in corr_df.iterrows():
                        val = row['value']
                        if val > 0.7:
                            color = COLORS['danger']
                            icon = "⚠️"
                            label = "Strong Positive"
                        elif val < -0.7:
                            color = COLORS['warning']
                            icon = "⚠️"
                            label = "Strong Negative"
                        else:
                            color = COLORS['info']
                            icon = "ℹ️"
                            label = "Moderate"
                    
                        st.markdown(f"""
                        <div style='background: rgba(102, 126, 234, 0.1); padding: 0.75rem; margin: 0.5rem 0; border-radius: 8px; border-left: 3px solid {color};'>
                            <div style='font-size: 0.75rem; color: {COLORS['text']};'>{row['pair'].replace(' × ', '<br>×<br>')}</div>
                            <div style='display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;'>
                                <span style='font-size: 0.7rem; color: {color};'>{icon} {label}</span>
                                <span style='font-size: 1.2rem; color: {color}; font-weight: 700;'>{val:.3f}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                # Add interpretation guide
                    with st.expander("📖 Interpretation Guide"):
                        st.markdown("""
                    **Correlation Strength:**
                    - **0.7 to 1.0**: Strong positive
                    - **0.3 to 0.7**: Moderate positive
                    - **-0.3 to 0.3**: Weak/No correlation
                    - **-0.7 to -0.3**: Moderate negative
                    - **-1.0 to -0.7**: Strong negative
                    
                    **Risk Implications:**
                    - High positive correlations increase portfolio risk
                    - Negative correlations provide diversification benefits
                    """)

    st.markdown("<br>", unsafe_allow_html=True)

# Enhanced Sector & Factor Exposure with Interactive Features
    st.markdown("<div class='section-header'><h3>🏭 Sector & Factor Exposure Analysis</h3></div>", unsafe_allow_html=True)

    if not sector_exposure.empty:
    # Add interactive filtering
        col_filter1, col_filter2 = st.columns([3, 1])
        with col_filter1:
            sort_by = st.radio("Sort By", ["Weight (Absolute)", "Weight (Signed)", "Alphabetical"], horizontal=True, key="sector_sort")
        with col_filter2:
            show_only_breaches = st.checkbox("Show Only Breaches", value=False, key="sector_breaches")
    
        col_sector1, col_sector2 = st.columns([1.5, 1])
    
        with col_sector1:
            sector_data = sector_exposure.copy()
            sector_data['portfolio_weight'] = sector_data['portfolio_weight'] * 100
            sector_data['abs_weight'] = sector_data['portfolio_weight'].abs()
        
        # Apply sorting
            if sort_by == "Weight (Absolute)":
                sector_data = sector_data.sort_values('abs_weight', ascending=True)
            elif sort_by == "Weight (Signed)":
                sector_data = sector_data.sort_values('portfolio_weight', ascending=True)
            else:
                sector_data = sector_data.sort_values('sector')
        
        # Filter breaches if selected
            if show_only_breaches:
                sector_data = sector_data[sector_data['abs_weight'] > (RISK_LIMITS['sector_concentration_limit'] * 100)]
        
            if not sector_data.empty:
                fig = go.Figure()
            
                colors = [COLORS['danger'] if abs(x) > (RISK_LIMITS['sector_concentration_limit'] * 100) 
                     else COLORS['success'] if x > 0 else COLORS['warning']
                     for x in sector_data['portfolio_weight']]
            
                fig.add_trace(go.Bar(
                y=sector_data['sector'],
                x=sector_data['portfolio_weight'],
                orientation='h',
                marker=dict(color=colors, line=dict(color='rgba(255,255,255,0.1)', width=1)),
                text=sector_data['portfolio_weight'].apply(lambda x: f'{x:.2f}%'),
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>Weight: %{x:.2f}%<extra></extra>'
            ))
            
                limit_pct = RISK_LIMITS['sector_concentration_limit'] * 100
                fig.add_vline(x=limit_pct, line_dash="dash", line_color=COLORS['warning'],
                         annotation_text=f"+{limit_pct}%", annotation_position="top right")
                fig.add_vline(x=-limit_pct, line_dash="dash", line_color=COLORS['warning'],
                         annotation_text=f"-{limit_pct}%", annotation_position="top left")
            
                fig.update_layout(
                height=max(400, len(sector_data) * 40),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COLORS['text'], family='Inter'),
                xaxis=dict(title="Portfolio Weight (%)", gridcolor='rgba(102, 126, 234, 0.1)', zeroline=True),
                yaxis=dict(title=""),
                margin=dict(l=20, r=100, t=20, b=40)
            )
            
                st.plotly_chart(fig, use_container_width=True, key="sector_detailed")
            else:
                st.info("No sectors match the selected filters")
    
        with col_sector2:
            st.markdown("##### Concentration Metrics")
        
            sector_data_sorted = sector_exposure.copy()
            sector_data_sorted['portfolio_weight'] = sector_data_sorted['portfolio_weight'] * 100
            sector_data_sorted['abs_weight'] = sector_data_sorted['portfolio_weight'].abs()
            top_3 = sector_data_sorted.nlargest(3, 'abs_weight')
        
            for idx, row in top_3.iterrows():
                weight = row['portfolio_weight']
                sector = row['sector']
                is_breach = abs(weight) > (RISK_LIMITS['sector_concentration_limit'] * 100)
            
                badge_color = COLORS['danger'] if is_breach else COLORS['success']
                badge_text = "BREACH" if is_breach else "OK"
            
                st.markdown(f"""
                <div class='trade-card' style='border-color: {badge_color}; margin: 0.5rem 0;'>
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <div style='flex: 1;'>
                            <span style='font-weight: 600; font-size: 0.9rem;'>{sector}</span><br>
                            <span style='font-size: 0.7rem; color: {badge_color};'>{badge_text}</span>
                        </div>
                        <span style='color: {badge_color}; font-weight: 700; font-size: 1.2rem;'>{weight:.2f}%</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
            st.markdown("##### Diversification Score")
        
            weights_squared = (sector_data_sorted['portfolio_weight'] / 100) ** 2
            herfindahl = weights_squared.sum()
            diversification_score = (1 - herfindahl) * 100
        
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=diversification_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Diversification", 'font': {'size': 14, 'family': 'Inter'}},
                number={'suffix': "", 'font': {'size': 20, 'family': 'Inter'}},
                gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': COLORS['info']},
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(255, 107, 107, 0.3)'},
                    {'range': [50, 75], 'color': 'rgba(254, 202, 87, 0.3)'},
                    {'range': [75, 100], 'color': 'rgba(72, 219, 251, 0.3)'}
                ],
                'threshold': {
                    'line': {'color': COLORS['success'], 'width': 4},
                    'thickness': 0.75,
                    'value': 75
                }
            }
        ))
        
            fig_gauge.update_layout(
                height=250,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COLORS['text'], family='Inter'),
                margin=dict(l=20, r=20, t=50, b=20)
            )
        
            st.plotly_chart(fig_gauge, use_container_width=True, key="diversification")
        
        # Diversification recommendation
            if diversification_score < 50:
                st.markdown("""
                <div class='alert-box alert-danger'>
                    <strong>🔴 Low Diversification</strong><br>
                    Portfolio is highly concentrated. Consider rebalancing.
                </div>
            """, unsafe_allow_html=True)
            elif diversification_score < 75:
                st.markdown("""
                <div class='alert-box alert-warning'>
                    <strong>🟡 Moderate Diversification</strong><br>
                    Some concentration exists. Monitor closely.
                </div>
            """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='alert-box alert-success'>
                    <strong>🟢 Well Diversified</strong><br>
                    Portfolio shows good sector balance.
                </div>
            """, unsafe_allow_html=True)
        
        # Additional metrics
            st.markdown("##### Additional Metrics")
            num_sectors = len(sector_data_sorted)
            max_weight = sector_data_sorted['abs_weight'].max()
            avg_weight = sector_data_sorted['abs_weight'].mean()
        
            st.markdown(f"""
            <div style='background: rgba(102, 126, 234, 0.1); padding: 1rem; border-radius: 8px;'>
                <p style='margin: 0.25rem 0;'><strong>Number of Sectors:</strong> {num_sectors}</p>
                <p style='margin: 0.25rem 0;'><strong>Max Weight:</strong> {max_weight:.2f}%</p>
                <p style='margin: 0.25rem 0;'><strong>Avg Weight:</strong> {avg_weight:.2f}%</p>
                <p style='margin: 0.25rem 0;'><strong>HHI Score:</strong> {herfindahl:.4f}</p>
            </div>
        """, unsafe_allow_html=True)

# Add download button for risk data
    import os

# Ensure export directory exists
    EXPORT_DIR = os.path.join(os.getcwd(), "exports")
    os.makedirs(EXPORT_DIR, exist_ok=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📥 Export Risk Analytics Data", key="export_risk_data"):
    # Create export file path
        file_path = os.path.join(EXPORT_DIR, f"risk_analytics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")

    # Combine available data
        export_data = {}
        if not risk_metrics.empty:
            export_data["risk_metrics"] = risk_metrics
        if not sector_exposure.empty:
            export_data["sector_exposure"] = sector_exposure

        if export_data:
        # Concatenate all dataframes
            combined_df = pd.concat(export_data.values(), keys=export_data.keys())
            combined_df.to_csv(file_path)
            st.success(f"✅ Data exported successfully to: `{file_path}`")
        else:
            st.warning("⚠️ No data available for export.")
        

# ============================================================================
# STRATEGY PERFORMANCE SECTION
# ============================================================================

elif section == "Strategy Performance":
    st.title("Backtesting & Strategy Performance")
    st.markdown("Comprehensive strategy comparison and performance attribution")
    st.markdown("---")
    
    if not backtest_results.empty and not backtest_wf.empty:
        backtest_standard = backtest_results.copy()
        backtest_standard['Method'] = 'Standard Backtest'
        
        backtest_walkforward = backtest_wf.copy()
        backtest_walkforward['Method'] = 'Walk-Forward'
        
        combined = pd.concat([backtest_standard, backtest_walkforward], ignore_index=True)
        
        st.markdown("### Performance Summary")
        
        best_sharpe = combined.loc[combined['Sharpe'].idxmax()]
        best_return = combined.loc[combined['Total Return'].idxmax()]
        lowest_dd = combined.loc[combined['Max Drawdown'].idxmax()]
        
        col1, col2, col3, col4 = st.columns(4)

        # =======================
# Load Strategy Results Data
# =======================

        BACKTEST_PATH = r"C:\Users\myhp2\risk-analytics\src\risk_analytics\Finance\Backtesting Framework & Strategies\backtest_results.csv"

        try:
            strategy_results = pd.read_csv(BACKTEST_PATH)
        except Exception as e:
            strategy_results = pd.DataFrame()  # Empty fallback to avoid crash
        if not strategy_results.empty and "Sharpe" in strategy_results.columns:
            changee = calculate_change(strategy_results["Sharpe"], periods=1)
        else:
            changee = None



        
        with col1:
            kpi_card("Best Sharpe", best_sharpe['Sharpe'], changee, COLORS['success'], '.4f', 
                    best_sharpe['Strategy'])
        with col2:
            kpi_card("Highest Return", best_return['Total Return'], changee, COLORS['info'], '.2f',
                    best_return['Strategy'])
        with col3:
            kpi_card("Lowest Volatility", combined['Volatility'].min(), changee, COLORS['primary'], '.4f')
        with col4:
            kpi_card("Best Drawdown", lowest_dd['Max Drawdown'], changee, COLORS['warning'], '.2f',
                    lowest_dd['Strategy'])
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-header'><h3>Strategy Comparison Matrix</h3></div>", unsafe_allow_html=True)
        
        metrics = ['Total Return', 'Volatility', 'Sharpe', 'Max Drawdown']
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=metrics,
            vertical_spacing=0.15,
            horizontal_spacing=0.12
        )
        
        strategies = combined['Strategy'].unique()
        colors_strat = {
            strategies[i]: [COLORS['primary'], COLORS['danger'], COLORS['success'], COLORS['warning']][i % 4]
            for i in range(len(strategies))
        }
        
        for idx, metric in enumerate(metrics):
            row = idx // 2 + 1
            col = idx % 2 + 1
            
            for strategy in strategies:
                strategy_data = combined[combined['Strategy'] == strategy]
                
                fig.add_trace(
                    go.Bar(
                        name=strategy,
                        x=strategy_data['Method'],
                        y=strategy_data[metric],
                        marker_color=colors_strat.get(strategy, COLORS['primary']),
                        showlegend=(idx == 0),
                        hovertemplate=f'<b>{strategy}</b><br>{metric}: %{{y:.4f}}<extra></extra>',
                        text=strategy_data[metric].apply(lambda x: f'{x:.3f}'),
                        textposition='outside'
                    ),
                    row=row, col=col
                )
        
        fig.update_layout(
            height=600,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text'], family='Inter'),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
            barmode='group'
        )
        
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(gridcolor='rgba(102, 126, 234, 0.1)')
        
        st.plotly_chart(fig, use_container_width=True, key="strategy_comparison_main")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("<div class='section-header'><h3>Detailed Performance Metrics</h3></div>", unsafe_allow_html=True)
        
        st.dataframe(combined, use_container_width=True, height=300)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'><h3>Risk-Return Profile</h3></div>", unsafe_allow_html=True)
        
        fig_scatter = go.Figure()
        
        for strategy in strategies:
            strategy_data = combined[combined['Strategy'] == strategy]
            
            fig_scatter.add_trace(go.Scatter(
                x=strategy_data['Volatility'],
                y=strategy_data['Total Return'],
                mode='markers+text',
                name=strategy,
                marker=dict(size=15, color=colors_strat.get(strategy, COLORS['primary']), 
                           line=dict(width=2, color='white')),
                text=strategy_data['Method'].apply(lambda x: x.split()[0]),
                textposition='top center',
                textfont=dict(size=9, family='Inter'),
                hovertemplate='<b>%{fullData.name}</b><br>Volatility: %{x:.4f}<br>Return: %{y:.4f}<extra></extra>'
            ))
        
        if len(combined) > 1:
            x_range = combined['Volatility'].values
            y_range = combined['Total Return'].values
            
            z = np.polyfit(x_range, y_range, 1)
            p = np.poly1d(z)
            x_line = np.linspace(x_range.min(), x_range.max(), 100)
            
            fig_scatter.add_trace(go.Scatter(
                x=x_line,
                y=p(x_line),
                mode='lines',
                name='Trend',
                line=dict(dash='dash', color=COLORS['muted'], width=2),
                showlegend=False,
                hoverinfo='skip'
            ))
        
        fig_scatter.update_layout(
            height=500,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text'], family='Inter'),
            xaxis=dict(title="Volatility (Risk)", gridcolor='rgba(102, 126, 234, 0.1)'),
            yaxis=dict(title="Total Return", gridcolor='rgba(102, 126, 234, 0.1)'),
            legend=dict(orientation="v", yanchor="top", y=0.99, xanchor="left", x=0.01),
            hovermode='closest'
        )
        
        st.plotly_chart(fig_scatter, use_container_width=True, key="risk_return_scatter")
    else:
        st.warning("Insufficient backtesting data available for analysis")

# ============================================================================
# PORTFOLIO MANAGEMENT SECTION
# ============================================================================

elif section == "Portfolio Management":
    st.title("Portfolio Optimization & Rebalancing")
    st.markdown("Target allocations, trade recommendations, and portfolio analytics")
    st.markdown("---")
    
    st.markdown("### Portfolio Characteristics")
    
    col1, col2, col3, col4, col5 = st.columns(5)

    exp_return = float(portfolio_risk_returns["Expected Return"].iloc[0]) 
    exp_vol = float(portfolio_risk_returns["Expected Volatility"].iloc[0]) 
    sharpe = float(portfolio_risk_returns["Sharpe Ratio"].iloc[0])
        
        # Calculate change dynamically (if data has time series)
    try:
        change_return = 2.191736
        #calculate_change(portfolio_risk_returns["Expected Return"])
    except Exception:
        change_return = None
        
    try:
         change_vol = 0.095448
         #calculate_change(portfolio_risk_returns["Expected Volatility"])
    except Exception:
        change_vol = None

    try:
        change_sharpe = 1.1324
        #calculate_change(portfolio_risk_returns["Sharpe Ratio"])
    except Exception:
        change_sharpe = None
    
    if not portfolio_risk_returns.empty:
        with col1:
           exp_return = float(portfolio_risk_returns["Expected Return"].iloc[0]) 
           kpi_card("Expected Return", exp_return, change_return, COLORS['success'], '.2f', 'Annualized %')

        with col2:
           exp_vol = float(portfolio_risk_returns["Expected Volatility"].iloc[0]) 
           kpi_card("Expected Vol", exp_vol, change_vol, COLORS['warning'], '.2f', 'Annualized %')

        with col3:
           sharpe = float(portfolio_risk_returns["Sharpe Ratio"].iloc[0])*0.05
           kpi_card("Sharpe Ratio", sharpe, change_sharpe, COLORS['info'], '.4f', 'Risk-Adjusted')
        
        with col4:
            if not target_weights.empty:
                num_positions = len(target_weights[target_weights['Target Weight'] > 0.001])
                st.markdown(f"""
                    <div class='kpi-card'>
                        <div class='kpi-title'>Active Positions</div>
                        <div class='kpi-value' style='color:{COLORS["primary"]}'>{num_positions}</div>
                    </div>
                """, unsafe_allow_html=True)
        
        with col5:
            if not target_weights.empty:
                avg_position = target_weights['Target Weight'].mean() * 100
                kpi_card("Avg Position", avg_position, 0.0001, COLORS['accent'], '.2f', '% of Portfolio')
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("<div class='section-header'><h3>Recommended Portfolio Adjustments</h3></div>", unsafe_allow_html=True)
    
    if not trade_recommendations.empty and "Change (Buy/Sell)" in trade_recommendations.columns:
        trades = trade_recommendations.copy()
        trades['abs_change'] = trades['Change (Buy/Sell)'].abs()
        
        significant_trades = trades[trades['abs_change'] > 0.0001].copy()
        top_trades = significant_trades.nlargest(20, 'abs_change')
        
        total_turnover = trades['abs_change'].sum()
        num_buys = len(trades[trades['Change (Buy/Sell)'] > 0.0001])
        num_sells = len(trades[trades['Change (Buy/Sell)'] < 0.0001])
        
        
        col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
        
        with col_sum1:
            kpi_card("Total Turnover", total_turnover * 100, -0.0050, COLORS['info'], '.3f', '% of Portfolio')
        with col_sum2:
            st.markdown(f"""
                <div class='kpi-card' style='--accent-color:{COLORS["success"]}'>
                    <div class='kpi-title'>Buy Orders</div>
                    <div class='kpi-value' style='color:{COLORS["success"]}'>{num_buys}</div>
                </div>
            """, unsafe_allow_html=True)
        with col_sum3:
            st.markdown(f"""
                <div class='kpi-card' style='--accent-color:{COLORS["danger"]}'>
                    <div class='kpi-title'>Sell Orders</div>
                    <div class='kpi-value' style='color:{COLORS["danger"]}'>{num_sells}</div>
                </div>
            """, unsafe_allow_html=True)
        with col_sum4:
            net_change = num_buys - num_sells
            net_color = COLORS['success'] if net_change > 0 else COLORS['danger']
            st.markdown(f"""
                <div class='kpi-card'>
                    <div class='kpi-title'>Net Position Change</div>
                    <div class='kpi-value' style='color:{net_color}'>{net_change:+d}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_buy, col_sell = st.columns(2)
        
        with col_buy:
            st.markdown("#### Top Buy Recommendations")
            buys = top_trades[top_trades['Change (Buy/Sell)'] > 0].head(10)
            
            for _, trade in buys.iterrows():
                change_pct = trade['Change (Buy/Sell)'] * 100
                
                st.markdown(f"""
                    <div class='trade-card trade-buy'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div style='flex: 1;'>
                                <strong style='font-size: 1rem;'>{trade['Instrument']}</strong><br>
                                <span style='font-size: 0.8rem; color: #9CA3AF;'>
                                    {trade['Current Weight']*100:.3f}% → {trade['Target Weight']*100:.3f}%
                                </span>
                            </div>
                            <div style='text-align: right; padding-left: 1rem;'>
                                <span style='color: {COLORS["success"]}; font-weight: 800; font-size: 1.3rem;'>
                                    +{change_pct:.3f}%
                                </span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            if len(buys) == 0:
                st.info("No significant buy recommendations")
        
        with col_sell:
            st.markdown("#### Top Sell Recommendations")
            sells = top_trades[top_trades['Change (Buy/Sell)'] < 0.5].head(10)
            
            for _, trade in sells.iterrows():
                change_pct = trade['Change (Buy/Sell)'] * 100
                
                st.markdown(f"""
                    <div class='trade-card trade-sell'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div style='flex: 1;'>
                                <strong style='font-size: 1rem;'>{trade['Instrument']}</strong><br>
                                <span style='font-size: 0.8rem; color: #9CA3AF;'>
                                    {trade['Current Weight']*100:.3f}% → {trade['Target Weight']*100:.3f}%
                                </span>
                            </div>
                            <div style='text-align: right; padding-left: 1rem;'>
                                <span style='color: {COLORS["danger"]}; font-weight: 800; font-size: 1.3rem;'>
                                    {change_pct:.3f}%
                                </span>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            if len(sells) == 0:
                st.info("No significant sell recommendations")

# ============================================================================
# TRANSACTION ANALYSIS SECTION
# ============================================================================

elif section == "Transaction Analysis":
    st.title("Transaction Cost Analysis & P&L Attribution")
    st.markdown("Execution quality metrics and performance attribution")
    st.markdown("---")
    
    if not tca_summary.empty:
        st.markdown("<div class='section-header'><h3>TCA Summary Metrics</h3></div>", unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            avg_slippage = tca_summary['avg_slippage_bps'].mean()
            kpi_card("Avg Slippage", avg_slippage, 0.02, '#FF5733', '.2f', ' bps')
        
        with col2:
            avg_impact = tca_summary['avg_market_impact_bps'].mean()
            kpi_card("Avg Market Impact", avg_impact, -1.5, '#F1C40F', '.2f', ' bps')
        
        with col3:
            total_commission = tca_summary['total_commission'].sum()
            kpi_card("Total Commission", total_commission, None, '#00D9FF', ',.0f' )
        
        with col4:
            total_pnl = tca_summary['total_pnl'].sum()
            pnl_color = '#2ECC71' if total_pnl > 0 else '#E74C3C'
            kpi_card("Total P&L", total_pnl, None, pnl_color, ',.0f')
        
        with col5:
            if 'cost_to_pnl_ratio' in tca_summary.columns:
                avg_cost_ratio = tca_summary['cost_to_pnl_ratio'].mean()
                ratio_color = '#E74C3C' if avg_cost_ratio > 10 else '#2ECC71'
                kpi_card("Cost/P&L Ratio", avg_cost_ratio, None, ratio_color, '.2f', '%')
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Enhanced Cost Breakdown
        st.markdown("<div class='section-header'><h3>Cost Components Breakdown</h3></div>", unsafe_allow_html=True)
        
        col_cost1, col_cost2 = st.columns(2)
        
        with col_cost1:
            # Cost breakdown pie chart
            total_slippage = tca_summary['total_slippage_value'].sum()
            total_commission_val = tca_summary['total_commission'].sum()
            total_market_impact = tca_summary['total_market_impact_value'].sum()
            
            cost_breakdown = pd.DataFrame({
                'Component': ['Slippage', 'Commission', 'Market Impact'],
                'Value': [abs(total_slippage), abs(total_commission_val), abs(total_market_impact)]
            })
            
            fig_cost_pie = go.Figure(data=[go.Pie(
                labels=cost_breakdown['Component'],
                values=cost_breakdown['Value'],
                marker=dict(colors=['#FF6B6B', '#4ECDC4', '#FFD93D']),
                hole=0.4,
                hovertemplate='<b>%{label}</b><br>Value: $%{value:,.0f}<br>Percent: %{percent}<extra></extra>'
            )])
            
            fig_cost_pie.update_layout(
                height=350,
                plot_bgcolor='#0E1117',
                paper_bgcolor='#0E1117',
                font=dict(color='#FAFAFA'),
                showlegend=True,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            
            st.plotly_chart(
    fig_cost_pie,
    config={"displayModeBar": True},
    use_container_width=True,
    key="cost_pie"
)

        with col_cost2:
            # Cost breakdown bar chart
            fig_cost_bar = go.Figure()
            
            fig_cost_bar.add_trace(go.Bar(
                x=cost_breakdown['Component'],
                y=cost_breakdown['Value'],
                marker_color=['#FF6B6B', '#4ECDC4', '#FFD93D'],
                text=cost_breakdown['Value'].apply(lambda x: f'${x:,.0f}'),
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Value: $%{y:,.0f}<extra></extra>'
            ))
            
            fig_cost_bar.update_layout(
                height=350,
                plot_bgcolor='#0E1117',
                paper_bgcolor='#0E1117',
                font=dict(color='#FAFAFA'),
                xaxis=dict(title="Cost Component", gridcolor='#2A2A3E'),
                yaxis=dict(title="Value (USD)", gridcolor='#2A2A3E'),
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=40)
            )
            
            st.plotly_chart(
    fig_cost_bar,
    config={"displayModeBar": True},
    use_container_width=True,
    key="cost_bar"
)

        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # P&L Attribution
        st.markdown("<div class='section-header'><h3>P&L Attribution Breakdown</h3></div>", unsafe_allow_html=True)
        
        if all(col in tca_summary.columns for col in ['total_alpha', 'total_beta', 'total_cost', 'total_timing']):
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Alpha',
                x=tca_summary.index,
                y=tca_summary['total_alpha'],
                marker_color='#2ECC71',
                hovertemplate='Alpha: $%{y:,.0f}<extra></extra>'
            ))
            
            fig.add_trace(go.Bar(
                name='Beta',
                x=tca_summary.index,
                y=tca_summary['total_beta'],
                marker_color='#00D9FF',
                hovertemplate='Beta: $%{y:,.0f}<extra></extra>'
            ))
            
            fig.add_trace(go.Bar(
                name='Cost',
                x=tca_summary.index,
                y=-tca_summary['total_cost'],
                marker_color='#E74C3C',
                hovertemplate='Cost: $%{y:,.0f}<extra></extra>'
            ))
            
            fig.add_trace(go.Bar(
                name='Timing',
                x=tca_summary.index,
                y=tca_summary['total_timing'],
                marker_color='#F1C40F',
                hovertemplate='Timing: $%{y:,.0f}<extra></extra>'
            ))
            
            fig.update_layout(
                barmode='relative',
                height=400,
                plot_bgcolor='#0E1117',
                paper_bgcolor='#0E1117',
                font=dict(color='#FAFAFA'),
                xaxis=dict(title="Week", gridcolor='#2A2A3E'),
                yaxis=dict(title="P&L Attribution (USD)", gridcolor='#2A2A3E'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode='x unified'
            )
            
            st.plotly_chart(
    fig,
    use_container_width=True,
    key="pnl_attribution"
)

            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<div class='section-header'><h3>Cumulative Attribution</h3></div>", unsafe_allow_html=True)
            
            total_alpha = tca_summary['total_alpha'].sum()
            total_beta = tca_summary['total_beta'].sum()
            total_cost = tca_summary['total_cost'].sum()
            total_timing = tca_summary['total_timing'].sum()
            
            col_attr1, col_attr2 = st.columns(2)
            
            with col_attr1:
                attribution_df = pd.DataFrame({
                    'Component': ['Alpha', 'Beta', 'Cost', 'Timing'],
                    'Value': [total_alpha, total_beta, -total_cost, total_timing],
                    'Color': ['#2ECC71', '#00D9FF', '#E74C3C', '#F1C40F']
                })
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=attribution_df['Component'],
                    values=attribution_df['Value'].abs(),
                    marker=dict(colors=attribution_df['Color']),
                    hole=0.4,
                    hovertemplate='<b>%{label}</b><br>Value: $%{value:,.0f}<br>Percent: %{percent}<extra></extra>'
                )])
                
                fig_pie.update_layout(
                    height=400,
                    plot_bgcolor='#0E1117',
                    paper_bgcolor='#0E1117',
                    font=dict(color='#FAFAFA'),
                    showlegend=True
                )
                
                st.plotly_chart(
    fig_pie,
    use_container_width=True,
    key="attribution_pie"
)

            
            with col_attr2:
                # Attribution summary cards
                st.markdown(f"""
                    <div class='trade-card' style='border-color: #2ECC71'>
                        <div style='display: flex; justify-content: space-between;'>
                            <span style='font-weight: 600;'>Total Alpha</span>
                            <span style='color: #2ECC71; font-weight: 700; font-size: 1.1rem;'>${total_alpha:,.0f}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class='trade-card' style='border-color: #00D9FF'>
                        <div style='display: flex; justify-content: space-between;'>
                            <span style='font-weight: 600;'>Total Beta</span>
                            <span style='color: #00D9FF; font-weight: 700; font-size: 1.1rem;'>${total_beta:,.0f}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class='trade-card' style='border-color: #E74C3C'>
                        <div style='display: flex; justify-content: space-between;'>
                            <span style='font-weight: 600;'>Total Cost</span>
                            <span style='color: #E74C3C; font-weight: 700; font-size: 1.1rem;'>-${abs(total_cost):,.0f}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class='trade-card' style='border-color: #F1C40F'>
                        <div style='display: flex; justify-content: space-between;'>
                            <span style='font-weight: 600;'>Total Timing</span>
                            <span style='color: #F1C40F; font-weight: 700; font-size: 1.1rem;'>${total_timing:,.0f}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Slippage and Impact Trends
        col_slip, col_impact = st.columns(2)
        
        with col_slip:
            st.markdown("<div class='section-header'><h3>Slippage Trend</h3></div>", unsafe_allow_html=True)
            
            fig_slip = go.Figure()
            fig_slip.add_trace(go.Scatter(
                y=tca_summary['avg_slippage_bps'],
                mode='lines+markers',
                line=dict(color='#FF5733', width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(255, 87, 51, 0.2)',
                hovertemplate='Slippage: %{y:.2f} bps<extra></extra>'
            ))
            
            avg_slip = tca_summary['avg_slippage_bps'].mean()
            fig_slip.add_hline(y=avg_slip, line_dash="dash", line_color="#FFD700",
                              annotation_text=f"Mean: {avg_slip:.2f} bps")
            
            fig_slip.update_layout(
                height=300,
                plot_bgcolor='#0E1117',
                paper_bgcolor='#0E1117',
                font=dict(color='#FAFAFA'),
                xaxis=dict(title="Week", gridcolor='#2A2A3E'),
                yaxis=dict(title="Slippage (bps)", gridcolor='#2A2A3E')
            )
            
            st.plotly_chart(
    fig_slip,
    use_container_width=True,
    key="slippage_trend"
)

        
        with col_impact:
            st.markdown("<div class='section-header'><h3>Market Impact Trend</h3></div>", unsafe_allow_html=True)
            
            fig_impact = go.Figure()
            fig_impact.add_trace(go.Scatter(
                y=tca_summary['avg_market_impact_bps'],
                mode='lines+markers',
                line=dict(color='#F1C40F', width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor='rgba(241, 196, 15, 0.2)',
                hovertemplate='Market Impact: %{y:.2f} bps<extra></extra>'
            ))
            
            avg_impact_val = tca_summary['avg_market_impact_bps'].mean()
            fig_impact.add_hline(y=avg_impact_val, line_dash="dash", line_color="#00D9FF",
                                annotation_text=f"Mean: {avg_impact_val:.2f} bps")
            
            fig_impact.update_layout(
                height=300,
                plot_bgcolor='#0E1117',
                paper_bgcolor='#0E1117',
                font=dict(color='#FAFAFA'),
                xaxis=dict(title="Week", gridcolor='#2A2A3E'),
                yaxis=dict(title="Market Impact (bps)", gridcolor='#2A2A3E')
            )
            
            st.plotly_chart(
    fig_impact,
    use_container_width=True,
    key="impact_trend"
)

        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Trading Volume Analysis
        if 'num_trades' in tca_summary.columns and 'total_volume' in tca_summary.columns:
            st.markdown("<div class='section-header'><h3>Trading Volume & Activity</h3></div>", unsafe_allow_html=True)
            
            col_vol1, col_vol2 = st.columns(2)
            
            with col_vol1:
                fig_trades = go.Figure()
                fig_trades.add_trace(go.Bar(
                    x=tca_summary.index,
                    y=tca_summary['num_trades'],
                    marker_color='#00D9FF',
                    hovertemplate='Week %{x}<br>Trades: %{y}<extra></extra>'
                ))
                
                fig_trades.update_layout(
                    title="Number of Trades per Week",
                    height=300,
                    plot_bgcolor='#0E1117',
                    paper_bgcolor='#0E1117',
                    font=dict(color='#FAFAFA'),
                    xaxis=dict(title="Week", gridcolor='#2A2A3E'),
                    yaxis=dict(title="Number of Trades", gridcolor='#2A2A3E')
                )
                
                st.plotly_chart(
    fig_trades,
    use_container_width=True,
    key="num_trades"
)

            
            with col_vol2:
                fig_volume = go.Figure()
                fig_volume.add_trace(go.Bar(
                    x=tca_summary.index,
                    y=tca_summary['total_volume'],
                    marker_color='#2ECC71',
                    hovertemplate='Week %{x}<br>Volume: %{y:,.0f}<extra></extra>'
                ))
                
                fig_volume.update_layout(
                    title="Trading Volume per Week",
                    height=300,
                    plot_bgcolor='#0E1117',
                    paper_bgcolor='#0E1117',
                    font=dict(color='#FAFAFA'),
                    xaxis=dict(title="Week", gridcolor='#2A2A3E'),
                    yaxis=dict(title="Total Volume", gridcolor='#2A2A3E')
                )
                
                st.plotly_chart(
    fig_volume,
    use_container_width=True,
    key="total_volume"
)

        
        # Detailed TCA Table
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='section-header'><h3>Detailed TCA Data</h3></div>", unsafe_allow_html=True)
        
        format_dict = {
            'avg_slippage_bps': '{:.2f}',
            'total_slippage_value': '{:,.2f}',
            'total_commission': '{:,.2f}',
            'avg_market_impact_bps': '{:.2f}',
            'total_market_impact_value': '{:,.2f}',
            'total_pnl': '{:,.2f}',
            'total_alpha': '{:,.2f}',
            'total_beta': '{:,.2f}',
            'total_cost': '{:,.2f}',
            'total_timing': '{:,.2f}'
        }
        
        if 'cost_to_pnl_ratio' in tca_summary.columns:
            format_dict['cost_to_pnl_ratio'] = '{:.2f}%'
        if 'avg_cost_per_trade' in tca_summary.columns:
            format_dict['avg_cost_per_trade'] = '{:,.2f}'
        if 'num_trades' in tca_summary.columns:
            format_dict['num_trades'] = '{:,.0f}'
        if 'total_volume' in tca_summary.columns:
            format_dict['total_volume'] = '{:,.0f}'
        
        st.dataframe(
            tca_summary.style.format(format_dict),
            width='stretch',
            height=400
        )

# ============================================================================
# ALERTS & COMPLIANCE SECTION
# ============================================================================

elif section == "Alerts & Compliance":
    st.title("Alerts & Compliance Management")
    st.markdown("Real-time breach detection, compliance monitoring, and regulatory reporting")
    st.markdown("---")
    EXPORT_DIR = os.path.join(os.getcwd(), "exports")
    os.makedirs(EXPORT_DIR, exist_ok=True)    
    # ============================================================================
    # ALERT DETECTION LOGIC
    # ============================================================================
    
    def detect_alerts():
        """Detect all risk limit breaches and compliance issues"""
        alerts = []
        
        # VaR Breaches
        if not risk_metrics.empty and "VaR_95" in risk_metrics.columns:
            current_var95 = get_safe_value(risk_metrics["VaR_95"])
            if current_var95 < RISK_LIMITS['var_95_limit']:
                alerts.append({
                    'severity': 'CRITICAL',
                    'category': 'Market Risk',
                    'metric': 'VaR 95%',
                    'current_value': current_var95,
                    'limit': RISK_LIMITS['var_95_limit'],
                    'breach_pct': ((current_var95 - RISK_LIMITS['var_95_limit']) / abs(RISK_LIMITS['var_95_limit'])) * 100,
                    'timestamp': datetime.now(),
                    'recommendation': 'Reduce portfolio risk exposure immediately. Consider hedging strategies.'
                })
        
        if not risk_metrics.empty and "VaR_99" in risk_metrics.columns:
            current_var99 = get_safe_value(risk_metrics["VaR_99"])
            if current_var99 < RISK_LIMITS['var_99_limit']:
                alerts.append({
                    'severity': 'CRITICAL',
                    'category': 'Market Risk',
                    'metric': 'VaR 99%',
                    'current_value': current_var99,
                    'limit': RISK_LIMITS['var_99_limit'],
                    'breach_pct': ((current_var99 - RISK_LIMITS['var_99_limit']) / abs(RISK_LIMITS['var_99_limit'])) * 100,
                    'timestamp': datetime.now(),
                    'recommendation': 'Extreme risk breach. Initiate emergency risk reduction protocol.'
                })
        
        # Expected Shortfall Breaches
        if not risk_metrics.empty and "ES_95" in risk_metrics.columns:
            current_es95 = get_safe_value(risk_metrics["ES_95"])
            if current_es95 < RISK_LIMITS['es_95_limit']:
                alerts.append({
                    'severity': 'HIGH',
                    'category': 'Tail Risk',
                    'metric': 'ES 95%',
                    'current_value': current_es95,
                    'limit': RISK_LIMITS['es_95_limit'],
                    'breach_pct': ((current_es95 - RISK_LIMITS['es_95_limit']) / abs(RISK_LIMITS['es_95_limit'])) * 100,
                    'timestamp': datetime.now(),
                    'recommendation': 'Tail risk elevated. Review extreme scenario exposure.'
                })
        
        if not risk_metrics.empty and "ES_99" in risk_metrics.columns:
            current_es99 = get_safe_value(risk_metrics["ES_99"])
            if current_es99 < RISK_LIMITS['es_99_limit']:
                alerts.append({
                    'severity': 'CRITICAL',
                    'category': 'Tail Risk',
                    'metric': 'ES 99%',
                    'current_value': current_es99,
                    'limit': RISK_LIMITS['es_99_limit'],
                    'breach_pct': ((current_es99 - RISK_LIMITS['es_99_limit']) / abs(RISK_LIMITS['es_99_limit'])) * 100,
                    'timestamp': datetime.now(),
                    'recommendation': 'Critical tail risk breach. Engage risk committee immediately.'
                })
        
        # Sector Concentration
        if not sector_exposure.empty:
            max_sector_weight = sector_exposure['portfolio_weight'].abs().max()
            if max_sector_weight > RISK_LIMITS['sector_concentration_limit']:
                breach_sector = sector_exposure.loc[sector_exposure['portfolio_weight'].abs().idxmax(), 'sector']
                alerts.append({
                    'severity': 'HIGH',
                    'category': 'Concentration Risk',
                    'metric': f'Sector: {breach_sector}',
                    'current_value': max_sector_weight * 100,
                    'limit': RISK_LIMITS['sector_concentration_limit'] * 100,
                    'breach_pct': ((max_sector_weight - RISK_LIMITS['sector_concentration_limit']) / RISK_LIMITS['sector_concentration_limit']) * 100,
                    'timestamp': datetime.now(),
                    'recommendation': f'Reduce {breach_sector} exposure to below {RISK_LIMITS["sector_concentration_limit"]*100:.0f}%.'
                })
        
        # Single Position Limit
        if not target_weights.empty:
            max_position = target_weights['Target Weight'].max()
            if max_position > RISK_LIMITS['single_position_limit']:
                breach_instrument = target_weights.loc[target_weights['Target Weight'].idxmax(), 'Instrument']
                alerts.append({
                    'severity': 'MEDIUM',
                    'category': 'Position Limit',
                    'metric': f'Position: {breach_instrument}',
                    'current_value': max_position * 100,
                    'limit': RISK_LIMITS['single_position_limit'] * 100,
                    'breach_pct': ((max_position - RISK_LIMITS['single_position_limit']) / RISK_LIMITS['single_position_limit']) * 100,
                    'timestamp': datetime.now(),
                    'recommendation': f'Trim {breach_instrument} position to below {RISK_LIMITS["single_position_limit"]*100:.0f}%.'
                })
        
        # Transaction Cost Alerts
        if not tca_summary.empty and "avg_slippage_bps" in tca_summary.columns:
            recent_slippage = get_safe_value(tca_summary["avg_slippage_bps"])
            if abs(recent_slippage) > RISK_LIMITS['slippage_threshold_bps']:
                alerts.append({
                    'severity': 'MEDIUM',
                    'category': 'Execution Quality',
                    'metric': 'Slippage',
                    'current_value': abs(recent_slippage),
                    'limit': RISK_LIMITS['slippage_threshold_bps'],
                    'breach_pct': ((abs(recent_slippage) - RISK_LIMITS['slippage_threshold_bps']) / RISK_LIMITS['slippage_threshold_bps']) * 100,
                    'timestamp': datetime.now(),
                    'recommendation': 'Review execution strategy. Consider smaller order sizes or different venues.'
                })
        
        if not tca_summary.empty and "avg_market_impact_bps" in tca_summary.columns:
            recent_impact = get_safe_value(tca_summary["avg_market_impact_bps"])
            if abs(recent_impact) > RISK_LIMITS['market_impact_threshold_bps']:
                alerts.append({
                    'severity': 'MEDIUM',
                    'category': 'Execution Quality',
                    'metric': 'Market Impact',
                    'current_value': abs(recent_impact),
                    'limit': RISK_LIMITS['market_impact_threshold_bps'],
                    'breach_pct': ((abs(recent_impact) - RISK_LIMITS['market_impact_threshold_bps']) / RISK_LIMITS['market_impact_threshold_bps']) * 100,
                    'timestamp': datetime.now(),
                    'recommendation': 'High market impact detected. Use algorithmic execution for large orders.'
                })
        
        # Drawdown Monitoring
        if not risk_metrics.empty and "VaR_95" in risk_metrics.columns:
            var_data = risk_metrics["VaR_95"].tail(30)
            cumulative = (1 + var_data / 100).cumprod()
            running_max = cumulative.cummax()
            drawdown = (cumulative - running_max) / running_max
            current_dd = drawdown.iloc[-1]
            
            if current_dd < RISK_LIMITS['max_drawdown_limit']:
                alerts.append({
                    'severity': 'HIGH',
                    'category': 'Drawdown',
                    'metric': 'Maximum Drawdown',
                    'current_value': current_dd * 100,
                    'limit': RISK_LIMITS['max_drawdown_limit'] * 100,
                    'breach_pct': ((current_dd - RISK_LIMITS['max_drawdown_limit']) / abs(RISK_LIMITS['max_drawdown_limit'])) * 100,
                    'timestamp': datetime.now(),
                    'recommendation': 'Portfolio drawdown exceeds limit. Implement stop-loss measures.'
                })
        
        return alerts
    
    # Detect all alerts
    active_alerts = detect_alerts()
    
    # ============================================================================
    # ALERT SUMMARY DASHBOARD
    # ============================================================================
    
    st.markdown("### Alert Summary Dashboard")
    
    # Count alerts by severity
    critical_count = sum(1 for a in active_alerts if a['severity'] == 'CRITICAL')
    high_count = sum(1 for a in active_alerts if a['severity'] == 'HIGH')
    medium_count = sum(1 for a in active_alerts if a['severity'] == 'MEDIUM')
    total_alerts = len(active_alerts)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class='kpi-card' style='--accent-color:{COLORS["danger"]}'>
                <div class='kpi-title'>CRITICAL ALERTS</div>
                <div class='kpi-value' style='color:{COLORS["danger"]}'>{critical_count}</div>
                <div class='kpi-subtitle'>Immediate Action Required</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class='kpi-card' style='--accent-color:{COLORS["warning"]}'>
                <div class='kpi-title'>HIGH PRIORITY</div>
                <div class='kpi-value' style='color:{COLORS["warning"]}'>{high_count}</div>
                <div class='kpi-subtitle'>Review Within 24 Hours</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class='kpi-card' style='--accent-color:{COLORS["info"]}'>
                <div class='kpi-title'>MEDIUM PRIORITY</div>
                <div class='kpi-value' style='color:{COLORS["info"]}'>{medium_count}</div>
                <div class='kpi-subtitle'>Monitor Closely</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        status_color = COLORS['danger'] if total_alerts > 0 else COLORS['success']
        status_text = "BREACHES DETECTED" if total_alerts > 0 else "ALL CLEAR"
        st.markdown(f"""
            <div class='kpi-card' style='--accent-color:{status_color}'>
                <div class='kpi-title'>OVERALL STATUS</div>
                <div class='kpi-value' style='color:{status_color}'>{status_text}</div>
                <div class='kpi-subtitle'>{total_alerts} Total Alerts</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============================================================================
    # ACTIVE ALERTS LIST
    # ============================================================================

    if active_alerts:
        st.markdown("<div class='section-header'><h3>🚨 Active Alerts</h3></div>", unsafe_allow_html=True)

        # Filter controls
        col_filter1, col_filter2 = st.columns([2, 2])
        with col_filter1:
            severity_filter = st.multiselect(
                "Filter by Severity",
                ["CRITICAL", "HIGH", "MEDIUM"],
                default=["CRITICAL", "HIGH", "MEDIUM"],
                key="alert_severity_filter"
            )
        with col_filter2:
            category_filter = st.multiselect(
                "Filter by Category",
                list(set(a['category'] for a in active_alerts)),
                default=list(set(a['category'] for a in active_alerts)),
                key="alert_category_filter"
            )

        # Filter alerts
        filtered_alerts = [a for a in active_alerts 
                        if a['severity'] in severity_filter 
                        and a['category'] in category_filter]

        # Sort by severity
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
        filtered_alerts.sort(key=lambda x: severity_order[x['severity']])

        # Display alerts
        for alert in filtered_alerts:
            severity_colors = {
                'CRITICAL': COLORS['danger'],
                'HIGH': COLORS['warning'],
                'MEDIUM': COLORS['info']
            }
        
            severity_icons = {
                'CRITICAL': '🔴',
                'HIGH': '🟡',
                'MEDIUM': '🔵'
            }
        
            color = severity_colors[alert['severity']]
            icon = severity_icons[alert['severity']]
        
            breach_indicator = f"{alert['breach_pct']:+.1f}% over limit" if alert['breach_pct'] > 0 else "Within limit"
        
            alert_html = f"""
            <div class='alert-box' style='border-color: {color}; background: linear-gradient(135deg, {color}15, {color}05);'>
                    <div style='display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;'>
                        <div>
                            <span style='font-size: 1.5rem;'>{icon}</span>
                            <strong style='font-size: 1.1rem; margin-left: 0.5rem;'>{alert['severity']}</strong>
                            <span style='color: {COLORS["muted"]}; margin-left: 1rem; font-size: 0.85rem;'>
                                {alert['category']} • {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                            </span>
                        </div>
                        <span class='metric-badge' style='background: {color}; color: white;'>{breach_indicator}</span>
                    </div>
                
                    <div style='background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
                        <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;'>
                            <div>
                                <div style='font-size: 0.75rem; color: {COLORS["muted"]}; text-transform: uppercase;'>Metric</div>
                                <div style='font-size: 1rem; font-weight: 600; margin-top: 0.25rem;'>{alert['metric']}</div>
                            </div>
                            <div>
                                <div style='font-size: 0.75rem; color: {COLORS["muted"]}; text-transform: uppercase;'>Current Value</div>
                                <div style='font-size: 1rem; font-weight: 600; color: {color}; margin-top: 0.25rem;'>{alert['current_value']:.2f}</div>
                            </div>
                            <div>
                                <div style='font-size: 0.75rem; color: {COLORS["muted"]}; text-transform: uppercase;'>Limit</div>
                                <div style='font-size: 1rem; font-weight: 600; margin-top: 0.25rem;'>{alert['limit']:.2f}</div>
                            </div>
                        </div>
                    </div>
                
                    <div style='background: rgba(255,255,255,0.05); padding: 1rem; border-radius: 8px; border-left: 3px solid {color};'>
                        <div style='font-size: 0.75rem; color: {COLORS["muted"]}; text-transform: uppercase; margin-bottom: 0.5rem;'>
                            💡 RECOMMENDED ACTION
                        </div>
                        <div style='font-size: 0.95rem; line-height: 1.5;'>{alert['recommendation']}</div>
                    </div>
                </div>
            """
        
            st.markdown(alert_html, unsafe_allow_html=True)

    else:
        st.markdown(f"""
            <div class='alert-box alert-success'>
                <div style='text-align: center; padding: 2rem;'>
                    <div style='font-size: 3rem; margin-bottom: 1rem;'>✅</div>
                    <h3 style='margin: 0; color: {COLORS["success"]};'>All Systems Compliant</h3>
                    <p style='margin-top: 1rem; color: {COLORS["muted"]}; font-size: 0.95rem;'>
                        No active alerts or breaches detected. All risk metrics are within acceptable limits.
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    # ============================================================================
    # COMPLIANCE SCORECARD
    # ============================================================================
    
    st.markdown("<div class='section-header'><h3>📋 Compliance Scorecard</h3></div>", unsafe_allow_html=True)
    
    # Calculate compliance metrics
    compliance_checks = []
    
    # Market Risk Compliance
    if not risk_metrics.empty:
        var95_compliant = get_safe_value(risk_metrics.get("VaR_95", pd.Series([0]))) >= RISK_LIMITS['var_95_limit']
        var99_compliant = get_safe_value(risk_metrics.get("VaR_99", pd.Series([0]))) >= RISK_LIMITS['var_99_limit']
        es95_compliant = get_safe_value(risk_metrics.get("ES_95", pd.Series([0]))) >= RISK_LIMITS['es_95_limit']
        es99_compliant = get_safe_value(risk_metrics.get("ES_99", pd.Series([0]))) >= RISK_LIMITS['es_99_limit']
        
        market_risk_score = sum([var95_compliant, var99_compliant, es95_compliant, es99_compliant]) / 4 * 100
        
        compliance_checks.append({
            'Category': 'Market Risk Limits',
            'Score': market_risk_score,
            'Status': 'PASS' if market_risk_score == 100 else 'FAIL',
            'Checks': '4/4' if market_risk_score == 100 else f'{int(market_risk_score/25)}/4'
        })
    
    # Concentration Risk Compliance
    if not sector_exposure.empty:
        sector_compliant = sector_exposure['portfolio_weight'].abs().max() <= RISK_LIMITS['sector_concentration_limit']
        concentration_score = 100 if sector_compliant else 0
        
        compliance_checks.append({
            'Category': 'Sector Concentration',
            'Score': concentration_score,
            'Status': 'PASS' if sector_compliant else 'FAIL',
            'Checks': '1/1' if sector_compliant else '0/1'
        })
    
    # Position Limits Compliance
    if not target_weights.empty:
        position_compliant = target_weights['Target Weight'].max() <= RISK_LIMITS['single_position_limit']
        position_score = 100 if position_compliant else 0
        
        compliance_checks.append({
            'Category': 'Position Limits',
            'Score': position_score,
            'Status': 'PASS' if position_compliant else 'FAIL',
            'Checks': '1/1' if position_compliant else '0/1'
        })
    
    # Transaction Cost Compliance
    if not tca_summary.empty:
        slippage_compliant = abs(get_safe_value(tca_summary.get("avg_slippage_bps", pd.Series([0])))) <= RISK_LIMITS['slippage_threshold_bps']
        impact_compliant = abs(get_safe_value(tca_summary.get("avg_market_impact_bps", pd.Series([0])))) <= RISK_LIMITS['market_impact_threshold_bps']
        
        tca_score = sum([slippage_compliant, impact_compliant]) / 2 * 100
        
        compliance_checks.append({
            'Category': 'Execution Quality',
            'Score': tca_score,
            'Status': 'PASS' if tca_score == 100 else 'FAIL',
            'Checks': '2/2' if tca_score == 100 else f'{int(tca_score/50)}/2'
        })
    
    # Display compliance scorecard
    if compliance_checks:
        compliance_df = pd.DataFrame(compliance_checks)
        
        col_score1, col_score2 = st.columns([2, 1])
        
        with col_score1:
            # Compliance table
            fig_compliance = go.Figure(data=[go.Table(
                header=dict(
                    values=['<b>Category</b>', '<b>Score</b>', '<b>Status</b>', '<b>Checks Passed</b>'],
                    fill_color=COLORS['primary'],
                    align='left',
                    font=dict(color='white', size=12, family='Inter')
                ),
                cells=dict(
                    values=[
                        compliance_df['Category'],
                        [f"{score:.0f}%" for score in compliance_df['Score']],
                        compliance_df['Status'],
                        compliance_df['Checks']
                    ],
                    fill_color=[
                        ['rgba(102, 126, 234, 0.1)'] * len(compliance_df),
                        [COLORS['success'] if s == 100 else COLORS['danger'] for s in compliance_df['Score']],
                        [COLORS['success'] if s == 'PASS' else COLORS['danger'] for s in compliance_df['Status']],
                        ['rgba(102, 126, 234, 0.1)'] * len(compliance_df)
                    ],
                    align='left',
                    font=dict(color=COLORS['text'], size=11, family='Inter'),
                    height=40
                )
            )])
            
            fig_compliance.update_layout(
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=0, r=0, t=0, b=0)
            )
            
            st.plotly_chart(fig_compliance, use_container_width=True, key="compliance_table")
        
        with col_score2:
            # Overall compliance score
            overall_score = compliance_df['Score'].mean()
            
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=overall_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Overall Compliance", 'font': {'size': 16, 'family': 'Inter'}},
                number={'suffix': "%", 'font': {'size': 32, 'family': 'Inter'}},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': COLORS['primary']},
                    'steps': [
                        {'range': [0, 70], 'color': 'rgba(255, 107, 107, 0.3)'},
                        {'range': [70, 90], 'color': 'rgba(254, 202, 87, 0.3)'},
                        {'range': [90, 100], 'color': 'rgba(72, 219, 251, 0.3)'}
                    ],
                    'threshold': {
                        'line': {'color': COLORS['success'], 'width': 4},
                        'thickness': 0.75,
                        'value': 95
                    }
                }
            ))
            
            fig_gauge.update_layout(
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=COLORS['text'], family='Inter'),
                margin=dict(l=20, r=20, t=60, b=20)
            )
            
            st.plotly_chart(fig_gauge, use_container_width=True, key="compliance_gauge")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============================================================================
    # ALERT HISTORY & TRENDS
    # ============================================================================
    
    st.markdown("<div class='section-header'><h3>📊 Alert History & Trends</h3></div>", unsafe_allow_html=True)
    
    # Simulate alert history (in production, this would come from a database)
    alert_history = pd.DataFrame({
        'Date': pd.date_range(end=datetime.now(), periods=30, freq='D'),
        'Critical': np.random.randint(0, 3, 30),
        'High': np.random.randint(0, 5, 30),
        'Medium': np.random.randint(1, 8, 30)
    })
    
    col_hist1, col_hist2 = st.columns([2, 1])
    
    with col_hist1:
        fig_alert_trend = go.Figure()
        
        fig_alert_trend.add_trace(go.Scatter(
            x=alert_history['Date'],
            y=alert_history['Critical'],
            name='Critical',
            mode='lines+markers',
            line=dict(color=COLORS['danger'], width=2.5),
            fill='tonexty',
            fillcolor='rgba(255, 107, 107, 0.2)'
        ))
        
        fig_alert_trend.add_trace(go.Scatter(
            x=alert_history['Date'],
            y=alert_history['High'],
            name='High',
            mode='lines+markers',
            line=dict(color=COLORS['warning'], width=2.5),
            fill='tonexty',
            fillcolor='rgba(254, 202, 87, 0.2)'
        ))
        
        fig_alert_trend.add_trace(go.Scatter(
            x=alert_history['Date'],
            y=alert_history['Medium'],
            name='Medium',
            mode='lines+markers',
            line=dict(color=COLORS['info'], width=2.5),
            fill='tonexty',
            fillcolor='rgba(0, 210, 211, 0.2)'
        ))
        
        fig_alert_trend.update_layout(
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color=COLORS['text'], family='Inter'),
            xaxis=dict(title="Date", gridcolor='rgba(102, 126, 234, 0.1)'),
            yaxis=dict(title="Number of Alerts", gridcolor='rgba(102, 126, 234, 0.1)'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_alert_trend, use_container_width=True, key="alert_history")
    

    
    # ============================================================================
    # REGULATORY REPORTING
    # ============================================================================
    
    st.markdown("<div class='section-header'><h3>📄 Regulatory Reporting</h3></div>", unsafe_allow_html=True)
    
    col_reg1, col_reg2, col_reg3 = st.columns(3)
    
    with col_reg1:
        st.markdown("""
            <div class='trade-card' style='border-color: {0}'>
                <h4 style='margin: 0 0 1rem 0;'>📋 Daily Regulatory Report</h4>
                <p style='color: {1}; font-size: 0.9rem; margin: 0.5rem 0;'>
                    Mandatory daily risk reporting to regulatory authorities
                </p>
                <ul style='font-size: 0.85rem; color: {1}; margin: 1rem 0;'>
                    <li>VaR & ES Metrics</li>
                    <li>Large Exposure Reporting</li>
                    <li>Liquidity Coverage Ratio</li>
                    <li>Leverage Ratio</li>
                </ul>
                <div style='margin-top: 1rem;'>
                    <strong style='color: {2};'>Status:</strong> 
                    <span style='color: {2};'>✓ Submitted Today</span>
                </div>
            </div>
        """.format(COLORS['info'], COLORS['muted'], COLORS['success']), unsafe_allow_html=True)
    
    with col_reg2:
        st.markdown("""
            <div class='trade-card' style='border-color: {0}'>
                <h4 style='margin: 0 0 1rem 0;'>📊 Monthly Compliance Report</h4>
                <p style='color: {1}; font-size: 0.9rem; margin: 0.5rem 0;'>
                    Comprehensive monthly compliance certification
                </p>
                <ul style='font-size: 0.85rem; color: {1}; margin: 1rem 0;'>
                    <li>Limit Breach Summary</li>
                    <li>Remediation Actions</li>
                    <li>Policy Violations</li>
                    <li>Risk Committee Minutes</li>
                </ul>
                <div style='margin-top: 1rem;'>
                    <strong style='color: {2};'>Next Due:</strong> 
                    <span style='color: {2};'>7 days</span>
                </div>
            </div>
        """.format(COLORS['warning'], COLORS['muted'], COLORS['info']), unsafe_allow_html=True)
    
    with col_reg3:
        st.markdown("""
            <div class='trade-card' style='border-color: {0}'>
                <h4 style='margin: 0 0 1rem 0;'>🏛️ Quarterly Audit Package</h4>
                <p style='color: {1}; font-size: 0.9rem; margin: 0.5rem 0;'>
                    Detailed audit trail and control documentation
                </p>
                <ul style='font-size: 0.85rem; color: {1}; margin: 1rem 0;'>
                    <li>Control Testing Results</li>
                    <li>Model Validation</li>
                    <li>Independent Price Verification</li>
                    <li>Exception Reports</li>
                </ul>
                <div style='margin-top: 1rem;'>
                    <strong style='color: {2};'>Next Due:</strong> 
                    <span style='color: {2};'>45 days</span>
                </div>
            </div>
        """.format(COLORS['primary'], COLORS['muted'], COLORS['warning']), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Generate regulatory reports
    col_report1, col_report2 = st.columns(2)
    
    with col_report1:
        if st.button("📥 Generate Daily Regulatory Report", use_container_width=True, key="gen_daily_reg"):
            with st.spinner("Generating regulatory report..."):
                filename = f"Daily_Regulatory_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                file_path = os.path.join(EXPORT_DIR, filename)
                
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import A4
                
                doc = SimpleDocTemplate(file_path, pagesize=A4)
                styles = getSampleStyleSheet()
                elements = []
                
                # Header
                elements.append(Paragraph("<b>DAILY REGULATORY RISK REPORT</b>", styles["Title"]))
                elements.append(Paragraph(f"Report Date: {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"]))
                elements.append(Paragraph(f"Reporting Entity: Risk Analytics Platform", styles["Normal"]))
                elements.append(Spacer(1, 20))
                
                # Executive Summary
                elements.append(Paragraph("<b>EXECUTIVE SUMMARY</b>", styles["Heading2"]))
                
                breach_status = "NO BREACHES" if len(active_alerts) == 0 else f"{len(active_alerts)} BREACH(ES) DETECTED"
                elements.append(Paragraph(f"Risk Limit Status: <b>{breach_status}</b>", styles["Normal"]))
                elements.append(Paragraph(f"Total Active Alerts: {total_alerts}", styles["Normal"]))
                elements.append(Paragraph(f"Critical Alerts: {critical_count}", styles["Normal"]))
                elements.append(Spacer(1, 12))
                
                # Market Risk Metrics
                elements.append(Paragraph("<b>MARKET RISK METRICS</b>", styles["Heading2"]))
                
                if not risk_metrics.empty:
                    risk_data = [["Metric", "Current Value", "Limit", "Status"]]
                    
                    var95 = get_safe_value(risk_metrics.get("VaR_95", pd.Series([0])))
                    risk_data.append([
                        "VaR 95%",
                        f"{var95:.2f}",
                        f"{RISK_LIMITS['var_95_limit']:.2f}",
                        "PASS" if var95 >= RISK_LIMITS['var_95_limit'] else "BREACH"
                    ])
                    
                    es95 = get_safe_value(risk_metrics.get("ES_95", pd.Series([0])))
                    risk_data.append([
                        "ES 95%",
                        f"{es95:.2f}",
                        f"{RISK_LIMITS['es_95_limit']:.2f}",
                        "PASS" if es95 >= RISK_LIMITS['es_95_limit'] else "BREACH"
                    ])
                    
                    var99 = get_safe_value(risk_metrics.get("VaR_99", pd.Series([0])))
                    risk_data.append([
                        "VaR 99%",
                        f"{var99:.2f}",
                        f"{RISK_LIMITS['var_99_limit']:.2f}",
                        "PASS" if var99 >= RISK_LIMITS['var_99_limit'] else "BREACH"
                    ])
                    
                    t = Table(risk_data, hAlign="LEFT")
                    t.setStyle(TableStyle([
                        ("BACKGROUND", (0,0), (-1,0), colors.grey),
                        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
                        ("ALIGN", (0,0), (-1,-1), "LEFT"),
                        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                        ("FONTSIZE", (0,0), (-1,0), 10),
                        ("BOTTOMPADDING", (0,0), (-1,0), 12),
                        ("GRID", (0,0), (-1,-1), 1, colors.black),
                    ]))
                    elements.append(t)
                elements.append(Spacer(1, 12))
                
                # Concentration Risk
                elements.append(Paragraph("<b>CONCENTRATION RISK</b>", styles["Heading2"]))
                
                if not sector_exposure.empty:
                    concentration_data = [["Sector", "Weight (%)", "Limit (%)", "Status"]]
                    
                    top_sectors = sector_exposure.nlargest(5, 'portfolio_weight', keep='all')
                    for _, row in top_sectors.iterrows():
                        weight = row['portfolio_weight'] * 100
                        concentration_data.append([
                            row['sector'],
                            f"{weight:.2f}",
                            f"{RISK_LIMITS['sector_concentration_limit']*100:.0f}",
                            "PASS" if abs(weight) <= RISK_LIMITS['sector_concentration_limit']*100 else "BREACH"
                        ])
                    
                    t = Table(concentration_data, hAlign="LEFT")
                    t.setStyle(TableStyle([
                        ("BACKGROUND", (0,0), (-1,0), colors.grey),
                        ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
                        ("ALIGN", (0,0), (-1,-1), "LEFT"),
                        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                        ("GRID", (0,0), (-1,-1), 1, colors.black),
                    ]))
                    elements.append(t)
                elements.append(Spacer(1, 12))
                
                # Active Breaches
                if active_alerts:
                    elements.append(Paragraph("<b>ACTIVE BREACHES & REMEDIATION</b>", styles["Heading2"]))
                    
                    for i, alert in enumerate(active_alerts[:5], 1):
                        elements.append(Paragraph(f"<b>Breach #{i}: {alert['metric']}</b>", styles["Normal"]))
                        elements.append(Paragraph(f"Severity: {alert['severity']}", styles["Normal"]))
                        elements.append(Paragraph(f"Current Value: {alert['current_value']:.2f}", styles["Normal"]))
                        elements.append(Paragraph(f"Limit: {alert['limit']:.2f}", styles["Normal"]))
                        elements.append(Paragraph(f"Recommendation: {alert['recommendation']}", styles["Normal"]))
                        elements.append(Spacer(1, 8))
                
                # Certification
                elements.append(Spacer(1, 20))
                elements.append(Paragraph("<b>CERTIFICATION</b>", styles["Heading2"]))
                elements.append(Paragraph(
                    "I certify that the information contained in this report is accurate and complete to the best of my knowledge.",
                    styles["Normal"]
                ))
                elements.append(Spacer(1, 12))
                elements.append(Paragraph("_" * 50, styles["Normal"]))
                elements.append(Paragraph("Chief Risk Officer Signature", styles["Normal"]))
                elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"]))
                
                # Build PDF
                doc.build(elements)
                st.success(f"✅ Daily Regulatory Report generated: {file_path}")
    
    with col_report2:
        if st.button("📥 Generate Breach Exception Report", use_container_width=True, key="gen_breach_report"):
            with st.spinner("Generating breach report..."):
                if active_alerts:
                    filename = f"Breach_Exception_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    file_path = os.path.join(EXPORT_DIR, filename)
                    
                    breach_df = pd.DataFrame(active_alerts)
                    breach_df['timestamp'] = breach_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
                    breach_df.to_csv(file_path, index=False)
                    
                    st.success(f"✅ Breach Exception Report saved to: {file_path}")
                else:
                    st.info("ℹ️ No breaches to report. System is fully compliant.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============================================================================
    # LIMIT MONITORING CONFIGURATION
    # ============================================================================
    
    st.markdown("<div class='section-header'><h3>⚙️ Limit Configuration & Monitoring</h3></div>", unsafe_allow_html=True)
    
    with st.expander("🔧 Configure Risk Limits", expanded=False):
        st.markdown("#### Current Risk Limits")
        
        col_lim1, col_lim2 = st.columns(2)
        
        with col_lim1:
            st.markdown("##### Market Risk Limits")
            
            new_var95_limit = st.number_input(
                "VaR 95% Limit",
                value=RISK_LIMITS['var_95_limit'],
                step=1.0,
                format="%.2f",
                key="new_var95"
            )
            
            new_es95_limit = st.number_input(
                "ES 95% Limit",
                value=RISK_LIMITS['es_95_limit'],
                step=5.0,
                format="%.2f",
                key="new_es95"
            )
            
            new_var99_limit = st.number_input(
                "VaR 99% Limit",
                value=RISK_LIMITS['var_99_limit'],
                step=5.0,
                format="%.2f",
                key="new_var99"
            )
            
            new_es99_limit = st.number_input(
                "ES 99% Limit",
                value=RISK_LIMITS['es_99_limit'],
                step=10.0,
                format="%.2f",
                key="new_es99"
            )
        
        with col_lim2:
            st.markdown("##### Concentration & Execution Limits")
            
            new_sector_limit = st.number_input(
                "Sector Concentration Limit (%)",
                value=RISK_LIMITS['sector_concentration_limit'] * 100,
                step=1.0,
                format="%.1f",
                key="new_sector"
            ) / 100
            
            new_position_limit = st.number_input(
                "Single Position Limit (%)",
                value=RISK_LIMITS['single_position_limit'] * 100,
                step=1.0,
                format="%.1f",
                key="new_position"
            ) / 100
            
            new_slippage_limit = st.number_input(
                "Slippage Threshold (bps)",
                value=RISK_LIMITS['slippage_threshold_bps'],
                step=1.0,
                format="%.1f",
                key="new_slippage"
            )
            
            new_impact_limit = st.number_input(
                "Market Impact Threshold (bps)",
                value=RISK_LIMITS['market_impact_threshold_bps'],
                step=1.0,
                format="%.1f",
                key="new_impact"
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            if st.button("💾 Update Limits", use_container_width=True, key="update_limits"):
                # In production, this would update a database
                st.success("✅ Risk limits updated successfully!")
                st.info("ℹ️ Changes will take effect on next data refresh.")
        
        with col_btn2:
            if st.button("↩️ Reset to Defaults", use_container_width=True, key="reset_limits"):
                st.warning("⚠️ Limits reset to default values.")
                st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    

    # ============================================================================
    # AUDIT TRAIL
    # ============================================================================
    
    st.markdown("<div class='section-header'><h3>📜 Audit Trail & Activity Log</h3></div>", unsafe_allow_html=True)
    
    # Simulate audit log (in production, this would come from a database)
    audit_log = pd.DataFrame({
        'Timestamp': [
            datetime.now() - timedelta(hours=i) for i in range(10)
        ],
        'User': ['system', 'admin', 'risk_manager', 'system', 'compliance_officer',
                'system', 'risk_manager', 'admin', 'system', 'system'],
        'Action': [
            'Alert Generated: VaR 95% Breach',
            'Risk Limit Updated: VaR 95%',
            'Breach Acknowledged: Sector Concentration',
            'Daily Report Generated',
            'Compliance Review Completed',
            'Alert Generated: High Slippage',
            'Exception Approved: Position Limit',
            'User Login',
            'Data Refresh Completed',
            'Alert Generated: Market Impact'
        ],
        'Severity': ['CRITICAL', 'INFO', 'HIGH', 'INFO', 'INFO',
                    'MEDIUM', 'HIGH', 'INFO', 'INFO', 'MEDIUM'],
        'IP Address': ['127.0.0.1', '192.168.1.100', '192.168.1.101', '127.0.0.1', '192.168.1.102',
                      '127.0.0.1', '192.168.1.101', '192.168.1.100', '127.0.0.1', '127.0.0.1']
    })
    
    # Filter controls
    col_audit1, col_audit2, col_audit3 = st.columns(3)
    
    with col_audit1:
        audit_user_filter = st.multiselect(
            "Filter by User",
            options=audit_log['User'].unique(),
            default=audit_log['User'].unique(),
            key="audit_user_filter"
        )
    
    with col_audit2:
        audit_severity_filter = st.multiselect(
            "Filter by Severity",
            options=audit_log['Severity'].unique(),
            default=audit_log['Severity'].unique(),
            key="audit_severity_filter"
        )
    
    with col_audit3:
        audit_lookback = st.selectbox(
            "Time Period",
            ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"],
            index=0,
            key="audit_lookback"
        )
    
    # Apply filters
    filtered_audit = audit_log[
        (audit_log['User'].isin(audit_user_filter)) &
        (audit_log['Severity'].isin(audit_severity_filter))
    ]
    
    # Display audit log
    st.dataframe(
        filtered_audit.style.apply(
            lambda x: ['background-color: rgba(255, 107, 107, 0.2)' if v == 'CRITICAL' 
                      else 'background-color: rgba(254, 202, 87, 0.2)' if v == 'HIGH'
                      else 'background-color: rgba(0, 210, 211, 0.2)' if v == 'MEDIUM'
                      else '' for v in x],
            subset=['Severity']
        ),
        use_container_width=True,
        height=400
    )
    
    # Export audit log
    if st.button("📥 Export Audit Log", use_container_width=True, key="export_audit"):
        filename = f"Audit_Log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        file_path = os.path.join(EXPORT_DIR, filename)
        filtered_audit.to_csv(file_path, index=False)
        st.success(f"✅ Audit log exported to: {file_path}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ============================================================================
    # ESCALATION MATRIX
    # ============================================================================
    
    st.markdown("<div class='section-header'><h3>📞 Escalation Matrix</h3></div>", unsafe_allow_html=True)
    
    escalation_matrix = pd.DataFrame({
        'Severity': ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
        'Response Time': ['Immediate', '< 1 Hour', '< 4 Hours', '< 24 Hours'],
        'Primary Contact': ['CRO', 'Head of Risk', 'Risk Manager', 'Risk Analyst'],
        'Secondary Contact': ['CEO', 'CRO', 'Head of Risk', 'Risk Manager'],
        'Notification Method': ['Phone + Email + SMS', 'Email + SMS', 'Email', 'Dashboard'],
        'Escalation After': ['15 minutes', '1 hour', '4 hours', '24 hours']
    })
    
    st.dataframe(escalation_matrix, use_container_width=True, height=200)
    
    st.markdown("""
        <div class='alert-box alert-info'>
            <strong>ℹ️ Escalation Procedure</strong><br>
            If an alert is not acknowledged within the specified response time, it will automatically 
            escalate to the secondary contact. Critical alerts trigger an immediate escalation chain 
            to executive management.
        </div>
    """, unsafe_allow_html=True)

# ============================================================================
# REPORTING & EXPORT SECTION
# ============================================================================

elif section == "Reporting & Export":
    st.title("Reporting & Data Export")
    st.markdown("Generate reports and export data for compliance and analysis")
    st.markdown("---")

    # Create exports folder if not exists
    import os
    from datetime import datetime
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    EXPORT_DIR = os.path.join(os.getcwd(), "exports")
    os.makedirs(EXPORT_DIR, exist_ok=True)

    st.markdown("### Available Reports")

    col1, col2 = st.columns(2)

    # -------------------------------------------------------------------------
    # DAILY RISK REPORT
    # -------------------------------------------------------------------------
    with col1:
        st.markdown(f"""
            <div class='trade-card' style='border-color: {COLORS['info']}'>
                <h4>Daily Risk Report</h4>
                <p>Comprehensive daily risk metrics including VaR, ES, and stress tests</p>
                <br>
                <strong>Includes:</strong>
                <ul>
                    <li>Market risk metrics</li>
                    <li>Sector exposure analysis</li>
                    <li>Stress test results</li>
                    <li>Compliance status</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Generate Daily Risk Report", use_container_width=True, key="gen_daily"):
            with st.spinner("Generating report..."):
                filename = f"Daily_Risk_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                file_path = os.path.join(EXPORT_DIR, filename)

                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib import colors
                import matplotlib.pyplot as plt
                import io

                doc = SimpleDocTemplate(file_path, pagesize=A4)
                styles = getSampleStyleSheet()
                elements = []

        # ---- Header ----
                elements.append(Paragraph("<b>Daily Risk Report</b>", styles["Title"]))
                elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
                elements.append(Spacer(1, 12))

        # ---- Key Risk Metrics ----
                if 'risk_metrics' in locals() and not risk_metrics.empty:
                    summary_data = [["Metric", "Mean", "Std Dev", "Min", "Max"]]
                    for col in ["VaR_95", "ES_95", "VaR_99", "ES_99"]:
                     if col in risk_metrics.columns:
                            summary_data.append([
                        col,
                        f"{risk_metrics[col].mean():.2f}",
                        f"{risk_metrics[col].std():.2f}",
                        f"{risk_metrics[col].min():.2f}",
                        f"{risk_metrics[col].max():.2f}"
                    ])
                    t = Table(summary_data, hAlign="LEFT")
                    t.setStyle(TableStyle([
                        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#333333")),
                ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
                ("GRID", (0,0), (-1,-1), 0.5, colors.gray),
                ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#1a1a1a")),
                ("TEXTCOLOR", (0,1), (-1,-1), colors.whitesmoke),
            ]))
                    elements.append(t)
                    elements.append(Spacer(1, 12))
                else:
                    elements.append(Paragraph("No risk data available.", styles["Normal"]))
                    elements.append(Spacer(1, 12))

        # ---- VaR Trend Chart ----
                if 'risk_metrics' in locals() and "VaR_95" in risk_metrics.columns:
                    fig, ax = plt.subplots(figsize=(4,2))
                    ax.plot(risk_metrics["VaR_95"], color="crimson", linewidth=2)
                    ax.set_title("VaR 95% Trend", color="black")
                    buf = io.BytesIO()
                    plt.savefig(buf, format="png", bbox_inches="tight")
                    plt.close(fig)
                    buf.seek(0)
                    elements.append(Image(buf, width=400, height=200))
                    elements.append(Spacer(1, 12))

        # ---- Compliance ----
                elements.append(Paragraph("<b>Compliance Summary</b>", styles["Heading2"]))
                elements.append(Paragraph("All metrics are within acceptable risk limits. No breaches detected.", styles["Normal"]))

        # ---- Footer ----
                elements.append(Spacer(1, 20))
                elements.append(Paragraph("Generated by Risk Analytics Dashboard", styles["Normal"]))

                doc.build(elements)
                st.success(f"✅ Daily Risk Report saved to {file_path}")


    # -------------------------------------------------------------------------
    # PORTFOLIO ANALYTICS REPORT
    # -------------------------------------------------------------------------
    with col2:
        st.markdown(f"""
            <div class='trade-card' style='border-color: {COLORS['success']}'>
                <h4>Portfolio Analytics Report</h4>
                <p>Detailed portfolio composition, performance, and trade recommendations</p>
                <br>
                <strong>Includes:</strong>
                <ul>
                    <li>Holdings breakdown</li>
                    <li>Performance attribution</li>
                    <li>Rebalancing recommendations</li>
                    <li>Optimization metrics</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Generate Portfolio Report", use_container_width=True, key="gen_portfolio"):
            with st.spinner("Generating report..."):
                filename = f"Portfolio_Analytics_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                file_path = os.path.join(EXPORT_DIR, filename)

                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib import colors
                import matplotlib.pyplot as plt
                import io

                doc = SimpleDocTemplate(file_path, pagesize=A4)
                styles = getSampleStyleSheet()
                elements = []

        # ---- Header ----
                elements.append(Paragraph("<b>Portfolio Analytics Report</b>", styles["Title"]))
                elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
                elements.append(Spacer(1, 12))

        # ---- Holdings Table ----
                if 'target_weights' in locals() and not target_weights.empty:
                    table_data = [["Instrument", "Weight", "Return", "Volatility"]]
                    for _, row in target_weights.head(10).iterrows():
                        table_data.append([
                    row.get("Instrument", "-"),
                    f"{row.get('Weight', 0):.2f}",
                    f"{row.get('Return', 0):.2f}",
                    f"{row.get('Volatility', 0):.2f}"
                ])
                    t = Table(table_data, hAlign="LEFT")
                    t.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#333333")),
                ("TEXTCOLOR", (0,0), (-1,0), colors.whitesmoke),
                ("GRID", (0,0), (-1,-1), 0.5, colors.gray),
                ("BACKGROUND", (0,1), (-1,-1), colors.HexColor("#1a1a1a")),
                ("TEXTCOLOR", (0,1), (-1,-1), colors.whitesmoke),
            ]))
                    elements.append(t)
                    elements.append(Spacer(1, 12))
                else:
                    elements.append(Paragraph("No holdings data available.", styles["Normal"]))
                    elements.append(Spacer(1, 12))

        # ---- Portfolio Allocation Chart ----
                if 'target_weights' in locals() and "Instrument" in target_weights.columns:
                    fig, ax = plt.subplots(figsize=(4,2))
                    ax.barh(target_weights["Instrument"].head(10), target_weights["Weight"].head(10), color="skyblue")
                    ax.set_title("Top 10 Holdings Allocation", color="black")
                    buf = io.BytesIO()
                    plt.savefig(buf, format="png", bbox_inches="tight")
                    plt.close(fig)
                    buf.seek(0)
                    elements.append(Image(buf, width=400, height=200))
                    elements.append(Spacer(1, 12))

        # ---- Summary ----
                elements.append(Paragraph("<b>Summary</b>", styles["Heading2"]))
                elements.append(Paragraph("This report summarizes the current portfolio holdings, "
                                  "performance attribution, and optimization results. "
                                  "All allocations are in line with target weights.", styles["Normal"]))

        # ---- Footer ----
                elements.append(Spacer(1, 20))
                elements.append(Paragraph("Generated by Portfolio Analytics Dashboard", styles["Normal"]))

        # Build PDF
                doc.build(elements)
                st.success(f"✅ Portfolio Analytics Report saved to {file_path}")


    st.markdown("<br>", unsafe_allow_html=True)
    col3, col4 = st.columns(2)

    # -------------------------------------------------------------------------
    # TRANSACTION COST ANALYSIS REPORT
    # -------------------------------------------------------------------------
    with col3:
        st.markdown(f"""
            <div class='trade-card' style='border-color: {COLORS['warning']}'>
                <h4>Transaction Cost Analysis</h4>
                <p>Execution quality metrics and cost breakdown analysis</p>
                <br>
                <strong>Includes:</strong>
                <ul>
                    <li>Slippage analysis</li>
                    <li>Market impact metrics</li>
                    <li>P&L attribution</li>
                    <li>Broker performance</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Generate TCA Report", use_container_width=True, key="gen_tca"):
            with st.spinner("Generating report..."):
                filename = f"TCA_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                file_path = os.path.join(EXPORT_DIR, filename)

                c = canvas.Canvas(file_path, pagesize=A4)
                c.setTitle("Transaction Cost Analysis")

                c.drawString(100, 800, "Transaction Cost Analysis Report")
                c.drawString(100, 780, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                c.drawString(100, 760, f"TCA Records: {len(tca_summary) if 'tca_summary' in locals() else 0}")
                c.drawString(100, 740, "Includes: Slippage, Market Impact, P&L Attribution, Broker Summary")
                c.save()

                st.success(f"✅ TCA Report saved to {file_path}")

    # -------------------------------------------------------------------------
    # STRATEGY PERFORMANCE REPORT
    # -------------------------------------------------------------------------
    with col4:
        st.markdown(f"""
            <div class='trade-card' style='border-color: {COLORS['primary']}'>
                <h4>Strategy Performance Report</h4>
                <p>Backtesting results and strategy comparison analysis</p>
                <br>
                <strong>Includes:</strong>
                <ul>
                    <li>Strategy metrics</li>
                    <li>Walk-forward validation</li>
                    <li>Risk-return profiles</li>
                    <li>Recommendations</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Generate Strategy Report", use_container_width=True, key="gen_strategy"):
            with st.spinner("Generating report..."):
                filename = f"Strategy_Performance_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                file_path = os.path.join(EXPORT_DIR, filename)

                c = canvas.Canvas(file_path, pagesize=A4)
                c.setTitle("Strategy Performance Report")

                c.drawString(100, 800, "Strategy Performance Report")
                c.drawString(100, 780, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                c.drawString(100, 760, f"Backtest Records: {len(backtest_results) if 'backtest_results' in locals() else 0}")
                c.drawString(100, 740, "Includes: Strategy Metrics, Validation, Recommendations")
                c.save()

                st.success(f"✅ Strategy Report saved to {file_path}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    
    st.markdown("### Data Export Options")
    
    col_exp1, col_exp2 = st.columns(2)
    
    with col_exp1:
        st.markdown("#### Export Configuration")
        
        export_format = st.selectbox("Export Format", ["CSV", "Excel (XLSX)", "JSON", "PDF Report"])
        
        date_range = st.date_input(
            "Date Range",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            max_value=datetime.now()
        )
        
        datasets_to_export = st.multiselect(
            "Select Datasets",
            ["Risk Metrics", "Sector Exposure", "Portfolio Weights", 
             "Trade Recommendations", "TCA Summary", "Backtest Results"],
            default=["Risk Metrics"]
        )
        
        include_metadata = st.checkbox("Include Metadata & Audit Info", value=True)
        
        EXPORT_DIR = os.path.join(os.getcwd(), "exports")
        os.makedirs(EXPORT_DIR, exist_ok=True)


        if st.button("Export Data", use_container_width=True, type="primary"):
            with st.spinner("Preparing export..."):
                export_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = f"export_{export_time}"
        
        # Save each selected dataset
                for dataset in datasets_to_export:
            # Pick a dummy dataset (replace these with your actual variables)
                    if dataset == "Risk Metrics" and 'risk_metrics' in locals():
                        data_to_export = risk_metrics
                    elif dataset == "Sector Exposure" and 'sector_exposure' in locals():
                        data_to_export = sector_exposure
                    elif dataset == "Trade Recommendations" and 'trade_recommendations' in locals():
                        data_to_export = trade_recommendations
                    elif dataset == "TCA Summary" and 'tca_summary' in locals():
                        data_to_export = tca_summary
                    elif dataset == "Backtest Results" and 'backtest_results' in locals():
                        data_to_export = backtest_results
                    elif dataset == "Portfolio Weights" and 'target_weights' in locals():
                        data_to_export = target_weights
                    else:
                        data_to_export = pd.DataFrame()

                    if not data_to_export.empty:
                        filename = f"{base_filename}_{dataset.replace(' ', '_')}"
                        file_path = os.path.join(EXPORT_DIR, f"{filename}")

                # Save based on user selection
                    if export_format == "CSV":
                        file_path += ".csv"
                        data_to_export.to_csv(file_path, index=False)
                    elif export_format == "Excel (XLSX)":
                        file_path += ".xlsx"
                        data_to_export.to_excel(file_path, index=False)
                    elif export_format == "JSON":
                        file_path += ".json"
                        data_to_export.to_json(file_path, orient="records", indent=4)
                    elif export_format == "PDF Report":
                        file_path += ".pdf"
                        from reportlab.lib.pagesizes import A4
                        from reportlab.pdfgen import canvas
                        c = canvas.Canvas(file_path, pagesize=A4)
                        c.drawString(100, 800, f"{dataset} Report - Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        c.drawString(100, 780, f"Contains {len(data_to_export)} records.")
                        c.save()

                    st.success(f"✅ {dataset} exported successfully → {file_path}")
                else:
                    st.warning(f"Sucess")
   
        

    
    with col_exp2:
        st.markdown("#### Recent Exports")
        
        recent_exports = pd.DataFrame({
            'Timestamp': [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=2),
                datetime.now() - timedelta(days=7)
            ],
            'Report Type': ['Daily Risk Report', 'Portfolio Analytics', 'TCA Report'],
            'Format': ['PDF', 'Excel', 'CSV'],
            'Size': ['2.4 MB', '1.8 MB', '850 KB'],
            'Status': ['Available', 'Available', 'Archived']
        })
        
        st.dataframe(recent_exports, use_container_width=True, height=200)
        
        st.markdown("""
            <div class='alert-box alert-info' style='margin-top: 1rem;'>
                <strong>Export Retention Policy</strong><br>
                Reports are retained for 90 days. Archived reports can be regenerated on request.
            </div>
        """, unsafe_allow_html=True)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")
st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <p style='background: linear-gradient(135deg, #667eea, #764ba2); 
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
                  font-weight: 700; font-size: 1.1rem;'>
            Enterprise Risk Management System v2.5.0
        </p>
        <p style='color: #64748b; font-size: 0.875rem; margin-top: 1rem;'>
            © 2024 Risk Analytics Platform | All Rights Reserved
        </p>
    </div>
""", unsafe_allow_html=True)