import pandas as pd
import requests
import time

AI_SERVICE_URL = "http://api-gateway-service:8080/predict"

# Load the real cleaned dataset once when the service starts
df = pd.read_csv("cleaned_data.csv")

def send_sensor_data(sensor_data):
    try:
        response = requests.post(AI_SERVICE_URL, json=sensor_data)
        print("Sent data:")
        print(sensor_data)
        print("AI Response:")
        print(response.json())
    except Exception as e:
        print(f"Error sending data: {e}")

if __name__ == "__main__":
    print("Starting Data Ingestion Service...")

    while True:
        # Pick one random real row each time, simulating a reading
        # arriving from a random station right now
        row = df.sample(1).iloc[0]

        sensor_data = {
            "station": str(row["station"]),
            "PM2.5": float(row["PM2.5"]),
            "PM10": float(row["PM10"]),
            "SO2": float(row["SO2"]),
            "NO2": float(row["NO2"]),
            "CO": float(row["CO"]),
            "O3": float(row["O3"]),
            "TEMP": float(row["TEMP"]),
            "PRES": float(row["PRES"]),
            "DEWP": float(row["DEWP"]),
            "RAIN": float(row["RAIN"]),
            "WSPM": float(row["WSPM"])
        }

        send_sensor_data(sensor_data)
        time.sleep(5)