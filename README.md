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

**Flow:** Ingestion → Gateway → Inference → Database → Dashboard (reads independently).

**Scalability:** AI Inference Service runs 2 replicas in Kubernetes, since it's the only
service performing real computation and carries the load once all 12 stations are
sending data concurrently. The Gateway decouples Ingestion from Inference, so replica
count can change without affecting any other service.

**Modularity:** Each service has a single responsibility and communicates only through
its API contract. Proven during development — switching Ingestion's transport from MQTT
to HTTP only required changes inside that one service.

**Fault tolerance:** Observed directly during testing — a temporary 503 error occurred
when the Gateway forwarded a request before Inference had finished starting up.
Ingestion's retry logic caught this and recovered automatically on the next cycle.
On Kubernetes, failed pods also restart automatically.

## Dataset

**Source:** Beijing Multi-Site Air Quality Dataset, UCI Machine Learning Repository
(archive.ics.uci.edu/dataset/501). Real hourly readings from 12 government-run
monitoring stations in Beijing, March 2013 – February 2017. CC BY 4.0 licensed.

**Cleaning steps applied:**
1. Checked for stray non-numeric values in numeric columns (`pd.to_numeric` with
   `errors="coerce"`) — none found.
2. Filled missing values using forward-fill then backward-fill, applied per-column
   on the hourly time series.
3. Checked pollutant columns (PM2.5, PM10, SO2, NO2, CO, O3) for negative values,
   which are physically impossible for a concentration reading, and treated them as
   missing. Temperature and dew point were deliberately excluded from this check,
   since sub-zero readings are real and expected for Beijing winters.
4. Converted PM2.5 into 4 risk categories (Good / Moderate / Unhealthy / Hazardous)
   using standard AQI-style breakpoints — this became the model's prediction target.

## Model

XGBoost classifier trained on 10 features (PM10, SO2, NO2, CO, O3, TEMP, PRES, DEWP,
RAIN, WSPM). PM2.5 was deliberately excluded from the feature set, since the target
label was derived directly from it — including it would let the model look up the
answer instead of learning the relationship between other conditions and risk.
Wind direction (`wd`) was excluded to keep the feature set numeric and simple.

**Test accuracy: 83.59%.** Per-category performance: Good 0.91 f1, Hazardous 0.87,
Unhealthy 0.79, Moderate 0.74. The two middle categories score lower since they sit
next to each other on an ordinal scale, making boundary cases genuinely harder to
separate than the two extremes.

## Build, Run, and Deploy Instructions

### Local (Docker Compose)