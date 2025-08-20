import time
import traceback
import requests
from sqlalchemy import text
from db.session import engine
from core import config
from services import llm_service, notification_service

def get_weather_forecast(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        forecast = data['list'][0]['weather'][0]['description']
        return f"Ramalan cuaca 3 jam ke depan: {forecast}."
    except Exception as e:
        print(f"Gagal mengambil data cuaca: {e}. Menggunakan data tiruan.")
        return "Informasi cuaca tidak tersedia. Data tiruan: heavy rain."

def run_agent():
    print("Agen AI Prediktif (Refactored) dimulai...")
    if not engine:
        print("Agen dihentikan: Koneksi DB tidak tersedia.")
        return

    while True:
        try:
            print(f"\n--- Siklus Agen Dimulai (Interval: {config.AGENT_CYCLE_SECONDS} detik) ---")
            
            with engine.connect() as connection:
                stmt_sensor = text("SELECT latitude, longitude FROM sensors WHERE id = :id")
                sensor_info = connection.execute(stmt_sensor, {"id": config.SENSOR_ID_TEST}).fetchone()
                
                stmt_history = text("""
                    SELECT reading_value, timestamp FROM sensor_readings 
                    WHERE sensor_id = :id AND timestamp > NOW() - INTERVAL 2 HOUR 
                    ORDER BY timestamp ASC
                """)
                history_data = connection.execute(stmt_history, {"id": config.SENSOR_ID_TEST}).fetchall()

            if not sensor_info or len(history_data) < 5:
                print("Data histori tidak cukup untuk prediksi. Melewati siklus.")
                time.sleep(config.AGENT_CYCLE_SECONDS)
                continue

            weather_data = get_weather_forecast(sensor_info.latitude, sensor_info.longitude, config.WEATHER_API_KEY)
            prediction_result = llm_service.get_llm_prediction(history_data, weather_data)

            if prediction_result and prediction_result.get("is_danger_predicted"):
                print("!!! PREDIKSI BAHAYA DITERIMA !!!")
                reason = prediction_result.get('reasoning', 'Alasan tidak tersedia.')
                confidence = prediction_result.get('confidence_score', 0.0)
                
                # 1. Ambil semua token dari database
                with engine.connect() as connection:
                    tokens_result = connection.execute(text("SELECT token FROM fcm_tokens")).fetchall()
                    tokens = [row[0] for row in tokens_result]

                # 2. Panggil notification_service (yang sudah direfactor)
                notification_service.send_multicast_notification(
                    tokens=tokens,
                    title="🚨 PREDIKSI PERINGATAN DINI 🚨",
                    body=reason
                )

                # 3. Logika menyimpan alert ke DB (yang hilang sebelumnya)
                print("Menyimpan catatan peringatan ke database...")
                with engine.connect() as connection:
                    # Kita gunakan `confidence_score` untuk menentukan alert_level
                    alert_level = 3 if confidence > 0.75 else 2
                    
                    alert_stmt = text("""
                        INSERT INTO alerts (sensor_id, alert_level, message, generated_at)
                        VALUES (:id, :level, :msg, NOW(3))
                    """)
                    connection.execute(
                        alert_stmt, 
                        {"id": config.SENSOR_ID_TEST, "level": alert_level, "msg": reason}
                    )
                    connection.commit()
                print("Catatan peringatan berhasil disimpan.")

                time.sleep(180) 
            else:
                print("Kondisi diprediksi aman.")
            
            time.sleep(config.AGENT_CYCLE_SECONDS)

        except Exception as e:
            print("!!! TERJADI ERROR PADA SIKLUS AGEN !!!")
            traceback.print_exc()
            time.sleep(config.AGENT_CYCLE_SECONDS * 2)