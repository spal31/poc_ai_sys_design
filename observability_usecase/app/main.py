from fastapi import FastAPI
from prometheus_client import generate_latest
from fastapi.responses import Response

import time
import random

from metrics import *
from tracing import *

from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

app = FastAPI()

FastAPIInstrumentor.instrument_app(app)

@app.get("/metrics")
def metrics():
    update_memory()
    return Response(generate_latest(),
                    media_type="text/plain")

@app.get("/payment")
def payment():

    start = time.time()

    # simulate work
    time.sleep(random.uniform(0.1,0.5))

    if random.randint(1,2)==2:
        network_errors.inc()
        http_requests.labels("GET","/payment","500").inc()
        return {"status":"error"}

    latency=time.time()-start

    http_latency.labels("/payment").observe(latency)

    http_requests.labels("GET","/payment","200").inc()

    return {"status":"success"}