# load_test.py
import asyncio
import time
import httpx

URL = "http://127.0.0.1:8000/api/v1/predict"
API_KEY = "my_super_secret_api_key_123"
CONCURRENT_REQUESTS = 100

HEADERS = {"X-API-Key": API_KEY}

VALID_HOUSING_PAYLOAD = {
    "MedInc": 8.3252,
    "HouseAge": 41.0,
    "AveRooms": 6.9841,
    "AveBedrms": 1.0238,
    "Population": 322.0,
    "AveOccup": 2.5555,
    "Latitude": 37.88,
    "Longitude": -122.23
}

async def send_request(client, req_id):
    start = time.perf_counter()
    try:
        # Don't override client timeouts here
        response = await client.post(URL, headers=HEADERS, json=VALID_HOUSING_PAYLOAD)
        latency = (time.perf_counter() - start) * 1000
        if response.status_code != 200:
            print(f"Req #{req_id} failed with status {response.status_code}: {response.text}")
        return response.status_code, latency
    except Exception as e:
        if req_id == 0:
            print(f"Req #0 Exception: {type(e).__name__} -> {e}")
        return "ERROR", 0

async def main():
    print(f"🚀 Launching {CONCURRENT_REQUESTS} concurrent requests to {URL}...")
    start_time = time.perf_counter()
    
    # Allow 100 connections with a 30-second timeout for queueing
    limits = httpx.Limits(max_keepalive_connections=100, max_connections=100)
    timeout = httpx.Timeout(30.0, connect=10.0)
    
    async with httpx.AsyncClient(limits=limits, timeout=timeout) as client:
        tasks = [send_request(client, i) for i in range(CONCURRENT_REQUESTS)]
        results = await asyncio.gather(*tasks)
        
    total_time = time.perf_counter() - start_time
    
    statuses = [r[0] for r in results]
    latencies = [r[1] for r in results if r[0] == 200]
    
    success_count = statuses.count(200)
    failed_count = len(statuses) - success_count
    
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    max_latency = max(latencies) if latencies else 0
    
    print("\n--- Load Test Results ---")
    print(f"Total Time Taken    : {total_time:.2f}s")
    print(f"Successful (200 OK) : {success_count}/{CONCURRENT_REQUESTS}")
    print(f"Failed Requests     : {failed_count}")
    print(f"Average Latency     : {avg_latency:.2f} ms")
    print(f"Max Latency         : {max_latency:.2f} ms")

if __name__ == "__main__":
    asyncio.run(main())