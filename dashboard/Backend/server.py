from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import time
import google.generativeai as genai
import pandas as pd
import re

# Configure the generative model
genai.configure(api_key="") # add API key here
app = Flask(__name__)
CORS(app)


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
    # sust = df["Sustainability Classification"]
    if not product_row.empty:
        return product_row.iloc[0]['Product Link'], product_row.iloc[0]['Sustainability Classification']
    else:
        return (f"Product '{product_name}' not found."+"\n~$~", 0)
    

def get_product_name(output):

    products = re.findall("<.*>", output)
    if products==[]:
      return
    plist = []
    print("Links to the products: ")
    for i in products:
        # print(i+": " )
        link, sust = get_product_link("./Backend/Merged_file.csv", i[1:-2])
        if sust == 0:
            sust = '(sustainable!)'
        else:
            sust = ''
        plist.append({'link': "https://www.croma.com" + str(link), 'name' : i[1:-1], 'sustainability': str(sust)})
    print(plist)
    return plist
    


model = genai.GenerativeModel(
  model_name="gemini-1.5-pro",
  generation_config=generation_config,
)

files = [
  upload_to_gemini("./Backend/final.csv", mime_type="text/csv"), # You may need to update the file paths
]

wait_for_files_active(files)

# Chat session setup (optional - you might have to handle session tokens differently)
chat_session = model.start_chat(
  history=[
    {
      "role": "user",
      "parts": [
        files[0],
        "You are a shopkeeper, now the user will ask you for product suggestions. Use the CSV file to find top 5 or fewer suitable products and print their name and price with a short description of each. Only the product names should be enclosed in angle brackets like <product_name>.",
      ],
    },
  ]
)

# Function to generate chatbot response
def generate_output(prompt):
    output1 = ''
    response = chat_session.send_message(prompt, stream=True)
    for chunk in response:
        if chunk.text:
            output1 += str(chunk.text)
    return output1

# Route for the chatbot interface
@app.route('/')
def index():
    return render_template('index.html')

# Route for chatbot communication
@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    prompt = data.get('message', '')
    response = generate_output(prompt)
    product_links = get_product_name(response)
    
    return jsonify({
        'response': response,
        'product_links': product_links
    })

if __name__ == '__main__':
    app.run(port=5010, debug=True)