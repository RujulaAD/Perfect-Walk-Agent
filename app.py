import streamlit as st
import json
from sensor import fetch_street_view
from brain import analyze_street

st.set_page_config(page_title="The Perfect Walk", page_icon="🚶🏾‍♀️", layout="centered")

st.title("🚶🏾‍♀️ The Perfect Walk Agent")
st.write("Enter any address in the world. Our Multimodal AI will analyze the street-level environment for safety, accessibility, and vibe.")

address = st.text_input("Enter an Address or Intersection (e.g., Times Square, NY):")

if st.button("Analyze Environment"):
    if address:
        with st.spinner("🛰️ Pinging Google Satellites for Street View..."):
            image_file = "temp_street.jpg"
            fetch_street_view(address, image_file)
            st.image(image_file, caption=f"Live view of: {address}")
            
        with st.spinner("🧠 Gemini Vision AI is analyzing the environment..."):
            json_data = analyze_street(image_file)
            parsed_data = json.loads(json_data)
            
            st.success("Analysis Complete!")
            
            # --- THE NEW UI DASHBOARD STARTS HERE ---
            
            # 1. The AI's Human Summary
            st.subheader("📝 Agent Summary")
            st.info(parsed_data.get("brief_summary", "No summary provided."))
            
            st.divider() # A clean visual line
            
            # 2. Creating a 2x2 Grid for the scores
            col1, col2 = st.columns(2)
            
            # Column 1: Sensory & Safety
            with col1:
                st.subheader("🌿 Sensory & Vibe")
                vibe = parsed_data["sensory_and_comfort"]
                st.metric("Peace & Quiet", f"{vibe['sensory_peaceful']} / 5")
                st.metric("Shade & Trees", f"{vibe['shade_coverage']} / 5")
                st.metric("Nature Immersion", f"{vibe['nature_immersion']} / 5")
                
                st.subheader("🛡️ Safety")
                safety = parsed_data["safety_and_security"]
                st.metric("Nighttime Lighting", f"{safety['nighttime_lighting']} / 5")
                st.metric("Pedestrian Activity", f"{safety['eyes_on_street']} / 5")

            # Column 2: Mobility & Culture
            with col2:
                st.subheader("♿ Mobility")
                mobility = parsed_data["mobility"]
                st.metric("Flat Terrain", f"{mobility['elevation_accessibility']} / 5")
                st.metric("Stroller Friendly", f"{mobility['stroller_friendly']} / 5")
                st.metric("Bike/Scooter Safety", f"{mobility['micro_mobility_safety']} / 5")
                
                st.subheader("🎨 Culture")
                culture = parsed_data["aesthetics_and_culture"]
                st.metric("Architecture & Beauty", f"{culture['historic_aesthetic']} / 5")
                st.metric("Local vs Tourist", f"{culture['tourist_density']} / 5")