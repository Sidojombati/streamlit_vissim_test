import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from utils import to_excel

st.title("Flows")

# ---------------------------------------------------------
# Load uploaded or placeholder data
# ---------------------------------------------------------
if "uploaded_data" in st.session_state:
    df = st.session_state["uploaded_data"]
else:
    # Create placeholder 15-minute intervals
    intervals = pd.date_range("07:00", "09:00", freq="15min").strftime("%H:%M")
    links = [f"Link {i}" for i in range(1, 11)]

    data = []
    np.random.seed(1)
    for link in links:
        for t in intervals:
            model = np.random.randint(500, 1500)
            obs = np.random.randint(500, 1500)
            abs_diff = abs(model - obs)
            pct_diff = abs_diff / obs * 100 if obs != 0 else 0

            data.append({
                "Link": link,
                "Time Interval": t,
                "Modelled Flow": model,
                "Observed Flow": obs,
                "Absolute Difference": abs_diff,
                "Percentage Difference": pct_diff
            })

    df = pd.DataFrame(data)

# ---------------------------------------------------------
# Time interval slider
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

# Filter by time window
df_window = df[df["Time Interval"].isin(selected_intervals)]

# ---------------------------------------------------------
# Summary table (averaged across selected time window)
# ---------------------------------------------------------
summary = (
    df_window.groupby("Link")
    .agg({
        "Modelled Flow": "mean",
        "Observed Flow": "mean",
        "Absolute Difference": "mean",
        "Percentage Difference": "mean"
    })
    .reset_index()
)

summary = summary.round(2)

# ---------------------------------------------------------
# Show/hide table toggle
# ---------------------------------------------------------
show_table = st.checkbox("Show summary table", value=True)

if show_table:
    st.subheader("Average Flows Across Selected Time Window")
    st.write(f"Time range: **{intervals[start_idx]} → {intervals[end_idx]}**")
    st.dataframe(summary)

    excel_data = to_excel(summary, sheet_name="Flows")
    st.download_button(
        label="Download as Excel",
        data=excel_data,
        file_name=f"flows_summary_{intervals[start_idx]}_{intervals[end_idx]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ---------------------------------------------------------
# Multi-select for charts
# ---------------------------------------------------------
links = summary["Link"].unique()
selected_links = st.multiselect(
    "Select links to display charts",
    links,
    default=links[:1]
)

df_filtered = df_window[df_window["Link"].isin(selected_links)]

# ---------------------------------------------------------
# Display multiple charts
# ---------------------------------------------------------
st.subheader("Flow Comparison Charts")

for link in selected_links:
    df_chart = df_filtered[df_filtered["Link"] == link]

    st.markdown(f"### {link}")

    chart = (
        alt.Chart(df_chart)
        .transform_fold(["Modelled Flow", "Observed Flow"], as_=["Type", "Flow"])
        .mark_line(point=True)
        .encode(
            x="Time Interval:N",
            y="Flow:Q",
            color="Type:N"
        )
    )

    st.altair_chart(chart, use_container_width=True)
