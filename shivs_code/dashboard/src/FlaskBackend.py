from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import subprocess
import os
from flask_cors import CORS
import threading
import queue
import signal
import json
import time

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

chatbot_process = None
input_queue = queue.Queue()
output_queue = queue.Queue()
stop_event = threading.Event()

def run_chatbot():
    global chatbot_process
    while not stop_event.is_set():
        try:
            print("Starting chatbot process...")
            chatbot_process = subprocess.Popen(
                ['python', 'C:/Users/Marsman/genaihack_croma-main/shivs_code/Chatbotcode.py'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8'
            )
            print(f"Chatbot process started with PID: {chatbot_process.pid}")

            # Wait for initialization message
            init_message = chatbot_process.stdout.readline().strip()
            print(f"Chatbot initialization: {init_message}")

            while not stop_event.is_set() and chatbot_process.poll() is None:
                if not input_queue.empty():
                    try:
                        user_input = input_queue.get(timeout=1)
                        print(f"Sending user input to chatbot: {user_input}")
                        chatbot_process.stdin.write(f"{user_input}\n")
                        chatbot_process.stdin.flush()
                    except BrokenPipeError:
                        print("BrokenPipeError: Chatbot process has terminated")
                        break

                try:
                    output = chatbot_process.stdout.readline().strip()
                    if output:
                        print(f"Raw chatbot output: {output}")
                        output_queue.put(output)
                except Exception as e:
                    print(f"Error reading from Chatbot: {e}")

            if chatbot_process.poll() is not None:
                print(f"Chatbot process terminated unexpectedly. Return code: {chatbot_process.returncode}")
                stderr_output = chatbot_process.stderr.read()
                if stderr_output:
                    print(f"Chatbot process stderr: {stderr_output}")
                print("Restarting chatbot process...")

        except Exception as e:
            print(f"Error in run_chatbot: {e}")
        finally:
            if chatbot_process:
                print(f"Terminating chatbot process with PID: {chatbot_process.pid}")
                chatbot_process.terminate()
                try:
                    chatbot_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print("Chatbot process did not terminate, forcing kill...")
                    chatbot_process.kill()
                print("Chatbot process terminated")

def start_chatbot():
    threading.Thread(target=run_chatbot, daemon=True).start()

def stop_chatbot():
    global chatbot_process
    stop_event.set()
    if chatbot_process:
        chatbot_process.terminate()
        try:
            chatbot_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            chatbot_process.kill()
    print("Chatbot process stopped")

@app.route('/')
def index():
    return "Flask backend is running"

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        print("Received POST request to /predict")
        data = request.json
        print(f"Received data: {data}")
        
        if not data or 'message' not in data:
            return jsonify({"error": "Invalid request data"}), 400
        
        user_input = data['message']
        print(f"User input: {user_input}")
        
        if chatbot_process is None or chatbot_process.poll() is not None:
            print("Chatbot process not running. Starting...")
            start_chatbot()
            time.sleep(5)  # Increased wait time for process to start

        print("Putting user input into queue")
        input_queue.put(user_input)
        
        print("Waiting for chatbot response...")
        try:
            output = output_queue.get(timeout=60)  # Increased timeout to 60 seconds
            print(f"Raw chatbot output: {output}")
            
            try:
                output_data = json.loads(output)
            except json.JSONDecodeError as e:
                print(f"Failed to parse chatbot output as JSON: {output}")
                return jsonify({"error": "Invalid response from chatbot"}), 500
            
        except queue.Empty:
            print("Timeout waiting for Chatbot response")
            return jsonify({"error": "Timeout waiting for Chatbot response"}), 504
        
        if "error" in output_data:
            print(f"Chatbot error: {output_data['error']}")
            return jsonify({"error": output_data['error']}), 500
        
        response_data = {
            "response": output_data.get("response", ""),
            "location": output_data.get("coordinates", [])[-1] if output_data.get("coordinates") else None,
            "top_cities": output_data.get("top_cities", [])
        }
        
        print(f"Sending response: {response_data}")
        
        # Emit the response via WebSocket
        socketio.emit('chatbot_response', response_data)
        
        return jsonify(response_data)
    
    except Exception as e:
        print(f"Unexpected error in /predict: {str(e)}")
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    

def signal_handler(signum, frame):
    print("Received termination signal. Shutting down gracefully...")
    stop_chatbot()
    os._exit(0)

if __name__ == '__main__':
    print("Starting Flask server")
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    start_chatbot()
    try:
        socketio.run(app, debug=True, port=5002)
    finally:
        stop_chatbot()