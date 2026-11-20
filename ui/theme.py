"""
PulsePoint Cyber-Medical Intelligence System
Futuristic Cyber-Medical Theme, Custom CSS & Plotly Layout Specifications
"""

import plotly.graph_objects as go
import plotly.io as pio

# Cyber-Medical Color Palette Tokens
COLOR_BG_DARK = "#070b19"
COLOR_SURFACE_CARD = "rgba(13, 23, 48, 0.78)"
COLOR_CARD_BORDER = "rgba(0, 242, 254, 0.22)"
COLOR_CYAN_ACCENT = "#00f2fe"
COLOR_NEON_BLUE = "#4facfe"
COLOR_PURPLE_ACCENT = "#a855f7"
COLOR_SUCCESS_GREEN = "#00f5a0"
COLOR_WARNING_AMBER = "#ffaa00"
COLOR_ALERT_RED = "#ff3366"
COLOR_TEXT_PRIMARY = "#f0f6fc"
COLOR_TEXT_MUTED = "#8b949e"

CYBER_MEDICAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Rajdhani:wght@500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

/* Global Reset & Futuristic Background with High-Tech Grid */
.stApp {
    background-color: #070b19 !important;
    background-image: 
        radial-gradient(circle at 10% 15%, rgba(0, 242, 254, 0.08) 0%, transparent 45%),
        radial-gradient(circle at 90% 85%, rgba(168, 85, 247, 0.07) 0%, transparent 50%),
        linear-gradient(rgba(0, 242, 254, 0.015) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 242, 254, 0.015) 1px, transparent 1px),
        linear-gradient(180deg, #070b19 0%, #0a1128 100%) !important;
    background-size: 100% 100%, 100% 100%, 40px 40px, 40px 40px, 100% 100% !important;
    font-family: 'Outfit', 'Inter', -apple-system, sans-serif !important;
    color: #f0f6fc !important;
}

/* Hide Default UI Chrome, Toolbars, Watermarks & Auto-Generated Multi-Page Sidebar List */
#MainMenu {visibility: hidden !important; display: none !important;}
footer {visibility: hidden !important; display: none !important;}
header {visibility: hidden !important;}
[data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
[data-testid="stDecoration"] {visibility: hidden !important; display: none !important;}
[data-testid="stStatusWidget"] {visibility: hidden !important; display: none !important;}
[data-testid="stSidebarNav"] {display: none !important;}
div[data-testid="stSidebarNavItems"] {display: none !important;}
div[data-testid="stSidebarNavSeparator"] {display: none !important;}
.viewerBadge_container__r5tak {display: none !important;}
.styles_viewerBadge__CvC9N {display: none !important;}

/* High-Tech Animated Glowing Border Card */
.cyber-card {
    background: rgba(13, 23, 48, 0.78) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(0, 242, 254, 0.22) !important;
    border-radius: 14px !important;
    padding: 1.25rem !important;
    margin-bottom: 1.2rem !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45), 0 0 1px 1px rgba(0, 242, 254, 0.12) !important;
    transition: all 0.28s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    overflow: hidden !important;
}

.cyber-card:hover {
    border-color: rgba(0, 242, 254, 0.55) !important;
    box-shadow: 0 14px 44px 0 rgba(0, 0, 0, 0.65), 0 0 18px rgba(0, 242, 254, 0.25) !important;
    transform: translateY(-2px) !important;
}

/* Glowing Corner Accents */
.cyber-card::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 24px;
    height: 24px;
    border-top: 2px solid #00f2fe;
    border-right: 2px solid #00f2fe;
    border-top-right-radius: 12px;
    opacity: 0.6;
}

/* Futuristic KPI Metric Card */
.kpi-container {
    background: linear-gradient(135deg, rgba(16, 32, 68, 0.82) 0%, rgba(9, 18, 38, 0.90) 100%) !important;
    border: 1px solid rgba(0, 242, 254, 0.25) !important;
    border-radius: 12px !important;
    padding: 1.15rem 1.25rem !important;
    position: relative !important;
    overflow: hidden !important;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
    transition: transform 0.2s ease, border-color 0.2s ease !important;
}

.kpi-container:hover {
    transform: translateY(-2px) !important;
    border-color: rgba(0, 242, 254, 0.6) !important;
}

.kpi-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg, #00f2fe 0%, #4facfe 100%);
    box-shadow: 0 0 10px #00f2fe;
}

.kpi-title {
    font-size: 0.80rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: #8b949e !important;
    margin-bottom: 0.35rem !important;
}

.kpi-value {
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    letter-spacing: -0.02em !important;
    line-height: 1.1 !important;
    font-family: 'Rajdhani', 'Outfit', sans-serif !important;
    text-shadow: 0 0 12px rgba(0, 242, 254, 0.3) !important;
}

.kpi-subtext {
    font-size: 0.78rem !important;
    margin-top: 0.4rem !important;
    font-weight: 600 !important;
}

