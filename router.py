import os
import googlemaps
from dotenv import load_dotenv

# 1. Load your Maps API key from the hidden vault
load_dotenv()
MAPS_KEY = os.getenv('GOOGLE_MAPS_KEY')

# Initialize the Google Maps Client
gmaps = googlemaps.Client(key=MAPS_KEY)

def get_route_waypoints(origin: str, destination: str):
    """
    Requests walking directions from Google Maps and extracts coordinate checkpoints along the path.
    """
    print(f"Calculating walking route from '{origin}' to '{destination}'...")
    
    # 2. Call the Directions API specifically requesting walking mode
    directions = gmaps.directions(origin, destination, mode="walking")
    
    if not directions:
        print("Error: No route found.")
        return []
        
    # 3. Drill down into the JSON response to grab the steps of the journey
    steps = directions[0]['legs'][0]['steps']
    waypoints = []
    
    # 4. Loop through every turn/step and grab its starting coordinates
    for step in steps:
        lat = step['start_location']['lat']
        lng = step['start_location']['lng']
        
        # Google Street View accepts raw coordinate strings just like an address!
        coordinate_string = f"{lat},{lng}"
        waypoints.append(coordinate_string)
        
    print(f"📍 Successfully extracted {len(waypoints)} checkpoints to evaluate.")
    return waypoints

# --- Local Test Engine ---
if __name__ == "__main__":
    # A quick test walk in NYC from Times Square to Bryant Park
    start_point = "Times Square, New York, NY"
    end_point = "Bryant Park, New York, NY"
    
    checkpoints = get_route_waypoints(start_point, end_point)
    
    print("\nCheckpoints ready for AI evaluation:")
    for cp in checkpoints:
        print(cp)