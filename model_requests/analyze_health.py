import json
import os
from google import genai
from google.api_core import exceptions
from dotenv import load_dotenv
from database.schemas import HealthAnalysis
from fastapi.encoders import jsonable_encoder

load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = os.getenv('GEMINI_MODEL')

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in the environment.")

client = genai.Client(api_key=GEMINI_API_KEY)

def analyze_health_data(health_data: dict):
    safe_data = jsonable_encoder(health_data)

    prompt = f"""
        Analyze the following health data for the user. 
        User Age: {safe_data.get('user_age', 'Unknown')}
        User Weight: {safe_data.get('user_weight', 'Unknown')}
        User Height: {safe_data.get('user_height', 'Unknown')}
        User Gender: {safe_data.get('user_gender', "Unknown")}
        Data: {json.dumps(safe_data.get('user_health_data', []))}
        
        Provide a strict JSON response analyzing intensity and recommendations.
        """
    
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": HealthAnalysis,
            }
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response.")
            
        return json.loads(response.text)
    except exceptions.ResourceExhausted as e:
        print(f"QUOTA ERROR: {e}")
        return {"error": "API_QUOTA_EXHAUSTED", "details": "Check billing or wait 60s."}
    except exceptions.GoogleAPICallError as e:
        print(f"API Error: {e}")
        return {"error": "The AI service is currently unavailable."}
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return {"error": "An internal error occurred during analysis."}