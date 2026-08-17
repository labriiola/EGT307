# EGT307 Air Quality Forecasting & Early-Warning System

## Project Overview and Objectives

This project addresses a real-world air quality monitoring problem using an IoT-based
microservices architecture. Air pollution changes rapidly and varies significantly by
location, but most public reporting relies on static hourly readings with no predictive
lead time. This system ingests hourly sensor data from 12 real government air-quality
monitoring stations, classifies the risk level using a trained machine learning model,
and displays live predictions on a dashboard for public health monitoring.

**Objectives:**
1. Develop a machine learning model that classifies air-quality risk level from
   multi-station sensor data.
2. Implement the system as an independent, containerised microservices architecture.
3. Containerise each microservice using Docker and push to a public registry.
4. Deploy the system on a Kubernetes (Minikube) cluster with scaling on the
   AI Inference Service.
5. Provide a live dashboard showing current readings and predicted risk per station.

## System Architecture

Five independent microservices:

| Service | Purpose | Technology |
|---|---|---|
| Ingestion Service | Replays real sensor readings from the dataset, sends to the gateway | Python, pandas, requests |
| API Gateway | Single entry point; routes requests to the AI Inference Service | FastAPI, httpx |
| AI Inference Service | Loads the trained model, predicts AQI risk level, saves to database | FastAPI, XGBoost, scikit-learn |
| Database Service | Stores readings and predictions | PostgreSQL |
| Dashboard Service | Displays live readings and predictions | Streamlit |

Flow: Ingestion -> Gateway -> Inference -> Database -> Dashboard (reads independently).

Scalability: AI Inference Service runs 2 replicas in Kubernetes, since it's the only
service performing real computation and carries the load once all 12 stations are
sending data concurrently. The Gateway decouples Ingestion from Inference, so replica
count can change without affecting any other service.

Modularity: Each service has a single responsibility and communicates only through
its API contract. Proven during development, switching Ingestion's transport from MQTT
to HTTP only required changes inside that one service.

Fault tolerance: Observed directly during testing, a temporary 503 error occurred
when the Gateway forwarded a request before Inference had finished starting up.
Ingestion's retry logic caught this and recovered automatically on the next cycle.
On Kubernetes, failed pods also restart automatically.

## Dataset

Source: Beijing Multi-Site Air Quality Dataset, UCI Machine Learning Repository
(archive.ics.uci.edu/dataset/501). Real hourly readings from 12 government-run
monitoring stations in Beijing, March 2013 to February 2017. CC BY 4.0 licensed.

Cleaning steps applied:
1. Checked for stray non-numeric values in numeric columns (pd.to_numeric with
   errors="coerce") - none found.
2. Filled missing values using forward-fill then backward-fill, applied per-column
   on the hourly time series.
3. Checked pollutant columns (PM2.5, PM10, SO2, NO2, CO, O3) for negative values,
   which are physically impossible for a concentration reading, and treated them as
   missing. Temperature and dew point were deliberately excluded from this check,
   since sub-zero readings are real and expected for Beijing winters.
4. Converted PM2.5 into 4 risk categories (Good / Moderate / Unhealthy / Hazardous)
   using standard AQI-style breakpoints - this became the model's prediction target.

## Model

XGBoost classifier trained on 10 features (PM10, SO2, NO2, CO, O3, TEMP, PRES, DEWP,
RAIN, WSPM). PM2.5 was deliberately excluded from the feature set, since the target
label was derived directly from it, including it would let the model look up the
answer instead of learning the relationship between other conditions and risk.
Wind direction (wd) was excluded to keep the feature set numeric and simple.

Test accuracy: 83.59%. Per-category performance: Good 0.91 f1, Hazardous 0.87,
Unhealthy 0.79, Moderate 0.74. The two middle categories score lower since they sit
next to each other on an ordinal scale, making boundary cases genuinely harder to
separate than the two extremes.

## Build, Run, and Deploy Instructions

### Local (Docker Compose)

docker-compose up --build

Dashboard available at http://localhost:8501

### Kubernetes (Minikube)

minikube start
minikube addons enable metrics-server
kubectl apply -f kubernetes/db-secret.yaml
kubectl apply -f kubernetes/db-config.yaml
kubectl apply -f kubernetes/database-deployment.yaml
kubectl apply -f kubernetes/ai-inference-deployment.yaml
kubectl apply -f kubernetes/ai-inference-hpa.yaml
kubectl apply -f kubernetes/api-gateway-deployment.yaml
kubectl apply -f kubernetes/dashboard-deployment.yaml
kubectl apply -f kubernetes/ingestion-deployment.yaml
kubectl get pods
minikube service dashboard-service

### Configuration Management

Database credentials (DB_USER, DB_PASS) are stored in a Kubernetes Secret
(db-secret.yaml), base64-encoded rather than hardcoded in source code or YAML.
Non-sensitive database configuration (DB_HOST, DB_NAME) is stored separately in a
ConfigMap (db-config.yaml). Both database-service and ai-inference-service read
these values at runtime via secretKeyRef/configMapKeyRef, with ai-inference-service
also falling back to sensible defaults via os.environ.get() so it still runs correctly
outside Kubernetes (e.g. under Docker Compose, which does not use Secrets/ConfigMaps).

### Autoscaling

ai-inference-service has a HorizontalPodAutoscaler (ai-inference-hpa.yaml) targeting
50% average CPU utilization, scaling between 2 and 4 replicas. This was chosen because
Inference is the only service performing real computation, the one whose load actually
depends on how many stations are sending data concurrently. Confirmed working via
kubectl get hpa, which shows live CPU usage tracked against the target (e.g. 2%/50%)
rather than a fixed, manually-picked replica count.

### Rolling Updates

Kubernetes Deployments use a rolling update strategy by default, pods are replaced one
at a time rather than all at once, so the service stays available throughout an update.
This was observed directly during development: kubectl rollout status confirmed each
change (Secret, ConfigMap, and HPA additions) completed with zero downtime, and
kubectl rollout history shows 6 tracked revisions for the AI Inference Service
deployment. If a bad update were pushed, kubectl rollout undo would revert to the
previous working revision.

### Persistent Storage

`database-service` uses a PersistentVolumeClaim (`db-pvc.yaml`, 1Gi) mounted at
PostgreSQL's data directory, so stored readings and predictions survive pod restarts
and rescheduling rather than being lost. Verified directly: after deleting the running
database pod, the replacement pod's logs showed "Skipping initialization" — confirming
it found and reused the existing data rather than starting from a blank database.

### Docker Hub Images

All images are public under yixinn/: egt307-ingestion-service,
egt307-api-gateway-service, egt307-ai-inference-service,
egt307-database-service, egt307-dashboard-service.

## Known Issues and Limitations

- Wind direction (wd) is excluded from the model's features to avoid the added
  complexity of one-hot encoding a non-ordinal categorical variable; a future
  iteration could include it for a potential accuracy improvement.
- Missing values are handled with forward/backward-fill rather than interpolation;
  simple and defensible for hourly data, but not the only valid method.
- The model classifies current risk from a single reading rather than forecasting
  future conditions ahead of time; true time-series forecasting was out of scope
  given the project timeline.
- Ingestion replays real historical data in random order to simulate a live feed for
  demo purposes, rather than representing true real-time sensor streaming.