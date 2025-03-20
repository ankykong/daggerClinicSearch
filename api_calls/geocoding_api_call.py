import requests
import os
from dotenv import load_dotenv
import argparse
import json

load_dotenv()


def main(address):
    # Example of accessing an environment variable
    api_key = os.getenv("PLACES_API_KEY")
    if not api_key:
        print("Error: PLACES_API_KEY not found in .env file")
        return

    # Parse the address string and replace spaces with +
    parsed_address = address.replace(" ", "+")

    # Example geocoding API call
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": parsed_address,
        "key": api_key
    }
    # print(f"Making API call to: {base_url}?address={parsed_address}&api_key={api_key}")

    response = requests.get(base_url, params=params)
    return response.json()


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Geocode an address using Google Maps API')
    parser.add_argument('address', type=str, help='The address to geocode')

    # Parse arguments
    args = parser.parse_args()

    # print("Before Result")
    # Call main function with the provided address
    result = main(args.address)

    # Print the result
    if result:
        with open('geocoding_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        # print("After Result")
