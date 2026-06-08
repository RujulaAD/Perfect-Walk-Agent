import os
import googlemaps
from dotenv import load_dotenv

load_dotenv()
MAPS_KEY = os.getenv('GOOGLE_MAPS_KEY')
gmaps = googlemaps.Client(key=MAPS_KEY)

def get_multiple_routes(origin: str, destination: str):
    """
    Requests multiple alternative walking routes from Google Maps.
    Returns a list of dictionaries containing waypoints and text instructions.
    """
    print(f"Asking Google for ALL walking paths from '{origin}' to '{destination}'...")
    
    directions = gmaps.directions(origin, destination, mode="walking", alternatives=True)
    
    if not directions:
        print("Error: No routes found.")
        return []
        
    all_routes = []
    
    for route_index, route in enumerate(directions):
        steps = route['legs'][0]['steps']
        waypoints = []
        instructions = [] # <-- NEW: Create a list to hold the text
        
        for step in steps:
            lat = step['start_location']['lat']
            lng = step['start_location']['lng']
            waypoints.append(f"{lat},{lng}")
            
            # <-- NEW: Grab Google's raw HTML instruction for this step
            instructions.append(step['html_instructions']) 
            
        # <-- NEW: Save both lists into a dictionary
        all_routes.append({
            "waypoints": waypoints,
            "instructions": instructions
        })
        print(f"Route {route_index + 1}: Found {len(waypoints)} checkpoints.")
        
    print(f"Successfully extracted {len(all_routes)} distinct walking routes.")
    return all_routes

# --- Local Test Engine ---
if __name__ == "__main__":
    start_point = "Washington Square Park, New York, NY"
    end_point = "Union Square, New York, NY"
    
    routes = get_multiple_routes(start_point, end_point)