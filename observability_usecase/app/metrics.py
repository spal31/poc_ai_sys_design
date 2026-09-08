from prometheus_client import Counter, Histogram, Gauge
import psutil

# Number of HTTP requests
http_requests = Counter(
    "http_requests_total",
    "Total HTTP Requests",
    ["method","endpoint","status"]
)

# Request latency
http_latency = Histogram(
    "http_request_duration_seconds",
    "HTTP latency",
    ["endpoint"]
)

# Memory usage
memory_usage = Gauge(
    "memory_usage_percent",
    "RAM usage percentage"
)

# Network errors
network_errors = Counter(
    "network_errors_total",
    "Network Errors"
)

def update_memory():
   # memory_usage.set(psutil.virtual_memory().percent)
   memory_usage.set(90.1)