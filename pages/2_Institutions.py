"""
Page 2 — Where Students Enroll
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from data import (
    esd_enrollment, district_enrollment,
    ENROLL_COLORS,
)

st.set_page_config(page_title="Where Students Enroll", page_icon="🏛️", layout="wide")

st.title("🏛️ Where Students Enroll")
st.caption(
    "Postsecondary enrollment for ESD 121 graduates. "
    "Institutions with fewer than 10 enrollees are suppressed and shown as '0–1%' to protect privacy. "
    "Source: OSPI High School Graduate Outcomes."
)

# ── Load data ──────────────────────────────────────────────────────────────────
esd_df  = esd_enrollment()
dist_df = district_enrollment()

# ── Controls ───────────────────────────────────────────────────────────────────
top_col1, top_col2 = st.columns([1, 1])

with top_col1:
    # Cohort year
    all_years = sorted(esd_df["CohortYearTTL"].unique())
    selected_year = st.selectbox("Graduation cohort", all_years, index=len(all_years)-1)

with top_col2:
    # First-year vs cumulative
    enroll_type = st.radio(
        "Enrollment window",
        ["First fall after graduation", "Cumulative (within study window)"],
        horizontal=True,
    )
    fall_flag = "Y" if "First fall" in enroll_type else "N"

# Filter ESD-wide for selected year + type
esd_sub = esd_df[
    (esd_df["CohortYearTTL"] == selected_year) &
    (esd_df["FallFirstYearFlg"] == fall_flag)
].copy()

# Use numeric Pct where available; treat redacted as 0.005 (midpoint of 0–1%) for display
esd_sub["PctNum"] = esd_sub["Pct"].fillna(0.005)

st.divider()

# ── Section 1: ESD-wide 2-year vs 4-year split ────────────────────────────────
st.subheader("ESD 121 enrollment overview")

type_totals = esd_sub.groupby("PSEnrollLevel")["PctNum"].sum().reset_index()

split_col1, split_col2 = st.columns([1, 2])

with split_col1:
    # Donut chart
    fig_donut = go.Figure(go.Pie(
        labels=type_totals["PSEnrollLevel"],
        values=type_totals["PctNum"],
        hole=0.55,
        marker_colors=[ENROLL_COLORS.get(lv, "#888") for lv in type_totals["PSEnrollLevel"]],
        textinfo="label+percent",
        hovertemplate="%{label}: %{percent}<extra></extra>",
    ))
    fig_donut.update_layout(
        showlegend=False,
        height=260,
        margin=dict(t=10, b=10, l=10, r=10),
        annotations=[dict(text="Enrollment<br>split", x=0.5, y=0.5, font_size=13, showarrow=False)],
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with split_col2:
    # Metric callouts
    for _, row in type_totals.iterrows():
        pct = round(row["PctNum"] * 100)
        color = ENROLL_COLORS.get(row["PSEnrollLevel"], "#888")
        st.markdown(
            f"""
            <div style="padding:10px 16px;margin-bottom:10px;border-left:4px solid {color};background:var(--background-secondary)">
                <div style="font-size:13px;color:#666">{row['PSEnrollLevel']}</div>
                <div style="font-size:28px;font-weight:600">{pct}%</div>
                <div style="font-size:12px;color:#888">of graduates enrolled</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Section 2: Top institutions bar chart ─────────────────────────────────────
st.subheader("Top institutions by enrollment share")

# Filter out "Other" catch-all rows for the ranked chart
ranked = esd_sub[~esd_sub["PSOrganizationTTL"].str.startswith("Other")].copy()
ranked = ranked.sort_values("PctNum", ascending=True)

fig_inst = go.Figure(go.Bar(
    x=ranked["PctNum"] * 100,
    y=ranked["PSOrganizationTTL"],
    orientation="h",
    marker_color=[ENROLL_COLORS.get(lv, "#888") for lv in ranked["PSEnrollLevel"]],
    text=[f"{v*100:.0f}%" if v > 0.005 else "<1%" for v in ranked["PctNum"]],
    textposition="outside",
    hovertemplate="<b>%{y}</b><br>%{x:.1f}% of graduates<extra></extra>",
))

