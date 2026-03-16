import streamlit as st
import json
import plotly.graph_objects as go
import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

st.markdown('<div class="app-header">3. COMPLIANCE REPORT</div>', unsafe_allow_html=True)

if not st.session_state.report:
    st.warning("No generated report found. Please run a compliance check in the Input section.")
    if st.button("Go to Input ➔", type="primary"):
        st.switch_page("pages/1_Input.py")
    st.stop()

rep = st.session_state.report

st.markdown('<div class="panel-label">// OVERVIEW SUMMARY</div>', unsafe_allow_html=True)
r_c1, r_c2, r_c3 = st.columns([2, 1, 3])

with r_c1:
    color_sub = "#64748b" if st.session_state.theme == "light" else "#888"
    st.markdown(f'<div class="score-large">{rep["compliance_score"]}</div><div style="color:{color_sub};font-size:1rem;font-weight:700;letter-spacing:0.15em;margin-top:0.8rem;">COMPLIANCE SCORE</div>', unsafe_allow_html=True)

with r_c2:
    st.markdown(f'<div class="grade-badge">{rep["grade"]}</div>', unsafe_allow_html=True)

with r_c3:
    risk_color = "#db2777" if st.session_state.theme == "light" else "#f472b6"
    st.markdown(f'<br><div style="font-size: 1.5rem; font-weight: 800; color: {risk_color};">RISK ASSESSMENT: {rep["risk_level"].upper()}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="bw-card" style="margin-top:1rem;"><i>{rep["executive_summary"]}</i></div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

c_act1, c_act2 = st.columns([1, 1])

with c_act1:
    if rep.get("top_3_critical_actions"):
        st.markdown('<div class="panel-label">// CRITICAL REMEDIATIONS REQUIRED</div>', unsafe_allow_html=True)
        for i, act in enumerate(rep["top_3_critical_actions"]):
            marker_color = "#dc2626" if st.session_state.theme == "light" else "#ff0055"
            st.markdown(f"<div style='margin-bottom: 0.8rem; font-size: 1.2rem; font-weight: 700;'><span style='color: {marker_color};'>{i+1}.</span> {act}</div>", unsafe_allow_html=True)
    else:
        st.success("No critical remediations required. Excellent work!")

with c_act2:
    st.markdown('<div class="panel-label">// QUICK METRICS</div>', unsafe_allow_html=True)
    st.metric("RULES PASSED", f"{rep['passed_rules']} / {rep['total_rules']}")
    crit_count = sum(1 for vlist in rep.get("violations_by_category", {}).values() for v in vlist if v['severity'].lower() == 'critical')
    st.metric("CRITICAL VIOLATIONS", crit_count)

st.markdown("<hr>", unsafe_allow_html=True)

st.markdown('<div class="panel-label">// DETAILED VIOLATIONS REGISTER</div>', unsafe_allow_html=True)

    border_color = "#ddd" if st.session_state.theme == "light" else "#333"
    table_html = [
        "<table style='width: 100%; border-collapse: collapse; margin-bottom: 2rem;'>",
        "<thead>",
        f"<tr style='border-bottom: 2px solid {border_color}; text-align: left;'>",
    "<th>RULE ID</th>",
    "<th>RULE NAME</th>",
    "<th>CATEGORY</th>",
    "<th>SEVERITY</th>",
    "<th>REMEDIATION</th>",
    "</tr>",
    "</thead>",
    "<tbody>"
]

has_violations = False
for cat, v_list in rep.get("violations_by_category", {}).items():
    if v_list:
        has_violations = True
    for v in v_list:
        cls = f"violation-{v['severity'].lower()}"
        row = (
            f"<tr class='{cls}'>"
            f"<td><strong>{v['rule_id']}</strong></td>"
            f"<td>{v['rule_name']}</td>"
            f"<td>{v['category']}</td>"
            f"<td style='text-transform: uppercase;'>{v['severity']}</td>"
            f"<td>{v['remediation']}</td>"
            f"</tr>"
        )
        table_html.append(row)
        
table_html.append("</tbody></table>")

if has_violations:
    st.markdown("".join(table_html), unsafe_allow_html=True)
else:
    st.info("No policy violations detected. This document is fully compliant.")

st.markdown("---")

t1, t2, t3 = st.columns(3)
with t1:
    report_json = json.dumps(rep, indent=2)
    st.download_button("⬇ DOWNLOAD JSON REPORT", report_json, file_name=f"report_{st.session_state.run_id}.json", mime="application/json", use_container_width=True)

with t2:
    if st.button("View Agent Logs ➔", type="secondary", use_container_width=True):
        st.switch_page("pages/2_Activity.py")
        
with t3:
    if st.button("Advanced Analytics Dashboard ➔", type="primary", use_container_width=True):
        st.switch_page("pages/4_Advanced_Analysis.py")
