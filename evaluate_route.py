import time
import json
from router import get_route_waypoints
from sensor import fetch_street_view
from brain import analyze_street

def analyze_entire_route(start: str, end: str):
    print("Starting Route Analysis Engine...")
    
    # 1. Get the list of coordinates along the path
    waypoints = get_route_waypoints(start, end)
    
    if not waypoints:
        print("Could not extract any waypoints. Aborting.")
        return
    
    route_scores = []
    
    # 2. Loop through every single coordinate checkpoint
    for index, coordinate in enumerate(waypoints):
        print(f"\n--- Processing Checkpoint {index + 1} of {len(waypoints)} ({coordinate}) ---")
        
        # Define a temporary image name for this specific stop
        temp_image_path = f"checkpoint_{index + 1}.jpg"
        
        try:
            # 3. Sensor: Download the real-world street view image
            print("Downloading image from Google Street View...")
            fetch_street_view(coordinate, temp_image_path)
            
            # 4. Brain: Feed the image to Gemini and get structured JSON back
            print("Asking Gemini Vision AI to grade the environment...")
            raw_ai_analysis = analyze_street(temp_image_path)
            
            # Parse the AI's response text into a standard Python dictionary
            checkpoint_data = json.loads(raw_ai_analysis)
            
            # Save the checkpoint data to our master list
            route_scores.append(checkpoint_data)
            print(f"Checkpoint {index + 1} successfully graded!")
            
        except Exception as e:
            print(f" Failed to evaluate checkpoint {index + 1}: {e}")
            
        # Optional: Sleep for 1 second between calls to be nice to rate limits
        time.sleep(1)
        
    print("\n==============================================")
    print("FINAL ROUTE METRICS SUMMARY")
    print("==============================================")
    print(f"Total Checkpoints Evaluated: {len(route_scores)}")
    
    # 5. Let's look at the brief summary of the first checkpoint as a quick test
    if route_scores:
        print("\nFirst Checkpoint Vibe Check:")
        print(route_scores[0].get("brief_summary"))

if __name__ == "__main__":
    # Let's run the full pipeline test!
    analyze_entire_route("Times Square, New York, NY", "Bryant Park, New York, NY")