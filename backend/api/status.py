from fastapi import APIRouter
from sqlalchemy import text
from db.session import engine

router = APIRouter()

@router.get("/latest")
def get_latest_status():
    """
    Mengambil peringatan terakhir yang aktif (dalam 3 jam terakhir) 
    untuk menentukan status sistem saat ini.
    """
    stmt = text("""
        SELECT message, alert_level, feedback 
        FROM alerts 
        WHERE generated_at > NOW() - INTERVAL 3 HOUR 
        ORDER BY generated_at DESC 
        LIMIT 1
    """)
    
    try:
        with engine.connect() as connection:
            latest_alert = connection.execute(stmt).fetchone()
        
        if latest_alert:

             # Jika peringatan terakhir sudah ditandai sebagai 'false_alarm' oleh petugas,
            # maka anggap kondisi saat ini aman.
            if latest_alert.feedback == 'false_alarm':
                return {
                    "status": "safe",
                    "level": 0,
                    "message": "The last warning has been corrected as a False Alarm by the operator."
                }
            
            # Jika ada peringatan dalam 3 jam terakhir, kirim itu
            return {
                "status": "danger",
                "level": latest_alert.alert_level,
                "message": latest_alert.message
            }
        else:
            # Jika tidak ada, berarti kondisi aman
            return {
                "status": "safe",
                "level": 0,
                "message": "All sensors are in normal condition."
            }
    except Exception as e:
        # Jika database error, kembalikan status tidak diketahui
        return {
            "status": "unknown",
            "level": -1,
            "message": f"Failed to retrieve status: {e}"
        }