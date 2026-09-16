# Task 19: Integration & Load Testing Report

## 1. Environment & Setup
- **Architecture:** Containerized FastAPI service with Prometheus monitoring (`docker-compose`).
- **Endpoints Tested:** `/api/v1/health`, `/metrics`, `/api/v1/predict`, `/api/v1/predict-batch`.

## 2. Integration Test Results
- Executed `tests/test_integration.py` against running container over HTTP (`httpx`).
- **Result:** All 4 endpoints returned `200 OK` with required headers (`X-API-Key`) and expected payload attributes.

- **command:**
-Run Integration Tests (Inside Container)
"docker compose exec api pytest tests/test_integration.py -v"

## 3. Load Test Results
- File: `load_test.py` 
- **Concurrency:** 100 simultaneous requests to `/api/v1/predict`
- **Results:**
  Total Time Taken    : 25.07s
  Successful (200 OK) : 100/100
  Failed Requests     : 0
  Average Latency     : 20418.59 ms
  Max Latency         : 21309.31 ms

 - **command:**
-Run Load Test (From Host Terminal)
"python load_test.py" 

