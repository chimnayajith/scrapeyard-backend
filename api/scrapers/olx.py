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
                car_names.append(name.text.strip() if name else "N/A")

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

            car_data = pd.DataFrame({
                'Manufacture Year': manufacture_year,
                'Car Name': car_names,
                'Mileage': kilometers,
                'Price': prices,
                'URL': urls,
                'EMI': "N/A",
                'Fuel Type': "N/A",
                'Image URL': image_urls,
                'source': 'olx'
            })

            # print("Initial Car Data:\n", car_data)

            # Scrape additional data from the collected URLs
            # additional_data = self.scrape_additional_data(urls)

            # Check if additional data has been collected
            # print("Additional Data:\n", additional_data)

            # Merge additional data with car data
            # if not additional_data.empty:
            #     car_data = car_data.merge(additional_data, on='URL', how='left')

            # print("Merged Car Data:\n", car_data)
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
                # Debugging output to check the response from each URL
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
