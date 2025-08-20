import os
from sqlalchemy import create_engine
from core import config

# Dapatkan path CA Cert. Asumsi disimpan di dalam folder backend/
ca_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ca.pem")

DATABASE_URL = (
    f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    f"?ssl_ca={config.CA_PATH}"
)

try:
    engine = create_engine(DATABASE_URL)
    # Coba buat koneksi untuk memvalidasi
    connection = engine.connect()
    connection.close()
    print("Koneksi ke TiDB Cloud berhasil dibuat.")
except Exception as e:
    print(f"Gagal membuat koneksi ke database: {e}")
    engine = None