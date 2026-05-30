"""
Page 1 — Earnings Outcomes
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from data import (
    esd_trend, esd_all_y10, statewide_all_y10,
    demo_y10_esd, district_y10, district_trend,
    ACH_COLORS, ACH_ORDER, ACH_3,
)

st.set_page_config(page_title="Earnings Outcomes", page_icon="💰", layout="wide")

st.title("💰 Earnings Outcomes")
st.caption(
    "Median annual earnings (2024 dollars) at year 10 after high school graduation. "
    "Source: OSPI High School Graduate Outcomes."
)

# ── Load data ──────────────────────────────────────────────────────────────────
trend_df   = esd_trend()
esd_all    = esd_all_y10()
sw_all     = statewide_all_y10()
demo_df    = demo_y10_esd()
dist_df    = district_y10()
dist_trend = district_trend()

# ── Section 1: ESD Overview metrics ───────────────────────────────────────────
st.subheader("ESD 121 at a glance — year 10 earnings")

cols = st.columns(4)
for i, ach in enumerate(ACH_ORDER):
    row = trend_df[(trend_df["HighestAchievement"] == ach) & (trend_df["YearAfterGrad"] == 10)]
    if not row.empty:
        val = int(row["MedianEarnings"].iloc[0])
        cols[i].metric(ach, f"${val:,}")

# ── Section 2: Trend chart ─────────────────────────────────────────────────────
st.subheader("Earnings over time — all ESD 121 students")

fig_trend = go.Figure()
for ach in ACH_ORDER:
    sub = trend_df[trend_df["HighestAchievement"] == ach].sort_values("YearAfterGrad")
    dash = "dot" if ach == "HS Diploma" else "dash" if ach == "Associate/Certificate" else "solid"
    fig_trend.add_trace(go.Scatter(
        x=sub["YearAfterGrad"], y=sub["MedianEarnings"],
        mode="lines+markers", name=ach,
        line=dict(color=ACH_COLORS[ach], dash=dash, width=2),
        marker=dict(size=5),
        hovertemplate=f"<b>{ach}</b><br>Year %{{x}}: $%{{y:,}}<extra></extra>",
    ))

fig_trend.update_layout(
    xaxis_title="Years after high school graduation",
    yaxis_title="Median annual earnings",
    yaxis_tickprefix="$", yaxis_tickformat=",",
    legend=dict(orientation="h", y=-0.2),
    height=400, margin=dict(t=20, b=60),
    hovermode="x unified",
)
fig_trend.update_xaxes(dtick=1)
st.plotly_chart(fig_trend, use_container_width=True)

st.caption(
    "⚠️ Apprenticeship data begins at year 5 due to program length. "
    "Apprenticeships offer high-wage jobs but few openings exist; interpret with caution in subgroup analyses."
)

# ── Section 3: Demographics ────────────────────────────────────────────────────
st.subheader("Earnings by demographic group — year 10")
st.markdown(
    "Bars show how each subgroup compares to the selected all-students average. "
    "Right of zero = earning more. Left of zero = earning less."
)

demo_col1, demo_col2 = st.columns([1, 2])

with demo_col1:
    demo_group = st.selectbox(
        "Demographic group",
        ["Race/Ethnicity", "Gender", "FRPL", "GPA"],
        key="demo_group",
    )
    benchmark = st.selectbox(
        "Compare to",
        ["ESD 121 median — all students", "State median — all students"],
        key="benchmark",
    )

base_map   = esd_all if "ESD" in benchmark else sw_all
base_label = "ESD 121 all students" if "ESD" in benchmark else "Statewide all students"

# Short labels for long demographic values
SHORT = {
    "American Indian or Alaska Native":               "Am. Indian / AK Native",
    "Native Hawaiian and Other Pacific Islander":     "NH / Pacific Islander",
    "Hispanic or Latino of any race(s)":              "Hispanic / Latino",
    "Black or African American":                      "Black / African American",
    "Two or More Races":                              "Two or more races",
}

filtered = demo_df[demo_df["DemographicGrouping"] == demo_group].copy()
filtered["Label"] = filtered["DemographicValue"].map(lambda v: SHORT.get(v, v))
filtered["Base"]  = filtered["HighestAchievement"].map(base_map)
filtered["Diff"]  = filtered["MedianEarnings"] - filtered["Base"]
filtered = filtered[filtered["HighestAchievement"].isin(ACH_3)]

fig_demo = go.Figure()
for ach in ACH_3:
    sub = filtered[filtered["HighestAchievement"] == ach].sort_values("Label")
    fig_demo.add_trace(go.Bar(
        x=sub["Diff"],
        y=sub["Label"],
        name=ach,
        orientation="h",
        marker_color=[ACH_COLORS[ach] if v >= 0 else ACH_COLORS[ach] + "88" for v in sub["Diff"]],
        customdata=sub[["MedianEarnings", "Base", "HighestAchievement"]].values,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{customdata[2]}<br>"
            "Earns: $%{customdata[0]:,}<br>"
            f"{base_label}: $%{{customdata[1]:,}}<br>"
            "Difference: %{x:+,}<extra></extra>"
        ),
    ))

# Zero line annotation
fig_demo.add_vline(x=0, line_width=1.5, line_color="rgba(0,0,0,0.4)")

fig_demo.update_layout(
    barmode="group",
    xaxis_title=f"← Earning less than {base_label}   |   Earning more than {base_label} →",
    xaxis_tickprefix="$" ,
    xaxis=dict(tickformat="+,d"),
    legend=dict(orientation="h", y=-0.25),
    height=max(350, len(filtered["Label"].unique()) * 55 + 100),
    margin=dict(t=20, b=80, l=180),
    hovermode="closest",
)

# Benchmark callout
benchmark_text = "  |  ".join(
    [f"{a}: ${base_map[a]:,}" for a in ACH_3 if a in base_map]
)
st.caption(f"**{base_label} benchmarks:** {benchmark_text}")
st.plotly_chart(fig_demo, use_container_width=True)

st.caption(
    "Apprenticeship is excluded from demographic breakouts due to small subgroup sample sizes across many groups."
)

# ── Section 4: District comparison ────────────────────────────────────────────
st.subheader("District comparison — year 10 earnings")

dist_ach = st.selectbox(
    "Achievement level",
    ACH_3,
    key="dist_ach",
)

esd_avg = esd_all.get(dist_ach, 0)
sub_dist = dist_df[dist_df["HighestAchievement"] == dist_ach].copy()
sub_dist["Diff"] = sub_dist["MedianEarnings"] - esd_avg
sub_dist = sub_dist.sort_values("Diff", ascending=True)

# Add ESD row at zero
esd_row = pd.DataFrame([{
    "DistrictTTL": "ESD 121 average",
    "HighestAchievement": dist_ach,
    "MedianEarnings": esd_avg,
    "NumRecords": None,
    "Diff": 0,
}])
plot_dist = pd.concat([sub_dist, esd_row], ignore_index=True).sort_values("Diff", ascending=True)

bar_colors = plot_dist["Diff"].apply(
    lambda d: "rgba(100,100,100,0.5)" if d == 0
    else ("rgba(24,95,165,0.85)" if d > 0 else "rgba(153,60,29,0.85)")
).tolist()

fig_dist = go.Figure(go.Bar(
    x=plot_dist["Diff"],
    y=plot_dist["DistrictTTL"],
    orientation="h",
    marker_color=bar_colors,
    customdata=plot_dist[["MedianEarnings", "DistrictTTL"]].values,
    hovertemplate=(
        "<b>%{customdata[1]}</b><br>"
        f"Median earnings: $%{{customdata[0]:,}}<br>"
        f"vs ESD avg (${esd_avg:,}): %{{x:+,}}<extra></extra>"
    ),
))

fig_dist.add_vline(x=0, line_width=1.5, line_dash="dash", line_color="rgba(80,80,80,0.6)")
fig_dist.update_layout(
    xaxis_title=f"← Below ESD 121 average (${esd_avg:,})   |   Above ESD 121 average →",
    xaxis=dict(tickformat="+,d", tickprefix="$"),
    height=max(500, len(plot_dist) * 22 + 80),
    margin=dict(t=20, b=60, l=160),
    showlegend=False,
)
st.plotly_chart(fig_dist, use_container_width=True)
st.caption("Click and drag on the chart to zoom. Double-click to reset.")

# ── Section 5: District drill-down ────────────────────────────────────────────
st.subheader("District drill-down — earnings over time")

districts = sorted(dist_trend["DistrictTTL"].unique())
selected_district = st.selectbox("Select a district", districts, key="drill_district")

sub_trend = dist_trend[dist_trend["DistrictTTL"] == selected_district].copy()

fig_drill = go.Figure()
for ach in ACH_3:
    s = sub_trend[sub_trend["HighestAchievement"] == ach].sort_values("YearAfterGrad")
    if s.empty:
        continue
    dash = "dot" if ach == "HS Diploma" else "dash" if ach == "Associate/Certificate" else "solid"
    fig_drill.add_trace(go.Scatter(
        x=s["YearAfterGrad"], y=s["MedianEarnings"],
        mode="lines+markers", name=ach,
        line=dict(color=ACH_COLORS[ach], dash=dash, width=2),
        marker=dict(size=5),
        hovertemplate=f"<b>{ach}</b><br>Year %{{x}}: $%{{y:,}}<extra></extra>",
    ))

fig_drill.update_layout(
    title=f"{selected_district} — earnings trend by credential",
    xaxis_title="Years after graduation",
    yaxis_title="Median annual earnings",
    yaxis_tickprefix="$", yaxis_tickformat=",",
    legend=dict(orientation="h", y=-0.25),
    height=380, margin=dict(t=50, b=80),
    hovermode="x unified",
)
fig_drill.update_xaxes(dtick=1)
st.plotly_chart(fig_drill, use_container_width=True)
