# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core import config


app = FastAPI(title="Agen Lingkungan API - Refactored")

# Menambahkan Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": f"API Agen Lingkungan v2 berjalan."}

# Di sini kita akan "include" router dari folder api/
# app.include_router(ingest.router)
# app.include_router(history.router)
# app.include_router(notifications.router)

# Untuk saat ini, kita bisa pindahkan endpoint lama ke sini agar tetap berfungsi
from api import devices, sensors, alerts, notifications
app.include_router(devices.router, prefix="/devices", tags=["Devices"])
app.include_router(sensors.router, prefix="/sensors", tags=["Sensors"])
app.include_router(alerts.router, prefix="/alerts", tags=["Alerts"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
