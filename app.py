import streamlit as st
import json
import os
from router import get_route_waypoints
from sensor import fetch_street_view
from brain import analyze_street

st.set_page_config(page_title="The Perfect Walk", page_icon="🚶🏾‍♀️", layout="centered")

st.title("The Perfect Walk Agent")
st.write("Enter your origin and destination. Our Multi-stage AI pipeline will extract waypoints, download real street-level conditions, and score the entire path.")

# Create two input fields side-by-side
col_in1, col_in2 = st.columns(2)
with col_in1:
    origin = st.text_input("Origin:", value="Times Square, New York, NY")
with col_in2:
    destination = st.text_input("Destination:", value="Bryant Park, New York, NY")

if st.button("Analyze Entire Walking Route", type="primary"):
    if origin and destination:
        
        # 1. Fetch the route checkpoints
        with st.spinner("Mapping route via Google Directions API..."):
            waypoints = get_route_waypoints(origin, destination)
            
        if not waypoints:
            st.error("No walking route found between those locations.")
        else:
            st.success(f"Extracted {len(waypoints)} key checkpoints along the path!")
            
            route_scores = []
            
            # Create a clean loading progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # 2. Run the Evaluation Loop
            for idx, coord in enumerate(waypoints):
                status_text.markdown(f"**Processing Checkpoint {idx+1} of {len(waypoints)}** ({coord})...")
                
                img_path = f"checkpoint_{idx+1}.jpg"
                
                # Fetch street view image
                fetch_street_view(coord, img_path)
                
                # Analyze image with Gemini
                raw_json = analyze_street(img_path)
                parsed_json = json.loads(raw_json)
                
                # Keep track of the results
                route_scores.append((img_path, parsed_json))
                
                # Update progress bar
                progress_bar.progress((idx + 1) / len(waypoints))
                
            status_text.success("Whole route evaluated successfully!")
            
            st.divider()
            
            # 3. Calculate Global Averages
            num_pts = len(route_scores)
            avg_peace = sum(item[1]["sensory_and_comfort"]["sensory_peaceful"] for item in route_scores) / num_pts
            avg_shade = sum(item[1]["sensory_and_comfort"]["shade_coverage"] for item in route_scores) / num_pts
            avg_light = sum(item[1]["safety_and_security"]["nighttime_lighting"] for item in route_scores) / num_pts
            avg_access = sum(item[1]["mobility"]["stroller_friendly"] for item in route_scores) / num_pts
            
            # 4. Display High-Level Metric Scorecards
            st.header("Route Scorecard Averages")
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("Peacefulness", f"{avg_peace:.1f} / 5")
            m_col2.metric("Shade Coverage", f"{avg_shade:.1f} / 5")
            m_col3.metric("Night Lighting", f"{avg_light:.1f} / 5")
            m_col4.metric("Accessibility", f"{avg_access:.1f} / 5")
            
            st.divider()
            
            # 5. Display the Visual Journey Timeline
            st.header("Visual Step-by-Step Journey")
            
            for idx, (img_file, data) in enumerate(route_scores):
                st.subheader(f"Stop {idx+1}: Checkpoint Evaluation")
                
                # Layout layout: split image and metrics cleanly
                layout_col1, layout_col2 = st.columns([1, 2])
                
                with layout_col1:
                    if os.path.exists(img_file):
                        st.image(img_file, use_container_width=True)
                
                with layout_col2:
                    st.markdown(f"**Agent Assessment:** {data.get('brief_summary')}")
                    
                    # Sub-metrics display
                    sm1, sm2, sm3, sm4 = st.columns(4)
                    sm1.caption(f"Quiet: {data['sensory_and_comfort']['sensory_peaceful']}/5")
                    sm2.caption(f"Shade: {data['sensory_and_comfort']['shade_coverage']}/5")
                    sm3.caption(f"Light: {data['safety_and_security']['nighttime_lighting']}/5")
                    sm4.caption(f"Mobility: {data['mobility']['stroller_friendly']}/5")
                st.write("")