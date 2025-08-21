import time
import traceback
import requests
from sqlalchemy import text
from db.session import engine
from core import config
from services import llm_service, notification_service

def get_weather_forecast(lat, lon, api_key):
    """Mengambil ramalan cuaca dari OpenWeatherMap."""
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        forecast = data['list'][0]['weather'][0]['description']
        return f"Ramalan cuaca 3 jam ke depan: {forecast}."
    except Exception as e:
        print(f"Gagal mengambil data cuaca: {e}. Menggunakan data tiruan.")
        return "Informasi cuaca tidak tersedia. Data tiruan: heavy rain."

def run_agent():
    """Fungsi utama agen prediktif dan multi-modal yang berjalan terus menerus."""
    print("Agen AI Multi-modal (Final) dimulai...")
    if not engine:
        print("Agen dihentikan: Koneksi DB tidak tersedia.")
        return

    while True:
        try:
            print(f"\n--- Siklus Agen Dimulai (Interval: {config.AGENT_CYCLE_SECONDS} detik) ---")
            
            prediction_result = None
            
            with engine.connect() as connection:
                # 1. AMBIL DATA UTAMA (SENSOR & CUACA)
                stmt_sensor_info = text("SELECT latitude, longitude FROM sensors WHERE id = :id")
                sensor_info = connection.execute(stmt_sensor_info, {"id": config.SENSOR_ID_TEST}).fetchone()
                
                stmt_history = text("""
                    SELECT reading_value, timestamp FROM sensor_readings 
                    WHERE sensor_id = :id AND timestamp > NOW() - INTERVAL 2 HOUR 
                    ORDER BY timestamp ASC
                """)
                history_data = connection.execute(stmt_history, {"id": config.SENSOR_ID_TEST}).fetchall()

                if not sensor_info or len(history_data) < 5:
                    print("Data histori tidak cukup. Melewati siklus.")
                    time.sleep(config.AGENT_CYCLE_SECONDS)
                    continue

                weather_data = get_weather_forecast(sensor_info.latitude, sensor_info.longitude, config.WEATHER_API_KEY)

                # 2. CEK & PROSES LAPORAN VISUAL (JIKA ADA)
                stmt_reports = text("SELECT id, image_url, notes FROM reports WHERE status = 'pending_analysis' ORDER BY created_at ASC LIMIT 1")
                new_report = connection.execute(stmt_reports).fetchone()

                if new_report:
                    print(f"Laporan baru ditemukan (ID: {new_report.id}). Menggunakan analisis multi-modal...")
                    # Panggil LLM dengan gambar
                    prediction_result = llm_service.analyze_report_with_vision(
                        history_data, weather_data, new_report.image_url, new_report.notes
                    )
                    
                    # Update status laporan agar tidak dianalisis lagi
                    stmt_update = text("UPDATE reports SET status = 'analyzed' WHERE id = :id")
                    connection.execute(stmt_update, {"id": new_report.id})
                    connection.commit()
                else:
                    # 3. JIKA TIDAK ADA LAPORAN, GUNAKAN ANALISIS TEKS-SAJA
                    print("Tidak ada laporan baru. Menggunakan analisis prediktif berbasis teks.")
                    prediction_result = llm_service.get_llm_prediction(history_data, weather_data)

            # 4. AMBIL TINDAKAN BERDASARKAN HASIL PREDIKSI
            if prediction_result and prediction_result.get("is_danger_predicted"):
                print("!!! PREDIKSI BAHAYA DITERIMA !!!")
                reason = prediction_result.get('reasoning', 'AI memprediksi potensi bahaya.')
                confidence = prediction_result.get('confidence_score', 0.0)
                
                with engine.connect() as connection:
                    tokens_result = connection.execute(text("SELECT token FROM fcm_tokens")).fetchall()
                    tokens = [row[0] for row in tokens_result]

                notification_service.send_multicast_notification(
                    tokens=tokens,
                    title="🚨 PREDIKSI PERINGATAN DINI 🚨",
                    body=reason
                )

                print("Menyimpan catatan peringatan ke database...")
                with engine.connect() as connection:
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
                
                # Setelah mengirim notifikasi penting, tunggu lebih lama.
                time.sleep(180) 
            else:
                print("Kondisi diprediksi aman.")
                time.sleep(config.AGENT_CYCLE_SECONDS)

        except Exception as e:
            print("!!! TERJADI ERROR PADA SIKLUS AGEN !!!")
            traceback.print_exc()
            time.sleep(config.AGENT_CYCLE_SECONDS * 2)

if __name__ == "__main__":
    run_agent()