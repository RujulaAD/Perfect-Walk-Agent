import os
import requests
from dotenv import load_dotenv

# Load the keys from .env vault
load_dotenv()

# Specifically grab the Maps key for this script
MAPS_KEY = os.getenv('GOOGLE_MAPS_KEY') 

def fetch_street_view(address: str, output_filename: str = "street.jpg"):
    """
    Pings the Google Street View Static API and downloads an image of the address.
    """
    print(f"Pinging satellites for: {address}...")
    
    url = "https://maps.googleapis.com/maps/api/streetview"
    
    # These are the instructions sent to Google's map servers
    params = {
        "size": "800x600",     # High resolution for the AI to analyze
        "location": address,   # The street we want to look at
        "fov": 120,            # Field of View (120 gives a nice wide street angle)
        "key": MAPS_KEY        # Using the specific Maps VIP pass here
    }
    
    # Make the request
    response = requests.get(url, params=params)
    
    # Check if it worked and save the image
    if response.status_code == 200:
        with open(output_filename, 'wb') as file:
            file.write(response.content)
        print(f"Success! Image saved locally as '{output_filename}'")
    else:
        print(f"Error: Google denied the request. Code {response.status_code}")

# --- Test it on a classic busy intersection ---
if __name__ == "__main__":
    test_location = "Times Square, New York, NY"
    fetch_street_view(test_location)