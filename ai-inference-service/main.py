from fastapi import FastAPI
import pandas as pd
import xgboost as xgb
import psycopg2
import json

app = FastAPI(title="AQI Inference Service")

# Database connection credentials (matches your Postgres Dockerfile)
DB_HOST = "database-service"
DB_NAME = "aqi_db"
DB_USER = "aqi_user"
DB_PASS = "aqi_pass"

# Load the trained model once when the container starts,
# not on every single request - loading from disk is slow,
# so this way it only happens once
model = xgb.XGBClassifier()
model.load_model("aqi_model.json")

# Load the label mapping (e.g. 0 -> "Good", 3 -> "Hazardous")
with open("label_mapping.json", "r") as f:
    label_mapping = json.load(f)

# Must match the exact column order used during training
feature_columns = ["PM10", "SO2", "NO2", "CO", "O3",
                    "TEMP", "PRES", "DEWP", "RAIN", "WSPM"]

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

@app.get("/")
def health_check():
    return {"status": "AI Inference Service is running and ready to predict."}

@app.post("/predict")
def predict_aqi(sensor_data: dict):
    station = sensor_data.get("station", "Unknown")

    print("Received sensor data:")
    print(sensor_data)

    # Build a one-row table from the incoming data, in the same
    # column order the model was trained on
    input_row = pd.DataFrame([[sensor_data.get(col) for col in feature_columns]],
                              columns=feature_columns)

    # Run the actual prediction
    prediction_number = model.predict(input_row)[0]
    predicted_risk = label_mapping[str(prediction_number)]

    # Save the prediction into the Postgres database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO predictions (station, risk_level) VALUES (%s, %s)",
            (station, predicted_risk)
        )
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Successfully saved prediction for {station} to database.")
    except Exception as e:
        print(f"Database error: {e}")

    return {"station": station, "predicted_risk": predicted_risk}