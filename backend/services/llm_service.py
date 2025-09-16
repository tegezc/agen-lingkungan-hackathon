import json
import warnings
import vertexai
import requests
from vertexai.generative_models import GenerativeModel
from core import config

# ------------------------------------------------------------
# initialitation Vertex AI
# ------------------------------------------------------------
vertexai.init(project=config.GOOGLE_PROJECT_ID, location=config.GOOGLE_LOCATION)

# Create the Gemini model
model = GenerativeModel("gemini-2.5-pro")

# Optional: temporarily suppress the deprecation warning
warnings.filterwarnings("ignore", category=UserWarning, module="vertexai.generative_models")

# ------------------------------------------------------------
# Text-only prediction function
# ------------------------------------------------------------
def get_llm_prediction(history_data, weather_data,examples=[]):
    """
    Requests a prediction from Gemini and parses its JSON output.
    """
    print("Requesting prediction from Gemini (text)...")

    history_str = ", ".join([f"{row.timestamp.strftime('%H:%M')}-{row.reading_value}cm"
                             for row in history_data])
    
    examples_str = "\n".join([f"- Case: {ex.message}, Human Feedback: {ex.feedback}" for ex in examples])
    prompt = f"""
    You are a senior hydrologist and risk analyst. Your task is to predict flood potential based on sensor and weather data.

    Available data:
    - Historical Water Level Data (Time-Value): {history_str}
    - Weather Forecast: {weather_data}
    - Previous Case Examples with Human Feedback: {examples_str if examples else "No prior examples."}

    Task: Based on all available text data and learning from past feedback, predict if the water level will cross the dangerous threshold of 85 cm in the next 3 hours.
    
    Provide the output ONLY in the following JSON format:
    {{"is_danger_predicted": boolean, "confidence_score": float, "reasoning": "string"}}
    """

    print("\n--- TEXT PROMPT SENT  ---")
    print(prompt)
    print("---------------------------------")

    try:
        response = model.generate_content(prompt)
        clean_response = response.text.replace("```json", "").replace("```", "").strip()
        print(f"Response from LLM (text): {clean_response}")
        return json.loads(clean_response)
    except Exception as e:
        print(f"Failed to call Vertex AI (text): {e}")
        return None

# ------------------------------------------------------------
# Multi-modal prediction function (text + image)
# ------------------------------------------------------------
def analyze_report_with_vision(history_data, weather_data, image_url, notes,examples=[]):
    """
    Requests a multi-modal prediction from Gemini (Text + Image).
    """
    print("Requesting multi-modal prediction from Gemini (Text + Image)...")

    try:
         # 1. Download the image data from the public GCS URL
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        image_bytes = response.content
        from vertexai.generative_models import Part
        image_part = Part.from_data(data=image_bytes, mime_type="image/jpeg")
    except Exception as e:
        print(f"Failed to download the image file from GCS: {e}")
        return None
    
     # 2. Prepare the text prompt
    history_str = ", ".join([f"{row.timestamp.strftime('%H:%M')}-{row.reading_value}cm"
                             for row in history_data])
    
    examples_str = "\n".join([f"- Case: {ex.message}, Human Feedback: {ex.feedback}" for ex in examples])
    prompt = f"""
    You are a senior hydrologist and risk analyst from TiDB. Your task is to predict flood potential.

    Available data:
    - Historical Data (Time-Value): {history_str}
    - Weather Forecast: {weather_data}
    - (Optional) Citizen Visual Report: Note from citizen: "{notes}"
    - (Optional) Previous Case Examples with Human Feedback: {examples_str if examples else "No prior examples."}

    Perform the following analysis (chain of thought):
    1. Analyze the trend from the historical sensor data.
    2. Correlate this trend with the weather forecast and any visual reports.
    3. Based on all available data and learning from past feedback, predict if the water level will cross the dangerous threshold of 85 cm.
    4. Provide a confidence score from 0.0 to 1.0.

    Provide the output ONLY in the following JSON format:
    {{"is_danger_predicted": boolean, "confidence_score": float, "reasoning": "string", "image_analysis": "string (if applicable)"}}
    """

    print("\n--- MULTI-MODAL PROMPT SENT ---")
    print(prompt)
    print("---------------------------------")

    try:
         # 3. Send the text prompt AND the image to Gemini
        response = model.generate_content([image_part, prompt])
        clean_response = response.text.replace("```json", "").replace("```", "").strip()
        print(f"Multi-modal Response from LLM: {clean_response}")
        return json.loads(clean_response)
    except Exception as e:
        print(f"Failed to call Vertex AI (multi-modal): {e}")
        return None
