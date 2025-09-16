# api/devices.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from db.session import engine

router = APIRouter()

class RegisterTokenPayload(BaseModel):
    token: str

@router.post("/register", status_code=201)
def register_device(payload: RegisterTokenPayload):
    """Receives and stores an FCM token from a mobile device."""
    if not engine:
        raise HTTPException(status_code=500, detail="Database connection is not available.")

     # Using "INSERT ... ON DUPLICATE KEY UPDATE" to handle existing tokens
    # This is an efficient way to register or update a token's timestamp.
    stmt = text("""
        INSERT INTO fcm_tokens (token, created_at, updated_at) 
        VALUES (:token, NOW(3), NOW(3))
        ON DUPLICATE KEY UPDATE updated_at = NOW(3)
    """)
    
    try:
        with engine.connect() as connection:
            connection.execute(stmt, {"token": payload.token})
            connection.commit()
        return {"status": "sukses", "token": payload.token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save token: {e}")