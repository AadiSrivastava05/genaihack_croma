import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import re
from supabase import create_client, Client

API_KEY = "AIzaSyDgtJZg8o9fYUlJm9xeYNkRwzQ2nbZiHQI"  #yo dont leak my api key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])
# promptFlag = True

def get_intent(prompt):
	response = model.generate_content(f"Determine if this user is asking for a product reccomendation. Respond with 'Intent: <intent>'. The intent should either be 'yes' or a 'no' depending on whether the user wants product reccomendations or not. This is the prompt: '{prompt}'.")
	output2 = response.text
	# result = output2.strip().split(",")
	intent = output2.split(":")[1].strip()
	# location = result[1].split(":")[1].strip()
	
	return intent

prompt = input()
response = model.generate_content(prompt)
# intent = get_intent(prompt)
print(response.text)

