# backend/api_endpoints.py
import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from datetime import datetime
from db.session import engine # Import engine dari lokasi baru
from services import notification_service # Import service notifikasi

router = APIRouter()

# --- Model Data ---
class SensorReadingPayload(BaseModel):
    sensor_id: str
    reading_value: float
    reading_unit: str

class ReadingHistoryItem(BaseModel):
    reading_value: float
    timestamp: datetime

class NotificationTestPayload(BaseModel):
    token: str

# --- Endpoints ---
@router.post("/ingest")
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


@router.get("/{sensor_id}/history", response_model=list[ReadingHistoryItem])
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
