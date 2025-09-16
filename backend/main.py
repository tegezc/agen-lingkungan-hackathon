# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core import config


app = FastAPI(title="environment Agent API - Refactored")

# Adding CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": f"Environment Agent API v2 is running."}

from api import devices, sensors, alerts, notifications, reports, status
app.include_router(devices.router, prefix="/devices", tags=["Devices"])
app.include_router(sensors.router, prefix="/sensors", tags=["Sensors"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])
app.include_router(status.router, prefix="/status", tags=["Status"])
