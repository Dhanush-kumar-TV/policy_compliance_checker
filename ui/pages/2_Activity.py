import streamlit as st
import pandas as pd
import json
import os
import datetime
import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from state.state_machine import ComplianceState

st.markdown("""
<div class="app-header">
    <span class="material-symbols-outlined" style="vertical-align: middle; font-size: 2.5rem; color: #1152d4;">monitor_heart</span>
    Live Scan Activity
</div>
""", unsafe_allow_html=True)

if not st.session_state.run_id:
    st.markdown('<div class="bw-card" style="text-align:center;">', unsafe_allow_html=True)
    st.warning("No active scan detected. Please initialize a scan in the Policy Dashboard.")
    if st.button("GO TO DASHBOARD ➔", type="primary"):
        st.switch_page("pages/1_Input.py")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------
# SUMMARY STATS (Stitch Style)
# ---------------------------------------------------------
sm = st.session_state.state_machine
current_state = sm.get_current()

st.markdown('<div class="panel-label">Scan Statistics</div>', unsafe_allow_html=True)
s_col1, s_col2, s_col3 = st.columns(3)

with s_col1:
    st.metric("CURRENT STATUS", current_state)
with s_col2:
    total_steps = len(st.session_state.transcript)
    st.metric("STEPS PROCESSED", total_steps)
with s_col3:
    st.metric("RUN ID", st.session_state.run_id[:8].upper())

# ---------------------------------------------------------
# STATE MACHINE / PIPELINE
# ---------------------------------------------------------
st.markdown('<div class="panel-label">Analysis Pipeline</div>', unsafe_allow_html=True)
st.markdown('<div class="bw-card" style="padding: 1rem;">', unsafe_allow_html=True)

states_order = [ComplianceState.IDLE.name, ComplianceState.PARSING.name, ComplianceState.VALIDATING.name, 
                ComplianceState.SCORING.name, ComplianceState.REPORTING.name, ComplianceState.DONE.name]

cols = st.columns(len(states_order))
for i, s in enumerate(states_order):
    is_active = (current_state == s)
    is_error = (current_state == ComplianceState.ERROR.name and s == ComplianceState.DONE.name)
    btn_label = "ERROR" if is_error else s
    
    with cols[i]:
        if is_active:
            st.markdown(f'<div class="state-badge active" style="width:100%">{btn_label}</div>', unsafe_allow_html=True)
        elif is_error:
            st.markdown(f'<div class="state-badge error" style="width:100%">{btn_label}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="state-badge" style="width:100%">{btn_label}</div>', unsafe_allow_html=True)

# Progress Bar
if current_state in states_order:
    idx = states_order.index(current_state)
    prog = idx / (len(states_order) - 1)
else:
    prog = 1.0
st.progress(prog)
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# ACTIVITY LOGS (Side-by-Side: Transcript & Tools)
# ---------------------------------------------------------
st.markdown('<div class="panel-label">Live Activity Logs</div>', unsafe_allow_html=True)
col_act, col_tool = st.columns([1, 1.2])

with col_act:
    with st.container(border=True):
        st.markdown("""
            <h4 style="margin-top:0; display:flex; align-items:center; gap:8px;">
                <span class="material-symbols-outlined text-primary">description</span>
                Agent Transcript
            </h4>
        """, unsafe_allow_html=True)
        transcript_text = "\n".join(st.session_state.transcript) if st.session_state.transcript else "Waiting for agent activity..."
        # transcript_height can be adjusted if needed
        st.text_area("Live Log", transcript_text, height=400, disabled=True, label_visibility="collapsed")

with col_tool:
    # Adding a wrapper for scrollable content inside the container is tricky in Streamlit
    # but the container itself will expand or we can use fixed height with CSS if needed.
    with st.container(border=True):
        st.markdown("""
            <h4 style="margin-top:0; display:flex; align-items:center; gap:8px;">
                <span class="material-symbols-outlined text-primary" style="color:#eab308;">terminal</span>
                Tool Execution
            </h4>
        """, unsafe_allow_html=True)
        
        log_file = os.path.join("logs", "runs", f"{st.session_state.run_id}.jsonl")
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                logs = [json.loads(line) for line in f]
                
            tool_calls = [log for log in logs if log["event_type"] == "tool_call" or "error" in log.get("data", {})]
            
            if not tool_calls:
                st.info("Agent is preparing tools...")
                
            for call in tool_calls:
                data = call["data"]
                tname = data.get("tool_name", "Unknown Tool")
                dur = data.get("duration_ms", 0)
                status = "SUCCESS" if "error" not in data else "ERROR"
                
                icon = "✅" if status == "SUCCESS" else "⚠️"
                with st.expander(f"{icon} {tname} — {dur:.0f}ms"):
                    st.markdown("**INVOCATION:**")
                    st.json(data.get("input", {}))
                    st.markdown("**RESPONSE:**")
                    if "error" in data:
                        st.error(data["error"])
                    else:
                        st.json(data.get("output", {}))
        else:
            st.info("Initializing tool logging pipeline...")

st.markdown("<br>", unsafe_allow_html=True)
if st.session_state.report:
    st.markdown('<div style="display:flex; justify-content:center;">', unsafe_allow_html=True)
    if st.button("GENERATE EXECUTIVE REPORT ➔", type="primary"):
        st.switch_page("pages/3_Report.py")
    st.markdown('</div>', unsafe_allow_html=True)
