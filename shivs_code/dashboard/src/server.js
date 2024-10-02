const express = require('express');
const http = require('http');
const { Server } = require("socket.io");
const cors = require('cors');
const fetch = require('node-fetch');

const app = express();
app.use(cors());

const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "http://localhost:3001",
    methods: ["GET", "POST"]
  },
  transports: ['websocket', 'polling']
});

io.on('connection', (socket) => {
  console.log('A user connected');
  console.log('Socket ID:', socket.id);

  socket.on('disconnect', (reason) => {
    console.log('User disconnected:', reason);
  });

  socket.on('error', (error) => {
    console.error('Socket error:', error);
  });

  socket.on('chatbot_message', async (message) => {
    console.log('Message received:', message);

    // Process and fetch the response from Flask backend
    try {
      const flaskResponse = await fetch('http://localhost:5002/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
      });
      
      if (!flaskResponse.ok) {
        throw new Error(`HTTP error! status: ${flaskResponse.status}`);
      }
      
      const data = await flaskResponse.json();
      console.log('Flask response:', data);
      
      socket.emit('chatbot_response', data.response);
      
      if (data.location) {
        socket.emit('location_update', data.location);
      }
    } catch (error) {
      console.error('Error fetching chatbot response:', error);
      socket.emit('chatbot_error', 'An error occurred while processing your request');
    }
  });
});

const PORT = process.env.PORT || 5001;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`WebSocket server is ready`);
});

server.on('error', (error) => {
  console.error('Server error:', error);
});

server.on('upgrade', (request, socket, head) => {
  console.log('Upgrade request received');
});



// const express = require('express');
// const http = require('http');
// const { Server } = require("socket.io");
// const cors = require('cors');
// const fetch = require('node-fetch');

// const app = express();
// app.use(cors());
// app.use(express.json());

// const server = http.createServer(app);
// const io = new Server(server, {
//   cors: {
//     origin: "http://localhost:3001",
//     methods: ["GET", "POST"]
//   },
//   transports: ['websocket', 'polling']
// });

// io.on('connection', (socket) => {
//   console.log('A user connected');
//   console.log('Socket ID:', socket.id);

//   socket.on('disconnect', (reason) => {
//     console.log('User disconnected:', reason);
//   });

//   socket.on('error', (error) => {
//     console.error('Socket error:', error);
//   });

//   socket.on('chatbot_message', async (message) => {
//     console.log('Message received:', message);

//     try {
//       const flaskResponse = await fetch('http://localhost:5002/predict', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ message: message })
//       });

//       if (!flaskResponse.ok) {
//         throw new Error(`HTTP error! status: ${flaskResponse.status}`);
//       }

//       const data = await flaskResponse.json();
//       console.log('Flask response:', data);

//       socket.emit('chatbot_response', data.response);

//       if (data.location) {
//         socket.emit('location_update', data.location);
//       }

//       if (data.top_cities) {
//         socket.emit('top_cities_update', data.top_cities);
//       }
//     } catch (error) {
//       console.error('Error fetching chatbot response:', error);
//       socket.emit('chatbot_error', 'An error occurred while processing your request');
//     }
//   });
// });

// const PORT = process.env.PORT || 5001;
// server.listen(PORT, () => {
//   console.log(`Server running on port ${PORT}`);
//   console.log(`WebSocket server is ready`);
// });
