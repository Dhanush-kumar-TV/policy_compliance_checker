import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

st.markdown("""
<div class="app-header">
    <span class="material-symbols-outlined" style="vertical-align: middle; font-size: 2.5rem; color: #1152d4;">analytics</span>
    Advanced Analytics Breakdown
</div>
""", unsafe_allow_html=True)

if not st.session_state.report:
    st.markdown('<div class="bw-card" style="text-align:center;">', unsafe_allow_html=True)
    st.warning("No generated data found. Please run a compliance scan in the Policy Dashboard.")
    if st.button("GO TO DASHBOARD ➔", type="primary"):
        st.switch_page("pages/1_Input.py")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

rep = st.session_state.report

# Prepare Data
violations_by_category = rep.get("violations_by_category", {})
all_violations = []
for cat, v_list in violations_by_category.items():
    for v in v_list:
        all_violations.append({
            "Category": cat,
            "Severity": v["severity"].capitalize(),
            "Rule Core": v["rule_id"].split("-")[0]
        })

df = pd.DataFrame(all_violations)

severity_colors = {
    "Critical": "#dc2626",
    "High": "#ea580c",
    "Medium": "#d97706",
    "Low": "#0284c7"
}

layout_theme = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#94a3b8", "family": "Inter, sans-serif", "size": 13},
    "xaxis": {"gridcolor": "rgba(255,255,255,0.05)", "linecolor": "rgba(255,255,255,0.1)", "tickcolor": "#64748b"},
    "yaxis": {"gridcolor": "rgba(255,255,255,0.05)", "linecolor": "rgba(255,255,255,0.1)", "tickcolor": "#64748b"},
    "margin": dict(t=40, l=40, r=40, b=40)
}

st.markdown('<div class="panel-label">Violation Distribution Analysis</div>', unsafe_allow_html=True)

if not df.empty:
    with st.container(border=True):
        fig_sun = px.sunburst(df, path=['Severity', 'Category'], color='Severity',
                              color_discrete_map=severity_colors)
        fig_sun.update_layout(**layout_theme, height=450)
        fig_sun.update_traces(textfont=dict(family="Inter", size=14, weight="bold"))
        st.plotly_chart(fig_sun, use_container_width=True)
else:
    with st.container(border=True):
        st.success("No violations found. Hierarchical breakdown is empty.")

st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="panel-label">Risk Profile (Radar)</div>', unsafe_allow_html=True)
    cats = list(violations_by_category.keys())
    counts = [len(v) for v in violations_by_category.values()]
    
    with st.container(border=True):
        if cats:
            cats.append(cats[0]); counts.append(counts[0])
            fig_radar = go.Figure(data=go.Scatterpolar(
                r=counts, theta=cats, fill='toself',
                fillcolor="rgba(17, 82, 212, 0.2)",
                line=dict(color="#1152d4", width=3),
                marker=dict(size=8, color="#1152d4")
            ))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, showline=False, gridcolor="rgba(255,255,255,0.1)"),
                    angularaxis=dict(gridcolor="rgba(255,255,255,0.1)")
                ),
                showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=layout_theme["font"], height=380, margin=dict(t=30, b=30, l=40, r=40)
            )
            st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.info("Insufficient data for radar.")

with c2:
    st.markdown('<div class="panel-label">Rules Progression</div>', unsafe_allow_html=True)
    with st.container(border=True):
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            x=["Result"], y=[rep["passed_rules"]], name="Passed",
            marker_color="#10b981", text=f"{rep['passed_rules']} Passed", textposition="auto"
        ))
        fig_bar.add_trace(go.Bar(
            x=["Result"], y=[rep["failed_rules"]], name="Failed",
            marker_color="#ef4444", text=f"{rep['failed_rules']} Failed", textposition="auto"
        ))
        fig_bar.update_layout(
            **layout_theme, barmode='stack', height=380,
            showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
f_c1, f_c2 = st.columns(2)
with f_c1:
    if st.button("⬅ RETURN TO EXECUTIVE REPORT", type="secondary", use_container_width=True):
        st.switch_page("pages/3_Report.py")
        
with f_c2:
    st.download_button("EXPORT ANALYTICS DATA (CSV)", df.to_csv(index=False), file_name=f"analysis_{st.session_state.run_id}.csv", mime="text/csv", type="primary", use_container_width=True)
