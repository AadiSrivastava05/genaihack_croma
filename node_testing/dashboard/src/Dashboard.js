import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { getAuth, signOut } from 'firebase/auth';
import io from 'socket.io-client';
import { MapContainer, TileLayer, Marker, Popup, useMap, Tooltip } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './styles.css';

const INITIAL_MAP_CENTER = { lat: 28.6139, lng: 77.2090, zoom: 10 }; // New Delhi coordinates
const SOCKET_URL = process.env.NODE_ENV === 'production' 
  ? 'https://yourdomain.com' 
  : 'http://localhost:5001';

// Fix Leaflet icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const Dashboard = () => {
  const auth = getAuth();
  const [mapCenter, setMapCenter] = useState(INITIAL_MAP_CENTER);
  const [chatMessages, setChatMessages] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [socket, setSocket] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [mapData, setMapData] = useState(null);
  const mapRef = useRef(null);
  
  const location = useLocation();

  useEffect(() => {
    const newSocket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      timeout: 10000,
    });

    newSocket.on('connect', () => {
      console.log('Connected to server');
    });

    newSocket.on('connect_error', (error) => {
      setError('Failed to connect to the server. Please try again later.');
    });

    newSocket.on('disconnect', (reason) => {
      console.log('Disconnected:', reason);
    });

    newSocket.on('initial_message', (data) => {
      setChatMessages([{ sender: 'Cromax', message: data.response + "\n" }]);
    });

    newSocket.on('chatbot_response', (data) => {
      setChatMessages(prevMessages => [...prevMessages, { sender: 'Cromax', message: data.response }]);
      if (data.mapData) {
        setMapData(data.mapData);
        setMapCenter({
          lat: data.mapData.lat,
          lng: data.mapData.lng,
          zoom: data.mapData.zoom
        });
      }
    });

    newSocket.on('chatbot_error', (errorMessage) => {
      setError(errorMessage);
      setIsLoading(false);
    });

    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  useEffect(() => {
    if (mapRef.current && mapCenter) {
      mapRef.current.setView([mapCenter.lat, mapCenter.lng], mapCenter.zoom);
    }
  }, [mapCenter]);

  const handleLogout = useCallback(() => {
    signOut(auth).then(() => {
      window.location.href = '/login';
    }).catch((error) => {
      setError('Failed to log out. Please try again.');
    });
  }, [auth]);

  const handleSendMessage = useCallback(() => {
    if (userInput.trim() === '') return;

    setIsLoading(true);
    setError(null);

    setChatMessages(prevMessages => [...prevMessages, { sender: 'You', message: userInput + "\n" }]);
    
    socket.emit('chatbot_message', userInput);

    setUserInput('');
    setIsLoading(false);
  }, [userInput, socket]);

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const showDashboardContent = location.pathname === '/home';

  const renderMessage = (message) => {
    return message.split('\n').map((line, index) => (
      <React.Fragment key={index}>
        {line}
        <br />
      </React.Fragment>
    ));
  };

  const MapComponent = () => {
    const map = useMap();
    mapRef.current = map;

    useEffect(() => {
      if (mapCenter) {
        map.setView([mapCenter.lat, mapCenter.lng], mapCenter.zoom);
      }
    }, [mapCenter, map]);

    return null;
  };

  return (
    <div className="dashboard-container">
      <div className="header">
        <div className="header-icons">
          <button className="icon-button"><i className="fas fa-envelope"></i></button>
          <button className="icon-button"><i className="fas fa-user"></i></button>
        </div>
      </div>

      <div className="sidebar">
        <nav className="menu">
          <Link to="/home" className="menu-item">
            <i className="fas fa-store"></i> Set up a store
          </Link>
          <Link to="/home/recommended" className="menu-item">
            <i className="fas fa-map-marker-alt"></i> Recommended
          </Link>
          <Link to="/home/forecast-demand" className="menu-item">
            <i className="fas fa-chart-line"></i> Forecast Demand
          </Link>
          <Link to="/home/how-to-use" className="menu-item">
            <i className="fas fa-question-circle"></i> How to use
          </Link>
          <Link to="/home/barchart" className="menu-item">
            <i className="fas fa-question-circle"></i> Bar Chart
          </Link>
        </nav>

        <div className="bottom-menu">
          <Link to="/home/settings" className="menu-item">
            <i className="fas fa-cog"></i> Settings
          </Link>
          <button className="menu-item" onClick={handleLogout}>
            <i className="fas fa-sign-out-alt"></i> Logout
          </button>
        </div>
      </div>

      <div className="main-content">
        {showDashboardContent && (
          <>
            <div className="chat-assistant">
              <div className="chat-header">
                <h3>Chat Assistant</h3>
              </div>
              <div className="chat-search">
                <input 
                  type="text" 
                  placeholder="Search in chat"
                  value={searchQuery}
                  onChange={handleSearchChange}
                />
                <button><i className="fas fa-search"></i></button>
              </div>
              <div className="chat-messages">
                {chatMessages.map((msg, index) => (
                  <div key={index} className={`message ${msg.sender.toLowerCase()}`}>
                    <strong>{msg.sender}:</strong> {renderMessage(msg.message)}
                  </div>
                ))}
                {error && (
                  <div className="error-message">
                    {error}
                    <button onClick={() => handleSendMessage()}>Retry</button>
                  </div>
                )}
              </div>
              <div className="chat-input">
                <input
                  type="text"
                  value={userInput}
                  onChange={(e) => setUserInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  placeholder="Ask a question"
                  disabled={isLoading}
                />
                <button onClick={handleSendMessage} disabled={isLoading}>
                  <i className="fas fa-paper-plane"></i>
                </button>
              </div>
            </div>

            <div className="map">
              <MapContainer center={[mapCenter.lat, mapCenter.lng]} zoom={mapCenter.zoom} style={{ height: '100%', width: '100%' }}>
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
                <MapComponent />
                {mapData && (
                  <>
                  <Marker position={[mapData.lat, mapData.lng]}>
                    <Tooltip direction="top" offset={[0, -20]} opacity={1} permanent={false}>
                      {mapData.name}
                    </Tooltip>
                  </Marker>
                  <Marker position={[mapData.lat5, mapData.lng5]}>
                    <Tooltip direction="top" offset={[0, -20]} opacity={1} permanent={false}>
                      {mapData.name5}
                    </Tooltip>
                  </Marker>
                  <Marker position={[mapData.lat4, mapData.lng4]}>
                    <Tooltip direction="top" offset={[0, -20]} opacity={1} permanent={false}>
                      {mapData.name4}
                    </Tooltip>
                  </Marker>
                  <Marker position={[mapData.lat3, mapData.lng3]}>
                    <Tooltip direction="top" offset={[0, -20]} opacity={1} permanent={false}>
                      {mapData.name3}
                    </Tooltip>
                  </Marker>
                  <Marker position={[mapData.lat2, mapData.lng2]}>
                    <Tooltip direction="top" offset={[0, -20]} opacity={1} permanent={false}>
                      {mapData.name2}
                    </Tooltip>
                  </Marker>
                  <Marker position={[mapData.lat1, mapData.lng1]}>
                    <Tooltip direction="top" offset={[0, -20]} opacity={1} permanent={false}>
                      {mapData.name1}
                    </Tooltip>
                  </Marker>
                </>

                )}
              </MapContainer>
            </div>
          </>
        )}

        <Outlet />
      </div>
    </div>
  );
};

export default Dashboard;