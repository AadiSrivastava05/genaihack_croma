import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai

API_KEY = "AIzaSyBW4NnpsbAjXbOfZ7r16x9NicsH00X00mA"  #yo dont leak my api key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

prompt='''
1.You will be provided some text.
2. You need to extract three data point from the text which is, the location of the shop user wants to set in, the maximum price and the minimum price they are willing to pay
3. Note that if any of them is missing from the user input, then give "NULL".
4. The output should be <location>, <maximum price>, <minimum price>

E.g. UserText = "I want to open a barber shop in Hyderabad. I have to buy a plot, in the rage 50k to 100k INR"
Output = "Hyderabad, 100000, 50000"
'''

query = "I want a layout for an outlet I'm planning to open in Nagpur. What will the best prospects be for it? The range I am looking for is 50k to 100k"
response = model.generate_content(prompt+query +'"')
responseList = str(response.text).split(', ')
search_location, maximum_price, minimum_price = responseList[0], responseList[1], responseList[2]


cred = credentials.Certificate("apikey.json")
# firebase_admin.initialize_app(cred)
db = firestore.client()

plots_ref = db.collection('plots')
query = plots_ref.where('price', '>=', minimum_price).where('price', '<=', maximum_price).stream()

matching_plots = []
for doc in query:
    plot_data = doc.to_dict()
    if search_location.lower() in data["city"].lower():
      matching_plots.append(plot_data)
    
# Print the matching plots
for plot in matching_plots:
    print(f"Plot Name: {plot_data['plot_name']}, City: {plot_data['city']}, Price: {plot_data['price']}")