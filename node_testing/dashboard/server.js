const express = require('express');
const http = require('http');
const { Server } = require("socket.io");
const cors = require('cors');

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

io.on('connection', async (socket) => {
  console.log('A user connected');

  try {
    const fetch = (await import('node-fetch')).default;
    const initialResponse = await fetch('http://localhost:5002/initial-output');
    
    if (!initialResponse.ok) {
      throw new Error(`HTTP error! status: ${initialResponse.status}`);
    }
    
    const initialData = await initialResponse.json();
    console.log('Initial Flask response:', initialData);
    
    socket.emit('initial_message', initialData);
  } catch (error) {
    console.error('Error fetching initial message:', error);
    socket.emit('chatbot_error', 'Failed to fetch initial message');
  }
  
  socket.on('chatbot_message', async (message) => {
    console.log('Message received:', message);
  
    try {
      const fetch = (await import('node-fetch')).default;
      const flaskResponse = await fetch('http://localhost:5002/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
      });
      
      if (!flaskResponse.ok) {
        const errorText = await flaskResponse.text();
        throw new Error(`HTTP error! status: ${flaskResponse.status}, message: ${errorText}`);
      }
      
      const data = await flaskResponse.json();
      console.log('Flask response:', data);
      
      socket.emit('chatbot_response', {
        response: data.response,
        mapData: data.map_data
      });
    } catch (error) {
      console.error('Error fetching chatbot response:', error);
      socket.emit('chatbot_error', `An error occurred while processing your request: ${error.message}`);
    }
  });

  socket.on('disconnect', (reason) => {
    console.log('User disconnected:', reason);
  });
});

const PORT = process.env.PORT || 5001;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`WebSocket server is ready`);
});
