import os
import googlemaps
from dotenv import load_dotenv

load_dotenv()
MAPS_KEY = os.getenv('GOOGLE_MAPS_KEY')
gmaps = googlemaps.Client(key=MAPS_KEY)

def get_multiple_routes(origin: str, destination: str):
    """
    Requests multiple alternative walking routes from Google Maps.
    Returns a list of routes, where each route is a list of coordinate waypoints.
    """
    print(f"Asking Google for ALL walking paths from '{origin}' to '{destination}'...")
    
    # 1. We added 'alternatives=True' to force Google to give us options
    directions = gmaps.directions(origin, destination, mode="walking", alternatives=True)
    
    if not directions:
        print("Error: No routes found.")
        return []
        
    all_routes = []
    
    # 2. Loop through every alternative route Google gave us (usually 1 to 3)
    for route_index, route in enumerate(directions):
        steps = route['legs'][0]['steps']
        waypoints = []
        
        # Extract the coordinates for this specific route
        for step in steps:
            lat = step['start_location']['lat']
            lng = step['start_location']['lng']
            waypoints.append(f"{lat},{lng}")
            
        all_routes.append(waypoints)
        print(f"Route {route_index + 1}: Found {len(waypoints)} checkpoints.")
        
    print(f"Successfully extracted {len(all_routes)} distinct walking routes.")
    return all_routes

# --- Local Test Engine ---
if __name__ == "__main__":
    start_point = "Washington Square Park, New York, NY"
    end_point = "Union Square, New York, NY"
    
    routes = get_multiple_routes(start_point, end_point)