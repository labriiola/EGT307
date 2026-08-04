from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI(title="API Gateway Service")

# This matches the container name and port in docker-compose.yml
AI_SERVICE_URL = "http://ai-inference-service:8000"

@app.get("/")
def gateway_root():
    return {"status": "API Gateway is running securely"}

@app.post("/predict")
async def route_to_inference(sensor_data: dict):
    """
    Receives sensor data from ingestion and forwards it
    to the AI Inference Microservice.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{AI_SERVICE_URL}/predict", json=sensor_data)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"AI Service is down or unreachable: {exc}")