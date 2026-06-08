import os
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
# This forces the AI to output exactly these keys and nothing else.
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

# Wrap all the categories into one master schema and ask for a quick summary
class StreetAnalysis(BaseModel):
    sensory_and_comfort: SensoryComfort
    safety_and_security: SafetySecurity
    mobility: Mobility
    aesthetics_and_culture: AestheticsCulture
    brief_summary: str = Field(description="A 2-sentence summary of the street's vibe.")

def analyze_street(image_path="street.jpg"):
    print("Booting up Gemini Vision AI...")
    print(f"Analyzing '{image_path}'...")
    
    # 3. Open the image downloaded in Phase 1
    img = Image.open(image_path)
    
    # The instruction given to the AI
    prompt = "You are an expert urban planner and accessibility auditor. Analyze this street view image and rate it strictly according to the provided schema."

    # 4. Send the image and the schema to Gemini 2.5 Flash
    response = client.models.generate_content(
        model='gemini-1.5-flash-8b',
        contents=[img, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=StreetAnalysis,
            temperature=0.1, # Low temperature keeps the AI highly analytical and strict
        ),
    )
    
    print("\n✅ Analysis Complete! Here is the structured data:\n")
    return response.text

if __name__ == "__main__":
    analyze_street()