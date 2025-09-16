from fastapi import APIRouter
from sqlalchemy import text
from db.session import engine

router = APIRouter()

@router.get("/latest")
def get_latest_status():
    """
     Fetches the last active alert (within the last 3 hours) 
    to determine the current system status.
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

            # If the last alert has been marked as a 'false_alarm' by an officer,
            # then consider the current condition to be safe.
            if latest_alert.feedback == 'false_alarm':
                return {
                    "status": "safe",
                    "level": 0,
                    "message": "The last warning has been corrected as a False Alarm by the operator."
                }
            
            # If there is an alert within the last 3 hours, send it
            return {
                "status": "danger",
                "level": latest_alert.alert_level,
                "message": latest_alert.message
            }
        else:
             # If there are none, it means the condition is safe
            return {
                "status": "safe",
                "level": 0,
                "message": "All sensors are in normal condition."
            }
    except Exception as e:
         # If there's a database error, return an unknown status
        return {
            "status": "unknown",
            "level": -1,
            "message": f"Failed to retrieve status: {e}"
        }