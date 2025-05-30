
import streamlit as st
import pandas as pd
import datetime
from typing import List
import openai

# ---- Simulated data & functions ----
openai.api_key = st.secrets["OPENAI_API_KEY"]

SIMULATED_WELL_DATA = {
    "Well_101": {"last_reported": "2024-04-01", "volume": 1200},
    "Well_102": {"last_reported": "2024-05-15", "volume": 900},
    "Well_103": {"last_reported": "2024-03-20", "volume": 1600},
}

def parse_jib_file(upload) -> pd.DataFrame:
    return pd.read_csv(upload)

def get_missing_pr_reports(wells: List[str]) -> List[str]:
    today = datetime.date.today()
    missing = []
    for well in wells:
        last_report = datetime.datetime.strptime(SIMULATED_WELL_DATA[well]['last_reported'], "%Y-%m-%d").date()
        if (today - last_report).days > 30:
            missing.append(well)
    return missing

def check_production_drop(well: str, last_month_volume: float) -> bool:
    return SIMULATED_WELL_DATA[well]['volume'] < 0.7 * last_month_volume

# ---- Streamlit UI ----
st.set_page_config(page_title="FieldMaven.ai – Agent Dashboard", layout="wide")
st.title("🛢️ FieldMaven.ai – Oil & Gas AI Agent")

st.sidebar.header("Upload & Controls")

# JIB Upload Section
uploaded_jib = st.sidebar.file_uploader("Upload JIB CSV", type=["csv"])
if uploaded_jib:
    jib_df = parse_jib_file(uploaded_jib)
    st.subheader("📄 JIB Report Summary")
    st.dataframe(jib_df)

# Missing PR Reports
st.subheader("⚠️ Missing PR Filings")
selected_wells = st.multiselect("Select wells to check:", list(SIMULATED_WELL_DATA.keys()))
if st.button("Check PR Filings") and selected_wells:
    missing = get_missing_pr_reports(selected_wells)
    if missing:
        st.error(f"Missing PR reports for: {', '.join(missing)}")
    else:
        st.success("All selected wells are up to date.")

# Production Drop Detection
st.subheader("📉 Production Drop Detection")
well_id = st.selectbox("Select well to analyze:", list(SIMULATED_WELL_DATA.keys()))
last_month_vol = st.number_input("Last month's volume (bbl):", min_value=0.0, step=100.0)
if st.button("Check for Drop"):
    if check_production_drop(well_id, last_month_vol):
        st.warning(f"Production drop detected on {well_id}!")
    else:
        st.success(f"Production for {well_id} is stable.")

# Agent Interaction (GPT-4 Simulation)
st.subheader("🤖 Ask FieldMaven")
user_query = st.text_input("Enter your question:")

if st.button("Ask") and user_query:
    prompt = f"You are FieldMaven, an expert oil & gas assistant. A user asked: '{user_query}'. Reply concisely."
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    st.info(response['choices'][0]['message']['content'])
