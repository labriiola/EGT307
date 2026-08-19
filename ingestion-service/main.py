# loads the cleaned dataset and lets us pick rows from it
import pandas as pd
# makes outbound HTTP calls to the gateway
import requests
# used for the delay between each simulated sensor reading
import time

# The gateway's address, ingestion sends everything through here, it never talks to inference directly
AI_SERVICE_URL = "http://api-gateway-service:8080/predict"

# Load the real cleaned dataset once when the service starts, not on every loop, reading a file from disk repeatedly would be slow and pointless since the data doesn't change while the container runs
df = pd.read_csv("cleaned_data.csv")

# Sends one reading to the gateway and prints what happened
def send_sensor_data(sensor_data):
    try:
        response = requests.post(AI_SERVICE_URL, json=sensor_data)
        print("Sent data:")
        print(sensor_data)
        print("AI Response:")
        print(response.json())
    except Exception as e:
        # If the gateway is unreachable, don't crash the whole service, just log the error and the loop will try again on the next cycle
        print(f"Error sending data: {e}")

if __name__ == "__main__":
    print("Starting Data Ingestion Service...")

    # Runs forever, simulating a live, continuous sensor feed
    while True:
        # Pick one random real row each time, simulating a reading arriving from a random station right now
        row = df.sample(1).iloc[0]

        # Build the payload to send. float()/str() convert pandas' own number types into plain Python types, without this, sending the data as JSON would fail with a "not serializable" error
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
        # Wait 5 seconds before sending the next reading, simulates a real sensor reporting on a regular interval, not flooding the system with requests all at once
        time.sleep(5)