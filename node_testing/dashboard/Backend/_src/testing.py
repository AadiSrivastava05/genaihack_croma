from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import time
import select
import json
import traceback

app = Flask(__name__)
CORS(app)

input_py_path = 'C:\\Users\\Marsman\\genaihack_croma-main\\node_testing\\dashboard\\Backend\\_src\\Chatbotcode.py'

process = subprocess.Popen(
    ['python','-u', input_py_path], 
    stdin=subprocess.PIPE, 
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    # bufsize=0  # Unbuffered
)


import subprocess

# def read_output(user_input):
#     print("here1")
#     # Write the user input to the process's stdin and get the output
#     process.stdin.write(user_input+'\n')  # Send input followed by a newline (if needed by the process)
#     # process.stdin.flush()  # Ensure all input is sent
#     print("here2")

#     # Read the output from stdout
#     output = process.stdout.read()
#     print("here3")

#     error = process.stderr.read()
#     print("here4")
#     # Optionally read the error (if needed)

#     return output, error


def read_output(user_input):
    # print("here1")
    # Write the user input to the process's stdin and flush
    process.stdin.write(user_input + '\n')
    process.stdin.flush()  # Ensure the input is sent immediately
    # print("here2")

    # Collect multi-line output from the process
    output = []
    f = 0
    # line = process.stdout.readline() # Read one line from stdout
    # output.append(line)
    while True:
        # print("hi")
        line = process.stdout.readline() # Read one line from stdout
        
        # process.stdout.readline()
        # print("hey")
        if line == '~$~\n':  # End if process terminates
            break
        if line:  # If there's a line of output, append it
            # print("yo")
            # print(line)
            output.append(line)
        else:
            break  # No more output to read for now

    print(''.join(output))

    # Optionally read the error (if any)
    error = "process.stderr.readline()"  # You can also loop through stderr if needed
    print("here4", error)

    return ''.join(output), error




@app.route('/initial-output', methods=['GET'])
def get_initial_output():
    initial_output, error_output = "Hello, I am Cromax!\n", ""
    print(f"Initial output from input.py: {initial_output}")
    if error_output:
        print(f"Error output: {error_output}")
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
        with open("C:\\Users\\Marsman\\genaihack_croma-main\\node_testing\\dashboard\\Backend\\_src\\latlon.txt", "r") as fp:
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
                    'name': (main_city[0]),
                    'lat': float(main_city[1]),
                    'lng': float(main_city[2]),
                    'zoom': int(main_city[3]),
                    'name1': (city1[0]),
                    'lat1': float(city1[1]),
                    'lng1': float(city1[2]),
                    'name2': (city2[0]),
                    'lat2': float(city2[1]),
                    'lng2': float(city2[2]),
                    'name3': (city3[0]),
                    'lat3': float(city3[1]),
                    'lng3': float(city3[2]),
                    'name4': (city4[0]),
                    'lat4': float(city4[1]),
                    'lng4': float(city4[2]),
                    'name5': (city5[0]),
                    'lat5': float(city5[1]),
                    'lng5': float(city5[2]),
                }
            else:
                main_city = lines[0].split(',')
                
                new_coordinates = {
                    'name': (main_city[0]),
                    'lat': float(main_city[1]),
                    'lng': float(main_city[2]),
                    'zoom': int(main_city[3]),
                    'name1': (main_city[0]),
                    'lat1': float(main_city[1]),
                    'lng1': float(main_city[2]),
                    'name2': (main_city[0]),
                    'lat2': float(main_city[1]),
                    'lng2': float(main_city[2]),
                    'name3': (main_city[0]),
                    'lat3': float(main_city[1]),
                    'lng3': float(main_city[2]),
                    'name4': (main_city[0]),
                    'lat4': float(main_city[1]),
                    'lng4': float(main_city[2]),
                    'name5': (main_city[0]),
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