# 👣 The Perfect Walk Agent

An autonomous AI routing engine that evaluates the physical environment of multiple walking paths to find your mathematically perfect route. 

Instead of just finding the shortest path, this agent translates your natural language preferences into mathematical weights, visually analyzes Google Street View imagery along multiple alternative routes, and scores them based on peacefulness, shade, lighting, and accessibility.

## Features
* **Natural Language Processing:** Uses Gemini 2.5 Flash-Lite to translate conversational prompts (e.g., *"I'm walking home late and want a well-lit route"*) into distinct routing weights.
* **Computer Vision Analysis:** Pulls live coordinates from the Google Maps API and evaluates Street View images using Google Gemini Vision AI to grade the physical safety and comfort of the street.
* **Graceful Degradation:** Built with resilient architecture. If the application hits daily LLM rate limits, it automatically intercepts the 429 error and safely falls back to standard environmental estimates without crashing the user interface.
* **Turn-by-Turn UI:** A seamless Streamlit dashboard that orchestrates background AI tasks, displays live progress, and renders human-readable navigation instructions alongside the AI's visual scorecard.

## System Architecture
1. **Translator (`translator.py`):** Converts natural language requests into a structured JSON weight matrix.
2. **Router (`router.py`):** Fetches multiple alternative route coordinates and turn-by-turn text instructions from the Google Directions API.
3. **Sensor (`sensor.py`):** Captures physical environment snapshots using the Google Street View Static API.
4. **Brain (`brain.py`):** Grades images against a strict Pydantic schema using Gemini Vision, outputting standardized scores for Lighting, Shade, Peacefulness, and Accessibility.
5. **Orchestrator (`app.py`):** Averages the environmental grades, multiplies them by the user's weights, crowns the winning route, and renders the interactive UI.

## Tech Stack
* **Language:** Python 3
* **Frontend:** Streamlit
* **Routing & Vision Intake:** Google Maps Directions API, Google Street View Static API
* **AI/ML Engine:** Google GenAI SDK (Gemini 2.5 Flash-Lite for Vision & Text)
* **Data Validation:** Pydantic

## Local Installation

### 1. Clone the repository
```bash
git clone [https://github.com/yourusername/perfect-walk-agent.git](https://github.com/yourusername/perfect-walk-agent.git)
cd perfect-walk-agent

### 2. Set up a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

### 3. Install dependencies
```bash
pip install -r requirements.txt

### 4. Set up Environment Variables
Create a .env file in the root directory and add your required API keys:

Code snippet
GOOGLE_MAPS_API_KEY="your_google_maps_key_here"
GEMINI_API_KEY="your_gemini_key_here"

### 5. Run the Application
```bash
streamlit run app.py

## Cloud Deployment
This application is containerized and ready for serverless deployment on Google Cloud Run. Ensure requirements.txt is locked to your specific dependency versions before triggering a cloud build pipeline.
