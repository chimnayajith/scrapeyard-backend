import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import CarSerializer
from .scrapers.cars24 import Cars24Scraper
from .scrapers.olx import OlxScraper
from .scrapers.carwala import CarWaleScraper
import subprocess
import json
import random

def getCoordinates(location):
    url = 'https://nominatim.openstreetmap.org/search'
    params = {
        'q': f'{location}',
        'format': 'json',
        'addressdetails': 1,
        'limit': 1,
        'polygon_geojson': 1,
        'email': 'chinmayajith30@gmail.com'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return {
            "lat":data[0]['lat'],
            "lon":data[0]['lon']
        }
    else:
        print(f"Error: {response.status_code}")

def randomizeCoordinates(coordinates):
    original_lat = float(coordinates['lat'])
    original_lon = float(coordinates['lon'])
    
    lat_random = original_lat + random.choice([-1, 1]) * random.uniform(0.1, 0.5)
    
    lon_random = original_lon + random.choice([-1, 1]) * random.uniform(0.1, 0.5)
    
    return {
        "lat": lat_random,
        "lon": lon_random
    }    

@api_view(['POST'])
def scrape_cars(request):
    location = request.data.get('location','kochi')

    coordinates = getCoordinates(location)
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
    carwale_scraper = CarWaleScraper()

    cars24_data = cars24_scraper.scrape(location_name)
    olx_data = olx_scraper.scrape(location_name, location_id)
    carwale_data = carwale_scraper.scrape(location_name) 

    # Normalize OLX data
    normalized_olx_data = []
    for olx_car in olx_data.to_dict('records'):
        normalized_olx_data.append({
            'brand': olx_car.get('Car Name', 'N/A'),
            'model':olx_car.get('Model Name', 'N/A'),
            'manufacture_year': olx_car.get('Manufacture Year', 'N/A'), 
            'mileage': olx_car.get('Kilometers', 'N/A'),  
            'fuel_type': olx_car.get('Fuel Type', 'N/A'), 
            'owner': olx_car.get('Owner', 'N/A'),  
            'price': olx_car.get('Price', 'N/A'),
            'emi': olx_car.get('EMI', 'N/A'),
            'url': olx_car.get('URL', 'N/A'),
            'image_url': olx_car.get('Image URL', 'N/A').strip(),
            'source': 'OLX',
            'location':randomizeCoordinates(coordinates),
        })

    # Normalize Cars24 data
    normalized_cars24_data = []
    for cars24_car in cars24_data.to_dict('records'):
        normalized_cars24_data.append({
            'brand': cars24_car.get('Car Name', 'N/A'),
            'model':cars24_car.get("Model Name", "N/A"),
            'manufacture_year': cars24_car.get('Manufacture Year', 'N/A'), 
            'mileage': cars24_car.get('Mileage', 'N/A'),  
            'fuel_type': cars24_car.get('Fuel Type', 'N/A'), 
            'owner': cars24_car.get('Owner', 'N/A'),  
            'price': cars24_car.get('Price', 'N/A'),
            'emi': cars24_car.get('EMI', 'N/A'),
            'url': cars24_car.get('URL', 'N/A'),
            'image_url': cars24_car.get('Image URL', 'N/A').strip(),
            'source':'Cars24',
            'location':randomizeCoordinates(coordinates),
        })

    normalized_carwale_data = []
    for carwale_car in carwale_data.to_dict('records'):
        normalized_carwale_data.append({
            'brand': carwale_car.get('car_name', 'N/A'),
            'model':carwale_car.get('model_name', 'N/A'),
            'manufacture_year': carwale_car.get('manufacture_year', 'N/A'), 
            'mileage': carwale_car.get('mileage', 'N/A'),  
            'fuel_type': carwale_car.get('fuel_type', 'N/A'), 
            'owner': 'N/A', 
            'price': carwale_car.get('price', 'N/A'),
            'emi': 'N/A',
            'url': carwale_car.get('url', 'N/A'),
            'image_url': 'N/A',
            'source': 'CarWale',
            'location':randomizeCoordinates(coordinates),
        })

    # Combine all data
    combined_data = normalized_cars24_data + normalized_olx_data + normalized_carwale_data

    try:
        # Serialize the combined data
        serializer = CarSerializer(combined_data, many=True)
        return Response({"coordinates":coordinates,"cars": serializer.data}, status=200)
    except Exception as e:
        print(f"Serialization error: {e}")
        return Response({"error": str(e)}, status=400)
