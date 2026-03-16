import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys; import os; sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

st.markdown('<div class="app-header">4. ADVANCED ANALYSIS</div>', unsafe_allow_html=True)

if not st.session_state.report:
    st.warning("No generated report found for analysis. Please run a compliance check in the Input section.")
    if st.button("Go to Input ➔", type="primary"):
        st.switch_page("pages/1_Input.py")
    st.stop()

rep = st.session_state.report

# Prepare Data
violations_by_category = rep.get("violations_by_category", {})

# Flatten violations for DataFrame
all_violations = []
for cat, v_list in violations_by_category.items():
    for v in v_list:
        all_violations.append({
            "Category": cat,
            "Severity": v["severity"].capitalize(),
            "Rule Core": v["rule_id"].split("-")[0]
        })

df = pd.DataFrame(all_violations)

# Color pallette matching the CSS
severity_colors = {
    "Critical": "#dc2626", # Red
    "High": "#ea580c",     # Orange
    "Medium": "#d97706",    # Amber
    "Low": "#0284c7"       # Blue
}

layout_theme = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#94a3b8", "family": "Inter, sans-serif", "size": 15},
    "xaxis": {"gridcolor": "rgba(255,255,255,0.1)", "linecolor": "rgba(255,255,255,0.2)", "tickcolor": "#64748b"},
    "yaxis": {"gridcolor": "rgba(255,255,255,0.1)", "linecolor": "rgba(255,255,255,0.2)", "tickcolor": "#64748b"}
}
if st.session_state.theme == "light":
    layout_theme["font"]["color"] = "#1e293b"
    layout_theme["xaxis"]["gridcolor"] = "rgba(0,0,0,0.1)"
    layout_theme["xaxis"]["linecolor"] = "rgba(0,0,0,0.3)"
    layout_theme["yaxis"]["gridcolor"] = "rgba(0,0,0,0.1)"
    layout_theme["yaxis"]["linecolor"] = "rgba(0,0,0,0.3)"


st.markdown('<div class="panel-label">// SEVERITY DISTRIBUTION SUNBURST</div>', unsafe_allow_html=True)
if not df.empty:
    fig_sun = px.sunburst(df, path=['Severity', 'Category'], color='Severity',
                          color_discrete_map=severity_colors,
                          title="Violation Hierarchical Breakdown")
    fig_sun.update_layout(**layout_theme, margin=dict(t=50, l=0, r=0, b=0), height=500)
    fig_sun.update_traces(textfont=dict(family="Outfit", size=16, weight="bold"))
    st.plotly_chart(fig_sun, use_container_width=True)
else:
    st.success("No violations to map! Perfect compliance.")

st.markdown("<hr>", unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="panel-label">// CATEGORY RADAR ANALYSIS</div>', unsafe_allow_html=True)
    cats = list(violations_by_category.keys())
    counts = [len(v) for v in violations_by_category.values()]
    
    if cats:
        # Close the radar loop
        cats.append(cats[0])
        counts.append(counts[0])
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=counts,
            theta=cats,
            fill='toself',
            fillcolor="rgba(244, 114, 182, 0.4)",
            line=dict(color="#f472b6", width=3),
            marker=dict(size=10, color="#8b5cf6")
        ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, showline=False, gridcolor="rgba(255,255,255,0.2)") if st.session_state.theme == "dark" else dict(visible=True, showline=False, gridcolor="rgba(0,0,0,0.2)"),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.2)") if st.session_state.theme == "dark" else dict(gridcolor="rgba(0,0,0,0.2)")
            ),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=layout_theme["font"],
            height=450
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("Insufficient data for radar chart.")

with c2:
    st.markdown('<div class="panel-label">// RULE PROGRESSION METRICS</div>', unsafe_allow_html=True)
    
    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        x=["Compliance Checks"],
        y=[rep["passed_rules"]],
        name="Passed",
        marker_color="#10b981",
        text=f"{rep['passed_rules']} Passed",
        textposition="auto",
        textfont=dict(size=18, family="Outfit", color="white")
    ))
    fig_bar.add_trace(go.Bar(
        x=["Compliance Checks"],
        y=[rep["failed_rules"]],
        name="Failed",
        marker_color="#ef4444",
        text=f"{rep['failed_rules']} Failed",
        textposition="auto",
        textfont=dict(size=18, family="Outfit", color="white")
    ))
    
    fig_bar.update_layout(
        **layout_theme,
        barmode='stack',
        height=450,
        title="Check Ratio",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_bar, use_container_width=True)


st.markdown("---")
# Cross Page Tracking buttons
f_c1, f_c2 = st.columns(2)
with f_c1:
    if st.button("⬅ Back to Report", type="secondary", use_container_width=True):
        st.switch_page("pages/3_Report.py")
        
with f_c2:
    st.download_button("Export Analysis Data (CSV)", df.to_csv(index=False), file_name=f"analysis_{st.session_state.run_id}.csv", mime="text/csv", type="primary", use_container_width=True)
