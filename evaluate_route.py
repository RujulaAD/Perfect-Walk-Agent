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
    
    if route_scores:
        # Initialize running totals for our metrics
        total_peaceful = 0
        total_shade = 0
        total_lighting = 0
        total_stroller = 0
        
        # Loop through each checkpoint and add up the scores
        for score in route_scores:
            total_peaceful += score["sensory_and_comfort"]["sensory_peaceful"]
            total_shade += score["sensory_and_comfort"]["shade_coverage"]
            total_lighting += score["safety_and_security"]["nighttime_lighting"]
            total_stroller += score["mobility"]["stroller_friendly"]
            
        # Calculate the mathematical averages
        num_points = len(route_scores)
        avg_peaceful = total_peaceful / num_points
        avg_shade = total_shade / num_points
        avg_lighting = total_lighting / num_points
        avg_stroller = total_stroller / num_points
        
        # Print the final scorecard
        print(f"\nAverage Peacefulness:  {avg_peaceful:.1f} / 5")
        print(f"Average Shade Coverage: {avg_shade:.1f} / 5")
        print(f"Average Night Lighting: {avg_lighting:.1f} / 5")
        print(f"Average Accessibility:  {avg_stroller:.1f} / 5")
        
        print("\n----------------------------------------------")
        print("Route Narrative Journey:")
        for idx, score in enumerate(route_scores):
            print(f"Stop {idx+1}: {score.get('brief_summary')}\n")

if __name__ == "__main__":
    analyze_entire_route("Times Square, New York, NY", "Bryant Park, New York, NY")