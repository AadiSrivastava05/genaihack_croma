import os
import time
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import pandas as pd
import re

genai.configure(api_key="") # add API key here

def upload_to_gemini(path, mime_type=None):
  """Uploads the given file to Gemini.

  See https://ai.google.dev/gemini-api/docs/prompting_with_media
  """
  file = genai.upload_file(path, mime_type=mime_type)
  return file

def wait_for_files_active(files):
  """Waits for the given files to be active.

  Some files uploaded to the Gemini API need to be processed before they can be
  used as prompt inputs. The status can be seen by querying the file's "state"
  field.

  This implementation uses a simple blocking polling loop. Production code
  should probably employ a more sophisticated approach.
  """
  for name in (file.name for file in files):
    file = genai.get_file(name)
    while file.state.name == "PROCESSING":
      print(".", end="", flush=True)
      time.sleep(10)
      file = genai.get_file(name)
    if file.state.name != "ACTIVE":
      raise Exception(f"File {file.name} failed to process")
  
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

def get_product_link(csv_file_path, product_name):

    try:
        df = pd.read_csv(csv_file_path)
    except FileNotFoundError:
        return "CSV file not found."

    product_row = df[df['Product Name'].str.contains(product_name.strip(), case=False, na=False, regex=False)]

    if not product_row.empty:
        return product_row.iloc[0]['Product Link']
    else:
        return f"Product '{product_name}' not found."+"\n~$~"
    

def get_product_name(output):
    products = re.findall("<.*>", output)
    if products==[]:
      return
    print("Links to the products: ")
    for i in products:
        print(i+": " )
        print("https://www.croma.com"+get_product_link("./Merged_file.csv", i[1:-2]))
    print("~$~")


model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
)

files = [
  upload_to_gemini("./final.csv", mime_type="text/csv"), # You may need to update the file paths
]

wait_for_files_active(files)

chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        files[0],
        "You are a shopkeeper, now the user will ask you for product suggestions. use the csv file to find top 5 or less suitable products and print their name and price with a short description of each. Only the product names should be enclosed in angle brackets like <product_name>.",
      ],
    },
    {
      "role": "model",
      "parts": [
        "Okay, I'm ready to help customers find the perfect products. Ask away! I have a complete list of products and their prices from my shop. 😊  Just tell me what you're looking for! \n",
      ],
    },
  ]
)
time.sleep(60)

def generate_output(prompt):
	output1 = ''
	response = chat_session.send_message(prompt, stream=True, safety_settings = {
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
    prompt = input()
    response = generate_output(prompt)
    time.sleep(20)
    print(response+"\n~$~")
    get_product_name(response)
