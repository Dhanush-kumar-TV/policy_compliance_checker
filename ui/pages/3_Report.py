import streamlit as st
import json
import plotly.graph_objects as go
import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

st.markdown("""
<div class="app-header">
    <span class="material-symbols-outlined" style="vertical-align: middle; font-size: 2.5rem; color: #1152d4;">policy</span>
    Executive Compliance Report
</div>
""", unsafe_allow_html=True)

if not st.session_state.report:
    st.markdown('<div class="bw-card" style="text-align:center;">', unsafe_allow_html=True)
    st.warning("No generated report found. Please run a compliance check in the Policy Dashboard.")
    if st.button("GO TO DASHBOARD ➔", type="primary"):
        st.switch_page("pages/1_Input.py")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

rep = st.session_state.report

# ---------------------------------------------------------
# EXECUTIVE TOPLINE (Stitch Cards)
# ---------------------------------------------------------
st.markdown('<div class="panel-label">Executive Topline</div>', unsafe_allow_html=True)
t_col1, t_col2, t_col3 = st.columns(3)

with t_col1:
    st.markdown(f"""
    <div class="bw-card" style="text-align:center; border-top: 4px solid #1152d4;">
        <div style="font-size: 0.75rem; color:#94a3b8; font-weight:700;">COMPLIANCE SCORE</div>
        <div style="font-size: 3.5rem; font-weight:900; color:#f1f5f9; margin: 0.5rem 0;">{rep["compliance_score"]}</div>
        <div style="font-size: 0.8rem; color:#1152d4; font-weight:700;">OUT OF 100</div>
    </div>
    """, unsafe_allow_html=True)

with t_col2:
    st.markdown(f"""
    <div class="bw-card" style="text-align:center; border-top: 4px solid #10b981;">
        <div style="font-size: 0.75rem; color:#94a3b8; font-weight:700;">AI GRADE</div>
        <div style="font-size: 3.5rem; font-weight:900; color:#10b981; margin: 0.5rem 0;">{rep["grade"]}</div>
        <div style="font-size: 0.8rem; color:#94a3b8; font-weight:700;">BASED ON LLM ANALYSIS</div>
    </div>
    """, unsafe_allow_html=True)

