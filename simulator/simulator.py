import requests
import time
import json
import random

# URL tempat backend API kita akan berjalan (untuk testing lokal)
BACKEND_URL = "http://127.0.0.1:8000/ingest"

# ID sensor hardcoded untuk simulasi
SENSOR_ID = "clw-ktl-01" 

def run_simulator():
    """Mengirim data sensor palsu ke backend setiap 5 detik."""
    print(f"Simulator untuk sensor '{SENSOR_ID}' dimulai...")
    print(f"Mengirim data ke: {BACKEND_URL}")

    while True:
        try:
            # Membuat data ketinggian air palsu yang sedikit bervariasi
            water_level = round(random.uniform(50.0, 75.0), 2)
            
            payload = {
                "sensor_id": SENSOR_ID,
                "reading_value": water_level,
                "reading_unit": "cm"
            }

            # Mengirim data sebagai JSON ke backend
            response = requests.post(BACKEND_URL, json=payload)
            response.raise_for_status()  # Ini akan error jika status code bukan 2xx

            print(f"Data terkirim: {payload}, Status: {response.status_code}, Respons: {response.json()}")

        except requests.exceptions.RequestException as e:
            print(f"Error: Tidak bisa terhubung ke backend. ({e})")

        # Tunggu 10 detik sebelum mengirim data berikutnya
        time.sleep(10)

if __name__ == "__main__":
    run_simulator()