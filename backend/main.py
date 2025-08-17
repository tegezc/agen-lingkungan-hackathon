# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core import config
# Di sini nanti kita akan mengimpor semua endpoint API kita
# from backend.api import ingest, history, notifications # Contoh

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
from api_endpoints import router as api_router # Kita akan buat file ini
app.include_router(api_router)