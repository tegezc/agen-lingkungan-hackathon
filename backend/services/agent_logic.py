import time
import traceback
import requests
from sqlalchemy import text
from db.session import engine
from core import config
from services import llm_service, notification_service

def get_weather_forecast(lat, lon, api_key):
    """Fetches the weather forecast from OpenWeatherMap."""
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        forecast = data['list'][0]['weather'][0]['description']
        return f"3-hour weather forecast: {forecast}."
    except Exception as e:
        print(f"Failed to fetch weather data: {e}. Using mock data.")
        return "Weather information unavailable. Mock data: heavy rain."

def run_agent():
    """The main function for the predictive and multi-modal agent that runs continuously."""
    print("Multi-modal AI Agent (Final) starting...")
    if not engine:
        print("Agent stopped: DB connection not available.")
        return

    while True:
        try:
            print(f"\n--- Agent Cycle Started (Interval: {config.AGENT_CYCLE_SECONDS} seconds) ---")
            
            prediction_result = None
            
            with engine.connect() as connection:
                # 1. AMBIL DATA UTAMA (SENSOR & CUACA)
                stmt_sensor_info = text("SELECT latitude, longitude FROM sensors WHERE id = :id")
                sensor_info = connection.execute(stmt_sensor_info, {"id": config.SENSOR_ID_TEST}).fetchone()

                 # --- QUERY BARU: Ambil Contoh Kasus ---
                stmt_examples = text("SELECT message, feedback FROM alerts WHERE feedback IS NOT NULL ORDER BY generated_at DESC LIMIT 3")
                examples = connection.execute(stmt_examples).fetchall()
                
                stmt_history = text("""
                    SELECT reading_value, timestamp FROM sensor_readings 
                    WHERE sensor_id = :id AND timestamp > NOW() - INTERVAL 2 HOUR 
                    ORDER BY timestamp ASC
                """)
                history_data = connection.execute(stmt_history, {"id": config.SENSOR_ID_TEST}).fetchall()

                if not sensor_info or len(history_data) < 5:
                    print("Insufficient history data. Skipping cycle.")
                    time.sleep(config.AGENT_CYCLE_SECONDS)
                    continue

                weather_data = get_weather_forecast(sensor_info.latitude, sensor_info.longitude, config.WEATHER_API_KEY)

                # 2. CEK & PROSES LAPORAN VISUAL (JIKA ADA)
                stmt_reports = text("SELECT id, image_url, notes FROM reports WHERE status = 'pending_analysis' ORDER BY created_at ASC LIMIT 1")
                new_report = connection.execute(stmt_reports).fetchone()

                if new_report:
                    print(f"New report found (ID: {new_report.id}). Using multi-modal analysis...")
                    # Panggil LLM dengan gambar
                    prediction_result = llm_service.analyze_report_with_vision(
                        history_data, weather_data, new_report.image_url, new_report.notes, examples=examples
                    )
                    
                    # Update status laporan agar tidak dianalisis lagi
                    stmt_update = text("UPDATE reports SET status = 'analyzed' WHERE id = :id")
                    connection.execute(stmt_update, {"id": new_report.id})
                    connection.commit()
                else:
                    # 3. JIKA TIDAK ADA LAPORAN, GUNAKAN ANALISIS TEKS-SAJA
                    print("No new reports. Using text-based predictive analysis.")
                    prediction_result = llm_service.get_llm_prediction(history_data, weather_data, examples=examples)

            # 4. AMBIL TINDAKAN BERDASARKAN HASIL PREDIKSI
            if prediction_result and prediction_result.get("is_danger_predicted"):
                print("!!! DANGER PREDICTION RECEIVED !!!")
                reason = prediction_result.get('reasoning', 'AI predicts potential danger.')
                confidence = prediction_result.get('confidence_score', 0.0)
                
                with engine.connect() as connection:
                    tokens_result = connection.execute(text("SELECT token FROM fcm_tokens")).fetchall()
                    tokens = [row[0] for row in tokens_result]

                notification_service.send_multicast_notification(
                    tokens=tokens,
                    title="🚨 PREDICTIVE EARLY WARNING 🚨",
                    body=reason
                )

                print("Alert record saved successfully.")
                with engine.connect() as connection:
                    alert_level = 3 if confidence > 0.75 else 2
    
                    alert_stmt = text("""
                    INSERT INTO alerts (sensor_id, alert_level, message, generated_at, confidence_score)
                    VALUES (:id, :level, :msg, NOW(3), :confidence)
                    """)
                    connection.execute(
                        alert_stmt, 
                        {
                            "id": config.SENSOR_ID_TEST, 
                            "level": alert_level, 
                            "msg": reason,
                            "confidence": confidence # <-- Kirim nilai confidence sebagai parameter
                        }
                    )
                    connection.commit()
                print("Condition predicted to be safe.")
                
                # Setelah mengirim notifikasi penting, tunggu lebih lama.
                time.sleep(180) 
            else:
                print("Condition predicted to be safe.")
                time.sleep(config.AGENT_CYCLE_SECONDS)

        except Exception as e:
            print("!!! AN ERROR OCCURRED IN THE AGENT CYCLE !!!")
            traceback.print_exc()
            time.sleep(config.AGENT_CYCLE_SECONDS * 2)

if __name__ == "__main__":
    run_agent()