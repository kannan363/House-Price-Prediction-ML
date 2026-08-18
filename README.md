# House Price Prediction & ML Monitoring API

An engineering-focused Machine Learning service designed to deploy, serve, and monitor a regression model in production.

## Project Scope (Day 1)
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

## Request Flow Sketch

[Client Request]
       │
       ▼
1. Input Validation (Pydantic schema checks non-negative values & numeric bounds)
       │
       ▼
2. Preprocessing Pipeline (Impute missing data, scale numbers, one-hot encode categoricals)
       │
       ▼
3. Model Inference (Scikit-Learn / XGBoost regressor predicts price)
       │
       ▼
4. Response Formatting (Attach metadata, request ID, execution time)
       │
       ▼
[Client Receives JSON Response]

