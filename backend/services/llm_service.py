import json
import warnings
import vertexai
from vertexai.generative_models import GenerativeModel
from core import config

# ------------------------------------------------------------
# Inisialisasi Vertex AI
# ------------------------------------------------------------
vertexai.init(project=config.GOOGLE_PROJECT_ID, location=config.GOOGLE_LOCATION)

# Buat model Gemini
model = GenerativeModel("gemini-2.5-pro")

# Optional: hilangkan deprecation warning sementara
warnings.filterwarnings("ignore", category=UserWarning, module="vertexai.generative_models")

# ------------------------------------------------------------
# Fungsi prediksi teks saja
# ------------------------------------------------------------
def get_llm_prediction(history_data, weather_data,examples=[]):
    """
    Meminta prediksi dari Gemini dan mem-parsing output JSON-nya.
    """
    print("Meminta prediksi dari Gemini (teks)...")

    history_str = ", ".join([f"{row.timestamp.strftime('%H:%M')}-{row.reading_value}cm"
                             for row in history_data])
    
    examples_str = "\n".join([f"- Kasus: {ex.message}, Umpan Balik Manusia: {ex.feedback}" for ex in examples])
    prompt = f"""
    Anda adalah seorang ahli hidrologi. Analisis data berikut:
    1. Data Histori Ketinggian Air: {history_str}
    2. Ramalan Cuaca: {weather_data}

    Data Tambahan - Contoh Kasus Terdahulu & Umpan Balik Manusia:
    {examples_str if examples else "Tidak ada contoh kasus."}

    Tugas: Berdasarkan SEMUA data di atas, termasuk belajar dari contoh kasus, buat prediksi akhir Anda.
    Pertanyaan: Berdasarkan data ini, apakah ketinggian air diprediksi akan melewati ambang batas berbahaya 85 cm dalam 3 jam ke depan?
    Berikan output HANYA dalam format JSON: {{"is_danger_predicted": boolean, "confidence_score": float, "reasoning": "string", "predicted_peak_level_cm": integer}}
    """

    print("\n--- PROMPT TEKS DIKIRIM  ---")
    print(prompt)
    print("---------------------------------")

    try:
        response = model.generate_content(prompt)
        clean_response = response.text.replace("```json", "").replace("```", "").strip()
        print(f"Respons dari LLM (teks): {clean_response}")
        return json.loads(clean_response)
    except Exception as e:
        print(f"Gagal memanggil Vertex AI (teks): {e}")
        return None

# ------------------------------------------------------------
# Fungsi prediksi multi-modal (teks + gambar)
# ------------------------------------------------------------
def analyze_report_with_vision(history_data, weather_data, image_path, notes,examples=[]):
    """
    Meminta prediksi multi-modal dari Gemini (Teks + Gambar)
    """
    print("Meminta prediksi multi-modal dari Gemini (Teks + Gambar)...")

    # 1. Baca data gambar dari file
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        from vertexai.generative_models import Part
        image_part = Part.from_data(data=image_bytes, mime_type="image/jpeg")
    except Exception as e:
        print(f"Gagal membaca file gambar: {e}")
        return None

    # 2. Siapkan prompt teks
    history_str = ", ".join([f"{row.timestamp.strftime('%H:%M')}-{row.reading_value}cm"
                             for row in history_data])
    
    examples_str = "\n".join([f"- Kasus: {ex.message}, Umpan Balik Manusia: {ex.feedback}" for ex in examples])
    prompt = f"""
    Anda adalah seorang ahli hidrologi dan analis risiko dari TiDB. Analisis semua data berikut untuk memprediksi potensi banjir secara akurat.

    Data yang tersedia:
    1.  **Data Histori Sensor Ketinggian Air:** {history_str}
    2.  **Ramalan Cuaca:** {weather_data}
    3.  **Laporan Visual dari Warga (Gambar Terlampir):** Catatan dari warga: "{notes}"

    Data Tambahan - Contoh Kasus Terdahulu & Umpan Balik Manusia:
    {examples_str if examples else "Tidak ada contoh kasus."}

    Tugas: Berdasarkan SEMUA data di atas, termasuk belajar dari contoh kasus, buat prediksi akhir Anda.


    Lakukan analisis berikut (chain of thought):
    1.  Analisis gambar terlampir. Apakah gambar tersebut menunjukkan adanya genangan air atau banjir? Seberapa parah kondisinya?
    2.  Analisis tren dari data histori sensor.
    3.  Korelasikan analisis visual, tren sensor, dan ramalan cuaca.
    4.  Buat prediksi akhir: apakah ketinggian air akan melewati ambang batas berbahaya 85 cm dalam 3 jam ke depan?
    
    Berikan output HANYA dalam format JSON: {{"is_danger_predicted": boolean, "confidence_score": float, "reasoning": "string", "image_analysis": "string"}}
    """

    # --- TAMBAHKAN PRINT DI SINI ---
    print("\n--- PROMPT MULTI-MODAL DIKIRIM ---")
    print(prompt)
    print("---------------------------------")

    try:
        # 3. Kirim prompt teks DAN gambar ke Gemini
        response = model.generate_content([image_part, prompt])
        clean_response = response.text.replace("```json", "").replace("```", "").strip()
        print(f"Respons Multi-modal dari LLM: {clean_response}")
        return json.loads(clean_response)
    except Exception as e:
        print(f"Gagal memanggil Vertex AI (multi-modal): {e}")
        return None
