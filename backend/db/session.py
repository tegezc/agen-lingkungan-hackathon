import os
from sqlalchemy import create_engine
from core import config

DATABASE_URL = (
    f"mysql+pymysql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
)

# Logika Adaptif untuk Konfigurasi SSL
ssl_args = {}
# Memeriksa environment variable yang akan kita set
if config.ENVIRONMENT == 'production':
    # Di Cloud Run, cukup aktifkan verifikasi SSL tanpa file CA spesifik
    # Driver akan menggunakan root CAs dari sistem
    ssl_args['ssl_verify_cert'] = True
    print("Running in PRODUCTION mode: Using system SSL verification.")
else:
    # Di lokal (development), kita tetap butuh file ca.pem
    # Asumsi ca.pem berada di folder `backend/`
  
    ssl_args['ssl_ca'] = config.CA_PATH
    print("Running in DEVELOPMENT mode: Using local ca.pem file.")
  

try:
    engine = create_engine(DATABASE_URL,connect_args={"ssl": ssl_args})
    # Coba buat koneksi untuk memvalidasi
    connection = engine.connect()
    connection.close()
    print("Connection to TiDB Cloud established successfully.")
except Exception as e:
    print(f"Failed to create database connection: {e}")
    engine = None