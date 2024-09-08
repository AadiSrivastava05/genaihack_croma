import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import re
from supabase import create_client, Client

API_KEY = "AIzaSyDgtJZg8o9fYUlJm9xeYNkRwzQ2nbZiHQI"  #yo dont leak my api key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])
promptFlag = True

prompt_init = '''
0. You are Deymax, an AI-model made to help users set up new shops. You help them gain an understanding of what type of shop they should open in which cities, who the competitors can be, what the demands are for which products and more. You will follow the below guidelines strictly.
1. You will be provided some text in the next prompt given by the user.
2. You need to extract two data points from the text which are, the location of the shop user wants to set in, and the domain of the shop(as in what kind of products, for example tech/groceries)
3. If the user didnt provide the location and domain ask them in a follow up prompt.
4. Now dive deeper in the location by suggesting the top 5 states/regions/districts/subcities/cities inside the location with the highest demand for the products of the selected domain. Make sure the 5 regions are inside the location and are sorted according to highest demand.
5. The suggestion output should be of the form: "Top 5 regions with the highest demand for {domain} products inside {location} are: {list of regions in bullet points} Please let me know which one do you want to explore. You can also respond with a region not inside this list as per your preference.". If there are less than 5 regions inside, then apologize for not being able to find more, and carry on.
6. Output the 5 regions in csv format first csv should include four things, location_name, location_lattitude, location_longitude, demand_score (as a percentage). It should start with "```csv" and end it with "```". All the data should be in the same line, and seperate two different elements using a newline. 
7. Then give the region names and add a little snippet explaining why this region can be better than the others.
6. Just dive deeper till we reach a district level or a subcity level or a similar.
8. Never deviate from the topic. If the users asks things which are irrelevant to the above, then keep making the above prompts, and apologize for not being able to help with the particular request, cause you can only focus on the above.
9. Don't give extra info, unless the user specifically asks for it. Make sure you don't deviate from the above ever.
10. If the user, in between prompts wants to change the location or the domain, then that is allowed. Suggest accordingly, help them with that specific.
11. Reply to the user's chats effectively.
12. If you've understood everything. Start with "Hello! I am Deymax".
'''

def detect_intent_and_location(user_prompt: str):

	response = model.generate_content(f"Determine if this user is explicitly asking for warehouse/godown details in a location and if they are, then extract the location. Respond with 'Intent: <intent>, Location: <location>' format. The intent can be either a 'yes' or a 'no' depending on whether the user wants to see the warehouse details in a specific location or not, respectively. If they want this information they will specifically mention it with emphasis.This is the prompt: '{user_prompt}'.")
	output2 = response.text
	result = output2.strip().split(",")
	intent = result[0].split(":")[1].strip()
	location = result[1].split(":")[1].strip()
	
	return intent, location

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

def generate_output(prompt):
	output1 = ''
	response = chat.send_message(prompt, stream=True, safety_settings = {
				HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE, 
				HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
				HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
				HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
				})
	for chunk in response:
		if chunk.text:
			output1 += str(chunk.text)
	return output1

while True:
	try:
		if promptFlag == True:
			prompt = prompt_init
			promptFlag = False
			output = generate_output(prompt)
			print(output)
		else:
			prompt = input()
			intent, location = detect_intent_and_location(prompt)
			if intent == 'yes':
				num, plots = query_supabase(location)
				for plot in plots:
					print(plot.strip())
				prompt = f"I am finalising the location as {location}"

			output = generate_output(prompt)

			csvData = re.findall("```csv.*```", output, re.DOTALL)
			if csvData != []:
				latLonData = csvData[0].split('\n')[1:-1]
				latLonData2 = csvData[0]
				print(re.sub(latLonData2,' ',output, re.DOTALL))
				latLonData = latLonData[1].split(',')
				fp = open("latlon.txt", 'w')
				fp.write(f"{float(latLonData[1])} {float(latLonData[2])}")	
				fp.close()
			else:
			 	print(output)

	except Exception as E:
		print("There was an issue in processing your last prompt, please rephase it")
		print(E)