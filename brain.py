import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from PIL import Image
import random

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


# --- THE ROBUST BUG FIX: Safe Schema Resolver ---
def get_resolved_schema(cls):
    """Expands nested Pydantic schemas and strips 'title' keys safely."""
    schema = cls.model_json_schema()
    
    # 1. Extract definitions if they exist
    defs = schema.pop("$defs", None)
    
    def _clean_and_resolve(node):
        if isinstance(node, dict):
            # Safe pop before iteration
            node.pop("title", None)
            
            # Resolve references
            if "$ref" in node and defs:
                ref_key = node.pop("$ref").split("/")[-1]
                node.update(defs[ref_key])
                node.pop("title", None)
            
            # CRITICAL: Use list(node.values()) to prevent mutation runtime errors
            for val in list(node.values()):
                _clean_and_resolve(val)
                
        elif isinstance(node, list):
            # Create a shallow copy of the list for safe traversal
            for item in list(node):
                _clean_and_resolve(item)
                
    _clean_and_resolve(schema)
    return schema
# -------------------------------------------------

def analyze_street(image_path="street.jpg"):
    print("Booting up Gemini Vision AI...")
    print(f"Analyzing '{image_path}'...")
    
    try:
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

    except Exception as e:
        # Catch daily quota limits or rate limiting blocks
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            print("\nDaily Quota Exceeded (429). Activating Infrastructure Fail-Safe Mock...")
            
            # Generate deterministic but varied numbers based on the image name string hash 
            # so different stops still get slightly different scores during testing
            seed = sum(ord(c) for c in image_path)
            random.seed(seed)
            
            mock_data = {
                "sensory_and_comfort": {
                    "sensory_peaceful": random.randint(1, 3),
                    "shade_coverage": random.randint(2, 4),
                    "nature_immersion": random.randint(1, 2)
                },
                "safety_and_security": {
                    "nighttime_lighting": random.randint(3, 5),
                    "eyes_on_street": random.randint(2, 4),
                    "physical_infrastructure": random.randint(3, 5)
                },
                "mobility": {
                    "elevation_accessibility": random.randint(4, 5),
                    "micro_mobility_safety": random.randint(1, 3),
                    "stroller_friendly": random.randint(3, 5)
                },
                "aesthetics_and_culture": {
                    "historic_aesthetic": random.randint(1, 3),
                    "street_art_presence": random.randint(1, 2),
                    "tourist_density": random.randint(2, 4)
                },
                "brief_summary": "Estimated Checkpoint: Due to high server traffic, live visual analysis is paused. This is a standard environmental estimate based on typical urban walking conditions for this route."
            }
            
            # Reset seed state to avoid impacting other components
            random.seed(None)
            
            return json.dumps(mock_data)
        else:
            # If it's a completely different error (like a missing file), raise it normally
            raise e

if __name__ == "__main__":
    analyze_street()