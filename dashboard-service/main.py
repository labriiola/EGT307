# the framework this whole app is built with
import streamlit as st
# used to hold the query results in a table
import pandas as pd
# SQLAlchemy's way of connecting to a database an alternative to psycopg2.connect() used by the other services
from sqlalchemy import create_engine

# --- CONFIGURATION ---
# Database credentials, must match database-service's actual username, password, and database name exactly
DB_USER = "aqi_user"
DB_PASS = "aqi_pass"
DB_HOST = "database-service"
DB_PORT = "5432"
DB_NAME = "aqi_db"

# Builds one connection string combining all 5 values above into the format SQLAlchemy expects
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- UI SETUP ---
# Configures the browser tab title and makes the page use the full screen width instead of a narrow centered column
st.set_page_config(page_title="Air Quality Dashboard", layout="wide")
st.title("EGT307 Air Quality IoT Dashboard")
st.markdown("Live sensor data and AI predictions pulling directly from the PostgreSQL database.")

# --- DATA FETCHING ---
# Connects to the database and pulls the 50 most recent predictions
def load_data():
    try:
        engine = create_engine(DATABASE_URL)
        query = "SELECT * FROM predictions ORDER BY id DESC LIMIT 50"
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        # If the connection or query fails, show the error on the page instead of the app crashing, and return an empty table so the rest of the code below still runs safely
        st.error(f"Failed to connect to database. Error: {e}")
        return pd.DataFrame()

# --- DISPLAY ---
# A manual refresh button, st.rerun() re-executes this whole script from the top, which re-runs load_data() and pulls fresh results
if st.button("Refresh Data"):
    st.rerun()

# Actually fetch the data (runs every time the page loads or refreshes)
data = load_data()

# Only try to display something if data was actually returned
if not data.empty:
    # Grab the very first row, since the query sorted newest first, this is the single most recent prediction
    latest = data.iloc[0]
    st.subheader(f"Latest Reading: {latest.get('station', 'Unknown Station')}")
    st.info(f"Predicted Risk Level: **{latest.get('risk_level', 'N/A')}**")

    # Show the full table of all 50 recent rows below the highlight
    st.subheader("Recent Sensor Data & Predictions")
    st.dataframe(data, use_container_width=True)
else:
    # If the table came back empty (or the query failed), show a helpful message instead of a blank page
    st.warning("No data found. Make sure the database credentials and table name are correct!")