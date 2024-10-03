import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import re
from supabase import create_client, Client

API_KEY = ""  												# add api key here
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

def detect_intent_and_location(user_prompt: str):

	response = model.generate_content(f"Determine if this user is asking for warehouse/godown/plot details in a location and if they are then extract the location. Respond with 'Intent: <intent>, Location: <location>' format. The intent can be either a 'yes' or a 'no' depending on whether the user wants to see the warehouse details in a specific location or not, respectively. This is the prompt: {user_prompt}")

	output = response.text
	result = output.strip().split(",")
	intent = result[0].split(":")[1].strip()
	location = result[1].split(":")[1].strip()
	
	return intent, location

'''
def extract_location(user_prompt: str):
	response = chat.send_message(f"Extract location from this prompt: {user_prompt}. The output should be the location and nothing else", stream=True, safety_settings = {
			HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE, 
			HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
			HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
			HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
			})
	output = ''
	for chunk in response:
		if chunk.text:
			output += chunk.text  
	return output
'''

def query_supabase(location: str):
	url: str = "https://ajkgqdvxmueqxtuvcjho.supabase.co"
	key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFqa2dxZHZ4bXVlcXh0dXZjamhvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjU1NTYyOTcsImV4cCI6MjA0MTEzMjI5N30.cwmfECvEYqu6FZXRFqcTw1zD-H6NoHkG_etfqPZ-hDw"
	supabase: Client = create_client(url, key)
	search_location = location
	response = supabase.table("PlotData").select("*").ilike("city", f"*{search_location}*").execute()
	plots = []
	for plot in response.data:
	    plots.append(f"Name of owner: {plot['owner_name']}, City: {plot['city']}, Price: {plot['price']}, link: {plot['link']} \n")
	return len(plots), plots


while True:
	print("enter >>> ")
	prompt = input()
	intent ,location = detect_intent_and_location(prompt)
	print(intent, location)
	if intent == 'yes':
		num, plots = query_supabase(location)
		for plot in plots:
			print(plot)
