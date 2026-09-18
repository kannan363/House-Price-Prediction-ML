# House Price Prediction & ML Monitoring API

An engineering-focused Machine Learning service designed to deploy, serve, and monitor a regression model in production.

> 🚀 **Live Production Deployment (Render)**
>
> **Public API Docs URL:** [https://house-price-prediction-ml-1-p2fj.onrender.com/docs](https://house-price-prediction-ml-1-p2fj.onrender.com/docs)

## Project Scope 
- **Dataset:** California Housing / Kaggle House Prices
- **Problem Type:** Regression (Continuous Price Prediction)
- **Primary Objective:** Build a production-ready REST API with strict request validation, structured logging, schema enforcement, and telemetry monitoring.

## API Contract (`POST /predict`)
Input: Accepts a JSON payload containing numerical and categorical features of a property—such as total square footage (gr_liv_area), number of bedrooms (bedrooms), building age (house_age), median area income (med_inc), and neighborhood location (neighborhood).

Output: Returns a JSON response containing the predicted continuous price (predicted_price_usd), currency unit, model metadata (model_version), execution latency (inference_time_ms), and a tracking request_id.

### Sample Input Payload
```json
{
  "med_inc": 8.32,
  "house_age": 41.0,
  "ave_rooms": 6.98,
  "ave_bedrooms": 2.02,
  "population": 322.0,
  "latitude": 37.88,
  "longitude": -122.23
}
## OUTPUT
{
  "request_id": "req-9a2b3c4d",
  "predicted_price_usd": 452600.0,
  "currency": "USD",
  "model_version": "v1.0.0",
  "inference_time_ms": 12.4,
  "timestamp": "2026-08-18T10:48:53Z"
}

---

## Run Commands & Quick Reference

### Docker Compose
- **Start Containers:** `docker compose up --build -d`
- **Swagger Documentation:** `http://127.0.0.1:8000/docs#/`
- **Prometheus Metrics:** `http://127.0.0.1:8000/metrics`

### Pytest Execution
- **Run Tests in Container:** `docker compose exec api pytest -v`

---
### Implemented Challenges (TASK 20 FINAL CHALLENGES)
--Challenge 1: In-Memory Response Caching:

Integrated cachetools.TTLCache (configured with maxsize=1000 and ttl=300 seconds).Generates a deterministic
MD5 hash key from incoming feature payloads. On identical requests within 5 minutes, the API serves the
cached response instantly without re-running model inference, saving CPU resources and reducing response
latency.

--Challenge 2: Pytest Automated via GitHub Actions CI/CD:

Configured a GitHub Actions workflow pipeline that triggers on every push and pull request.
Automates building the application container environment and executing pytest to guarantee that all API
routes, data validations, and model loading steps pass tests prior to deployment.
---

### Setup & Local Installation :
--Clone the repository:

"git clone <your-repository-url>"
"cd <your-repository-folder>"
--Launch via Docker Compose:

"docker compose up --build -d"
--Verify API endpoints:
Navigate to http://127.0.0.1:8000/docs#/ in your browser.

## What I Learned

- **End-to-End ML Pipeline & Model Training:
** Gained hands-on experience handling the complete machine learning lifecycle—from raw data cleaning,
handling missing values, and feature scaling, to training and evaluating regression models for optimal
production accuracy.

- **Production-Grade API Design:
** Building FastAPI routes with Pydantic validation ensures incoming data integrity before passing it to ML
pipelines.

- **Middleware & Traceability:
** Implementing custom HTTP middleware for unique `X-Request-ID` generation allows seamless request tracing
across structured logs and error handling.

- **Performance Optimization via Caching:
** Implementing response caching using deterministic hashing showed how easy it is to minimize redundant
compute loads on machine learning endpoints.

- **Containerization & CI/CD Discipline:
** Testing directly inside Docker containers (`docker compose exec api pytest -v`) paired with GitHub
Actions automation eliminates "works on my machine" issues and ensures predictable deployment pipelines.

- **Cloud Deployment & Production Hosting:** Learned how to deploy containerized web services to cloud
environments like Render, configure environment variables, manage web service builds, and expose public
HTTPS production endpoints.


## Architecture Diagram

```text
               +--------------------------------------------+
               |              Client Request                |
               +--------------------------------------------+
                                     │
                                     ▼
               +--------------------------------------------+
               |          Request Logging Middleware        |
               |          (Assigns X-Request-ID UUID)       |
               +--------------------------------------------+
                                     │
                                     ▼
               +--------------------------------------------+
               |        API Key Authentication Layer        |
               +--------------------------------------------+
                                     │
           +-------------------------+-------------------------+
           │                                                   │
           ▼                                                   ▼
+-----------------------+                           +-----------------------+
|  v1 Endpoint Router   |                           |  v2 Endpoint Router   |
| (/api/v1/predict)     |                           | (/api/v2/predict)     |
+-----------------------+                           +-----------------------+
           │                                                   │
           +-------------------------+-------------------------+
                                     │
                                     ▼
               +--------------------------------------------+
               |         In-Memory Response Cache           |
               |         (cachetools.TTLCache)              |
               +--------------------------------------------+
                 /                                        \
          [Cache Hit]                                 [Cache Miss]
               /                                            \
   Return Cached Result                      Run Joblib Scikit-Learn Pipeline
                                                             │
                                                   Store Result in Cache
                                                             │
                                                   Return Calculated Response