# backend/api/reports.py
import os
import shutil
import uuid
import traceback
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from sqlalchemy import text
from db.session import engine

router = APIRouter()
UPLOADS_DIR = "uploads"

@router.post("/", status_code=201)
def create_report(
    notes: str = Form(""), 
    image: UploadFile = File(...)
):
    # ... (kode untuk membuat nama file unik tetap sama) ...
    file_extension = os.path.splitext(image.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    save_path = os.path.join(UPLOADS_DIR, unique_filename)

    try:
        # 1. Simpan file gambar ke server
        print("Mencoba menyimpan file gambar...")
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        print(f"File berhasil disimpan di: {save_path}")

        # 2. Simpan informasi laporan ke database TiDB
        if not engine:
            raise HTTPException(status_code=500, detail="Koneksi database tidak tersedia.")

        print("Mencoba menyimpan catatan ke database...")
        stmt = text("""
            INSERT INTO reports (image_url, notes, status) 
            VALUES (:image_url, :notes, 'pending_analysis')
        """)
        with engine.connect() as connection:
            result = connection.execute(
                stmt, 
                {"image_url": save_path, "notes": notes}
            )
            connection.commit()
        print("Catatan berhasil disimpan ke database.")
        return {"status": "sukses", "report_id": result.lastrowid, "file_path": save_path}

    except Exception as e:
        # --- PENYADAP KITA ADA DI SINI ---
        print("--- TERJADI ERROR DI ENDPOINT /reports ---")
        traceback.print_exc() # Ini akan mencetak error asli ke konsol
        print("------------------------------------------")

        # Jika file sudah sempat dibuat, hapus lagi agar tidak ada sampah
        if os.path.exists(save_path):
            os.remove(save_path)

        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan internal: {str(e)}")
    finally:
        image.file.close()