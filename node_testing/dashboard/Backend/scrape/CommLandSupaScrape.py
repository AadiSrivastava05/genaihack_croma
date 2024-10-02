import requests
from bs4 import BeautifulSoup
import re

from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pandas as pd
import geopandas as gpd

import time

import os
from supabase import create_client, Client
from requests.structures import CaseInsensitiveDict
import urllib.parse

'''
url = "https://www.magicbricks.com/srp_commercial_land1.xml"

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
}

webpage = requests.get(url, headers=headers).text

with open("commercial_land_data.txt", "w") as fp:
 	fp.write(webpage)

'''

url: str = "https://ajkgqdvxmueqxtuvcjho.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFqa2dxZHZ4bXVlcXh0dXZjamhvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjU1NTYyOTcsImV4cCI6MjA0MTEzMjI5N30.cwmfECvEYqu6FZXRFqcTw1zD-H6NoHkG_etfqPZ-hDw"

apiKey = '085e718f0205455db5cac133ebf11b34'

headers1 = CaseInsensitiveDict()
headers1["Accept"] = "application/json"

supabase: Client = create_client(url, key)

with open('commercial_land_data.txt', 'r') as fp:
	links = [i.strip()[5:-6] for i in fp.readlines() if re.match("^<loc>", i.strip())]

headers0 = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36"
}
i = 13348
for url in links[i:]:
    i += 1
    try:
        # Set a 10-second timeout for the request
        webpage = requests.get(url.strip(), headers=headers0, timeout=10).text
        soup = BeautifulSoup(webpage, 'html.parser')
        json_scripts = soup.find_all("script", type='application/ld+json')
        names = re.findall(r'"@type":"Person","name":"(.*?)"', webpage)
        plots = re.findall(r'"object":\{"@type":"Residence","name":"(.*?)"\}', webpage)
        prices = re.findall(r'"priceSpecification":\{"@type":"PriceSpecification","price":(\d+),"priceCurrency":"INR"\}', webpage)

        results = list(zip(names, plots, prices))
        for infor in results:
            mainInfo = {"owner_name": infor[0], "city": infor[1][27:], "price": int(infor[-1]), "link": url.strip()}

            city_name = urllib.parse.quote_plus(infor[1][27:])
            
            # Set a 10-second timeout for the geolocation request as well
            url2 = f"https://api.geoapify.com/v1/geocode/search?text={city_name}&apiKey={apiKey}"
            resp = requests.get(url2, headers=headers1, timeout=10)
            latlnga = resp.json().get('features')[0].get('geometry').get('coordinates')
            bboxa = resp.json().get('features')[0].get('bbox')
            
            mainInfo['latitude'] = latlnga[1]
            mainInfo['longitude'] = latlnga[0]

            mainInfo['bboxBleftLat'] = bboxa[1]
            mainInfo['bboxBleftLng'] = bboxa[0]
            mainInfo['bboxTRightLat'] = bboxa[-1]
            mainInfo['bboxTRightlng'] = bboxa[-2]
            
            response = supabase.table('CommercialLandCoords').insert(mainInfo).execute()
            print(mainInfo, i)
    
    # Handle timeout exception
    except requests.exceptions.Timeout:
        print(f"Request timed out for URL: {url.strip()}, moving to next link.")
    
    except Exception as E:
        print(f"some error bruh: {E}")
