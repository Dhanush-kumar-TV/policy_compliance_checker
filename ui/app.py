import streamlit as st
import json
import os
import sys

# Ensure project root is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from state.state_machine import StateMachine, ComplianceState

# ---------------------------------------------------------
# CSS THEMES (Larger fonts, bolder text, vibrant colors)
# ---------------------------------------------------------

THEME_CSS = """
<style>
  /* ── Google Fonts: Inter (Global) ── */
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

  /* ── Animations ── */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* ── Global Reset ── */
  html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], [data-testid="stHeader"] {
    background-color: #101622 !important;
    color: #f1f5f9 !important;
    font-family: 'Inter', sans-serif !important;
  }
  
  [data-testid="stSidebar"] {
    background-color: #101622 !important;
    border-right: 1px solid #2d3a54 !important;
  }

  /* ── Page Header ── */
  .app-header {
    font-size: 2.5rem;
    font-weight: 900;
    color: #f1f5f9;
    letter-spacing: -0.03em;
    padding-bottom: 1rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid #2d3a54;
    animation: fadeIn 0.6s ease-out;
  }

  /* ── Panel Labels ── */
  .panel-label {
    font-size: 0.75rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #475569;
    margin: 2rem 0 1rem 0;
  }

  /* ── Cards ── */
  .bw-card {
    background-color: #1a2233;
    border: 1px solid #2d3a54;
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  }
  .bw-card:hover {
    border-color: #1152d4;
    transform: translateY(-2px);
  }

  /* ── State Badges ── */
  .state-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.5rem 1rem;
    border-radius: 1rem;
    background-color: #1a2233;
    border: 1px solid #2d3a54;
    color: #94a3b8;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
    transition: all 0.3s ease;
  }
  .state-badge.active {
    background-color: #1152d4;
    color: #ffffff;
    border-color: #1152d4;
    box-shadow: 0 0 15px rgba(17, 82, 212, 0.4);
  }
  .state-badge.error {
    background-color: #ef4444;
    color: #ffffff;
    border-color: #ef4444;
  }
  .state-badge.done {
    background-color: rgba(16, 185, 129, 0.1);
    color: #10b981;
    border-color: rgba(16, 185, 129, 0.2);
  }

  /* ── Indicators ── */
  .violation-critical { border-left: 4px solid #ef4444; background: rgba(239, 68, 68, 0.05); padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.5rem; }
  .violation-high { border-left: 4px solid #f97316; background: rgba(249, 115, 22, 0.05); padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.5rem; }
  .violation-medium { border-left: 4px solid #eab308; background: rgba(234, 179, 8, 0.05); padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.5rem; }
  .violation-low { border-left: 4px solid #3b82f6; background: rgba(59, 130, 246, 0.05); padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.5rem; }

  /* ── Buttons ── */
  div[data-testid="stButton"] button {
    border-radius: 0.75rem !important;
    font-weight: 700 !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.3s ease !important;
  }
  div[data-testid="stButton"] button[kind="primary"] {
    background-color: #1152d4 !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(17, 82, 212, 0.3) !important;
  }
  div[data-testid="stButton"] button[kind="primary"]:hover {
    background-color: #1a5fff !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 16px rgba(17, 82, 212, 0.4) !important;
  }
  div[data-testid="stButton"] button[kind="secondary"] {
    background-color: #1a2233 !important;
    color: #f1f5f9 !important;
    border: 1px solid #2d3a54 !important;
  }
  div[data-testid="stButton"] button[kind="secondary"]:hover {
    border-color: #1152d4 !important;
    color: #1152d4 !important;
  }

  /* ── Form Inputs ── */
  .stTextArea textarea, .stNumberInput input, .stSelectbox select {
    background-color: #1a2233 !important;
    border: 1px solid #2d3a54 !important;
    border-radius: 0.5rem !important;
    color: #f1f5f9 !important;
  }
  .stTextArea textarea:focus {
    border-color: #1152d4 !important;
    box-shadow: 0 0 0 2px rgba(17, 82, 212, 0.2) !important;
  }

  /* ── Metrics ── */
  [data-testid="stMetric"] {
    background-color: #1a2233;
    border: 1px solid #2d3a54;
    border-radius: 0.75rem;
    padding: 1.5rem !important;
  }
  [data-testid="stMetricLabel"] {
    font-weight: 700 !important;
    color: #94a3b8 !important;
    text-transform: uppercase !important;
    font-size: 0.75rem !important;
  }
  [data-testid="stMetricValue"] {
    font-weight: 900 !important;
    color: #f1f5f9 !important;
  }
  
  /* ── Progress ── */
  .stProgress > div > div {
    background-color: #1152d4 !important;
  }
  
  /* ── Sidebar Nav ── */
  [data-testid="stSidebarNav"] span {
    font-weight: 600 !important;
    color: #94a3b8 !important;
  }
  [data-testid="stSidebarNav"] a[aria-current="page"] span {
    color: #ffffff !important;
  }

  /* ── Native Container Override (Matching bw-card) ── */
  div[data-testid="element-container"]:has(div.stVerticalBlockBorderWrapper) > div.stVerticalBlockBorderWrapper {
    background-color: #1a2233 !important;
    border: 1px solid #2d3a54 !important;
    border-radius: 0.75rem !important;
    padding: 1.5rem !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
    transition: all 0.3s ease !important;
  }
  div.stVerticalBlockBorderWrapper:hover {
    border-color: #1152d4 !important;
  }
</style>
"""

