import re
import sys

with open('ui/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace button rules in THEME_CSS
old_theme_btn = """  /* ── Buttons ── */
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
  }"""

new_theme_btn = """  /* ── Buttons ── */
  button[kind="primary"] {
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
  button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(56, 189, 248, 0.5) !important;
    filter: brightness(1.1);
  }
  button[kind="secondary"] {
    background: rgba(30, 41, 59, 0.8) !important;
    color: #f8fafc !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.5rem !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
  }
  button[kind="secondary"]:hover {
    background: rgba(51, 65, 85, 0.8) !important;
    border-color: rgba(255, 255, 255, 0.2) !important;
    transform: translateY(-2px);
  }"""

text = text.replace(old_theme_btn, new_theme_btn)

# Replace button rules in LIGHT_THEME_CSS
old_light_btn = """  .stButton > button {
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
  }"""

new_light_btn = """  button[kind="primary"] {
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
  button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4) !important;
    filter: brightness(1.1);
  }
  button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.8) !important;
    color: #0f172a !important;
    border: 1px solid rgba(0, 0, 0, 0.1) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 1.5rem !important;
    border-radius: 8px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
  }
  button[kind="secondary"]:hover {
    background: rgba(241, 245, 249, 1) !important;
    border-color: rgba(0, 0, 0, 0.2) !important;
    transform: translateY(-2px);
  }"""

text = text.replace(old_light_btn, new_light_btn)

# Replace buttons and add type
text = text.replace('if st.button("☀/☾ THEME"):', 'if st.button("☀/☾ THEME", type="secondary"):')
text = text.replace('start_clicked = c_btn1.button("▶ START CHECK")', 'start_clicked = c_btn1.button("▶ START CHECK", type="primary")')
text = text.replace('reset_clicked = c_btn2.button("↺ RESET")', 'reset_clicked = c_btn2.button("↺ RESET", type="secondary")')

# Replace State Machine rendering
old_state_machine = """badges = []
for s in states_order:
    cls = "state-badge active" if current_state == s else "state-badge"
    if current_state == ComplianceState.ERROR.name and s == ComplianceState.DONE.name:
        cls = "state-badge error"
        s = "ERROR"
    badges.append(f'<div class="{cls}">{s}</div>')
    
st.markdown(" ".join(badges), unsafe_allow_html=True)"""

new_state_machine = """cols = st.columns(len(states_order))
for i, s in enumerate(states_order):
    is_active = (current_state == s)
    is_error = (current_state == ComplianceState.ERROR.name and s == ComplianceState.DONE.name)
    btn_label = "ERROR" if is_error else s
    btn_type = "primary" if (is_active or is_error) else "secondary"
    
    if cols[i].button(btn_label, key=f"state_btn_{s}", type=btn_type, use_container_width=True):
        if not is_error:
            sm._state = getattr(ComplianceState, s)
            st.rerun()"""

text = text.replace(old_state_machine, new_state_machine)

with open('ui/app.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated ui/app.py buttons successfully")
