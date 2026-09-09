from fastapi import FastAPI
from routes import router
from telemetry import setup_telemetry
from logger_setup import configure_logging


configure_logging()

app = FastAPI(title="Payment Service")

setup_telemetry(app)

app.include_router(router)