LIGHT_THEME_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
  @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

  html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], [data-testid="stHeader"] {
    background-color: #f6f6f8 !important;
    color: #0f172a !important;
    font-family: 'Inter', sans-serif !important;
  }
  
  [data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
  }

  /* ── Page Header ── */
  .app-header {
    font-size: 2.5rem;
    font-weight: 900;
    color: #0f172a;
    padding-bottom: 1rem;
    margin-bottom: 2rem;
    border-bottom: 1px solid #e2e8f0;
  }

  /* ── Cards ── */
  .bw-card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 0.75rem;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  /* ── State Badges ── */
  .state-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.5rem 1rem;
    border-radius: 1rem;
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    color: #64748b;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
  }
  .state-badge.active {
    background-color: #1152d4;
    color: #ffffff;
    border-color: #1152d4;
  }

  /* ── Buttons ── */
  div[data-testid="stButton"] button[kind="primary"] {
    background-color: #1152d4 !important;
    color: white !important;
    border: none !important;
    border-radius: 0.75rem !important;
  }
  
  div[data-testid="stButton"] button[kind="secondary"] {
    background-color: #ffffff !important;
    color: #475569 !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 0.75rem !important;
  }
</style>
"""



BW_CHART_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#94a3b8", "family": "Inter, sans-serif", "size": 14},
        "xaxis": {"gridcolor": "rgba(255,255,255,0.1)", "linecolor": "rgba(255,255,255,0.2)", "tickcolor": "#64748b"},
        "yaxis": {"gridcolor": "rgba(255,255,255,0.1)", "linecolor": "rgba(255,255,255,0.2)", "tickcolor": "#64748b"},
        "colorway": ["#f472b6", "#8b5cf6", "#38bdf8", "#10b981", "#fbbf24"],
    }
}

# ---------------------------------------------------------
# LOAD CONFIG & RULES (Shared)
# ---------------------------------------------------------
@st.cache_data
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

@st.cache_data
def load_rules(path):
    with open(path, "r") as f:
        return json.load(f)

# ---------------------------------------------------------
# MAIN APP ROUTER
# ---------------------------------------------------------

def main():
    st.set_page_config(page_title="Policy Compliance Checker", layout="wide", initial_sidebar_state="expanded")
    
    # Initialize global state
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"
    if "run_id" not in st.session_state:
        st.session_state.run_id = None
    if "report" not in st.session_state:
        st.session_state.report = None
    if "transcript" not in st.session_state:
        st.session_state.transcript = []
    if "state_machine" not in st.session_state:
        st.session_state.state_machine = StateMachine()
    if "stop_requested" not in st.session_state:
        st.session_state.stop_requested = False

    # Render CSS globally
    if st.session_state.theme == "light":
        st.markdown(LIGHT_THEME_CSS, unsafe_allow_html=True)
    else:
        st.markdown(THEME_CSS, unsafe_allow_html=True)

    # Sidebar Theme Control
    with st.sidebar:
        st.markdown("## Global Controls")
        if st.button("☀/☾ TOGGLE THEME", type="secondary"):
             st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
             st.rerun()

    # Define Multi-Page Structure
    pg = st.navigation([
        st.Page("pages/1_Input.py", title="1. Config & Input", icon="📄"),
        st.Page("pages/2_Activity.py", title="2. Agent Activity", icon="🤖"),
        st.Page("pages/3_Report.py", title="3. Compliance Report", icon="🛡️"),
        st.Page("pages/4_Advanced_Analysis.py", title="4. Advanced Analysis", icon="📊")
    ])

    pg.run()

if __name__ == "__main__":
    main()
