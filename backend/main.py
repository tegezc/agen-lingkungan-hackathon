import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, messaging

# Panggil fungsi ini di paling atas untuk memuat variabel dari file .env
load_dotenv()

# --- Inisialisasi Firebase Admin SDK ---
try:
    # Path ke file kunci rahasia Anda
    firebase_admin.initialize_app()
    print("Firebase Admin SDK berhasil diinisialisasi.")
except Exception as e:
    print(f"Error inisialisasi Firebase: {e}")

# --- Konfigurasi Koneksi Database (Sekarang Aman) ---
# Ambil variabel dari environment, bukan hardcode
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
CA_PATH = os.getenv("CA_CERT_PATH")

# Membuat Connection String
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?ssl_ca={CA_PATH}"
)

# Membuat engine database
try:
    engine = create_engine(DATABASE_URL)
    print("Koneksi ke TiDB Cloud berhasil.")
except Exception as e:
    print(f"Error koneksi ke database: {e}")
    engine = None

# --- Model Data (Validasi Input) ---
# Ini memastikan data yang masuk dari simulator memiliki format yang benar
class SensorReadingPayload(BaseModel):
    sensor_id: str
    reading_value: float
    reading_unit: str

class ReadingHistoryItem(BaseModel):
    reading_value: float
    timestamp: datetime

# Model untuk menerima FCM Token dari request
class NotificationTestPayload(BaseModel):
    token: str

# --- Aplikasi FastAPI ---
app = FastAPI(title="Agen Lingkungan API")

# Ini adalah konfigurasi untuk mengizinkan CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Izinkan permintaan dari semua origin (alamat)
    allow_credentials=True,
    allow_methods=["*"],  # Izinkan semua metode (GET, POST, dll)
    allow_headers=["*"],  # Izinkan semua header
)
# --------------------------------

@app.get("/")
def read_root():
    return {"status": "API Agen Lingkungan berjalan."}

@app.post("/test-notification")
def test_notification(payload: NotificationTestPayload):
    """Mengirim notifikasi tes ke token FCM tertentu."""
    message = messaging.Message(
        notification=messaging.Notification(
            title="🚨 Tes Peringatan Agen Lingkungan 🚨",
            body="Jika Anda menerima ini, koneksi Firebase berhasil!",
        ),
        token=payload.token,
    )

    try:
        response = messaging.send(message)
        print('Notifikasi berhasil dikirim:', response)
        return {"status": "sukses", "message_id": response}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest")
def ingest_data(payload: SensorReadingPayload):
    """Endpoint untuk menerima data sensor dan menyimpannya ke TiDB."""
    if not engine:
        raise HTTPException(status_code=500, detail="Koneksi database tidak tersedia.")

    try:
        with engine.connect() as connection:
            stmt = text("""
                INSERT INTO sensor_readings (sensor_id, reading_value, reading_unit, timestamp)
                VALUES (:sensor_id, :reading_value, :reading_unit, NOW(3))
            """)
            
            connection.execute(stmt, payload.dict())
            connection.commit()

        return {"status": "sukses", "data_diterima": payload}
    except Exception as e:
        # --- PERUBAHAN PENTING ADA DI SINI ---
        # Print error asli dan traceback-nya ke konsol untuk debugging
        print("--- TERJADI ERROR DATABASE ---")
        traceback.print_exc()
        print("------------------------------")
        
        # Tetap kirim respons 500 ke simulator, tapi kita sudah punya log error-nya
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan data: {str(e)}")

@app.get("/sensors/{sensor_id}/history", response_model=list[ReadingHistoryItem])
def get_sensor_history(sensor_id: str):
    """Endpoint untuk mengambil 100 data terakhir dari sebuah sensor."""
    if not engine:
        raise HTTPException(status_code=500, detail="Koneksi database tidak tersedia.")

    try:
        with engine.connect() as connection:
            stmt = text("""
                SELECT reading_value, timestamp FROM sensor_readings
                WHERE sensor_id = :id
                ORDER BY timestamp DESC
                LIMIT 100
            """)
            
            result = connection.execute(stmt, {"id": sensor_id})
            history = result.fetchall()
            
            # Mengurutkan kembali agar data tertua di depan untuk grafik
            return sorted(history, key=lambda x: x.timestamp)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data: {e}")
