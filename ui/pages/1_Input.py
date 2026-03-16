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

st.markdown("""
<div class="app-header">
    <span class="material-symbols-outlined" style="vertical-align: middle; font-size: 2.5rem; color: #1152d4;">policy</span>
    Policy Dashboard
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="panel-label">Configuration & Input</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="bw-card">', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**1. Policy Document**")
        policy_text = st.text_area("Paste text or upload file below", height=250, placeholder="Paste your policy text here...", label_visibility="collapsed")
        uploaded_file = st.file_uploader("Upload Policy (TXT, PDF)", type=["txt", "pdf"])
        
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
        st.markdown("**2. Analysis Settings**")
        seed_input = st.number_input("Random Seed", value=config["seed"], step=1)
        mode = st.selectbox("Orchestration Mode", ["multi-agent", "single-agent"])
        
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        c_btn1, c_btn2 = st.columns(2)
        start_clicked = c_btn1.button("▶ START SCAN", type="primary", use_container_width=True)
        reset_clicked = c_btn2.button("↺ RESET", type="secondary", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Shared Reset Logic
if reset_clicked:
    st.session_state.run_id = None
    st.session_state.report = None
    st.session_state.transcript = []
    st.session_state.state_machine.reset()
    st.session_state.stop_requested = False
    st.rerun()

# ---------------------------------------------------------
# REPOSITORY PERSISTENCE
# ---------------------------------------------------------
REPO_FILE = os.path.join("logs", "repository.json")

def load_repository():
    if os.path.exists(REPO_FILE):
        with open(REPO_FILE, "r") as f:
            return json.load(f)
    return [
        {"name": "Enterprise Data Privacy P2", "date": "Oct 24, 2023", "status": "PUBLISHED"},
        {"name": "Cloud Infrastructure Access", "date": "Oct 22, 2023", "status": "PUBLISHED"},
        {"name": "Information Security Standard", "date": "Oct 21, 2023", "status": "DRAFT"}
    ]

def save_to_repository(name, status="COMPLETED"):
    repo = load_repository()
    # Add new entry at top
    new_entry = {
        "name": name,
        "date": datetime.datetime.now().strftime("%b %d, %Y"),
        "status": status
    }
    repo.insert(0, new_entry)
    # Limit to top 10 for demo purposes
    repo = repo[:10]
    with open(REPO_FILE, "w") as f:
        json.dump(repo, f, indent=4)

if start_clicked and policy_text:
    import datetime # Ensure available here
    st.session_state.run_id = str(uuid.uuid4())
    st.session_state.report = None
    st.session_state.transcript = []
    st.session_state.stop_requested = False
    
    sm = st.session_state.state_machine
    sm.reset()
    sm.transition("document_uploaded")
    
    with st.spinner("Initializing AI Agents..."):
        try:
            if not policy_text or policy_text.strip() == "":
                raise ValueError("Policy document is empty.")
                
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
            
            # Save to repository successfully
            doc_name = (uploaded_file.name if uploaded_file else "Manual Input Policy")
            save_to_repository(doc_name, "COMPLETED")
                
        except Exception as e:
            current_state = sm.get_current()
            if current_state == ComplianceState.PARSING.name:
                sm.transition("parse_failed")
            elif current_state == ComplianceState.VALIDATING.name:
                sm.transition("validation_failed")
            else:
                sm._state = ComplianceState.ERROR
            st.error(f"Execution Error: {e}")

if st.session_state.run_id:
    st.markdown(f"""
    <div class="bw-card" style="border-left: 4px solid #1152d4;">
        <h4 style="margin:0; color:#1152d4;">SCAN IN PROGRESS / COMPLETE</h4>
        <p style="margin:5px 0; font-size:0.9rem; color:#94a3b8;">Run ID: {st.session_state.run_id}</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("VIEW LIVE ACTIVITY ➔", type="primary"):
        st.switch_page("pages/2_Activity.py")

# Premium Policy Repository Table (Now Dynamic)
st.markdown('<div class="panel-label">Policy Repository</div>', unsafe_allow_html=True)
repo_data = load_repository()
table_rows = ""
for item in repo_data:
    status_class = "done" if item["status"] in ["COMPLETED", "PUBLISHED"] else "active"
    table_rows += f'<tr style="border-bottom:1px solid #2d3a54;"><td style="padding:12px;">{item["name"]}</td><td style="padding:12px; color:#94a3b8;">{item["date"]}</td><td style="padding:12px;"><span class="state-badge {status_class}">{item["status"]}</span></td></tr>'

st.markdown(f"""
<div class="bw-card">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
<h4 style="margin:0;">Standard Policies</h4>
<div style="font-size: 0.8rem; color:#94a3b8;">Showing {len(repo_data)} items</div>
</div>
<table style="width:100%; border-collapse: collapse;">
<thead>
<tr style="text-align:left; color:#94a3b8; font-size:0.75rem; text-transform:uppercase;">
<th style="padding:10px; border-bottom:1px solid #2d3a54;">Policy Name</th>
<th style="padding:10px; border-bottom:1px solid #2d3a54;">Last Scanned</th>
<th style="padding:10px; border-bottom:1px solid #2d3a54;">Status</th>
</tr>
</thead>
<tbody>
{table_rows}
</tbody>
</table>
</div>
""", unsafe_allow_html=True)
