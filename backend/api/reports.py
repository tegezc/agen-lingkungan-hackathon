# backend/api/reports.py
import os
import shutil
import uuid
import traceback
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from sqlalchemy import text
from google.cloud import storage
from db.session import engine
from core import config

router = APIRouter()

GCS_BUCKET_NAME = config.BUCKET_STORE
storage_client = storage.Client()

@router.post("/", status_code=201)
def create_report(
    notes: str = Form(""), 
    image: UploadFile = File(...)
):
    file_extension = os.path.splitext(image.filename)[1]
    if file_extension.lower() not in ['.png', '.jpg', '.jpeg', '.webp']:
        raise HTTPException(status_code=400, detail="File format not supported.")
    
    bucket = storage_client.bucket(GCS_BUCKET_NAME)

    file_extension = os.path.splitext(image.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"

    blob = bucket.blob(unique_filename)
    try:
        # 1. Upload the file directly to GCS
        blob.upload_from_file(image.file)
        print(f"Image successfully uploaded to GCS: {blob.public_url}")

        blob.make_public()
        # 2. Save its public URL to TiDB
        stmt = text("INSERT INTO reports (image_url, notes) VALUES (:image_url, :notes)")
        with engine.connect() as connection:
            result = connection.execute(stmt, {"image_url": blob.public_url, "notes": notes})
            connection.commit()
        return {"status": "sukses", "report_id": result.lastrowid, "file_url": blob.public_url}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal: {str(e)}")
    finally:
        image.file.close()