import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re

class CarWaleScraper:
    def scrape(self, location="kochi"):
        url = f"https://www.carwale.com/used/{location}/"

        HEADERS = ({'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                    'Accept-Language': 'en-US, en;q=0.5'})
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            cars = []

            script_tag = soup.find('script', type='application/ld+json')
            json_data = json.loads(script_tag.string)

            car_list = json_data['@graph'][0]['itemListElement']

            for car in car_list:
                model_trimmed = re.sub(r'\s*\[\d{4}-\d{4}\]', '', car['model'])

                car_data = {
                    'car_name': f"{car['Brand']['name']}",
                    'model_name': model_trimmed,
                    'manufacture_year': car['vehicleModelDate'],
                    'mileage': car['mileageFromOdometer']['value'],
                    'fuel_type': car['fuelType'],
                    'owner': 'N/A',
                    'price': f"₹{car['offers']['price']}",
                    'emi': 'N/A',
                    'url': car['url'],
                    'image_url': car.get('image', 'N/A')[0]
                }

                cars.append(car_data)

            df = pd.DataFrame(cars)
            return df

        else:
            print(f"Failed to retrieve content: {response.status_code}")
            return pd.DataFrame()
