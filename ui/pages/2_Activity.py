import streamlit as st
import pandas as pd
import json
import os
import datetime
import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from state.state_machine import ComplianceState

st.markdown('<div class="app-header">2. AGENT ACTIVITY</div>', unsafe_allow_html=True)

if not st.session_state.run_id:
    st.warning("No active run found. Please initialize a document in the Input page.")
    if st.button("Go to Input ➔", type="primary"):
        st.switch_page("pages/1_Input.py")
    st.stop()

# ---------------------------------------------------------
# STATE MACHINE RENDERING
# ---------------------------------------------------------
st.markdown('<div class="panel-label">// STATE MACHINE</div>', unsafe_allow_html=True)
sm = st.session_state.state_machine
current_state = sm.get_current()

states_order = [ComplianceState.IDLE.name, ComplianceState.PARSING.name, ComplianceState.VALIDATING.name, 
                ComplianceState.SCORING.name, ComplianceState.REPORTING.name, ComplianceState.DONE.name]

cols = st.columns(len(states_order))
for i, s in enumerate(states_order):
    is_active = (current_state == s)
    is_error = (current_state == ComplianceState.ERROR.name and s == ComplianceState.DONE.name)
    btn_label = "ERROR" if is_error else s
    
    # Render with custom styles mapped to the types based on CSS
    if is_active or is_error:
        # We manually render the div purely for look, though a button click forces state change
        if is_error:
            st.markdown(f'<div class="state-badge error">{btn_label}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="state-badge active">{btn_label}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="state-badge">{btn_label}</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Progress bar
if current_state in states_order:
    idx = states_order.index(current_state)
    prog = idx / (len(states_order) - 1)
else:
    prog = 1.0
st.progress(prog)

# Transition history table
history = sm.get_history()
if history:
    df_hist = pd.DataFrame(history)
    st.dataframe(df_hist, use_container_width=True, hide_index=True)


col_act, col_tool = st.columns(2)

# ---------------------------------------------------------
# TRANSCRIPTS
# ---------------------------------------------------------
with col_act:
    st.markdown('<div class="panel-label">// AGENT TRANSCRIPT</div>', unsafe_allow_html=True)
    transcript_text = "\n".join(st.session_state.transcript)
    st.text_area("Live Transcript", transcript_text, height=350, disabled=True)
    
    total_steps = len(st.session_state.transcript)
    st.markdown(f"**TOTAL STEPS LOGGED:** {total_steps}", unsafe_allow_html=True)

# ---------------------------------------------------------
# TOOL CALLS
# ---------------------------------------------------------
with col_tool:
    st.markdown('<div class="panel-label">// TOOL INVOCATIONS</div>', unsafe_allow_html=True)
    
    log_file = os.path.join("logs", "runs", f"{st.session_state.run_id}.jsonl")
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = [json.loads(line) for line in f]
            
        tool_calls = [log for log in logs if log["event_type"] == "tool_call" or "error" in log.get("data", {})]
        
        for call in tool_calls:
            data = call["data"]
            tname = data.get("tool_name", "Unknown Tool")
            dur = data.get("duration_ms", 0)
            status = "SUCCESS" if "error" not in data else "ERROR"
            
            with st.expander(f"⚙️ {tname} — {dur:.0f}ms — {status}"):
                st.markdown("**INPUT:**")
                st.json(data.get("input", {}))
                st.markdown("**OUTPUT:**")
                if "error" in data:
                    st.error(data["error"])
                else:
                    st.json(data.get("output", {}))
    else:
        st.info("No tool logs generated yet.")

st.markdown("---")
if st.session_state.report:
    if st.button("View Generated Report ➔", type="primary"):
        st.switch_page("pages/3_Report.py")
