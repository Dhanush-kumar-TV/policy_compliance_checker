import streamlit as st
import uuid
import pypdf
import json

import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from agents.orchestrator import Orchestrator
from agents.compliance_agent import ComplianceAgent
from state.state_machine import ComplianceState

# Need to pull in the loaders from the main app or define them here
@st.cache_data
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

@st.cache_data
def load_rules(path):
    with open(path, "r") as f:
        return json.load(f)

config = load_config()
rules = load_rules(config["compliance_rules_path"])

st.markdown('<div class="app-header">1. POLICY INPUT</div>', unsafe_allow_html=True)
st.markdown('<div class="panel-label">// INPUT & CONTROLS</div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    policy_text = st.text_area("Paste Policy Document", height=250, placeholder="Paste your policy text here...")
    uploaded_file = st.file_uploader("Or upload text/pdf file", type=["txt", "pdf"])
    
    if uploaded_file:
        if uploaded_file.name.lower().endswith(".pdf"):
            reader = pypdf.PdfReader(uploaded_file)
            pdf_text = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pdf_text.append(text)
            policy_text = "\n".join(pdf_text)
        else:
            policy_text = uploaded_file.read().decode("utf-8")

with col2:
    seed_input = st.number_input("Seed", value=config["seed"], step=1)
    mode = st.selectbox("Agent Mode", ["multi-agent", "single-agent"])
    st.markdown("<br>", unsafe_allow_html=True)
    c_btn1, c_btn2 = st.columns(2)
    start_clicked = c_btn1.button("▶ START", type="primary", use_container_width=True)
    reset_clicked = c_btn2.button("↺ RESET", type="secondary", use_container_width=True)
    
if reset_clicked:
    st.session_state.run_id = None
    st.session_state.report = None
    st.session_state.transcript = []
    st.session_state.state_machine.reset()
    st.session_state.stop_requested = False
    st.rerun()

if start_clicked and policy_text:
    st.session_state.run_id = str(uuid.uuid4())
    st.session_state.report = None
    st.session_state.transcript = []
    st.session_state.stop_requested = False
    
    sm = st.session_state.state_machine
    sm.reset()
    sm.transition("document_uploaded")
    
    with st.spinner("Running Compliance Check..."):
        try:
            if not policy_text or policy_text.strip() == "":
                raise ValueError("Policy document is empty. Please paste or upload a policy.")
                
            tool_allowlist = ["document_parser_tool", "compliance_engine_tool", "violation_extractor_tool", "score_calculator_tool", "report_generator_tool"]
            
            if mode == "multi-agent":
                agent = Orchestrator(st.session_state.run_id, sm, tool_allowlist, rules, seed=seed_input)
            else:
                agent = ComplianceAgent(st.session_state.run_id, tool_allowlist, state_machine=sm, rules=rules, seed=seed_input)
                
            report = agent.run({"raw_text": policy_text, "document_id": f"doc_{seed_input}"})
            
            st.session_state.report = report
            if hasattr(agent, "transcript"):
                st.session_state.transcript = agent.transcript
            else:
                st.session_state.transcript = agent.compliance_agent.transcript + agent.violation_agent.transcript if mode == "multi-agent" else []
                
        except Exception as e:
            current_state = sm.get_current()
            if current_state == ComplianceState.PARSING.name:
                sm.transition("parse_failed")
            elif current_state == ComplianceState.VALIDATING.name:
                sm.transition("validation_failed")
            else:
                sm._state = ComplianceState.ERROR
            st.error(f"Error during execution: {e}")

if st.session_state.run_id:
    st.success(f"**RUN COMPLETE:** `{st.session_state.run_id}`")
    
    # Feature Link Button
    if st.button("View Activity & Progress ➔", type="primary"):
        st.switch_page("pages/2_Activity.py")
