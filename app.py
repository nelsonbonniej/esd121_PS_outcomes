"""
ESD 121 Graduate Outcomes — Home
"""

import streamlit as st

st.set_page_config(
    page_title="ESD 121 Graduate Outcomes",
    page_icon="🎓",
    layout="wide",
)

st.title("ESD 121 — High School Graduate Outcomes")
st.markdown(
    """
    This dashboard uses data from the Washington Office of Superintendent of Public Instruction (OSPI)
    to track what happens to ESD 121 graduates after high school.
    All earnings are adjusted to **2024 dollars** using the CPI-W index.

    ---

    **Use the navigation on the left to explore:**
    """
)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        ### 💰 Earnings Outcomes
        How much are graduates earning — by credential level, over time, across
        demographic groups, and by district?
        - ESD 121 trend vs. statewide benchmarks
        - Earnings gaps by race/ethnicity, gender, income, and GPA
        - District-level comparison and drill-down
        """
    )

with col2:
    st.markdown(
        """
        ### 🏛️ Where Students Enroll
        Which colleges and universities are ESD 121 graduates attending?
        - 4-year vs. 2-year / CTC breakdown
        - Top institutions by enrollment share
        - District-level enrollment patterns
        - Trends across the 2023–2025 cohorts
        """
    )

st.divider()
st.caption(
    "Data source: OSPI High School Graduate Outcomes dataset. "
    "Earnings data covers graduates within 15 years of high school completion. "
    "Cells with fewer than 10 individuals are suppressed (shown as 0–1%) to protect privacy."
)
