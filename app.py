import streamlit as st
import json
import os
from router import get_multiple_routes
from sensor import fetch_street_view
from brain import analyze_street
from translator import extract_user_weights
import time

st.set_page_config(page_title="The Perfect Walk", page_icon="🚶🏾‍♀️", layout="centered")

st.title("The Perfect Walk Agent")
st.write("Enter your locations and describe your ideal walk. The AI will evaluate multiple paths in the background and select the mathematically perfect route for you.")

# 1. New Input UI: Added the Prompt Box
col_in1, col_in2 = st.columns(2)
with col_in1:
    origin = st.text_input("Origin:", value="Times Square, New York, NY")
with col_in2:
    destination = st.text_input("Destination:", value="Bryant Park, New York, NY")

user_prompt = st.text_area(
    "What kind of walk do you want?", 
    value="I'm walking home late. I want the safest, most well-lit route. I don't care about nature or peace."
)

if st.button("Find My Perfect Route", type="primary"):
    if origin and destination and user_prompt:
        
        # 2. Translate Prompt to Math Weights
        with st.spinner("Translating your request into routing weights..."):
            weights = extract_user_weights(user_prompt)
            
        st.success("User Preferences Understood!")
        w_col1, w_col2, w_col3, w_col4 = st.columns(4)
        w_col1.metric("Peacefulness Priority", f"{weights.get('peacefulness_weight', 0.0)}")
        w_col2.metric("Shade Priority", f"{weights.get('shade_weight', 0.0)}")
        w_col3.metric("Lighting Priority", f"{weights.get('lighting_weight', 0.0)}")
        w_col4.metric("Accessibility Priority", f"{weights.get('accessibility_weight', 0.0)}")
        
        # 3. Ask Google Maps for alternative paths
        with st.spinner("Asking Google for alternative paths..."):
            all_routes = get_multiple_routes(origin, destination)
            
        if not all_routes:
            st.error("No routes found.")
        else:
            st.info(f"Found {len(all_routes)} possible routes. Evaluating physical environments in the background...")
            
            best_route_data = None
            best_score = -1
            
            # Setup master progress bar
            total_waypoints = sum(len(route) for route in all_routes)
            progress_bar = st.progress(0)
            waypoints_processed = 0
            
            # 4. Evaluate Every Route
            for route_idx, waypoints in enumerate(all_routes):
                route_scores = []

                # Check each waypoint on this specific route
                for wp_idx, coord in enumerate(waypoints):
                    img_path = f"route_{route_idx}_wp_{wp_idx}.jpg"

                    fetch_street_view(coord, img_path)
                    raw_json = analyze_street(img_path)
                    parsed_json = json.loads(raw_json)
                    route_scores.append((img_path, parsed_json))

                    waypoints_processed += 1
                    progress_bar.progress(waypoints_processed / total_waypoints)

                    # Throttle the loop to respect the 15 RPM API limit
                    time.sleep(4.5)
                    
                # 5. Math Engine: Calculate Averages for this Route
                num_pts = len(route_scores)
                avg_peace = sum(item[1]["sensory_and_comfort"]["sensory_peaceful"] for item in route_scores) / num_pts
                avg_shade = sum(item[1]["sensory_and_comfort"]["shade_coverage"] for item in route_scores) / num_pts
                avg_light = sum(item[1]["safety_and_security"]["nighttime_lighting"] for item in route_scores) / num_pts
                avg_access = sum(item[1]["mobility"]["stroller_friendly"] for item in route_scores) / num_pts
                
                # 6. Math Engine: Calculate Route Fit Score (%)
                sum_weights = weights.get('peacefulness_weight', 0) + weights.get('shade_weight', 0) + weights.get('lighting_weight', 0) + weights.get('accessibility_weight', 0)
                if sum_weights == 0: 
                    sum_weights = 1 # Prevent dividing by zero if user says they care about nothing
                    
                raw_score = (
                    avg_peace * weights.get('peacefulness_weight', 0) +
                    avg_shade * weights.get('shade_weight', 0) +
                    avg_light * weights.get('lighting_weight', 0) +
                    avg_access * weights.get('accessibility_weight', 0)
                )
                
                match_percentage = (raw_score / (5.0 * sum_weights)) * 100
                
                # If this route beats the previous best, it becomes the new winner
                if match_percentage > best_score:
                    best_score = match_percentage
                    best_route_data = {
                        "index": route_idx + 1,
                        "match": match_percentage,
                        "scores": route_scores,
                        "averages": (avg_peace, avg_shade, avg_light, avg_access)
                    }
                    
            # 7. Display ONLY the Winning Route
            st.divider()
            st.success(f"Winning Route Found: Route {best_route_data['index']} is a {best_route_data['match']:.1f}% Match!")
            
            avg_peace, avg_shade, avg_light, avg_access = best_route_data['averages']
            
            # Display Winner's Averages
            m_col1, m_col2, m_col3, m_col4 = st.columns(4)
            m_col1.metric("Average Peace", f"{avg_peace:.1f} / 5")
            m_col2.metric("Average Shade", f"{avg_shade:.1f} / 5")
            m_col3.metric("Average Light", f"{avg_light:.1f} / 5")
            m_col4.metric("Average Access", f"{avg_access:.1f} / 5")
            
            # Display Winner's Journey Map
            st.header("Your Optimized Journey")
            for idx, (img_file, data) in enumerate(best_route_data['scores']):
                st.subheader(f"Stop {idx+1}")
                layout_col1, layout_col2 = st.columns([1, 2])
                with layout_col1:
                    if os.path.exists(img_file):
                        st.image(img_file, use_container_width=True)
                with layout_col2:
                    st.markdown(f"**Agent Assessment:** {data.get('brief_summary')}")
                    sm1, sm2, sm3, sm4 = st.columns(4)
                    sm1.caption(f"Quiet: {data['sensory_and_comfort']['sensory_peaceful']}/5")
                    sm2.caption(f"Shade: {data['sensory_and_comfort']['shade_coverage']}/5")
                    sm3.caption(f"Light: {data['safety_and_security']['nighttime_lighting']}/5")
                    sm4.caption(f"Mobility: {data['mobility']['stroller_friendly']}/5")
                st.write("---")