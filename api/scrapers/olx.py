import subprocess
from bs4 import BeautifulSoup
import pandas as pd

class OlxScraper:
    def scrape(self, location_name, location_id):
        url = f"https://www.olx.in/{location_name}_g{location_id}/cars_c84"
        command = ['curl', '-s', url]
        
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            result_data = result.stdout
            soup = BeautifulSoup(result_data, 'html.parser')

            car_names = []
            manufacture_year = []
            kilometers = []
            prices = []
            urls = []
            image_urls = []

            car_items = soup.find_all('li', attrs={'data-aut-id': 'itemBox2'})[:10]

            for item in car_items:
                name = item.find('div', attrs={'data-aut-id': 'itemTitle'})
                full_car_name = name.text.strip() if name else "N/A"
                car_names.append(full_car_name)

                subtitle = item.find('div', attrs={'data-aut-id': 'itemSubTitle'})
                if subtitle:
                    year_km = subtitle.text.split(' - ')
                    if len(year_km) == 2:
                        manufacture_year.append(year_km[0].strip())
                        kilometers.append(year_km[1].strip())
                    else:
                        manufacture_year.append("N/A")
                        kilometers.append("N/A")
                else:
                    manufacture_year.append("N/A")
                    kilometers.append("N/A")
                
                price = item.find('span', attrs={'data-aut-id': 'itemPrice'})
                prices.append(price.text.strip() if price else "N/A")

                url = item.find('a', href=True)
                full_url = f"https://www.olx.in{url['href']}" if url else "N/A"
                urls.append(full_url)

                image = item.find('img')
                if image and image.get('srcset'):
                    img_url = image['srcset'].split(",")[-1].split(" ")[0]
                    image_urls.append(img_url)
                else:
                    image_urls.append("N/A")

            split_car_names = [car_name.split(" ", 1) for car_name in car_names]
            car_data = pd.DataFrame({
                'Manufacture Year': manufacture_year,
                'Car Name': [name[0] for name in split_car_names],  # First part
                'Model Name': [name[1].strip() if len(name) > 1 else "N/A" for name in split_car_names],  # Second part
                'Mileage': kilometers,
                'Price': prices,
                'URL': urls,
                'EMI': "N/A",
                'Fuel Type': "N/A",
                'Image URL': image_urls,
                'source': 'olx'
            })

            return car_data

        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running subprocess: {e}")
            return pd.DataFrame()

    def scrape_additional_data(self, urls):
        additional_details = []

        for url in urls:
            if url == "N/A":
                additional_details.append({
                    'URL': url,
                    'Fuel Type': "N/A",
                    'Owners': "N/A"
                })
                continue

            command = ['curl', '-s', url]
            try:
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                result_data = result.stdout
                soup = BeautifulSoup(result_data, 'html.parser')
                print(f"Scraping additional data from: {url}")
                
                owner = soup.find('div', class_="_3VRXh")
                fuel_type = soup.find('h2', class_='_3rMkw')

                additional_details.append({
                    'URL': url,
                    'Fuel Type': fuel_type.text.strip() if fuel_type else "N/A",
                    'Owners': f"{owner.text.strip()} Owner" if owner else "N/A"
                })

            except subprocess.CalledProcessError as e:
                print(f"An error occurred while scraping {url}: {e}")
                additional_details.append({
                    'URL': url,
                    'Fuel Type': "N/A",
                    'Owners': "N/A"
                })

        additional_data_df = pd.DataFrame(additional_details)
        return additional_data_df
