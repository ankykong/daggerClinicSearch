import json
import sys
import argparse
import os
from dotenv import load_dotenv

load_dotenv()


def parse_coordinates(data_str):
    """Parse coordinates from JSON data string."""
    try:
        print("DATA STRING:", data_str)
        print(type(data_str))
        data = json.loads(data_str)
        print(data)
        results = data.get('results', [{}])[0]
        print(results)
        nav_points = results.get('navigation_points', [{}])[0]
        print(nav_points)
        location = nav_points.get('location', {})
        print(location)
        lat = location.get('latitude')
        lng = location.get('longitude')

        if lat and lng:
            return {
                "latitude": lat,
                "longitude": lng,
                "formatted": f"Latitude: {lat}, Longitude: {lng}"
            }
        else:
            return {"error": "Navigation point coordinates not found"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON data"}
    except Exception as e:
        return {"error": f"Error parsing coordinates: {str(e)}"}


def main(input_file=None):
    # Check for API key (for consistency with geocoding_api_call.py)
    api_key = os.getenv("PLACES_API_KEY")
    if not api_key:
        print("Warning: PLACES_API_KEY not found in .env file")

    # Read data from file or stdin
    if input_file:
        try:
            with open(input_file, 'r') as f:
                data_str = f.read()
        except FileNotFoundError:
            print(f"Error: File {input_file} not found")
            return
    else:
        data_str = sys.stdin.read()

    # Parse the coordinates
    result = parse_coordinates(data_str)

    # Print the result
    if "error" in result:
        print(result["error"])
    else:
        print(result["formatted"])
        return result


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Parse coordinates from navigation point JSON data')
    parser.add_argument(
        '--file',
        type=str,
        help='JSON file to parse (defaults to stdin if not provided)')

    # Parse arguments
    args = parser.parse_args()

    # Call main function
    result = main(args.file)

    # Print full result object for debugging
    if result and "error" not in result:
        with open('parsed_coordinates.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("Parsed coordinates saved to parsed_coordinates.json")
