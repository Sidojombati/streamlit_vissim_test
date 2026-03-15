import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from utils import to_excel

st.title("Journey Times")

# ---------------------------------------------------------
# Load uploaded or placeholder data
# ---------------------------------------------------------
if "uploaded_data" in st.session_state:
    df = st.session_state["uploaded_data"]
else:
    intervals = pd.date_range("07:00", "09:00", freq="15min").strftime("%H:%M")
    routes = [f"Route {i}" for i in range(1, 6)]

    data = []
    np.random.seed(2)
    for r in routes:
        for t in intervals:
            model = np.random.randint(200, 600)
            obs = np.random.randint(200, 600)
            data.append({
                "Route": r,
                "Time Interval": t,
                "Modelled JT (s)": model,
                "Observed JT (s)": obs,
                "Abs Diff": abs(model - obs),
                "Pct Diff": abs(model - obs) / obs * 100
            })

    df = pd.DataFrame(data)

# ---------------------------------------------------------
# Time interval slider (applies to ALL routes)
# ---------------------------------------------------------
intervals = sorted(df["Time Interval"].unique())
start_idx, end_idx = st.slider(
    "Select a time range",
    min_value=0,
    max_value=len(intervals) - 1,
    value=(0, len(intervals) - 1),
    step=1
)

selected_intervals = intervals[start_idx:end_idx + 1]

# Filter entire dataset for validation summary
df_window = df[df["Time Interval"].isin(selected_intervals)]

# ---------------------------------------------------------
# Validation summary (per route)
# ---------------------------------------------------------
summary = (
    df_window.groupby("Route")
    .agg({
        "Abs Diff": "mean",
        "Pct Diff": "mean"
    })
    .reset_index()
)

summary["Pass/Fail"] = summary.apply(
    lambda row: "Pass" if (row["Abs Diff"] <= 60 and row["Pct Diff"] <= 15) else "Fail",
    axis=1
)

st.subheader("Validation Summary (across selected time window)")
st.write(f"Time range: **{intervals[start_idx]} → {intervals[end_idx]}**")
st.dataframe(summary)

# ---------------------------------------------------------
# Route selector (for detailed view)
# ---------------------------------------------------------
routes = df["Route"].unique()
selected_route = st.selectbox("Select a route to view details", routes)

df_filtered = df_window[df_window["Route"] == selected_route]

st.subheader(f"Journey Time Comparison for {selected_route}")
st.dataframe(df_filtered)

# ---------------------------------------------------------
# Export filtered data
# ---------------------------------------------------------
excel_data = to_excel(df_filtered, sheet_name="JourneyTimes")
st.download_button(
    label="Download as Excel",
    data=excel_data,
    file_name=f"journey_times_{selected_route}_{intervals[start_idx]}_{intervals[end_idx]}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# ---------------------------------------------------------
# Chart
# ---------------------------------------------------------
chart = (
    alt.Chart(df_filtered)
    .transform_fold(["Modelled JT (s)", "Observed JT (s)"], as_=["Type", "Time"])
    .mark_line(point=True)
    .encode(
        x="Time Interval:N",
        y="Time:Q",
        color="Type:N"
    )
)

st.altair_chart(chart, use_container_width=True)
