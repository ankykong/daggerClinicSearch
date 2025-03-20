import requests
import os
import json
from dotenv import load_dotenv
import argparse

load_dotenv()


def main(latitude, longitude, radius, place_type):
    # Access the API key from environment variables
    api_key = os.getenv("PLACES_API_KEY")
    if not api_key:
        print("Error: PLACES_API_KEY not found in .env file")
        return

    # Prepare the request payload
    payload = {
        "includedTypes": [place_type],
        "maxResultCount": 10,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": float(latitude),
                    "longitude": float(longitude)
                },
                "radius": float(radius)
            }
        }
    }

    # Set up the API endpoint and headers
    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.*"
    }

    # Make the API request
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Search for nearby places using Google Places API')
    parser.add_argument('latitude', type=float, help='Latitude of the center point')
    parser.add_argument('longitude', type=float, help='Longitude of the center point')
    parser.add_argument('radius', type=float, help='Search radius in meters')
    parser.add_argument('type', type=str, help='Type of place to search for (e.g., restaurant)')

    # Parse arguments
    args = parser.parse_args()

    # Call main function with the provided parameters
    result = main(args.latitude, args.longitude, args.radius, args.type)

    # Print the result
    if result:
        with open('nearby_places_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("Nearby places data saved to nearby_places_result.json")
