# simulator/simulator.py
import requests
import time
import json
import random
import argparse # Library untuk menerima argumen terminal

BACKEND_URL = "https://floodcast-service-669250331086.asia-southeast2.run.app/sensors/ingest"
SENSOR_ID = "clw-ktl-01"

def run_simulation(scenario):
    """Runs the simulation based on the selected scenario."""
    print(f"Simulator starting with scenario: '{scenario}'")
    water_level = 60.0

    while True:
        if scenario == 'normal':
            water_level = round(random.uniform(50.0, 70.0), 2)
        elif scenario == 'rising':
            water_level += 3.5
            if water_level > 100: water_level = 100 # Limit it so it doesn't get too high
        elif scenario == 'ambiguous':
            # Rise slowly then stabilize at an ambiguous level (e.g., 80-84 cm)
            if water_level < 80:
                water_level += 2.0
            else:
                water_level = round(random.uniform(80.0, 84.0), 2)
        
        payload = {
            "sensor_id": SENSOR_ID,
            "reading_value": round(water_level, 2),
            "reading_unit": "cm"
        }
        try:
            response = requests.post(BACKEND_URL, json=payload)
            print(f"Data sent: {payload}, Status: {response.status_code}")
        except requests.exceptions.RequestException:
            print(f"Error: Failed to connect to the backend. Retrying...")
        
        time.sleep(5) # Kita percepat interval untuk demo

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runs the sensor simulator for FloodCast.")
    parser.add_argument(
        '--scenario', 
        type=str, 
        default='normal', 
        choices=['normal', 'rising', 'ambiguous'],
        help="Choose the data scenario to be sent."
    )
    args = parser.parse_args()
    run_simulation(args.scenario)