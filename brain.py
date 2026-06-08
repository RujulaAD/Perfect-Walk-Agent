import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from PIL import Image

# 1. Load the Gemini API Key from vault
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize the Gemini Client
client = genai.Client(api_key=GEMINI_API_KEY)

# 2. Define "God-Mode" Scorecard using Pydantic
class SensoryComfort(BaseModel):
    sensory_peaceful: int = Field(description="5 = quiet residential, 1 = loud construction/heavy traffic")
    shade_coverage: int = Field(description="5 = dense tree canopy/sky-scraper shadows, 1 = open concrete/intense sun")
    nature_immersion: int = Field(description="5 = lush greenery/gardens, 1 = total concrete jungle")

class SafetySecurity(BaseModel):
    nighttime_lighting: int = Field(description="5 = well-lit with streetlamps and glowing storefronts, 1 = pitch black")
    eyes_on_street: int = Field(description="5 = active cafes and pedestrians, 1 = abandoned buildings/empty lots")
    physical_infrastructure: int = Field(description="5 = clear, wide sidewalks, 1 = missing sidewalks/scaffolding blocks")

class Mobility(BaseModel):
    elevation_accessibility: int = Field(description="5 = perfectly flat, 1 = steep hills or public stairs")
    micro_mobility_safety: int = Field(description="5 = physically protected bike lanes, 1 = sharing with trucks")
    stroller_friendly: int = Field(description="5 = smooth pavement with curb cuts, 1 = cracked pavement/cobblestones")

class AestheticsCulture(BaseModel):
    historic_aesthetic: int = Field(description="5 = beautiful architecture, 1 = sterile/parking garages")
    street_art_presence: int = Field(description="5 = beautiful murals/sculptures, 1 = blank walls/vandalism")
    tourist_density: int = Field(description="5 = quiet local spot, 1 = heavy tourist trap")

class StreetAnalysis(BaseModel):
    sensory_and_comfort: SensoryComfort
    safety_and_security: SafetySecurity
    mobility: Mobility
    aesthetics_and_culture: AestheticsCulture
    brief_summary: str = Field(description="A 2-sentence summary of the street's vibe.")
# --- THE BUG FIX: Expanded Schema Resolver ---
def get_resolved_schema(cls):
    """Expands nested Pydantic schemas and strips 'title' keys to satisfy Google GenAI."""
    schema = cls.model_json_schema()
    
    # 1. Extract and eliminate definitions if they exist
    defs = schema.pop("$defs", None)
    
    def _clean_and_resolve(node):
        if isinstance(node, dict):
            # Remove the forbidden title key if present
            node.pop("title", None)
            
            # Resolve references if present
            if "$ref" in node and defs:
                ref_key = node.pop("$ref").split("/")[-1]
                node.update(defs[ref_key])
                # Immediately clean the newly injected keys from the definition
                node.pop("title", None)
            
            # Recursively clean children
            for val in node.values():
                _clean_and_resolve(val)
                
        elif isinstance(node, list):
            for item in node:
                _clean_and_resolve(item)
                
    _clean_and_resolve(schema)
    return schema
# ---------------------------------------------
    
    # Recursively hunt down and replace every shortcut with the real data
    def _resolve(node):
        if isinstance(node, dict):
            if "$ref" in node:
                ref_key = node.pop("$ref").split("/")[-1]
                node.update(defs[ref_key])
            for val in node.values():
                _resolve(val)
        elif isinstance(node, list):
            for item in node:
                _resolve(item)
                
    _resolve(schema)
    return schema
# ------------------------------------

def analyze_street(image_path="street.jpg"):
    print("🧠 Booting up Gemini Vision AI...")
    print(f"👀 Analyzing '{image_path}'...")
    
    # 3. Open the image
    img = Image.open(image_path)
    prompt = "You are an expert urban planner and accessibility auditor. Analyze this street view image and rate it strictly according to the provided schema."

    # 4. Use our custom get_resolved_schema() instead of passing the raw class
    response = client.models.generate_content(
        model='gemini-2.5-flash-lite',
        contents=[img, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=get_resolved_schema(StreetAnalysis),
            temperature=0.1,
        ),
    )
    
    print("\nAnalysis Complete! Here is the structured data:\n")
    return response.text

if __name__ == "__main__":
    analyze_street()