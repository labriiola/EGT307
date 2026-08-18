# FastAPI: the web framework. HTTPException: lets us return a proper error response instead of the request just crashing silently
from fastapi import FastAPI, HTTPException
# httpx: a library for making outbound HTTP requests to other services, this is what lets the gateway actually call the inference service
import httpx

# Create the FastAPI application object, "app" is what uvicorn looks for
app = FastAPI(title="API Gateway Service")

# The address of the AI Inference Service inside the Docker/Kubernetes network.
# This matches the container/Service name and port used in both docker-compose.yml and the Kubernetes deployment files
AI_SERVICE_URL = "http://ai-inference-service:8000"

# A simple GET endpoint at "/" — lets anyone quickly check if the gateway itself is alive and running
@app.get("/")
def gateway_root():
    return {"status": "API Gateway is running securely"}

# The main endpoint, receives sensor data from ingestion and forwards it on to the inference service. "async def" means this function can handle other requests while waiting for the inference service to respond, instead of blocking everything else
@app.post("/predict")
async def route_to_inference(sensor_data: dict):
    """
    Receives sensor data from ingestion and forwards it
    to the AI Inference Microservice.
    """
    # Open a temporary HTTP client to make the outbound request
    async with httpx.AsyncClient() as client:
        try:
            # Forward the exact sensor data we received onward to inference's own /predict endpoint, and wait for its response
            response = await client.post(f"{AI_SERVICE_URL}/predict", json=sensor_data)
            # If inference returned an error status, this line raises an exception instead of silently continuing
            response.raise_for_status()
            # Send inference's answer straight back to whoever called the gateway
            return response.json()
        except httpx.RequestError as exc:
            # If inference is unreachable entirely (not started yet, crashed, network issue), return a proper 503 error instead of crashing
            raise HTTPException(status_code=503, detail=f"AI Service is down or unreachable: {exc}")