import time
import os
import traceback
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import firebase_admin
from firebase_admin import credentials, messaging

load_dotenv()

# Inisialisasi Firebase
try:
    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
        cred = credentials.ApplicationDefault()
    else:
        cred_path = os.path.join(os.path.dirname(__file__), "firebase-service-account.json")
        cred = credentials.Certificate(cred_path)
    
    firebase_admin.initialize_app(cred, name='agentWorkerApp')
    print("Agent Worker: Firebase Admin SDK berhasil diinisialisasi.")
except Exception as e:
    # Mencegah error jika sudah diinisialisasi oleh proses lain (misal: main.py)
    if 'already exists' not in str(e):
        print(f"Agent Worker: Error inisialisasi Firebase: {e}")

# Inisialisasi Database
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
CA_PATH = os.getenv("CA_CERT_PATH")
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?ssl_ca={CA_PATH}"
)
try:
    engine = create_engine(DATABASE_URL)
    print("Agent Worker: Koneksi ke TiDB Cloud berhasil.")
except Exception as e:
    print(f"Agent Worker: Error koneksi ke database: {e}")
    engine = None
# -------------------------------------------------------------

def get_weather_forecast(lat, lon, api_key):
    """Mengambil ramalan cuaca dari OpenWeatherMap."""
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        # Kita ambil deskripsi cuaca untuk 3 jam ke depan
        forecast = data['list'][0]['weather'][0]['description']
        return f"Ramalan cuaca 3 jam ke depan: {forecast}."
    except Exception as e:
        print(f"Gagal mengambil data cuaca: {e}")
        return "Informasi cuaca tidak tersedia."

def get_llm_prediction(history_data, weather_data):
    """Meminta prediksi dari LLM. (FUNGSI INI PERLU ANDA SESUAIKAN)"""
    # **PENTING**: Ganti bagian ini dengan logika panggilan ke LLM Anda (Bedrock, OpenAI, dll)
    print("Meminta prediksi dari LLM...")

    # Format data histori agar mudah dibaca LLM
    history_str = ", ".join([f"{row.timestamp.strftime('%H:%M')}-{row.reading_value}cm" for row in history_data])
    
    prompt = f"""
    Anda adalah seorang ahli hidrologi. Analisis data berikut:

    1. Data Histori Ketinggian Air (Waktu-Nilai): {history_str}
    2. Kondisi Cuaca Saat Ini: {weather_data}

    Pertanyaan: Berdasarkan tren data histori dan kondisi cuaca, apakah ketinggian air diprediksi akan melewati ambang batas berbahaya 85 cm dalam 3 jam ke depan?
    Jawab hanya dengan satu kata: 'YA' atau 'TIDAK'.
    """
    
    print("--- PROMPT UNTUK LLM ---")
    print(prompt)
    print("-------------------------")

    # --- GANTI DENGAN KODE PANGGILAN LLM ANDA ---
    # Contoh tiruan untuk testing:
    # Jika ada kata 'rain' di cuaca, kita anggap 'YA'
    if 'rain' in weather_data.lower():
        llm_response = 'YA'
    else:
        llm_response = 'TIDAK'
    # -------------------------------------------
    
    print(f"Respons dari LLM: {llm_response}")
    return llm_response.strip().upper()

def run_agent():
    """Fungsi utama agen prediktif yang berjalan terus menerus."""
    print("Agen AI Prediktif dimulai...")
    
    TARGET_FCM_TOKEN = os.getenv("FCM_TOKEN_TEST") # Ambil dari .env
    SENSOR_ID = "clw-ktl-01"
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

    if not all([engine, TARGET_FCM_TOKEN, WEATHER_API_KEY]):
        print("Agen dihentikan: Konfigurasi DB, FCM Token, atau Weather API Key tidak lengkap.")
        return

    while True:
        try:
            print("\n--- Siklus Agen Prediktif Dimulai ---")
            
            # 1. FETCH: Ambil data histori 2 jam terakhir & info lokasi sensor
            with engine.connect() as connection:
                stmt_sensor = text("SELECT latitude, longitude FROM sensors WHERE id = :id")
                sensor_info = connection.execute(stmt_sensor, {"id": SENSOR_ID}).fetchone()

                stmt_history = text("""
                    SELECT reading_value, timestamp FROM sensor_readings 
                    WHERE sensor_id = :id AND timestamp > NOW() - INTERVAL 2 HOUR 
                    ORDER BY timestamp ASC
                """)
                history_data = connection.execute(stmt_history, {"id": SENSOR_ID}).fetchall()

            if not sensor_info or len(history_data) < 5: # Butuh minimal 5 data point
                print("Data histori tidak cukup untuk prediksi. Melewati siklus.")
                time.sleep(60) # Coba lagi dalam 1 menit
                continue

            # 2. GET WEATHER: Dapatkan ramalan cuaca
            weather_data = get_weather_forecast(sensor_info.latitude, sensor_info.longitude, WEATHER_API_KEY)
            print(f"Data Cuaca Diterima: {weather_data}")

            # 3. PREDICT WITH LLM: Minta prediksi dari LLM
            prediction = get_llm_prediction(history_data, weather_data)

            # 4. DECIDE & ACT: Ambil tindakan berdasarkan prediksi
            if prediction == 'YA':
                print("!!! PREDIKSI BAHAYA DITERIMA !!!")
                
                message_body = f"AI memprediksi ketinggian air di Katulampa akan melewati batas aman. {weather_data}"
                message = messaging.Message(
                    notification=messaging.Notification(title="🚨 PREDIKSI PERINGATAN DINI 🚨", body=message_body),
                    token=TARGET_FCM_TOKEN,
                )
                
                response = messaging.send(message,app=firebase_admin.get_app('agentWorkerApp'))
                print(f"Notifikasi Prediksi berhasil dikirim: {response}")
                time.sleep(180) # Tunggu 3 menit setelah mengirim notifikasi
            else:
                print("Kondisi diprediksi aman.")
                time.sleep(60) # Cek lagi dalam 1 menit

        except Exception as e:
            print("!!! TERJADI ERROR PADA SIKLUS AGEN !!!")
            traceback.print_exc()
            time.sleep(60)

if __name__ == "__main__":
    run_agent()