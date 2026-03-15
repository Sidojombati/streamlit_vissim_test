import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from utils import to_excel

st.title("Queues")

# ---------------------------------------------------------
# Load uploaded or placeholder data
# ---------------------------------------------------------
if "uploaded_data" in st.session_state:
    df = st.session_state["uploaded_data"]
else:
    intervals = pd.date_range("07:00", "09:00", freq="15min").strftime("%H:%M")
    approaches = [f"Approach {i}" for i in range(1, 6)]

    data = []
    np.random.seed(3)
    for a in approaches:
        for t in intervals:
            data.append({
                "Approach": a,
                "Time Interval": t,
                "Modelled Queue (m)": np.random.randint(5, 50),
                "Observed Queue (m)": np.random.randint(5, 50)
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
df_window = df[df["Time Interval"].isin(selected_intervals)]

# ---------------------------------------------------------
# Multi-select for approaches
# ---------------------------------------------------------
approaches = df_window["Approach"].unique()
selected_approaches = st.multiselect(
    "Select one or more approaches",
    approaches,
    default=approaches[:1]
)

df_filtered = df_window[df_window["Approach"].isin(selected_approaches)]

# ---------------------------------------------------------
# Show/hide table toggle
# ---------------------------------------------------------
show_table = st.checkbox("Show table", value=True)

if show_table:
    st.subheader("Queue Data for Selected Approaches")
    st.write(f"Time range: **{intervals[start_idx]} → {intervals[end_idx]}**")
    st.dataframe(df_filtered)

    excel_data = to_excel(df_filtered, sheet_name="Queues")
    st.download_button(
        label="Download as Excel",
        data=excel_data,
        file_name=f"queues_{intervals[start_idx]}_{intervals[end_idx]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ---------------------------------------------------------
# Display multiple charts
# ---------------------------------------------------------
st.subheader("Queue Comparison Charts")

for approach in selected_approaches:
    df_chart = df_filtered[df_filtered["Approach"] == approach]

    st.markdown(f"### {approach}")

    chart = (
        alt.Chart(df_chart)
        .transform_fold(["Modelled Queue (m)", "Observed Queue (m)"], as_=["Type", "Queue"])
        .mark_line(point=True)
        .encode(
            x="Time Interval:N",
            y="Queue:Q",
            color="Type:N"
        )
    )

    st.altair_chart(chart, use_container_width=True)
