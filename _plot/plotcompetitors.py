from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests

import pandas as pd

def create_table_for_competitors(data: dict):
	global df
	names, addresses, lat, lon = [], [], [], []

	for index, val in enumerate(data.get('features')):
		names.append(val.get('properties').get('name'))
		addresses.append(val.get('properties').get('formatted'))
		lat.append(val.get('properties').get('lat'))
		lon.append(val.get('properties').get('lon'))

	actualDict = {"Name": names, "Address": addresses, "Latitude": lat, "Longitude": lon}
	df = pd.DataFrame(actualDict)
	return df

def get_coordinates(city_name):
	geolocator = Nominatim(user_agent="Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36")
	location = geolocator.geocode(city_name)
	if location:
		return location.latitude, location.longitude
	else:
		return None

def get_bounding_box(latitude, longitude, distance_km):
# Calculate the bounding box coordinates
	start = geodesic(kilometers=distance_km)
	bottom_left = start.destination((latitude, longitude), 225)
	top_right = start.destination((latitude, longitude), 45)
	return bottom_left, top_right

def get_competitor_data(city_name):
	'''specifically for electronics stores'''
	coordinates = get_coordinates(city_name)
	if coordinates:
		latitude, longitude = coordinates
		distance_km = 10 														 
		bottom_left, top_right = get_bounding_box(latitude, longitude, distance_km)

	url = 'https://api.geoapify.com/v2/places'
	params = {'categories': 'commercial.elektronics', 'filter': f"rect:{bottom_left.longitude},{bottom_left.latitude},{top_right.longitude},{top_right.latitude}", 'limit': 20, 'apiKey':'085e718f0205455db5cac133ebf11b34'}
	resp = requests.get(url=url, params=params)
	data = resp.json()
	return data

def findTop5(dataframe, city_name):
	distances = []
	storeLat, storeLon = get_coordinates(city_name)
	for index, row in dataframe.iterrows():
		lat = row['Latitude']
		lon = row['Longitude']
		distances.append(geodesic((storeLat, storeLon), (lat, lon)).kilometers)
	df = df.assign(Distances = distances)
	top5 = df.sort_values(by = 'Distances')[:5]
	return top5


city_name = "London"
print(top5(get_competitor_data(city_name), city_name)
