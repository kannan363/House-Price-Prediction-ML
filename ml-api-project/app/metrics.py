# app/metrics.py
from prometheus_client import Counter

PREDICTIONS_COUNTER = Counter(
    "ml_predictions_total",
    "Total number of predictions processed by the ML API",
    ["version", "status"]
)