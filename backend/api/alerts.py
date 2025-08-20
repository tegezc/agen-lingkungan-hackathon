from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from db.session import engine

router = APIRouter()

@router.get("/alerts")
def get_all_alerts():
    """Mengambil 20 catatan peringatan terakhir dari database."""
    stmt = text("SELECT generated_at, message, alert_level FROM alerts ORDER BY generated_at DESC LIMIT 20")
    try:
        with engine.connect() as connection:
            result = connection.execute(stmt).fetchall()
            # Mengubah hasil menjadi list of dictionary agar mudah diproses di frontend
            alerts = [
                {"timestamp": row.generated_at, "reasoning": row.message, "level": row.alert_level}
                for row in result
            ]
            return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal mengambil data alert: {e}") 