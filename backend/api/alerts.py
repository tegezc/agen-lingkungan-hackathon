# backend/api/alerts.py
import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from db.session import engine

router = APIRouter()

class FeedbackPayload(BaseModel):
    feedback: str # Akan berisi 'valid' atau 'false_alarm'

@router.get("/alerts")
def get_all_alerts():
    """Mengambil 20 catatan peringatan terakhir dari database."""
    stmt = text("SELECT id, generated_at, message, alert_level, confidence_score, feedback FROM alerts ORDER BY generated_at DESC LIMIT 20")
    try:
        with engine.connect() as connection:
            result = connection.execute(stmt).fetchall()
            alerts = [
                {
                    "id": str(row.id),
                    "timestamp": row.generated_at, 
                    "reasoning": row.message, 
                    "level": row.alert_level,
                    "confidence": row.confidence_score,
                    "feedback": row.feedback
                }
                for row in result
            ]
            return alerts
    except Exception as e:
         # --- PENYADAP KITA ADA DI SINI ---
        print("--- TERJADI ERROR DI ENDPOINT /alerts/ ---")
        traceback.print_exc() # Ini akan mencetak error asli ke konsol
        print("-----------------------------------------------------")
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data alert: {e}")

@router.post("/{alert_id}/feedback")
def submit_feedback(alert_id: str, payload: FeedbackPayload):
    """Menerima umpan balik dari petugas untuk sebuah peringatan."""
    if payload.feedback not in ['valid', 'false_alarm']:
        raise HTTPException(status_code=400, detail="Feedback tidak valid.")

    stmt = text("UPDATE alerts SET feedback = :feedback WHERE id = :id")
    try:
        with engine.connect() as connection:
            # 1. Jalankan perintah dan simpan hasilnya
            result = connection.execute(stmt, {"feedback": payload.feedback, "id": alert_id})

            # 2. PERIKSA APAKAH ADA BARIS YANG BERUBAH
            if result.rowcount == 0:
                # Jika tidak ada, berarti ID tidak ditemukan. Kirim error 404.
                raise HTTPException(status_code=404, detail=f"Alert dengan ID {alert_id} tidak ditemukan.")

            # 3. Jika berhasil, commit perubahan
            connection.commit()

        return {"status": "sukses", "alert_id": alert_id, "feedback": payload.feedback}
    except HTTPException as http_exc:
        # Pastikan HTTPException yang kita buat sendiri tidak tertangkap oleh blok di bawah
        raise http_exc
    except Exception as e:
           # --- PENYADAP KITA ADA DI SINI ---
        print("--- TERJADI ERROR DI ENDPOINT /alerts/ ---")
        traceback.print_exc() # Ini akan mencetak error asli ke konsol
        print("-----------------------------------------------------")
        raise HTTPException(status_code=500, detail=f"Gagal menyimpan feedback: {e}")