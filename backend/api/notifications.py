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
    """Endpoint for officers to send manual notifications to all devices."""
    try:
        print("Attempting to fetch tokens from the database...")
        with engine.connect() as connection:
            tokens_result = connection.execute(text("SELECT token FROM fcm_tokens")).fetchall()
            tokens = [row[0] for row in tokens_result]
        
        if not tokens:
            print("No tokens found.")
            raise HTTPException(status_code=404, detail="No registered devices found.")

        print(f"Tokens found: {tokens}. Attempting to send notification...")
        response = notification_service.send_multicast_notification(
            tokens=tokens,
            title="❗ IMPORTANT NOTICE FROM OFFICER ❗",
            body=payload.message
        )
        
        if response and response.success_count > 0:
            print("Notification sent successfully.")
            return {"status": "sukses", "sent_to": response.success_count}
        else:
            print("Notification function did not return a success response.")
            # Ini mungkin tidak akan ter-raise jika error ada di dalam service
            raise HTTPException(status_code=500, detail="Failed to send notification from the service.")

    except Exception as e:
        print("--- AN ERROR OCCURRED AT THE /notifications/manual ENDPOINT ---")
        traceback.print_exc() 
        print("-----------------------------------------------------")
        
        # Send a generic 500 response, but we already have the logs
        raise HTTPException(status_code=500, detail=str(e))