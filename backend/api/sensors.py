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

@router.post("/ingest")
def ingest_data(payload: SensorReadingPayload):
    """Endpoint to receive sensor data and save it to TiDB."""
    if not engine:
        raise HTTPException(status_code=500, detail="Database connection is not available.")

    try:
        with engine.connect() as connection:
            stmt = text("""
                INSERT INTO sensor_readings (sensor_id, reading_value, reading_unit, timestamp)
                VALUES (:sensor_id, :reading_value, :reading_unit, UTC_TIMESTAMP(3))
            """)
            
            connection.execute(stmt, payload.dict())
            connection.commit()

        return {"status": "sukses", "data_diterima": payload}
    except Exception as e:
        print("--- ERROR DATABASE ---")
        traceback.print_exc()
        print("------------------------------")
        
        # Tetap kirim respons 500 ke simulator, tapi kita sudah punya log error-nya
        raise HTTPException(status_code=500, detail=f"Failed to save data: {str(e)}")


@router.get("/{sensor_id}/history", response_model=list[ReadingHistoryItem])
def get_sensor_history(sensor_id: str):
    """Endpoint to fetch the last 100 data points from a sensor."""
    if not engine:
        raise HTTPException(status_code=500, detail="Database connection is not available.")

    try:
        with engine.connect() as connection:
            stmt = text("""
                SELECT reading_value, timestamp 
                FROM sensor_readings
                WHERE 
                    sensor_id = :id AND
                    timestamp >= (
                        SELECT MAX(timestamp) FROM sensor_readings WHERE sensor_id = :id
                    ) - INTERVAL 6 HOUR
                ORDER BY timestamp ASC
                LIMIT 100
            """)
            
            result = connection.execute(stmt, {"id": sensor_id})
            history_rows = result.fetchall()

            # Manually reformat the timestamp to standard ISO 8601 format (with 'Z')
            history = [
                {
                    "reading_value": row.reading_value,
                    "timestamp": row.timestamp.isoformat() + "Z"
                }
                for row in history_rows
            ]

            return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {e}")