# Add a legend manually via invisible scatter traces
for level, color in ENROLL_COLORS.items():
    fig_inst.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(size=10, color=color, symbol="square"),
        name=level, showlegend=True,
    ))

fig_inst.update_layout(
    xaxis_title="Share of graduates (%)",
    xaxis_ticksuffix="%",
    legend=dict(orientation="h", y=-0.2),
    height=max(350, len(ranked) * 28 + 80),
    margin=dict(t=20, b=60, l=220, r=80),
)
st.plotly_chart(fig_inst, use_container_width=True)

st.caption(
    "'Other 2 Year' and 'Other 4 Year' aggregate institutions with small individual enrollment shares. "
    "Suppressed institutions (0–1%) are excluded from this chart."
)

# ── Section 3: Trend across cohorts ───────────────────────────────────────────
st.subheader("Enrollment trends — 2023 to 2025 cohorts")

# Only "N" (cumulative) data has all three cohort years
trend_data = esd_df[esd_df["FallFirstYearFlg"] == "N"].copy()
trend_data["PctNum"] = trend_data["Pct"].fillna(0.005)

level_trend = trend_data.groupby(["CohortYearTTL", "PSEnrollLevel"])["PctNum"].sum().reset_index()

fig_trend = go.Figure()
for level, color in ENROLL_COLORS.items():
    sub = level_trend[level_trend["PSEnrollLevel"] == level].sort_values("CohortYearTTL")
    fig_trend.add_trace(go.Scatter(
        x=sub["CohortYearTTL"], y=sub["PctNum"] * 100,
        mode="lines+markers+text",
        name=level,
        line=dict(color=color, width=2),
        marker=dict(size=8),
        text=[f"{v*100:.0f}%" for v in sub["PctNum"]],
        textposition="top center",
        hovertemplate=f"<b>{level}</b><br>%{{x}}: %{{y:.1f}}%<extra></extra>",
    ))

fig_trend.update_layout(
    xaxis_title="Graduation cohort",
    yaxis_title="Share of graduates (%)",
    yaxis_ticksuffix="%",
    xaxis=dict(tickmode="array", tickvals=sorted(trend_data["CohortYearTTL"].unique())),
    legend=dict(orientation="h", y=-0.2),
    height=340, margin=dict(t=20, b=60),
)
st.plotly_chart(fig_trend, use_container_width=True)

st.caption(
    "Trend uses cumulative enrollment data (FallFirstYearFlg = N). "
    "2025 first-fall data is also available but covers a shorter window."
)

# ── Section 4: District drill-down ────────────────────────────────────────────
st.subheader("District enrollment breakdown")

dist_col1, dist_col2 = st.columns([1, 2])

with dist_col1:
    dist_year = st.selectbox(
        "Cohort year", sorted(dist_df["CohortYearTTL"].unique()),
        index=len(dist_df["CohortYearTTL"].unique())-1,
        key="dist_year",
    )
    dist_flag = st.radio(
        "Enrollment window",
        ["First fall", "Cumulative"],
        key="dist_flag",
        horizontal=True,
    )
    flag_val = "Y" if dist_flag == "First fall" else "N"

    selected_dist = st.selectbox(
        "Select a district",
        sorted(dist_df["DistrictTTL"].unique()),
        key="sel_district",
    )

dist_sub = dist_df[
    (dist_df["DistrictTTL"] == selected_dist) &
    (dist_df["CohortYearTTL"] == dist_year) &
    (dist_df["FallFirstYearFlg"] == flag_val)
].copy()
dist_sub["PctNum"] = dist_sub["Pct"].fillna(0.005)

with dist_col2:
    if dist_sub.empty:
        st.info("No data available for this selection.")
    else:
        # Donut for this district
        type_tot = dist_sub.groupby("PSEnrollLevel")["PctNum"].sum().reset_index()
        fig_d_donut = go.Figure(go.Pie(
            labels=type_tot["PSEnrollLevel"],
            values=type_tot["PctNum"],
            hole=0.55,
            marker_colors=[ENROLL_COLORS.get(lv, "#888") for lv in type_tot["PSEnrollLevel"]],
            textinfo="label+percent",
            hovertemplate="%{label}: %{percent}<extra></extra>",
        ))
        fig_d_donut.update_layout(
            showlegend=False, height=240,
            margin=dict(t=10, b=10, l=10, r=10),
            annotations=[dict(text=selected_dist, x=0.5, y=0.5, font_size=11, showarrow=False)],
        )
        st.plotly_chart(fig_d_donut, use_container_width=True)

