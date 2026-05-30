"""
Shared data loading for ESD 121 Graduate Outcomes dashboard.
All dataframes are cached so Excel files are only read once per session.
"""

import pandas as pd
import streamlit as st
from pathlib import Path

# ── File paths ─────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).parent
EARNINGS_FILE    = DATA_DIR / "High_School_Graduate_Outcomes__Earnings_20260530.xlsx"
ENROLLMENT_FILE  = DATA_DIR / "High_School_Graduate_Outcomes__Enrollment_by_Institution_20260530.xlsx"

# ── Color palette ──────────────────────────────────────────────────────────────
ACH_COLORS = {
    "HS Diploma":            "#993556",
    "Associate/Certificate": "#854F0B",
    "Bachelor's or Higher":  "#0F6E56",
    "Apprenticeship":        "#185FA5",
}
ACH_ORDER = ["HS Diploma", "Associate/Certificate", "Bachelor's or Higher", "Apprenticeship"]
ACH_3     = ["HS Diploma", "Associate/Certificate", "Bachelor's or Higher"]

ENROLL_COLORS = {
    "4 Year":      "#185FA5",
    "2 Year / CTC":"#854F0B",
}

# ── Loaders ────────────────────────────────────────────────────────────────────

@st.cache_data
def load_earnings():
    return pd.read_excel(EARNINGS_FILE)


@st.cache_data
def load_enrollment():
    return pd.read_excel(ENROLLMENT_FILE)


# ── Earnings helpers ───────────────────────────────────────────────────────────

@st.cache_data
def esd_trend():
    """ESD-wide earnings trend, all students, all years, all credentials."""
    df = load_earnings()
    return df[
        (df["DistrictType"] == "ESD") &
        (df["SchoolTTL"] == "ESD Wide") &
        (df["DemographicGrouping"] == "All Students") &
        (df["DemographicValue"] == "All")
    ][["HighestAchievement", "YearAfterGrad", "MedianEarnings", "NumRecords"]].copy()


@st.cache_data
def esd_all_y10():
    """ESD-wide all-students median at year 10, no apprenticeship."""
    df = load_earnings()
    return df[
        (df["DistrictType"] == "ESD") &
        (df["SchoolTTL"] == "ESD Wide") &
        (df["DemographicGrouping"] == "All Students") &
        (df["DemographicValue"] == "All") &
        (df["YearAfterGrad"] == 10) &
        (df["HighestAchievement"] != "Apprenticeship")
    ].set_index("HighestAchievement")["MedianEarnings"].to_dict()


@st.cache_data
def statewide_all_y10():
    """Statewide all-students median at year 10, no apprenticeship."""
    df = load_earnings()
    return df[
        (df["DistrictType"] == "Statewide") &
        (df["DemographicGrouping"] == "All Students") &
        (df["DemographicValue"] == "All") &
        (df["YearAfterGrad"] == 10) &
        (df["HighestAchievement"] != "Apprenticeship")
    ].set_index("HighestAchievement")["MedianEarnings"].to_dict()


@st.cache_data
def demo_y10_esd():
    """ESD-wide subgroup medians at year 10, no apprenticeship, no redacted."""
    df = load_earnings()
    out = df[
        (df["DistrictType"] == "ESD") &
        (df["SchoolTTL"] == "ESD Wide") &
        (df["DemographicGrouping"].isin(["Race/Ethnicity", "Gender", "FRPL", "GPA"])) &
        (df["YearAfterGrad"] == 10) &
        (df["HighestAchievement"] != "Apprenticeship")
    ].copy()
    return out[out["DemographicValue"] != "Other (Redacted)"]


@st.cache_data
def demo_y10_statewide():
    """Statewide subgroup medians at year 10, no apprenticeship, no redacted."""
    df = load_earnings()
    out = df[
        (df["DistrictType"] == "Statewide") &
        (df["DemographicGrouping"].isin(["Race/Ethnicity", "Gender", "FRPL", "GPA"])) &
        (df["YearAfterGrad"] == 10) &
        (df["HighestAchievement"] != "Apprenticeship")
    ].copy()
    return out[out["DemographicValue"] != "Other (Redacted)"]


@st.cache_data
def district_y10():
    """District-wide all-students medians at year 10, no apprenticeship."""
    df = load_earnings()
    return df[
        (df["DistrictType"] == "School Dist") &
        (df["SchoolTTL"] == "District Wide") &
        (df["DemographicGrouping"] == "All Students") &
        (df["DemographicValue"] == "All") &
        (df["YearAfterGrad"] == 10) &
        (df["HighestAchievement"] != "Apprenticeship")
    ][["DistrictTTL", "HighestAchievement", "MedianEarnings", "NumRecords"]].copy()


@st.cache_data
def district_trend():
    """District-wide all-students trend, all years, no apprenticeship."""
    df = load_earnings()
    return df[
        (df["DistrictType"] == "School Dist") &
        (df["SchoolTTL"] == "District Wide") &
        (df["DemographicGrouping"] == "All Students") &
        (df["DemographicValue"] == "All") &
        (df["HighestAchievement"] != "Apprenticeship")
    ][["DistrictTTL", "HighestAchievement", "YearAfterGrad", "MedianEarnings"]].copy()


# ── Enrollment helpers ─────────────────────────────────────────────────────────

@st.cache_data
def esd_enrollment():
    """ESD-wide enrollment, all cohorts, all flags."""
    df = load_enrollment()
    return df[
        (df["DistType"] == "ESD") &
        (df["SchoolTTL"] == "ESD Wide")
    ].copy()


@st.cache_data
def district_enrollment():
    """District-level enrollment, all cohorts, all flags."""
    df = load_enrollment()
    return df[df["DistType"] == "School Dist"].copy()
