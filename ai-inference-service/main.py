# The web framework this service is built on
from fastapi import FastAPI
# Builds a table (DataFrame) shaped exactly like the model expects
import pandas as pd
# The machine learning library that loads and runs the trained model
import xgboost as xgb
# Let Python talk to the PostgreSQL database
import psycopg2
# Used to load the label_mapping.json file
import json
# Used to read environment variables (for the Secret/ConfigMap values)
import os

# Create the actual FastAPI application object, "app" is what uvicorn looks for when it starts this service (matches the Dockerfile's CMD line)
app = FastAPI(title="AQI Inference Service")

# Database connection credentials (matches your Postgres Dockerfile) reads from environment variables if set (e.g. by Kubernetes via the Secret), otherwise falls back to these defaults - keeps docker-compose working unchanged
DB_HOST = os.environ.get("DB_HOST", "database-service")
DB_NAME = os.environ.get("DB_NAME", "aqi_db")
DB_USER = os.environ.get("DB_USER", "aqi_user")
DB_PASS = os.environ.get("DB_PASS", "aqi_pass")

# Load the trained model once when the container starts, not on every single request - loading from disk is slow, so this way it only happens once
model = xgb.XGBClassifier()
model.load_model("aqi_model.json")

# Load the label mapping (e.g. 0 -> "Good", 3 -> "Hazardous")
with open("label_mapping.json", "r") as f:
    label_mapping = json.load(f)

# Must match the exact column order used during training
feature_columns = ["PM10", "SO2", "NO2", "CO", "O3",
                    "TEMP", "PRES", "DEWP", "RAIN", "WSPM"]

# A reusable function that opens a new connection to the database, using the credentials defined above
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

# A simple GET endpoint at "/" — lets anyone (or Kubernetes) quickly check if this service is alive and running
@app.get("/")
def health_check():
    return {"status": "AI Inference Service is running and ready to predict."}

# The main endpoint — receives sensor data via POST and returns a prediction
@app.post("/predict")
def predict_aqi(sensor_data: dict):
    # Pull the station name out of the incoming data, default to "Unknown" if it's somehow missing
    station = sensor_data.get("station", "Unknown")

    # Print what was received, shows up in the pod's logs, useful for debugging
    print("Received sensor data:")
    print(sensor_data)

    # Build a one-row table from the incoming data, in the same column order the model was trained on
    input_row = pd.DataFrame([[sensor_data.get(col) for col in feature_columns]],
                              columns=feature_columns)

    # Run the actual prediction — model.predict() returns an array, [0] grabs the single result since we only sent one row
    prediction_number = model.predict(input_row)[0]
    # Convert the model's numeric answer (e.g. 3) back into a real word (e.g. "Hazardous")
    predicted_risk = label_mapping[str(prediction_number)]

    # Save the prediction into the Postgres database
    try:
        # Open a connection and a cursor (used to run SQL commands)
        conn = get_db_connection()
        cursor = conn.cursor()
        # Insert this station's prediction into the predictions table
        cursor.execute(
            "INSERT INTO predictions (station, risk_level) VALUES (%s, %s)",
            (station, predicted_risk)
        )
        # Commit actually saves the change permanently
        conn.commit()
        # Close both the cursor and the connection to free up resources
        cursor.close()
        conn.close()
        print(f"Successfully saved prediction for {station} to database.")
    except Exception as e:
        # If the database save fails for any reason, don't crash the whole request - just log the error and still return the prediction
        print(f"Database error: {e}")

    # Send the result back to whoever called this endpoint (the gateway)
    return {"station": station, "predicted_risk": predicted_risk}