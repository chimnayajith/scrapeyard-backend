# views.py
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import CarSerializer
from .scrapers.cars24 import Cars24Scraper
from .scrapers.olx import OlxScraper
import subprocess
import json

@api_view(['GET'])
def scrape_cars(request):
    location = request.query_params.get('location', 'kochi')
    location_code_url = "https://www.olx.in/api/locations/popular?lang=en-IN&limit=6524&type=CITY"
    location_command = ['curl', '-s', location_code_url]
    
    locations = subprocess.run(location_command, capture_output=True, text=True, check=True)
    locations_data = locations.stdout
    locations_json = json.loads(locations_data)

    location_id = None
    location_name = None
    for item in locations_json["data"]:
        if item["name"].lower() == location.lower():
            location_id = item["id"]
            location_name = item["name"].lower()
            break

    if location_id is None:
        return Response({"error": "Location not found"}, status=404)

    cars24_scraper = Cars24Scraper()
    olx_scraper = OlxScraper()

    cars24_data = cars24_scraper.scrape(location_name)
    olx_data = olx_scraper.scrape(location_name, location_id)

    # After scraping and normalizing OLX data
    normalized_olx_data = []
    for olx_car in olx_data.to_dict('records'):
        normalized_olx_data.append({
            'car_name': olx_car.get('Car Name', 'N/A'),
            'manufacture_year': olx_car.get('Manufacture Year', 'N/A'), 
            'mileage': olx_car.get('Kilometers', 'N/A'),  
            'fuel_type': olx_car.get('Fuel Type', 'N/A'), 
            'owner': olx_car.get('Owner', 'N/A'),  
            'price': olx_car.get('Price', 'N/A'),
            'emi': olx_car.get('EMI', 'N/A'),
            'url': olx_car.get('URL', 'N/A'),
            'image_url': olx_car.get('Image URL', 'N/A').strip()
        })

    # Normalize Cars24 data similarly
    normalized_cars24_data = []
    for cars24_car in cars24_data.to_dict('records'):
        normalized_cars24_data.append({
            'car_name': cars24_car.get('Car Name', 'N/A'),
            'manufacture_year': cars24_car.get('Manufacture Year', 'N/A'), 
            'mileage': cars24_car.get('Mileage', 'N/A'),  
            'fuel_type': cars24_car.get('Fuel Type', 'N/A'), 
            'owner': cars24_car.get('Owner', 'N/A'),  
            'price': cars24_car.get('Price', 'N/A'),
            'emi': cars24_car.get('EMI', 'N/A'),
            'url': cars24_car.get('URL', 'N/A'),
            'image_url': cars24_car.get('Image URL', 'N/A').strip()
        })

    # Combine both normalized lists
    combined_data = normalized_cars24_data + normalized_olx_data

    try:
        serializer = CarSerializer(combined_data, many=True)
        return Response({"cars": serializer.data}, status=200)
    except Exception as e:
        print(f"Serialization error: {e}")
        return Response({"error": str(e)}, status=400)
