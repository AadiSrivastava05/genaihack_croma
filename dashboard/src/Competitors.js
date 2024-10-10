import React, { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

const CompetitorsMap = () => {
  const [cityName, setCityName] = useState('');
  const [numberOfCompetitors, setNumberOfCompetitors] = useState('');
  const [error, setError] = useState('');
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const socket = useRef(null);

  useEffect(() => {
    console.log('Component mounted');

    if (!mapInstanceRef.current && mapRef.current) {
      console.log('Initializing map');
      mapInstanceRef.current = L.map(mapRef.current).setView([0, 0], 2);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
      }).addTo(mapInstanceRef.current);
      console.log('Map initialized');
    }

    console.log('Initializing Socket.IO connection');
    socket.current = io('http://localhost:5011', {
      transports: ['websocket'],
      cors: {
        origin: 'http://localhost:3000',
        methods: ["GET", "POST"]
      }
    });

    socket.current.on('connect', () => {
      console.log('Socket.IO connected');
    });

    socket.current.on('connect_error', (error) => {
      console.error('Socket.IO connection error:', error);
      setError('Unable to connect to the server. Please try again later.');
    });

    socket.current.on('competitor_data_update', (data) => {
      console.log('Received competitor data:', data);
      updateMap(data);
    });

    socket.current.on('error', (data) => {
      console.error('Received error from server:', data);
      setError(data.message || 'An error occurred. Please try again.');
    });

    return () => {
      if (socket.current) {
        console.log('Disconnecting Socket.IO');
        socket.current.disconnect();
      }
      if (mapInstanceRef.current) {
        console.log('Removing map');
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  const updateMap = (data) => {
    console.log('Updating map with data:', data);
    if (mapInstanceRef.current) {
      mapInstanceRef.current.eachLayer((layer) => {
        if (layer instanceof L.Marker) {
          mapInstanceRef.current.removeLayer(layer);
        }
      });

      const markers = [];
      for (let i = 0; i < Object.keys(data).length / 2 - 1; i++) {
        const lat = data[`lat${i}`];
        const lon = data[`lon${i}`];
        console.log(`Adding marker at: ${lat}, ${lon}`);
        const marker = L.marker([lat, lon]).addTo(mapInstanceRef.current);
        markers.push(marker);
      }

      const group = L.featureGroup(markers);
      mapInstanceRef.current.fitBounds(group.getBounds());

      console.log(`Setting view to: ${data.toZoomlat}, ${data.toZoomlon}`);
      mapInstanceRef.current.setView([data.toZoomlat, data.toZoomlon], 12);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    console.log(`Submitting search for ${cityName} with ${numberOfCompetitors} competitors`);
    if (socket.current) {
      socket.current.emit('competitor_data_request', {
        city_name: cityName,
        n: numberOfCompetitors
      });
    } else {
      setError('Socket is not initialized. Please try again.');
    }
  };

  return (
    <div>
      <div className="mb-4 p-4 bg-gray-100">
        <h2 className="text-xl font-bold mb-2">Search Competitors</h2>
        <form onSubmit={handleSubmit} className="flex flex-col space-y-2">
          <input
            type="text"
            value={cityName}
            onChange={(e) => setCityName(e.target.value)}
            placeholder="City Name"
            className="p-2 border rounded"
          />
          <input
            type="number"
            value={numberOfCompetitors}
            onChange={(e) => setNumberOfCompetitors(e.target.value)}
            placeholder="Number of Competitors"
            className="p-2 border rounded"
          />
          <button type="submit" className="p-2 bg-blue-500 text-white rounded">
            Search
          </button>
        </form>
        {error && <p className="text-red-500 mt-2">{error}</p>}
      </div>
      <div ref={mapRef} style={{ width: '100%', height: '500px' }} />
    </div>
  );
};

export default CompetitorsMap;