# Institution breakdown for selected district
if not dist_sub.empty:
    ranked_d = dist_sub[~dist_sub["PSOrganizationTTL"].str.startswith("Other")].sort_values("PctNum", ascending=True)
    if not ranked_d.empty:
        fig_d_inst = go.Figure(go.Bar(
            x=ranked_d["PctNum"] * 100,
            y=ranked_d["PSOrganizationTTL"],
            orientation="h",
            marker_color=[ENROLL_COLORS.get(lv, "#888") for lv in ranked_d["PSEnrollLevel"]],
            text=[f"{v*100:.0f}%" if v > 0.005 else "<1%" for v in ranked_d["PctNum"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{x:.1f}% of graduates<extra></extra>",
        ))
        fig_d_inst.update_layout(
            title=f"{selected_dist} — top institutions ({dist_year})",
            xaxis_title="Share of graduates (%)",
            xaxis_ticksuffix="%",
            height=max(300, len(ranked_d) * 26 + 80),
            margin=dict(t=50, b=40, l=220, r=80),
            showlegend=False,
        )
        st.plotly_chart(fig_d_inst, use_container_width=True)

# ── Section 5: Side-by-side district comparison ───────────────────────────────
st.subheader("Compare districts — 4-year vs 2-year enrollment")

comp_year = st.selectbox(
    "Cohort year", sorted(dist_df["CohortYearTTL"].unique()),
    key="comp_year",
)
comp_flag_label = st.radio("Enrollment window", ["First fall", "Cumulative"], key="comp_flag", horizontal=True)
comp_flag = "Y" if comp_flag_label == "First fall" else "N"

comp_df = dist_df[
    (dist_df["CohortYearTTL"] == comp_year) &
    (dist_df["FallFirstYearFlg"] == comp_flag)
].copy()
comp_df["PctNum"] = comp_df["Pct"].fillna(0.005)

comp_summary = comp_df.groupby(["DistrictTTL", "PSEnrollLevel"])["PctNum"].sum().unstack(fill_value=0).reset_index()
comp_summary.columns.name = None
for col in ["4 Year", "2 Year / CTC"]:
    if col not in comp_summary.columns:
        comp_summary[col] = 0
comp_summary["Total"] = comp_summary["4 Year"] + comp_summary["2 Year / CTC"]
comp_summary = comp_summary.sort_values("4 Year", ascending=True)

fig_comp = go.Figure()
fig_comp.add_trace(go.Bar(
    y=comp_summary["DistrictTTL"],
    x=comp_summary["4 Year"] * 100,
    name="4 Year", orientation="h",
    marker_color=ENROLL_COLORS["4 Year"],
    hovertemplate="<b>%{y}</b><br>4-year: %{x:.1f}%<extra></extra>",
))
fig_comp.add_trace(go.Bar(
    y=comp_summary["DistrictTTL"],
    x=comp_summary["2 Year / CTC"] * 100,
    name="2 Year / CTC", orientation="h",
    marker_color=ENROLL_COLORS["2 Year / CTC"],
    hovertemplate="<b>%{y}</b><br>2-year/CTC: %{x:.1f}%<extra></extra>",
))
fig_comp.update_layout(
    barmode="stack",
    xaxis_title="Share of graduates enrolling (%)",
    xaxis_ticksuffix="%",
    legend=dict(orientation="h", y=-0.15),
    height=max(500, len(comp_summary) * 22 + 100),
    margin=dict(t=20, b=60, l=160),
)
st.plotly_chart(fig_comp, use_container_width=True)
st.caption(
    "Percentages reflect graduates who enrolled, not total enrollment numbers. "
    "Suppressed values (<1%) are shown at 0.5% for display purposes."
)
