from flask_socketio import SocketIO, emit
import subprocess
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
from flask import send_from_directory
import os

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/predict', methods=['POST'])
def process_prompt():
    user_input = request.json.get('prompt')
    print(f"Received message from frontend: {user_input}")

    try:
        result = subprocess.run(
            ['python3', '/Users/shivbanafar/Desktop/Projects/genai-croma-v1/Backend/_src/Chatbotcode.py', user_input], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        output = result.stdout

    except Exception as e:
        output = f"Error running script: {str(e)}"
    print(f"Received response from Chatbotcode.py: {output}")

    return jsonify({'result': output})

@socketio.on('zoom_request')
def handle_zoom_request(data):
    # Open the file and parse it for zoom information
    try:
        with open('latlon.txt', 'r') as fp:
            fp = open("latlon.txt", 'r')
            data = fp.read().split('\n')
            mainCity = data[0].split(',')

            city1 = data[1].split(',')
            city2 = data[2].split(',')
            city3 = data[3].split(',')
            city4 = data[4].split(',')
            city5 = data[5].split(',')

            print("zoom request recieved")

        new_coordinates = {'lat': float(mainCity[0]), 'lng': float(mainCity[1]), 'zoom': int(mainCity[2]), 'lat1': float(city1[0]), 'lng1': float(city1[1]),'lat2': float(city2[0]), 'lng2': float(city2[1]),'lat3': float(city3[0]), 'lng3': float(city3[1]),'lat4': float(city4[0]), 'lng4': float(city4[1]),'lat5': float(city5[0]), 'lng5': float(city5[1]),}
        emit('zoom_update', new_coordinates)
    except Exception as e:
        print('zoom_update', {'error': f"Error reading file: {str(e)}"})
        

if __name__ == '__main__':
    socketio.run(app,port = 5002,debug = True)