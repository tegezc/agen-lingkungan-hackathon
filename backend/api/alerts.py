# backend/api/alerts.py
import traceback
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from db.session import engine

router = APIRouter()

class FeedbackPayload(BaseModel):
    feedback: str # 'valid' or 'false_alarm'

@router.get("/alerts")
def get_all_alerts():
    """Fetches the last 20 alert records from the database."""
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
        print("--- AN ERROR OCCURRED AT THE /alerts/alerts ENDPOINT ---")
        traceback.print_exc()
        print("-----------------------------------------------------")
        raise HTTPException(status_code=500, detail=f"Failed to fetch alert data: {e}")

@router.post("/{alert_id}/feedback")
def submit_feedback(alert_id: str, payload: FeedbackPayload):
    """"Receives feedback from an officer for an alert."""
    if payload.feedback not in ['valid', 'false_alarm']:
        raise HTTPException(status_code=400, detail="Feedback tidak valid.")

    stmt = text("UPDATE alerts SET feedback = :feedback WHERE id = :id")
    try:
        with engine.connect() as connection:
            # 1. Execute the command and store the result
            result = connection.execute(stmt, {"feedback": payload.feedback, "id": alert_id})

            # 2. CHECK IF ANY ROWS WERE AFFECTED
            if result.rowcount == 0:
               # If not, it means the ID was not found. Send a 404 error.
                raise HTTPException(status_code=404, detail=f"Alert with ID {alert_id} not found.")

            # 3. If successful, commit the changes
            connection.commit()

        return {"status": "sukses", "alert_id": alert_id, "feedback": payload.feedback}
    except HTTPException as http_exc:
         # Make sure the HTTPException we created ourselves is not caught by the block below
        raise http_exc
    except Exception as e:
        print("---AN ERROR OCCURRED AT THE /feedback ENDPOINT ---")
        traceback.print_exc()
        print("-----------------------------------------------------")
        raise HTTPException(status_code=500, detail=f"Failed to save feedback: {e}")