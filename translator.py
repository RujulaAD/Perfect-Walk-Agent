import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Load your Gemini API Key
load_dotenv()
GEMINI_KEY = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=GEMINI_KEY)

def extract_user_weights(user_prompt: str):
    """
    Translates a natural language user request into mathematical weights (0.0 to 1.0)
    for our 4 core route metrics.
    """
    print(f"Translating user request: '{user_prompt}'")
    
    # 2. The System Prompt (The Agent's Instructions)
    system_instruction = """
    You are an intelligent routing assistant. The user will provide a prompt describing their ideal walking route.
    Your job is to translate their request into mathematical weights across 4 specific metrics:
    1. peacefulness_weight (Requires quiet, low traffic, nature)
    2. shade_weight (Requires protection from sun/heat)
    3. lighting_weight (Requires safety, visibility, bright lights at night)
    4. accessibility_weight (Requires flat terrain, no stairs, mobility-friendly)

    Assign a float value between 0.0 and 1.0 for each metric. 
    Return ONLY a valid JSON object with these exact 4 keys.
    """
    
    try:
        # 3. Call the AI and force a JSON response
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json", 
            ),
        )
        return json.loads(response.text)
        
    except Exception as e:
        # 4. The Architectural Fail-Safe
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            print("\nDaily Quota Exceeded in Translator. Activating NLP Fail-Safe...")
            
            # Return a balanced, neutral set of weights to keep the math engine running
            return {
                "peacefulness_weight": 0.5,
                "shade_weight": 0.5,
                "lighting_weight": 0.5,
                "accessibility_weight": 0.5
            }
        else:
            # Re-raise the error if it's not a quota issue (e.g., missing API key)
            raise e