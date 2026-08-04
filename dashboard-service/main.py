import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# --- CONFIGURATION ---
DB_USER = "aqi_user"
DB_PASS = "aqi_pass"
DB_HOST = "database-service"
DB_PORT = "5432"
DB_NAME = "aqi_db"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- UI SETUP ---
st.set_page_config(page_title="Air Quality Dashboard", layout="wide")
st.title("EGT307 Air Quality IoT Dashboard")
st.markdown("Live sensor data and AI predictions pulling directly from the PostgreSQL database.")

# --- DATA FETCHING ---
def load_data():
    try:
        engine = create_engine(DATABASE_URL)
        query = "SELECT * FROM predictions ORDER BY id DESC LIMIT 50"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Failed to connect to database. Error: {e}")
        return pd.DataFrame()

# --- DISPLAY ---
if st.button("Refresh Data"):
    st.rerun()

data = load_data()

if not data.empty:
    latest = data.iloc[0]
    st.subheader(f"Latest Reading: {latest.get('station', 'Unknown Station')}")
    st.info(f"Predicted Risk Level: **{latest.get('risk_level', 'N/A')}**")

    st.subheader("Recent Sensor Data & Predictions")
    st.dataframe(data, use_container_width=True)
else:
    st.warning("No data found. Make sure the database credentials and table name are correct!")