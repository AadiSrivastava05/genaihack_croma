# from flask import Flask, render_template
# from flask_socketio import SocketIO, emit

# app = Flask(__name__)
# socketio = SocketIO(app)

# @app.route('/')
# def index():
#     return render_template('map.html')

# # Function to send coordinates and zoom level to the frontend
# @socketio.on('zoom_request')
# def handle_zoom():
#     # Sample coordinates and zoom level sent to frontend
#     # You can change these dynamically based on your logic
#     new_coordinates = {'lat': 19.0760, 'lng': 72.8777, 'zoom': 10}  # Example: Mumbai
#     emit('zoom_update', new_coordinates)

# if __name__ == '__main__':
#     socketio.run(app)

from flask import Flask, render_template
from flask_socketio import SocketIO, emit



app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('map.html')  # Serve your HTML file through Flask

# Emit zoom update when requested by the frontend
@socketio.on('zoom_request')
def handle_zoom_request(data):
    fp = open("latlon.txt", 'r')
    latlon2 = fp.read().split(' ')

    # if latlon2 == ['']:
    #     pass
    #     # new_coordinates = {'lat': 20.5937, 'lng': 78.9629, 'zoom': 10}  # Example: Mumbai  
    # else:  
    print('Zoom request received')
    # Send new coordinates and zoom level to the frontend
    zoom_level = {"country": 5.0, "state": 8.0, "city": 11.0, "subcity": 13.0, "district": 15.0}
    if latlon2[2] not in zoom_level.keys():
        zoom_amount=5
    else:
        zoom_amount = zoom_level[latlon2[2]]

    new_coordinates = {'lat': float(latlon2[0]), 'lng': float(latlon2[1]), 'zoom': zoom_amount}  # Example: Mumbai
    emit('zoom_update', new_coordinates)

if __name__ == '__main__':
    socketio.run(app, debug=True)

