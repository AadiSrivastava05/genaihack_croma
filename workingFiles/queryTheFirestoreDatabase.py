import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("apikey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

plots_ref = db.collection('plots')
docs = plots_ref.stream()

search_location = "Navi Mumbai"

matching_plots = []

for doc in docs:
	data = doc.to_dict()
	if search_location.lower() in data["city"].lower():
		matching_plots.append(data)

for plot in matching_plots:
	print(f"Plot Name: {plot['plot_name']}, City: {plot['city']}, Price: {plot['price']}")