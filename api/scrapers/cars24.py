import requests
from bs4 import BeautifulSoup
import pandas as pd

class Cars24Scraper:
    def scrape(self, location="mumbai"):
        url = f"https://www.cars24.com/buy-used-cars-{location}/"

        HEADERS = ({
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            'Accept-Language': 'en-US, en;q=0.5'
        })
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            manufacture_years = []
            car_names = []
            model_names = []
            kilometers = []
            fuel_types = []
            owners = []
            prices = []
            emis = []
            urls = []
            image_urls = []

            listings = soup.find_all('a', class_='_1_1Uy')

            for listing in listings:
                full_name = listing.find('h3', class_='_2Out2').text.strip()
                
                # Split the car name
                name_parts = full_name.split(" ", 1)
                manufacture_year = name_parts[0]
                car_name = name_parts[1].split(' ',1)[0]
                model_name = name_parts[1].split(' ',1)[1]
                manufacture_years.append(manufacture_year)
                car_names.append(car_name)
                model_names.append(model_name) 
                details = listing.find('ul', class_='_3jRcd').find_all('li')
                kilometers.append(details[1].text.strip())
                fuel_types.append(details[2].text.strip())
                owners.append(details[3].text.strip())

                price = listing.find('strong', class_='_37WXy').text.strip()
                emi = listing.find('span', class_='_1t1AA').text.strip()
                prices.append(price)
                emis.append(emi)

                car_url = listing['href']
                urls.append(car_url)
                
                image_tag = listing.find('img')
                image_url = image_tag['src'] if image_tag else None
                image_urls.append(image_url)

            # Create DataFrame with proper lists
            df = pd.DataFrame({
                'Manufacture Year': manufacture_years,
                'Car Name': car_names,
                'Model Name': model_names,
                'Mileage': kilometers,
                'Fuel Type': fuel_types,
                'Owner': owners,
                'Price': prices,
                'EMI': emis,
                'URL': urls,
                'Image URL': image_urls,
                'source': 'cars24'
            })
            return df

        else:
            print(f"Failed to retrieve content: {response.status_code}")
