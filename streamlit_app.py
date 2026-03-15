import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Vissim Dashboard", layout="wide")

st.title("Vissim Model Results Dashboard")
st.write("Upload Vissim output files and explore modelled vs observed results.")

# -------------------------
# File Upload Section
# -------------------------
st.subheader("Upload Vissim Data")

uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df_uploaded = pd.read_csv(uploaded_file)
    else:
        df_uploaded = pd.read_excel(uploaded_file)

    st.session_state["uploaded_data"] = df_uploaded
    st.write("Uploaded data preview:")
    st.dataframe(df_uploaded.head())
else:
    st.info("No file uploaded yet. Using placeholder data.")

st.subheader("Observed vs Modelled Flow Comparison")

# ---------------------------------------------------------
# Prepare data (average across intervals if needed)
# ---------------------------------------------------------
if "uploaded_data" in st.session_state:
    df = st.session_state["uploaded_data"]

    # Expecting columns: Link, Time Interval, Modelled Flow, Observed Flow
    df_avg = (
        df.groupby("Link")
        .agg({
            "Modelled Flow": "mean",
            "Observed Flow": "mean"
        })
        .reset_index()
    )
else:
    # Placeholder data
    np.random.seed(10)
    df_avg = pd.DataFrame({
        "Link": [f"Link {i}" for i in range(1, 11)],
        "Modelled Flow": np.random.randint(500, 1500, 10),
        "Observed Flow": np.random.randint(500, 1500, 10)
    })

# ---------------------------------------------------------
# Calculate line of best fit + R²
# ---------------------------------------------------------
x = df_avg["Observed Flow"]
y = df_avg["Modelled Flow"]

# Fit linear regression
coeffs = np.polyfit(x, y, 1)
slope, intercept = coeffs

# Predicted values
y_pred = slope * x + intercept

# R² calculation
ss_res = np.sum((y - y_pred) ** 2)
ss_tot = np.sum((y - np.mean(y)) ** 2)
r_squared = 1 - (ss_res / ss_tot)

# Add regression line to dataframe
df_line = pd.DataFrame({
    "Observed Flow": [x.min(), x.max()],
    "Modelled Flow": [slope * x.min() + intercept, slope * x.max() + intercept]
})

# ---------------------------------------------------------
# Build Altair scatter + regression line
# ---------------------------------------------------------
scatter = alt.Chart(df_avg).mark_circle(size=80).encode(
    x=alt.X("Observed Flow:Q", title="Observed Flow"),
    y=alt.Y("Modelled Flow:Q", title="Modelled Flow"),
    tooltip=["Link", "Observed Flow", "Modelled Flow"]
)

line = alt.Chart(df_line).mark_line(color="red").encode(
    x="Observed Flow:Q",
    y="Modelled Flow:Q"
)

chart = (scatter + line).properties(
    width=600,
    height=400,
    title=f"Observed vs Modelled Flows (R² = {r_squared:.3f})"
)

st.altair_chart(chart, use_container_width=True)