/* Glassmorphism Badge Pills */
.status-pill {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.pill-critical {
    background: rgba(255, 51, 102, 0.20);
    color: #ff3366;
    border: 1px solid rgba(255, 51, 102, 0.55);
    box-shadow: 0 0 12px rgba(255, 51, 102, 0.35);
    animation: pulse-critical 2s infinite;
}

@keyframes pulse-critical {
    0%, 100% { box-shadow: 0 0 8px rgba(255, 51, 102, 0.2); }
    50% { box-shadow: 0 0 18px rgba(255, 51, 102, 0.6); }
}

.pill-high {
    background: rgba(255, 170, 0, 0.20);
    color: #ffaa00;
    border: 1px solid rgba(255, 170, 0, 0.55);
}

.pill-normal {
    background: rgba(0, 245, 160, 0.18);
    color: #00f5a0;
    border: 1px solid rgba(0, 245, 160, 0.45);
    box-shadow: 0 0 8px rgba(0, 245, 160, 0.2);
}

.pill-info {
    background: rgba(0, 242, 254, 0.18);
    color: #00f2fe;
    border: 1px solid rgba(0, 242, 254, 0.45);
    box-shadow: 0 0 8px rgba(0, 242, 254, 0.2);
}

/* Ticker Bar */
.telemetry-ticker {
    background: rgba(10, 20, 44, 0.85);
    border: 1px solid rgba(0, 242, 254, 0.25);
    border-radius: 8px;
    padding: 7px 14px;
    font-size: 0.78rem;
    font-family: 'Rajdhani', monospace;
    font-weight: 600;
    letter-spacing: 0.06em;
    color: #00f2fe;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
}

/* Inputs, Selectors & Buttons Styling */
div[data-baseweb="select"] {
    background-color: rgba(14, 24, 50, 0.92) !important;
    border-color: rgba(0, 242, 254, 0.28) !important;
}

div[data-baseweb="select"]:hover {
    border-color: #00f2fe !important;
    box-shadow: 0 0 10px rgba(0, 242, 254, 0.2) !important;
}

.stButton>button {
    background: linear-gradient(135deg, rgba(0, 242, 254, 0.18) 0%, rgba(79, 172, 254, 0.28) 100%) !important;
    color: #00f2fe !important;
    border: 1px solid rgba(0, 242, 254, 0.45) !important;
    border-radius: 9px !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    padding: 0.55rem 1.35rem !important;
    transition: all 0.22s ease !important;
}

.stButton>button:hover {
    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
    color: #070b19 !important;
    box-shadow: 0 0 20px rgba(0, 242, 254, 0.55) !important;
    transform: translateY(-1px) !important;
}

/* Sidebar Customization */
section[data-testid="stSidebar"] {
    background-color: #050813 !important;
    border-right: 1px solid rgba(0, 242, 254, 0.20) !important;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4) !important;
}

/* Smooth Keyframe Entrance & Hover Animations for Streamlit */
@keyframes stFadeInUp {
    from {
        opacity: 0;
        transform: translateY(18px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes stPulseBorder {
    0%, 100% { border-color: rgba(0, 242, 254, 0.28); }
    50% { border-color: rgba(0, 242, 254, 0.68); }
}

.cyber-card, .kpi-container, div[data-testid="stPlotlyChart"], div[data-testid="stMetric"] {
    animation: stFadeInUp 0.55s cubic-bezier(0.16, 1, 0.3, 1) both !important;
}

.scenario-banner-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 18px;
    animation: stFadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
}

.scenario-banner-card {
    background: linear-gradient(135deg, rgba(15, 29, 62, 0.86) 0%, rgba(9, 17, 38, 0.92) 100%);
    border: 1px solid rgba(0, 242, 254, 0.26);
    border-radius: 12px;
    padding: 14px 16px;
    transition: all 0.25s ease;
    animation: stPulseBorder 4s infinite ease-in-out;
}

.scenario-banner-card:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 12px 28px rgba(0, 242, 254, 0.22);
    border-color: #00f2fe;
}
</style>
"""


def apply_plotly_cyber_theme(fig: go.Figure) -> go.Figure:
    """Applies unified cyber-medical styling and responsive margins to Plotly figures."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10, 18, 38, 0.5)",
        font=dict(family="Outfit, Rajdhani, Inter, sans-serif", color="#e6edf3", size=11),
        margin=dict(l=40, r=30, t=50, b=40),
        xaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.06)",
            linecolor="rgba(0, 242, 254, 0.25)",
            tickfont=dict(color="#8b949e", size=10),
            title_font=dict(color="#00f2fe", size=11)
        ),
        yaxis=dict(
            gridcolor="rgba(255, 255, 255, 0.06)",
            linecolor="rgba(0, 242, 254, 0.25)",
            tickfont=dict(color="#8b949e", size=10),
            title_font=dict(color="#00f2fe", size=11)
        ),
        legend=dict(
            bgcolor="rgba(11, 20, 42, 0.8)",
            bordercolor="rgba(0, 242, 254, 0.25)",
            borderwidth=1,
            font=dict(color="#e6edf3", size=10)
        ),
        title_font=dict(color="#ffffff", size=13, family="Outfit, sans-serif")
    )
    return fig
