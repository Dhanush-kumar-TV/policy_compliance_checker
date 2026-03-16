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
  /* ── Google Fonts: Outfit (display) + Inter (body) ── */
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800;900&family=Inter:wght@500;600;700&display=swap');

  /* ── Animations ── */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* ── Global Reset ── */
  html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], [data-testid="stHeader"] {
    background: linear-gradient(135deg, #020617 0%, #0f172a 100%) !important;
    background-attachment: fixed !important;
    color: #f8fafc !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.1rem !important;
  }
  
  /* High contrast for all text */
  p, div, li, span, label {
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    line-height: 1.6;
    color: #f8fafc !important;
  }

  /* Explicit labels styling */
  [data-testid="stWidgetLabel"] p {
    color: #f1f5f9 !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: rgba(15, 23, 42, 0.8) !important;
    backdrop-filter: blur(10px) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
  }
  
  [data-testid="stSidebarNav"] span {
      font-size: 1.2rem !important;
      font-weight: 700 !important;
      color: #f8fafc !important;
  }

  /* ── Page Header ── */
  .app-header {
    font-family: 'Outfit', sans-serif;
    font-size: 4rem;
    font-weight: 900;
    color: #38bdf8; /* Fallback */
    background: linear-gradient(90deg, #38bdf8, #f472b6, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
    border-bottom: 2px solid rgba(255, 255, 255, 0.2);
    padding-bottom: 1rem;
    margin-bottom: 2.5rem;
    animation: fadeIn 0.6s ease-out;
  }

  /* ── Section Labels ── */
  .panel-label {
    font-family: 'Outfit', sans-serif;
    font-size: 1.3rem;
    font-weight: 900;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #e2e8f0 !important;
    border-left: 6px solid #f472b6;
    padding-left: 1.2rem;
    margin-bottom: 2rem;
    margin-top: 3rem;
    animation: fadeIn 0.6s ease-out;
  }

  /* ── Cards / Boxes ── */
  .bw-card {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 2.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) backwards;
    font-size: 1.15rem;
    font-weight: 600;
  }
  .bw-card:hover {
    border-color: rgba(244, 114, 182, 0.4);
    transform: translateY(-6px) scale(1.01);
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(244, 114, 182, 0.1);
  }

  /* ── State Badge ── */
  .state-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    font-weight: 800;
    padding: 0.8rem 1.8rem;
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 30px;
    color: #94a3b8 !important;
    background: rgba(15, 23, 42, 0.9);
    letter-spacing: 0.05em;
    margin-right: 1rem;
    margin-bottom: 1rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
  }
  .state-badge.active {
    background: linear-gradient(135deg, #f472b6, #818cf8);
    color: #ffffff !important;
    border-color: transparent;
    box-shadow: 0 8px 25px rgba(244, 114, 182, 0.4);
    transform: translateY(-4px) scale(1.1);
  }
  .state-badge.error {
    background: linear-gradient(135deg, #ef4444, #991b1b);
    color: #ffffff !important;
    border-color: transparent;
    box-shadow: 0 8px 25px rgba(239, 68, 68, 0.4);
  }
  .state-badge.done {
    border-color: rgba(16, 185, 129, 0.6);
    color: #34d399 !important;
    background: rgba(16, 185, 129, 0.15);
    box-shadow: 0 4px 20px rgba(16, 185, 129, 0.15);
  }

  /* ── Score Display ── */
  .score-large {
    font-family: 'Outfit', sans-serif;
    font-size: 9rem;
    font-weight: 950;
    color: #ffffff; /* Fallback */
    background: linear-gradient(180deg, #ffffff 30%, #cbd5e1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 0.9;
    letter-spacing: -0.05em;
    filter: drop-shadow(0 4px 20px rgba(255,255,255,0.1));
  }
  .grade-badge {
    font-family: 'Outfit', sans-serif;
    font-size: 4rem;
    font-weight: 900;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 7.5rem;
    height: 7.5rem;
    border: 5px solid transparent;
    background: linear-gradient(#020617, #020617) padding-box, 
                linear-gradient(135deg, #f472b6, #c084fc) border-box;
    border-radius: 50%;
    color: #f8fafc !important;
    box-shadow: 0 15px 40px rgba(244, 114, 182, 0.2);
    animation: fadeIn 1s cubic-bezier(0.16, 1, 0.3, 1);
  }

  /* ── Violation Severity Rows ── */
  .violation-critical { border-left: 8px solid #ff0055; color: #f8fafc !important; margin-bottom: 1.2rem; background: linear-gradient(90deg, rgba(255, 0, 85, 0.15) 0%, rgba(30, 41, 59, 0) 100%); padding: 1.8rem; border-radius: 0 15px 15px 0; font-weight:700; font-size:1.15rem; box-shadow: 0 4px 15px rgba(255, 0, 85, 0.05); }
  .violation-high     { border-left: 8px solid #ff6600; color: #f1f5f9 !important; margin-bottom: 1.2rem; background: linear-gradient(90deg, rgba(255, 102, 0, 0.12) 0%, rgba(30, 41, 59, 0) 100%); padding: 1.8rem; border-radius: 0 15px 15px 0; font-weight:700; font-size:1.15rem; }
  .violation-medium   { border-left: 8px solid #fbbf24; color: #e2e8f0 !important; margin-bottom: 1.2rem; background: linear-gradient(90deg, rgba(251, 191, 36, 0.1) 0%, rgba(30, 41, 59, 0) 100%); padding: 1.8rem; border-radius: 0 15px 15px 0; font-weight:600;}
  .violation-low      { border-left: 8px solid #0ea5e9; color: #94a3b8 !important; margin-bottom: 1.2rem; background: linear-gradient(90deg, rgba(14, 165, 233, 0.08) 0%, rgba(30, 41, 59, 0) 100%); padding: 1.8rem; border-radius: 0 15px 15px 0; font-weight:600;}

  /* ── Buttons ── */
  button[kind="primary"] {
    background: linear-gradient(135deg, #f472b6 0%, #8b5cf6 100%) !important;
    background-size: 200% auto !important;
    color: #ffffff !important;
    border: none !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.25rem !important;
    letter-spacing: 0.08em !important;
    padding: 1rem 3rem !important;
    border-radius: 14px !important;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 10px 30px rgba(244, 114, 182, 0.3) !important;
    text-transform: uppercase;
  }
  button[kind="primary"]:hover {
    background-position: right center !important;
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 15px 40px rgba(244, 114, 182, 0.5) !important;
  }
  button[kind="secondary"] {
    background: rgba(30, 41, 59, 0.7) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    padding: 1rem 2.5rem !important;
    border-radius: 14px !important;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
  }
  button[kind="secondary"]:hover {
    background: rgba(51, 65, 85, 0.9) !important;
    border-color: #f472b6 !important;
    color: #f472b6 !important;
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(244, 114, 182, 0.2) !important;
  }

  /* ── Inputs ── */
  .stTextArea textarea, .stNumberInput input, .stSelectbox select {
    background: rgba(15, 23, 42, 0.8) !important;
    backdrop-filter: blur(8px) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 14px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.15rem !important;
    font-weight: 500 !important;
    padding: 1.4rem !important;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.4) !important;
    transition: all 0.3s ease !important;
  }
  /* Fix visibility for disabled text areas (Transcript) */
  .stTextArea textarea:disabled {
    color: #e2e8f0 !important;
    background: rgba(30, 41, 59, 0.6) !important;
    -webkit-text-fill-color: #e2e8f0 !important;
  }
  .stTextArea textarea:focus, .stNumberInput input:focus {
    border-color: #f472b6 !important;
    box-shadow: 0 0 0 4px rgba(244, 114, 182, 0.2), inset 0 2px 10px rgba(0,0,0,0.4) !important;
    outline: none !important;
  }

  /* ── Expanders ── */
  .streamlit-expanderHeader {
    background: rgba(30, 41, 59, 0.5) !important;
    backdrop-filter: blur(12px) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 14px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    padding: 1.2rem !important;
    transition: all 0.3s ease !important;
  }
  .streamlit-expanderHeader:hover {
    background: rgba(51, 65, 85, 0.8) !important;
    border-color: rgba(244, 114, 182, 0.3) !important;
  }

  /* ── Progress Bar ── */
  .stProgress > div > div {
    background: linear-gradient(90deg, #f472b6, #8b5cf6, #38bdf8) !important;
    border-radius: 10px !important;
    box-shadow: 0 0 20px rgba(244, 114, 182, 0.4) !important;
  }
  .stProgress > div {
    background-color: rgba(15, 23, 42, 0.9) !important;
    border-radius: 10px !important;
    height: 14px !important;
    border: 1px solid rgba(255,255,255,0.05);
  }

  /* ── Metrics ── */
  [data-testid="stMetric"] {
    background: rgba(30, 41, 59, 0.4);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 2.5rem;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  }
  [data-testid="stMetricLabel"] {
    font-family: 'Inter', sans-serif !important;
    color: #94a3b8 !important;
    font-size: 1.2rem !important;
    font-weight: 900 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.18em !important;
    margin-bottom: 0.8rem !important;
  }
  [data-testid="stMetricValue"] {
    font-family: 'Outfit', sans-serif !important;
    color: #38bdf8; /* Fallback */
    background: linear-gradient(90deg, #38bdf8, #f472b6);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    font-size: 4rem !important;
    font-weight: 950 !important;
  }

  /* ── Dividers ── */
  hr { border-color: rgba(255, 255, 255, 0.15) !important; margin: 3rem 0 !important; }

  /* ── Table Styling ── */
  table {
    border-collapse: separate !important;
    border-spacing: 0 !important;
    width: 100% !important;
    border-radius: 20px !important;
    overflow: hidden !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    background: rgba(15, 23, 42, 0.4) !important;
    backdrop-filter: blur(12px) !important;
  }
  th {
    background: rgba(30, 41, 59, 0.9) !important;
    color: #e2e8f0 !important;
    font-family: 'Outfit', sans-serif !important;
    font-size: 1.2rem !important;
    font-weight: 900 !important;
    letter-spacing: 0.1em !important;
    border-bottom: 2px solid rgba(255, 255, 255, 0.15) !important;
    padding: 1.8rem 1.5rem !important;
    text-transform: uppercase;
  }
  td {
    background: transparent !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
    padding: 1.5rem !important;
    color: #f8fafc !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.15rem !important;
    font-weight: 500 !important;
  }
  tr:last-child td {
    border-bottom: none !important;
  }
  tr:hover td {
    background: rgba(255, 255, 255, 0.08) !important;
  }
</style>
"""

LIGHT_THEME_CSS = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800;900&family=Inter:wght@500;600;700&display=swap');

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
  }

  html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], [data-testid="stHeader"] {
    background: 
      radial-gradient(at 0% 0%, rgba(219, 39, 119, 0.05) 0px, transparent 50%),
      radial-gradient(at 50% 0%, rgba(99, 102, 241, 0.05) 0px, transparent 50%),
      radial-gradient(at 100% 0%, rgba(147, 51, 234, 0.05) 0px, transparent 50%),
      #f8fafc !important;
    background-attachment: fixed !important;
    color: #0f172a !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.1rem !important;
  }
  
  /* High contrast for all text */
  p, div, li, span, label {
    font-size: 1.05rem !important;
    font-weight: 500 !important;
    line-height: 1.6;
    color: #0f172a !important;
  }

  /* Explicit labels styling */
  [data-testid="stWidgetLabel"] p {
    color: #1e293b !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
  }

  [data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.8) !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid rgba(0, 0, 0, 0.05) !important;
  }
  
  [data-testid="stSidebarNav"] span {
      font-size: 1.2rem !important;
      font-weight: 700 !important;
      color: #0f172a !important;
  }

  .app-header {
    font-family: 'Outfit', sans-serif;
    font-size: 4.5rem;
    font-weight: 950;
    color: #1e40af; /* Fallback */
    background: linear-gradient(135deg, #1e40af, #db2777, #7e22ce);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em;
    border-bottom: 2px solid rgba(0, 0, 0, 0.05);
    padding-bottom: 1.5rem;
    margin-bottom: 3rem;
    animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    filter: drop-shadow(0 4px 12px rgba(0,0,0,0.05));
  }
  
  .panel-label {
    font-family: 'Outfit', sans-serif;
    font-size: 1.3rem;
    font-weight: 900;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #475569 !important;
    border-left: 6px solid #db2777;
    padding-left: 1.2rem;
    margin-bottom: 2rem;
    margin-top: 3rem;
    animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1);
  }
  
  .bw-card {
    background: rgba(255, 255, 255, 0.75);
    backdrop-filter: blur(16px) saturate(180%);
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-radius: 20px;
    padding: 2.5rem;
    margin-bottom: 2rem;
    box-shadow: 
      0 10px 40px rgba(0, 0, 0, 0.04),
      0 0 0 1px rgba(0, 0, 0, 0.02);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) backwards;
    font-size: 1.15rem;
    font-weight: 600;
  }
  .bw-card:hover { 
    border-color: rgba(219, 39, 119, 0.3); 
    transform: translateY(-6px) scale(1.01); 
    box-shadow: 
      0 20px 50px rgba(0, 0, 0, 0.08),
      0 0 30px rgba(219, 39, 119, 0.1);
  }
  
  .state-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    font-weight: 800;
    padding: 0.8rem 1.8rem;
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 30px;
    color: #475569 !important;
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(8px);
    letter-spacing: 0.06em;
    margin-right: 1rem;
    margin-bottom: 1rem;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
  }
  .state-badge.active {
    background: linear-gradient(135deg, #db2777, #6366f1);
    color: #ffffff !important;
    border-color: transparent;
    box-shadow: 0 10px 25px rgba(219, 39, 119, 0.3);
    transform: translateY(-4px) scale(1.1);
  }
  .state-badge.error { background: linear-gradient(135deg, #ef4444, #991b1b); color: #ffffff !important; border-color: transparent; box-shadow: 0 8px 20px rgba(239, 68, 68, 0.25); }
  .state-badge.done { border-color: rgba(16, 185, 129, 0.5); color: #064e3b !important; background: rgba(16, 185, 129, 0.1); box-shadow: 0 4px 15px rgba(16, 185, 129, 0.1); }
  
  .score-large {
    font-family: 'Outfit', sans-serif;
    font-size: 9rem;
    font-weight: 950;
    color: #0f172a; /* Fallback */
    background: linear-gradient(180deg, #0f172a 30%, #475569 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 0.9;
    letter-spacing: -0.05em;
    filter: drop-shadow(0 4px 15px rgba(0,0,0,0.1));
  }
  .grade-badge {
    font-family: 'Outfit', sans-serif;
    font-size: 4rem;
    font-weight: 900;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 7.5rem;
    height: 7.5rem;
    border: 5px solid transparent;
    background: linear-gradient(#ffffff, #ffffff) padding-box, 
                linear-gradient(135deg, #db2777, #6366f1) border-box;
    border-radius: 50%;
    color: #0f172a !important;
    box-shadow: 0 15px 40px rgba(219, 39, 119, 0.2);
    animation: fadeIn 1s cubic-bezier(0.16, 1, 0.3, 1);
  }
  
  .violation-critical { border-left: 8px solid #dc2626; color: #7f1d1d !important; margin-bottom: 1.2rem; background: linear-gradient(90deg, rgba(220, 38, 38, 0.1) 0%, rgba(255, 255, 255, 0.5) 100%); padding: 1.8rem; border-radius: 0 15px 15px 0; font-weight:700; font-size:1.15rem; box-shadow: 0 4px 15px rgba(220, 38, 38, 0.05); }
  .violation-high     { border-left: 8px solid #ea580c; color: #9a3412 !important; margin-bottom: 1.2rem; background: linear-gradient(90deg, rgba(234, 88, 12, 0.08) 0%, rgba(255, 255, 255, 0.5) 100%); padding: 1.8rem; border-radius: 0 15px 15px 0; font-weight:700; font-size:1.15rem; }
  .violation-medium   { border-left: 8px solid #d97706; color: #854d0e !important; margin-bottom: 1.2rem; background: linear-gradient(90deg, rgba(217, 119, 6, 0.06) 0%, rgba(255, 255, 255, 0.5) 100%); padding: 1.8rem; border-radius: 0 15px 15px 0; font-weight:600;}
  .violation-low      { border-left: 8px solid #0284c7; color: #075985 !important; margin-bottom: 1.2rem; background: linear-gradient(90deg, rgba(2, 132, 199, 0.06) 0%, rgba(255, 255, 255, 0.5) 100%); padding: 1.8rem; border-radius: 0 15px 15px 0; font-weight:600;}
  
  button[kind="primary"] {
    background: linear-gradient(135deg, #1e40af 0%, #db2777 50%, #7e22ce 100%) !important;
    background-size: 200% auto !important;
    color: #ffffff !important;
    border: none !important;
    font-family: 'Outfit', sans-serif !important;
    font-weight: 800 !important;
    font-size: 1.25rem !important;
    letter-spacing: 0.08em !important;
    padding: 1rem 3rem !important;
    border-radius: 14px !important;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 10px 30px rgba(219, 39, 119, 0.3) !important;
    text-transform: uppercase;
  }
  button[kind="primary"]:hover {
    background-position: right center !important;
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 15px 40px rgba(219, 39, 119, 0.45) !important;
  }
  button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.95) !important;
    color: #1e293b !important;
    border: 1px solid rgba(0, 0, 0, 0.15) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    padding: 1rem 2.5rem !important;
    border-radius: 14px !important;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
  }
  button[kind="secondary"]:hover {
    background: #ffffff !important;
    border-color: #db2777 !important;
    color: #db2777 !important;
    transform: translateY(-4px);
    box-shadow: 0 8px 25px rgba(219, 39, 119, 0.12) !important;
  }
  
  .stTextArea textarea, .stNumberInput input, .stSelectbox select {
    background: rgba(255, 255, 255, 0.95) !important;
    color: #0f172a !important;
    border: 1px solid rgba(0, 0, 0, 0.2) !important;
    border-radius: 14px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.15rem !important;
    font-weight: 500 !important;
    padding: 1.4rem !important;
    box-shadow: 0 2px 10px rgba(0,0,0,0.02) !important;
    transition: all 0.3s ease !important;
  }
  /* Fix visibility for disabled text areas (Transcript) */
  .stTextArea textarea:disabled {
    color: #334155 !important;
    background: rgba(241, 245, 249, 0.8) !important;
    -webkit-text-fill-color: #334155 !important;
  }
  .stTextArea textarea:focus, .stNumberInput input:focus {
    border-color: #db2777 !important;
    background: #ffffff !important;
    box-shadow: 0 0 0 4px rgba(219, 39, 119, 0.15) !important;
    outline: none !important;
  }
  
  .streamlit-expanderHeader {
    background: rgba(255, 255, 255, 0.8) !important;
    backdrop-filter: blur(12px) !important;
    color: #1e293b !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    border-radius: 14px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    padding: 1.2rem !important;
    transition: all 0.3s ease !important;
  }
  .streamlit-expanderHeader:hover {
    background: rgba(255, 255, 255, 0.95) !important;
    border-color: rgba(219, 39, 119, 0.3) !important;
  }
  
  .stProgress > div > div { 
    background: linear-gradient(90deg, #1e40af, #db2777, #7e22ce) !important; 
    border-radius: 10px !important; 
    box-shadow: 0 0 20px rgba(219, 39, 119, 0.3) !important; 
  }
  .stProgress > div { background-color: rgba(0, 0, 0, 0.05) !important; border-radius: 10px !important; height: 14px !important; }
  
  [data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-radius: 20px;
    padding: 2.5rem;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04);
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  }
  [data-testid="stMetric"]:hover { 
    border-color: rgba(219, 39, 119, 0.3); 
    transform: translateY(-8px); 
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.08), 0 0 30px rgba(219, 39, 119, 0.1); 
  }
  [data-testid="stMetricLabel"] { font-family: 'Inter', sans-serif !important; color: #475569 !important; font-size: 1.2rem !important; font-weight: 900 !important; text-transform: uppercase !important; letter-spacing: 0.18em !important; }
  [data-testid="stMetricValue"] { font-family: 'Outfit', sans-serif !important; color: #1e40af; /* Fallback */ background: linear-gradient(90deg, #1e40af, #db2777); -webkit-background-clip: text !important; -webkit-text-fill-color: transparent !important; font-size: 4rem !important; font-weight: 950 !important; }
  
  hr { border-color: rgba(0, 0, 0, 0.1) !important; margin: 3rem 0 !important; }
  
  table { 
    border-collapse: separate !important; 
    border-spacing: 0 !important; 
    width: 100% !important; 
    border-radius: 20px !important; 
    overflow: hidden !important; 
    border: 1px solid rgba(0, 0, 0, 0.08) !important; 
    background: rgba(255, 255, 255, 0.6) !important; 
    backdrop-filter: blur(12px) !important;
  }
  th { 
    background: rgba(241, 245, 249, 0.95) !important; 
    color: #0f172a !important; 
    font-family: 'Outfit', sans-serif !important; 
    font-size: 1.2rem !important; 
    font-weight: 900 !important; 
    letter-spacing: 0.1em !important; 
    border-bottom: 2px solid rgba(0, 0, 0, 0.1) !important; 
    padding: 1.8rem 1.5rem !important; 
    text-transform: uppercase; 
  }
  td { 
    background: transparent !important; 
    border-bottom: 1px solid rgba(0, 0, 0, 0.05) !important; 
    padding: 1.5rem !important; 
    color: #0f172a !important; 
    font-family: 'Inter', sans-serif !important; 
    font-size: 1.15rem !important; 
    font-weight: 500 !important; 
  }
  tr:last-child td { border-bottom: none !important; }
  tr:hover td { background: rgba(255, 255, 255, 0.9) !important; }
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
