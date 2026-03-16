import sys
import re

with open('ui/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Replace the massive CSS block and BW_CHART_TEMPLATE
PREFIX_STR = 'THEME_CSS = """'
SUFFIX_STR = 'st.set_page_config('

start_idx = text.find(PREFIX_STR)
end_idx = text.find(SUFFIX_STR)

if start_idx == -1 or end_idx == -1:
    print("Could not find the bounds for CSS replacement.")
    sys.exit(1)

prefix = text[:start_idx]
suffix = text[end_idx:]

new_css = '''THEME_CSS = """
<style>
  /* ── Google Fonts: Outfit (display) + Inter (body) ── */
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Inter:wght@400;500;600&display=swap');

  /* ── Animations ── */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* ── Global Reset ── */
  html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], [data-testid="stHeader"] {
    background: linear-gradient(135deg, #0f172a 0%, #020617 100%) !important;
    background-attachment: fixed !important;
    color: #f8fafc !important;
    font-family: 'Inter', sans-serif !important;
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.8) !important;
    backdrop-filter: blur(10px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
  }

  /* ── Page Header ── */
  .app-header {
    font-family: 'Outfit', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #38bdf8, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 0.8rem;
    margin-bottom: 2rem;
    animation: fadeIn 0.6s ease-out;
  }

  /* ── Section Labels ── */
  .panel-label {
    font-family: 'Outfit', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #94a3b8;
    border-left: 3px solid #38bdf8;
    padding-left: 1rem;
    margin-bottom: 1.5rem;
    margin-top: 2.5rem;
    animation: fadeIn 0.6s ease-out;
  }

  /* ── Cards / Boxes ── */
  .bw-card {
    background: rgba(30, 41, 59, 0.5);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.8rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeIn 0.6s ease-out backwards;
  }
  .bw-card:hover {
    border-color: rgba(56, 189, 248, 0.4);
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4), 0 0 20px rgba(56, 189, 248, 0.1);
  }

  /* ── State Badge ── */
  .state-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.5rem 1.2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    color: #64748b;
    background: rgba(15, 23, 42, 0.6);
    letter-spacing: 0.05em;
    margin-right: 0.6rem;
    margin-bottom: 0.6rem;
    transition: all 0.3s ease;
  }
  .state-badge.active {
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    color: #ffffff;
    border-color: transparent;
    box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4);
    transform: scale(1.05);
  }
  .state-badge.error {
    background: linear-gradient(135deg, #ef4444, #b91c1c);
    color: #ffffff;
    border-color: transparent;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);
  }
  .state-badge.done {
    border-color: rgba(52, 211, 153, 0.4);
    color: #34d399;
    background: rgba(16, 185, 129, 0.1);
  }

  /* ── Score Display ── */
  .score-large {
    font-family: 'Outfit', sans-serif;
    font-size: 6.5rem;
    font-weight: 800;
    background: linear-gradient(180deg, #ffffff, #e2e8f0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    letter-spacing: -0.04em;
    filter: drop-shadow(0 4px 20px rgba(255,255,255,0.1));
  }
  .grade-badge {
    font-family: 'Outfit', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 5rem;
    height: 5rem;
    border: 3px solid transparent;
    background: linear-gradient(#0f172a, #0f172a) padding-box, 
                linear-gradient(135deg, #38bdf8, #c084fc) border-box;
    border-radius: 50%;
    color: #f8fafc;
    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.2);
  }

  /* ── Violation Severity Rows ── */
  .violation-critical { border-left: 4px solid #ef4444; color: #f8fafc; margin-bottom: 0.8rem; background: linear-gradient(90deg, rgba(239, 68, 68, 0.15) 0%, rgba(30, 41, 59, 0) 100%); padding: 1.2rem; border-radius: 0 8px 8px 0; }
  .violation-high     { border-left: 4px solid #f97316; color: #e2e8f0; margin-bottom: 0.8rem; background: linear-gradient(90deg, rgba(249, 115, 22, 0.1) 0%, rgba(30, 41, 59, 0) 100%); padding: 1.2rem; border-radius: 0 8px 8px 0; }
  .violation-medium   { border-left: 4px solid #eab308; color: #cbd5e1; margin-bottom: 0.8rem; background: linear-gradient(90deg, rgba(234, 179, 8, 0.05) 0%, rgba(30, 41, 59, 0) 100%); padding: 1.2rem; border-radius: 0 8px 8px 0; }
  .violation-low      { border-left: 4px solid #3b82f6; color: #94a3b8; margin-bottom: 0.8rem; background: linear-gradient(90deg, rgba(59, 130, 246, 0.05) 0%, rgba(30, 41, 59, 0) 100%); padding: 1.2rem; border-radius: 0 8px 8px 0; }

  /* ── Buttons ── */
  .stButton > button {
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%) !important;
    color: #ffffff !important;
    border: none !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 2rem !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(56, 189, 248, 0.3) !important;
  }
  .stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(56, 189, 248, 0.5) !important;
    filter: brightness(1.1);
  }
  .stButton.reset-btn > button {
    background: rgba(30, 41, 59, 0.8) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    box-shadow: none !important;
  }
  .stButton.reset-btn > button:hover {
    background: rgba(51, 65, 85, 0.8) !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
  }

  /* ── Inputs ── */
  .stTextArea textarea, .stNumberInput input, .stSelectbox select {
    background: rgba(15, 23, 42, 0.6) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    padding: 1rem !important;
    transition: all 0.3s ease !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.2) !important;
  }
  .stTextArea textarea:focus, .stNumberInput input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2), inset 0 2px 4px rgba(0,0,0,0.2) !important;
    outline: none !important;
  }

  /* ── Expanders ── */
  .streamlit-expanderHeader {
    background: rgba(30, 41, 59, 0.4) !important;
    backdrop-filter: blur(8px) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
  }
  .streamlit-expanderHeader:hover {
    background: rgba(51, 65, 85, 0.6) !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
  }

  /* ── Progress Bar ── */
  .stProgress > div > div {
    background: linear-gradient(90deg, #38bdf8, #c084fc) !important;
    border-radius: 6px !important;
    box-shadow: 0 0 10px rgba(56, 189, 248, 0.5) !important;
  }
  .stProgress > div {
    background-color: rgba(30, 41, 59, 0.8) !important;
    border-radius: 6px !important;
    height: 8px !important;
    overflow: hidden !important;
  }

  /* ── Metrics ── */
  [data-testid="stMetric"] {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
  }
  [data-testid="stMetric"]:hover {
    border-color: rgba(139, 92, 246, 0.4);
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3), 0 0 20px rgba(139, 92, 246, 0.15);
  }
  [data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    margin-bottom: 0.5rem !important;
  }
  [data-testid="stMetricValue"] {
    font-family: 'Outfit', sans-serif !important;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    font-size: 2.8rem !important;
    font-weight: 800 !important;
  }

  /* ── Dividers ── */
  hr { border-color: rgba(255, 255, 255, 0.1) !important; }

  /* ── Plotly charts ── */
  .js-plotly-plot .plotly { background: transparent !important; }
  
  /* ── Table Styling ── */
  table {
    border-collapse: separate !important;
    border-spacing: 0 !important;
    width: 100% !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    background: rgba(15, 23, 42, 0.4) !important;
  }
  th {
    background: rgba(30, 41, 59, 0.8) !important;
    color: #94a3b8 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
    padding: 1.2rem 1rem !important;
    text-transform: uppercase;
  }
  td {
    background: transparent !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    padding: 1rem !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
  }
  tr:last-child td {
    border-bottom: none !important;
  }
  tr:hover td {
    background: rgba(255, 255, 255, 0.03) !important;
  }
</style>
"""

LIGHT_THEME_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Inter:wght@400;500;600&display=swap');

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], [data-testid="stHeader"] {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%) !important;
    background-attachment: fixed !important;
    color: #0f172a !important;
    font-family: 'Inter', sans-serif !important;
  }
  [data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.8) !important;
    backdrop-filter: blur(10px) !important;
    border-right: 1px solid rgba(0, 0, 0, 0.05) !important;
  }
  .app-header {
    font-family: 'Outfit', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #2563eb, #6366f1, #9333ea);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    padding-bottom: 0.8rem;
    margin-bottom: 2rem;
    animation: fadeIn 0.6s ease-out;
  }
  .panel-label {
    font-family: 'Outfit', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #64748b;
    border-left: 3px solid #2563eb;
    padding-left: 1rem;
    margin-bottom: 1.5rem;
    margin-top: 2.5rem;
    animation: fadeIn 0.6s ease-out;
  }
  .bw-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-radius: 12px;
    padding: 1.8rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeIn 0.6s ease-out backwards;
  }
  .bw-card:hover { 
    border-color: rgba(99, 102, 241, 0.4); 
    transform: translateY(-4px); 
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08), 0 0 20px rgba(99, 102, 241, 0.1);
  }
  .state-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.5rem 1.2rem;
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-radius: 20px;
    color: #64748b;
    background: rgba(255, 255, 255, 0.8);
    letter-spacing: 0.05em;
    margin-right: 0.6rem;
    margin-bottom: 0.6rem;
    transition: all 0.3s ease;
  }
  .state-badge.active {
    background: linear-gradient(135deg, #3b82f6, #6366f1);
    color: #ffffff;
    border-color: transparent;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    transform: scale(1.05);
  }
  .state-badge.error { background: linear-gradient(135deg, #ef4444, #b91c1c); color: #ffffff; border-color: transparent; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3); }
  .state-badge.done { border-color: rgba(16, 185, 129, 0.3); color: #059669; background: rgba(16, 185, 129, 0.1); }
  .score-large {
    font-family: 'Outfit', sans-serif;
    font-size: 6.5rem;
    font-weight: 800;
    background: linear-gradient(180deg, #1e293b, #475569);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    letter-spacing: -0.04em;
    filter: drop-shadow(0 2px 10px rgba(0,0,0,0.05));
  }
  .grade-badge {
    font-family: 'Outfit', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 5rem;
    height: 5rem;
    border: 3px solid transparent;
    background: linear-gradient(#ffffff, #ffffff) padding-box, 
                linear-gradient(135deg, #3b82f6, #a855f7) border-box;
    border-radius: 50%;
    color: #1e293b;
    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.15);
  }
  .violation-critical { border-left: 4px solid #ef4444; color: #7f1d1d; margin-bottom: 0.8rem; background: linear-gradient(90deg, rgba(239, 68, 68, 0.1) 0%, rgba(255, 255, 255, 0) 100%); padding: 1.2rem; border-radius: 0 8px 8px 0; }
  .violation-high     { border-left: 4px solid #f97316; color: #9a3412; margin-bottom: 0.8rem; background: linear-gradient(90deg, rgba(249, 115, 22, 0.08) 0%, rgba(255, 255, 255, 0) 100%); padding: 1.2rem; border-radius: 0 8px 8px 0; }
  .violation-medium   { border-left: 4px solid #eab308; color: #854d0e; margin-bottom: 0.8rem; background: linear-gradient(90deg, rgba(234, 179, 8, 0.08) 0%, rgba(255, 255, 255, 0) 100%); padding: 1.2rem; border-radius: 0 8px 8px 0; }
  .violation-low      { border-left: 4px solid #3b82f6; color: #1e40af; margin-bottom: 0.8rem; background: linear-gradient(90deg, rgba(59, 130, 246, 0.05) 0%, rgba(255, 255, 255, 0) 100%); padding: 1.2rem; border-radius: 0 8px 8px 0; }
  
  .stButton > button {
    background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%) !important;
    color: #ffffff !important;
    border: none !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 2rem !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.25) !important;
  }
  .stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
    filter: brightness(1.1);
  }
  .stButton.reset-btn > button {
    background: rgba(255, 255, 255, 0.8) !important;
    color: #0f172a !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
  }
  .stButton.reset-btn > button:hover {
    background: rgba(241, 245, 249, 1) !important;
    border-color: rgba(0, 0, 0, 0.2) !important;
  }
  .stTextArea textarea, .stNumberInput input, .stSelectbox select {
    background: rgba(255, 255, 255, 0.8) !important;
    color: #0f172a !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    padding: 1rem !important;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.02) !important;
    transition: all 0.3s ease !important;
  }
  .stTextArea textarea:focus, .stNumberInput input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2), inset 0 2px 4px rgba(0,0,0,0.02) !important;
    outline: none !important;
  }
  .streamlit-expanderHeader {
    background: rgba(255, 255, 255, 0.6) !important;
    backdrop-filter: blur(8px) !important;
    color: #1e293b !important;
    border: 1px solid rgba(0, 0, 0, 0.05) !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
  }
  .streamlit-expanderHeader:hover {
    background: rgba(241, 245, 249, 0.8) !important;
    border-color: rgba(0, 0, 0, 0.1) !important;
  }
  .stProgress > div > div { background: linear-gradient(90deg, #3b82f6, #9333ea) !important; border-radius: 6px !important; box-shadow: 0 0 10px rgba(59, 130, 246, 0.3) !important; }
  .stProgress > div { background-color: rgba(0, 0, 0, 0.05) !important; border-radius: 6px !important; height: 8px !important; overflow: hidden !important; }
  [data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.5);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.04);
    transition: all 0.3s ease;
  }
  [data-testid="stMetric"]:hover { border-color: rgba(99, 102, 241, 0.3); transform: translateY(-4px); box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08), 0 0 20px rgba(99, 102, 241, 0.1); }
  [data-testid="stMetricLabel"] { font-family: 'Inter', sans-serif !important; color: #64748b !important; font-size: 0.85rem !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; }
  [data-testid="stMetricValue"] { font-family: 'Outfit', sans-serif !important; background: linear-gradient(90deg, #2563eb, #6366f1); -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; font-size: 2.8rem !important; font-weight: 800 !important; }
  hr { border-color: rgba(0, 0, 0, 0.05) !important; }
  table { border-collapse: separate !important; border-spacing: 0 !important; width: 100% !important; border-radius: 12px !important; overflow: hidden !important; border: 1px solid rgba(0, 0, 0, 0.05) !important; background: rgba(255, 255, 255, 0.4) !important; }
  th { background: rgba(248, 250, 252, 0.8) !important; color: #475569 !important; font-family: 'Outfit', sans-serif !important; font-size: 0.9rem !important; font-weight: 600 !important; letter-spacing: 0.05em !important; border-bottom: 2px solid rgba(0, 0, 0, 0.05) !important; padding: 1.2rem 1rem !important; text-transform: uppercase; }
  td { background: transparent !important; border-bottom: 1px solid rgba(0, 0, 0, 0.02) !important; padding: 1rem !important; color: #1e293b !important; font-family: 'Inter', sans-serif !important; font-size: 0.95rem !important; }
  tr:last-child td { border-bottom: none !important; }
  tr:hover td { background: rgba(255, 255, 255, 0.5) !important; }
</style>
"""

BW_CHART_TEMPLATE = {
    "layout": {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {"color": "#94a3b8", "family": "Inter, sans-serif"},
        "xaxis": {"gridcolor": "rgba(255,255,255,0.05)", "linecolor": "rgba(255,255,255,0.1)", "tickcolor": "#64748b"},
        "yaxis": {"gridcolor": "rgba(255,255,255,0.05)", "linecolor": "rgba(255,255,255,0.1)", "tickcolor": "#64748b"},
        "colorway": ["#38bdf8", "#818cf8", "#c084fc", "#34d399", "#fbbf24"],
    }
}
'''

text = prefix + new_css + suffix

# 2. Update specific lines to reflect the aesthetics
text = text.replace(
    'st.markdown(f"<div style=\'font-family:Syne;font-size:1.5rem;color:#FFF;\'>{active_agent}</div>", unsafe_allow_html=True)',
    'st.markdown(f"<div style=\'font-family:Outfit, sans-serif;font-size:1.6rem;font-weight:800;color:#38bdf8;text-shadow:0 0 10px rgba(56,189,248,0.3);\'>{active_agent}</div>", unsafe_allow_html=True)'
)

text = text.replace(
    'fig_bar = go.Figure(data=[go.Bar(x=cats, y=counts, marker_color=["#FFFFFF", "#888888"]*(len(cats)//2 + 1))])',
    'fig_bar = go.Figure(data=[go.Bar(x=cats, y=counts, marker_color=["#38bdf8", "#818cf8", "#c084fc", "#e879f9", "#34d399", "#fbbf24"]*(len(cats)//2 + 1))])'
)

text = text.replace(
    'fig_line = go.Figure(data=[go.Scatter(x=[1], y=[rep[\'compliance_score\']], mode="lines+markers", \n                                              line=dict(color="#FFFFFF"), marker=dict(symbol="circle-open", size=10, color="#FFFFFF"))])',
    'fig_line = go.Figure(data=[go.Scatter(x=[1], y=[rep[\'compliance_score\']], mode="lines+markers", \n                                              line=dict(color="#38bdf8", width=3), marker=dict(symbol="circle", size=12, color="#818cf8"))])'
)

# Gauge Chart string replacements
gauge_original = """            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#FFFFFF"},
                "bar": {"color": "#FFFFFF"},
                "bgcolor": "#111111",
                "bordercolor": "#333333",
                "steps": [
                    {"range": [0, 40],  "color": "#1A1A1A"},
                    {"range": [40, 60], "color": "#222222"},
                    {"range": [60, 80], "color": "#2A2A2A"},
                    {"range": [80, 100],"color": "#333333"},
                ],
            },
            number={"font": {"color": "#FFFFFF", "family": "Syne", "size": 48}},
        ))
        fig.update_layout(paper_bgcolor="#000000", font_color="#FFFFFF", height=300)"""

gauge_new = """            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#64748b"},
                "bar": {"color": "#38bdf8"},
                "bgcolor": "rgba(15, 23, 42, 0.5)",
                "bordercolor": "rgba(255, 255, 255, 0.1)",
                "steps": [
                    {"range": [0, 40],  "color": "rgba(239, 68, 68, 0.3)"},
                    {"range": [40, 60], "color": "rgba(249, 115, 22, 0.3)"},
                    {"range": [60, 80], "color": "rgba(234, 179, 8, 0.3)"},
                    {"range": [80, 100],"color": "rgba(52, 211, 153, 0.3)"},
                ],
            },
            number={"font": {"color": "#38bdf8", "family": "Outfit", "size": 48}},
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="#e2e8f0", height=300)"""

text = text.replace(gauge_original, gauge_new)

with open('ui/app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("UI successfully updated.")