with t_col3:
    risk_color = "#ef4444" if rep["risk_level"].lower() in ["high", "critical"] else "#eab308"
    st.markdown(f"""
    <div class="bw-card" style="text-align:center; border-top: 4px solid {risk_color};">
        <div style="font-size: 0.75rem; color:#94a3b8; font-weight:700;">RISK LEVEL</div>
        <div style="font-size: 1.5rem; font-weight:900; color:{risk_color}; margin: 1.5rem 0;">{rep["risk_level"].upper()}</div>
        <div style="font-size: 0.8rem; color:#94a3b8; font-weight:700;">AUTO-ASSESSED</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="panel-label">Executive Summary</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="bw-card">
    <p style="font-size: 1.1rem; line-height: 1.6; font-style: italic; color: #cbd5e1;">
        "{rep["executive_summary"]}"
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# REMEDIATION & FINDINGS
# ---------------------------------------------------------
st.markdown('<div class="panel-label">Findings & Remediation</div>', unsafe_allow_html=True)
c_act1, c_act2 = st.columns([1.5, 1])

with c_act1:
    remediation_html = [
        '<div class="bw-card" style="min-height:300px;">',
        '<h4>Top Remediation Steps</h4>'
    ]
    if rep.get("top_3_critical_actions"):
        for i, act in enumerate(rep["top_3_critical_actions"]):
            remediation_html.append(f"""
<div style="display:flex; gap:15px; margin-bottom:1.5rem; align-items:flex-start;">
    <div style="background:#1152d4; color:white; width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-shrink:0; font-weight:bold;">{i+1}</div>
    <div style="font-size:1rem; color:#f1f5f9; font-weight:500;">{act}</div>
</div>
            """)
    else:
        remediation_html.append('<div style="color:#10b981; font-weight:600; padding:1rem 0;">No active violations found.</div>')
    remediation_html.append('</div>')
    st.markdown("".join(remediation_html), unsafe_allow_html=True)

with c_act2:
    crit_count = sum(1 for vlist in rep.get("violations_by_category", {}).values() for v in vlist if v['severity'].lower() == 'critical')
    st.markdown(f"""
<div class="bw-card" style="min-height:300px;">
    <h4>Analysis Metrics</h4>
    <div style="margin-top:20px;">
        <div style="font-size:0.75rem; color:#94a3b8; font-weight:700; text-transform:uppercase; margin-bottom:5px;">Rules Passed</div>
        <div style="font-size:1.8rem; font-weight:900; color:#f1f5f9;">{rep['passed_rules']} / {rep['total_rules']}</div>
    </div>
    <div style="margin-top:25px;">
        <div style="font-size:0.75rem; color:#94a3b8; font-weight:700; text-transform:uppercase; margin-bottom:5px;">Critical Violations</div>
        <div style="font-size:1.8rem; font-weight:900; color:{'#ef4444' if crit_count > 0 else '#10b981'};">{crit_count}</div>
    </div>
</div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# DETAILED REGISTER (Table)
# ---------------------------------------------------------
st.markdown('<div class="panel-label">Policy Violation Register</div>', unsafe_allow_html=True)
st.markdown('<div class="bw-card">', unsafe_allow_html=True)

table_html = [
    "<table style='width: 100%; border-collapse: collapse;'>",
    "<thead>",
    "<tr style='border-bottom: 2px solid #2d3a54; text-align: left; color:#94a3b8; font-size:0.75rem; text-transform:uppercase;'>",
    "<th style='padding:12px;'>Rule</th>",
    "<th style='padding:12px;'>Severity</th>",
    "<th style='padding:12px;'>Remediation Strategy</th>",
    "</tr>",
    "</thead>",
    "<tbody>"
]

has_violations = False
for cat, v_list in rep.get("violations_by_category", {}).items():
    for v in v_list:
        has_violations = True
        sev = v['severity'].upper()
        sev_color = "#ef4444" if sev == "CRITICAL" else "#f97316" if sev == "HIGH" else "#eab308"
        
        row = f"""
<tr style="border-bottom: 1px solid #2d3a54;">
<td style="padding:15px;">
<div style="font-weight:700; color:#f1f5f9;">{v['rule_id']}</div>
<div style="font-size:0.8rem; color:#94a3b8;">{v['rule_name']}</div>
</td>
<td style="padding:15px;">
<span style="color:{sev_color}; font-weight:900; font-size:0.75rem;">● {sev}</span>
</td>
<td style="padding:15px; font-size:0.9rem; color:#cbd5e1;">{v['remediation']}</td>
</tr>
"""
        table_html.append(row)

if not has_violations:
    st.markdown("<div style='text-align:center; padding:2rem; color:#10b981;'>No violations detected. Document is 100% compliant.</div>", unsafe_allow_html=True)
else:
    table_html.append("</tbody></table>")
    st.markdown("".join(table_html), unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# FOOTER / EXPORT
# ---------------------------------------------------------
st.markdown("<br>", unsafe_allow_html=True)
f_col1, f_col2, f_col3 = st.columns(3)

with f_col1:
    report_json = json.dumps(rep, indent=2)
    st.download_button("⬇ EXPORT JSON", report_json, file_name=f"report_{st.session_state.run_id}.json", mime="application/json", use_container_width=True)

with f_col2:
    if st.button("LIVE ENGINE LOGS", type="secondary", use_container_width=True):
        st.switch_page("pages/2_Activity.py")
        
with f_col3:
    if st.button("ADVANCED ANALYTICS", type="primary", use_container_width=True):
        st.switch_page("pages/4_Advanced_Analysis.py")
