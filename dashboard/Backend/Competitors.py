from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import requests
import pandas as pd
import geopandas as gpd

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
	params = {'categories': 'commercial.elektronics', 'filter': f"rect:{bottom_left.longitude},{bottom_left.latitude},{top_right.longitude},{top_right.latitude}", 'limit': 20, 'apiKey':''} # enter API key here
	resp = requests.get(url=url, params=params)
	data = resp.json()
	return data

def findTopn(dataframe, city_name, n):
	distances = []
	storeLat, storeLon = get_coordinates(city_name)
	for index, row in dataframe.iterrows():
		lat = row['Latitude']
		lon = row['Longitude']
		distances.append(geodesic((storeLat, storeLon), (lat, lon)).kilometers)
	df = dataframe.assign(Distances = distances)
	topn = df.sort_values(by = 'Distances')[:int(n)]
	return topn

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
	return render_template('map2.html')  

@socketio.on('competitor_data_request')
def handle_competitor_request(data):
	city_name = data.get('city_name')
	n = data.get('n')
	print('request received')
	df = findTopn(create_table_for_competitors(get_competitor_data(city_name)), city_name, n)
	all_coordinates = {}
	j = 0
	for i, row in df.iterrows():
		all_coordinates[f'lat{j}'] = row['Latitude']
		all_coordinates[f'lon{j}'] = row['Longitude']
		j += 1

	all_coordinates['toZoomlat'] = get_coordinates(city_name)[0]
	all_coordinates['toZoomlon'] = get_coordinates(city_name)[1]
	print(all_coordinates)
	emit('competitor_data_update', all_coordinates)

if __name__ == '__main__':
	socketio.run(app, debug=True, port=5011)