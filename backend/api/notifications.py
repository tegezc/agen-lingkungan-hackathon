# backend/api/notifications.py
import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from db.session import engine
from services import notification_service

router = APIRouter()

class ManualNotificationPayload(BaseModel):
    message: str

@router.post("/manual")
def send_manual_notification(payload: ManualNotificationPayload):
    """Endpoint untuk petugas mengirim notifikasi manual ke semua perangkat."""
    try:
        print("Mencoba mengambil token dari database...")
        with engine.connect() as connection:
            tokens_result = connection.execute(text("SELECT token FROM fcm_tokens")).fetchall()
            tokens = [row[0] for row in tokens_result]
        
        if not tokens:
            print("Tidak ada token ditemukan.")
            raise HTTPException(status_code=404, detail="Tidak ada perangkat terdaftar.")

        print(f"Token ditemukan: {tokens}. Mencoba mengirim notifikasi...")
        response = notification_service.send_multicast_notification(
            tokens=tokens,
            title="❗ PEMBERITAHUAN PENTING DARI PETUGAS ❗",
            body=payload.message
        )
        
        if response and response.success_count > 0:
            print("Notifikasi berhasil dikirim.")
            return {"status": "sukses", "sent_to": response.success_count}
        else:
            print("Fungsi notifikasi tidak mengembalikan respons sukses.")
            # Ini mungkin tidak akan ter-raise jika error ada di dalam service
            raise HTTPException(status_code=500, detail="Gagal mengirim notifikasi dari service.")

    except Exception as e:
        # --- PENYADAP KITA ADA DI SINI ---
        print("--- TERJADI ERROR DI ENDPOINT /notifications/manual ---")
        traceback.print_exc() # Ini akan mencetak error asli ke konsol
        print("-----------------------------------------------------")
        
        # Kirim respons 500 yang generic, tapi kita sudah punya log-nya
        raise HTTPException(status_code=500, detail=str(e))