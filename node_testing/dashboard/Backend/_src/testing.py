from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import time
import select
import json
import traceback
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the path to Chatbotcode.py from environment variable
input_py_path = os.getenv('CHATBOT_CODE_PATH', '/home/purge/genaihack_croma/node_testing/dashboard/Backend/_src/Chatbotcode.py')

# Start the Chatbotcode.py process
try:
    process = subprocess.Popen(
        ['python3', '-u', input_py_path], 
        stdin=subprocess.PIPE, 
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    logger.info(f"Started Chatbotcode.py process with PID {process.pid}")
except Exception as e:
    logger.error(f"Failed to start Chatbotcode.py process: {str(e)}")
    raise

def read_output(user_input):
    try:
        process.stdin.write(user_input + '\n')
        process.stdin.flush()

        output = []
        while True:
            line = process.stdout.readline()
            if line == '~$~\n':
                break
            if line:
                output.append(line)
            else:
                break

        logger.info(f"Received output from Chatbotcode.py: {''.join(output)}")
        return ''.join(output), ""
    except Exception as e:
        error_message = f"Error reading output: {str(e)}"
        logger.error(error_message)
        return "", error_message

@app.route('/initial-output', methods=['GET'])
def get_initial_output():
    try:
        initial_output, error_output = "Hello, I am Cromax!", ""
        logger.info(f"Initial output: {initial_output}")
        return jsonify({"response": initial_output, "error": error_output})
    except Exception as e:
        error_message = f"Error in get_initial_output: {str(e)}"
        logger.error(error_message)
        return jsonify({"response": initial_output, "error": error_output})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        print(f"Received message from frontend: {user_message}")
        
        # process.stdin.write((user_message + '\n').encode('utf-8'))
        # process.stdin.flush()

        output, error_output = read_output(user_message)
        print(f"Received response from Chatbotcode.py: {output}")
        if error_output:
            print(f"Error output: {error_output}")

        # Read map data from latlon.txt
        map_data = read_map_data()

        return jsonify({
            "response": output,
            "map_data": map_data,
            "error": error_output
        })
    except Exception as e:
        error_message = f"An error occurred: {str(e)}\n{traceback.format_exc()}"
        print(error_message)
        return jsonify({"error": error_message}), 500

def read_map_data():
    try:
        with open("/home/purge/genaihack_croma/node_testing/dashboard/Backend/_src/latlon.txt", "r") as fp:
            lines = fp.readlines()

            if len(lines) > 1:
            # Split each line using commas
                main_city = lines[0].split(',')
                city1 = lines[1].split(',')
                city2 = lines[2].split(',')
                city3 = lines[3].split(',')
                city4 = lines[4].split(',')
                city5 = lines[5].split(',')
                
                new_coordinates = {
                    'name': main_city[0],
                    'lat': float(main_city[1]),
                    'lng': float(main_city[2]),
                    'zoom': int(main_city[3]),
                    'name1': city1[0],
                    'lat1': float(city1[1]),
                    'lng1': float(city1[2]),
                    'name2': city2[0],
                    'lat2': float(city2[1]),
                    'lng2': float(city2[2]),
                    'name3': city3[0],
                    'lat3': float(city3[1]),
                    'lng3': float(city3[2]),
                    'name4': city4[0],
                    'lat4': float(city4[1]),
                    'lng4': float(city4[2]),
                    'name5': city5[0],
                    'lat5': float(city5[1]),
                    'lng5': float(city5[2]),
                }
            else:
                main_city = lines[0].split(',')
                
                new_coordinates = {
                    'name': main_city[0],
                    'lat': float(main_city[1]),
                    'lng': float(main_city[2]),
                    'zoom': int(main_city[3]),
                    'name1': main_city[0],
                    'lat1': float(main_city[1]),
                    'lng1': float(main_city[2]),
                    'name2': main_city[0],
                    'lat2': float(main_city[1]),
                    'lng2': float(main_city[2]),
                    'nam3': main_city[0],
                    'lat3': float(main_city[1]),
                    'lng3': float(main_city[2]),
                    'name4': main_city[0],
                    'lat4': float(main_city[1]),
                    'lng4': float(main_city[2]),
                    'name5': main_city[0],
                    'lat5': float(main_city[1]),
                    'lng5': float(main_city[2]),
                }

            return new_coordinates
    except FileNotFoundError:
        print("latlon.txt file not found")
        return None
    except Exception as e:
        print(f"Error reading map data: {str(e)}")
        return None

if __name__ == '__main__':
    app.run(port=5002, debug=True)