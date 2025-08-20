import json
import vertexai
from vertexai.generative_models import GenerativeModel
from core import config

vertexai.init(project=config.GOOGLE_PROJECT_ID, location=config.GOOGLE_LOCATION)
#model = GenerativeModel(model_name="gemini-1.5-pro-001")
model = GenerativeModel(model_name="gemini-2.0-flash-001")

def get_llm_prediction(history_data, weather_data):
    """Meminta prediksi dari Google Gemini dan mem-parsing output JSON-nya."""
    print("Meminta prediksi dari Gemini...")
    history_str = ", ".join([f"{row.timestamp.strftime('%H:%M')}-{row.reading_value}cm" for row in history_data])
    
    prompt = f"""
    Anda adalah seorang ahli hidrologi. Analisis data berikut:
    1. Data Histori Ketinggian Air: {history_str}
    2. Ramalan Cuaca: {weather_data}
    Pertanyaan: Berdasarkan data ini, apakah ketinggian air diprediksi akan melewati ambang batas berbahaya 85 cm dalam 3 jam ke depan?
    Berikan output HANYA dalam format JSON: {{"is_danger_predicted": boolean, "confidence_score": float, "reasoning": "string", "predicted_peak_level_cm": integer}}
    """

    try:
        response = model.generate_content(prompt)
        clean_response = response.text.replace("```json", "").replace("```", "").strip()
        print(f"Respons dari LLM: {clean_response}")
        return json.loads(clean_response)  # Parsing string JSON menjadi dictionary
    except Exception as e:
        print(f"Gagal memanggil atau mem-parsing respons Vertex AI: {e}")
        return None