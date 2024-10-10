const express = require('express');
const http = require('http');
const { Server } = require("socket.io");
const cors = require('cors');
const path = require('path');

const app = express();
app.use(cors());

const server = http.createServer(app);
const io = new Server(server);

// Serve static files from the React app
app.use(express.static(path.join(__dirname, 'client/build')));

io.on('connection', (socket) => {
    console.log('A user connected');

    socket.on('chatbot_message', async (message) => {
        console.log('Message received:', message);

        try {
            const fetch = (await import('node-fetch')).default;
            const flaskResponse = await fetch('http://localhost:5010/ask', {
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
                product_links: data.product_links
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

// The "catchall" handler: for any request that doesn't
// match one above, send back React's index.html file.
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'client/build', 'index.html'));
});

const PORT = process.env.PORT || 5005;
server.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
    console.log(`WebSocket server is ready`);
});