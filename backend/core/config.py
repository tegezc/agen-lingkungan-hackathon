import os
from dotenv import load_dotenv

load_dotenv()

# --- Database Config
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
CA_PATH = os.getenv("CA_CERT_PATH")

# --- Firebase Config
# Menggunakan GOOGLE_APPLICATION_CREDENTIALS adalah best practice
# Pastikan env var ini di-set ke path file service account JSON Anda
# GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# --- Agent Config
# Ambil dari .env atau gunakan default
AGENT_CYCLE_SECONDS = int(os.getenv("AGENT_CYCLE_SECONDS", 60))
SENSOR_ID_TEST = os.getenv("SENSOR_ID_TEST", "clw-ktl-01")

# --- Weather API Config
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# --- Vertex AI Config
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "asia-southeast1")