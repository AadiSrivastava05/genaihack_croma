import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { getAuth, signOut } from 'firebase/auth';
import io from 'socket.io-client';
import './styles.css';

const INITIAL_MAP_CENTER = { lat: 20.5937, lng: 78.9629, zoom: 5 };
const SOCKET_URL = 'http://localhost:5001';
const API_URL = 'http://localhost:5002/predict';

const Dashboard = () => {
  const navigate = useNavigate();
  const auth = getAuth();
  const [mapCenter, setMapCenter] = useState(INITIAL_MAP_CENTER);
  const [chatOutput, setChatOutput] = useState('');
  const [userInput, setUserInput] = useState('');
  const [socket, setSocket] = useState(null);
  const [plots, setPlots] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const newSocket = io(SOCKET_URL, {
      transports: ['websocket', 'polling'],
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      timeout: 10000,
    });

    newSocket.on('connect', () => {
      console.log('Connected to server');
      console.log('Socket ID:', newSocket.id);
    });

    newSocket.on('connect_error', (error) => {
      console.error('Connection error:', error);
      setError('Failed to connect to the server. Please try again later.');
    });

    newSocket.on('disconnect', (reason) => {
      console.log('Disconnected:', reason);
    });

    newSocket.on('chatbot_response', (data) => {
      console.log('Received chatbot response:', data);
      setChatOutput(prevOutput => `${prevOutput}\nDeymax: ${data.response}`);
      if (data.location) {
        setMapCenter(prevCenter => ({
          ...prevCenter,
          ...data.location,
          zoom: 17
        }));
      }
      if (data.top_cities && data.top_cities.length > 0) {
        setPlots(data.top_cities);
      }
    });

    setSocket(newSocket);

    return () => {
      console.log('Cleaning up socket connection');
      newSocket.close();
    };
  }, []);

  const handleLogout = useCallback(() => {
    signOut(auth).then(() => {
      navigate('/login');
    }).catch((error) => {
      console.error('Logout error:', error);
      setError('Failed to log out. Please try again.');
    });
  }, [auth, navigate]);

  const handleSendMessage = useCallback(async () => {
    if (userInput.trim() === '') return;
  
    setIsLoading(true);
    setError(null);
  
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 65000); // 65 seconds timeout
  
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userInput }),
        signal: controller.signal
      });
  
      clearTimeout(timeoutId);
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get response from the server');
      }
  
      setChatOutput(prevOutput => `${prevOutput}\nYou: ${userInput}`);
      setUserInput('');
    } catch (error) {
      console.error('Error sending message:', error);
      if (error.name === 'AbortError') {
        setError('The request timed out. Please try again.');
      } else {
        setError(error.message || 'Failed to get a response. Please try again later.');
      }
      setChatOutput(prevOutput => `${prevOutput}\nYou: ${userInput}\nError: ${error.message || 'Request failed'}`);
    } finally {
      setIsLoading(false);
    }
  }, [userInput]);
  
  // In the return statement, update the error display:
 
  return (
    <div className="container">
      {/* Sidebar */}
      <div className="sidebar">
        <h2>Dashboard</h2>
        <nav>
          <ul>
            <li><a href="#home">Home</a></li>
            <li><a href="#analytics">Analytics</a></li>
            <li><a href="#settings">Settings</a></li>
          </ul>
        </nav>
        <button onClick={handleLogout}>Logout</button>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <div className="chat-assistant">
          <div className="chat-header">
            <h3>Chat Assistant</h3>
          </div>
          <div className="chat-output">
            <pre>{chatOutput}</pre>
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
              placeholder="Type your message..."
              disabled={isLoading}
            />
            <button onClick={handleSendMessage} disabled={isLoading}>
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </div>
          {error && <div className="error-message">{error}</div>}
        </div>

        <div className="map">
          <iframe
            src={`https://www.openstreetmap.org/export/embed.html?bbox=${mapCenter.lng-0.1}%2C${mapCenter.lat-0.1}%2C${mapCenter.lng+0.1}%2C${mapCenter.lat+0.1}&layer=mapnik&marker=${mapCenter.lat}%2C${mapCenter.lng}`}
            width="100%"
            height="100%"
            frameBorder="0"
            scrolling="no"
            marginHeight="0"
            marginWidth="0"
            title="OpenStreetMap"
          ></iframe>
        </div>

        {plots.length > 0 && (
          <div className="plot-list">
            <h3>Available Plots</h3>
            <ul>
              {plots.map((plot, index) => (
                <li key={index}>{plot}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;


// import React, { useState, useEffect, useCallback } from 'react';
// import { useNavigate } from 'react-router-dom';
// import { getAuth, signOut } from 'firebase/auth';
// import io from 'socket.io-client';
// import './styles.css';

// const INITIAL_MAP_CENTER = { lat: 20.5937, lng: 78.9629, zoom: 5 };
// const SOCKET_URL = 'http://localhost:5001';
// const API_URL = 'http://localhost:5002/predict';

// const Dashboard = () => {
//   const navigate = useNavigate();
//   const auth = getAuth();
//   const [mapCenter, setMapCenter] = useState(INITIAL_MAP_CENTER);
//   const [chatOutput, setChatOutput] = useState('');
//   const [userInput, setUserInput] = useState('');
//   const [socket, setSocket] = useState(null);
//   const [plots, setPlots] = useState([]);
//   const [isLoading, setIsLoading] = useState(false);
//   const [error, setError] = useState(null);

//   useEffect(() => {
//     const newSocket = io(SOCKET_URL, {
//       transports: ['websocket', 'polling'],
//       reconnectionAttempts: 5,
//       reconnectionDelay: 1000,
//       timeout: 10000,
//     });

//     newSocket.on('connect', () => {
//       console.log('Connected to server');
//       console.log('Socket ID:', newSocket.id);
//     });

//     newSocket.on('connect_error', (error) => {
//       console.error('Connection error:', error);
//       setError('Failed to connect to the server. Please try again later.');
//     });

//     newSocket.on('disconnect', (reason) => {
//       console.log('Disconnected:', reason);
//     });

//     newSocket.on('zoom_update', (newLocation) => {
//       console.log('Received zoom update:', newLocation);
//       setMapCenter(prevCenter => ({
//         ...prevCenter,
//         ...newLocation,
//         zoom: newLocation.zoom || 17
//       }));
//     });

//     newSocket.on('plot_data', (data) => {
//       console.log('Received plot data:', data);
//       setPlots(data.plots);
//     });

//     setSocket(newSocket);

//     return () => {
//       console.log('Cleaning up socket connection');
//       newSocket.close();
//     };
//   }, []);

//   const handleLogout = useCallback(() => {
//     signOut(auth).then(() => {
//       navigate('/login');
//     }).catch((error) => {
//       console.error('Logout error:', error);
//       setError('Failed to log out. Please try again.');
//     });
//   }, [auth, navigate]);

//   const getPrediction = useCallback(async (inputData) => {
//     try {
//       const response = await fetch(API_URL, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify(inputData),
//       });
//       if (!response.ok) {
//         const errorText = await response.text();
//         throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`);
//       }
//       return await response.json();
//     } catch (error) {
//       console.error('Error:', error);
//       throw error;
//     }
//   }, []);

//   const handleSendMessage = useCallback(async () => {
//     if (userInput.trim() === '') return;

//     setIsLoading(true);
//     setError(null);

//     try {
//       const result = await getPrediction({ message: userInput });
      
//       if (result.response) {
//         setChatOutput(prevOutput => `${prevOutput}\nYou: ${userInput}\nDeymax: ${result.response}`);
//       }

//       if (result.location) {
//         setMapCenter(prevCenter => ({
//           ...prevCenter,
//           ...result.location,
//           zoom: 17
//         }));
//       }

//       if (result.plots && result.plots.length > 0) {
//         setPlots(result.plots);
//       }
//     } catch (error) {
//       console.error('Error sending message:', error);
//       setChatOutput(prevOutput => `${prevOutput}\nYou: ${userInput}\nError: Failed to get response from the server. Please try again later.`);
//       setError('Failed to get a response. Please try again later.');
//     } finally {
//       setIsLoading(false);
//       setUserInput('');
//     }
//   }, [userInput, getPrediction]);

//   return (
//     <div className="container">
//       {/* Sidebar */}
//       <div className="sidebar">
//         <h2>Dashboard</h2>
//         <nav>
//           <ul>
//             <li><a href="#home">Home</a></li>
//             <li><a href="#analytics">Analytics</a></li>
//             <li><a href="#settings">Settings</a></li>
//           </ul>
//         </nav>
//         <button onClick={handleLogout}>Logout</button>
//       </div>

//       {/* Main Content */}
//       <div className="main-content">
//         <div className="chat-assistant">
//           <div className="chat-header">
//             <h3>Chat Assistant</h3>
//           </div>
//           <div className="chat-output">
//             <pre>{chatOutput}</pre>
//           </div>
//           <div className="chat-input">
//             <input
//               type="text"
//               value={userInput}
//               onChange={(e) => setUserInput(e.target.value)}
//               onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
//               placeholder="Type your message..."
//               disabled={isLoading}
//             />
//             <button onClick={handleSendMessage} disabled={isLoading}>
//               {isLoading ? 'Sending...' : 'Send'}
//             </button>
//           </div>
//           {error && <div className="error-message">{error}</div>}
//         </div>

//         <div className="map">
//           <iframe
//             src={`https://www.openstreetmap.org/export/embed.html?bbox=${mapCenter.lng-0.1}%2C${mapCenter.lat-0.1}%2C${mapCenter.lng+0.1}%2C${mapCenter.lat+0.1}&layer=mapnik&marker=${mapCenter.lat}%2C${mapCenter.lng}`}
//             width="100%"
//             height="100%"
//             frameBorder="0"
//             scrolling="no"
//             marginHeight="0"
//             marginWidth="0"
//             title="OpenStreetMap"
//           ></iframe>
//         </div>

//         {plots.length > 0 && (
//           <div className="plot-list">
//             <h3>Available Plots</h3>
//             <ul>
//               {plots.map((plot, index) => (
//                 <li key={index}>{plot}</li>
//               ))}
//             </ul>
//           </div>
//         )}
//       </div>
//     </div>
//   );
// };

// export default Dashboard;



// import React, { useState, useEffect } from 'react';
// import { Link, useNavigate } from 'react-router-dom';
// import { getAuth, signOut } from 'firebase/auth';
// import './styles.css';

// const Dashboard = () => {
//   const navigate = useNavigate();
//   const auth = getAuth();
//   const [mapData, setMapData] = useState(null);

//   useEffect(() => {
//     // This is where you would call your Geoapify code
//     // and set the result to the mapData state
//     const fetchMapData = async () => {
//       try {
//         // Replace this with your actual Geoapify API call
//         const response = await fetch('YOUR_GEOAPIFY_API_ENDPOINT');
//         const data = await response.json();
//         setMapData(data);
//       } catch (error) {
//         console.error('Error fetching map data:', error);
//       }
//     };

//     fetchMapData();
//   }, []);

//   const handleLogout = () => {
//     signOut(auth)
//       .then(() => {
//         navigate('/login'); // Redirect to login page after logout
//       })
//       .catch((error) => {
//         console.error('Logout error:', error);
//       });
//   };

//   return (
//     <div className="container">
//       {/* Sidebar */}
//       <div className="sidebar">
//         <div className="sidebar-header">
//           <h2>*Name*</h2>
//         </div>

//         <div className="menu">
//           <Link to="/setup-store" className="menu-item">
//             <i className="fas fa-store"></i> Set up a store
//           </Link>
//           <Link to="/recommended" className="menu-item">
//             <i className="fas fa-map-marker-alt"></i> Recommended
//           </Link>
//           <Link to="/forecast-demand" className="menu-item">
//             <i className="fas fa-chart-line"></i> Forecast Demand
//           </Link>
//           <Link to="/how-to-use" className="menu-item">
//             <i className="fas fa-question-circle"></i> How to use
//           </Link>
//         </div>

//         <div className="bottom-menu">
//           <button className="settings">
//             <i className="fas fa-cog"></i> Settings
//           </button>
//           <button className="logout" onClick={handleLogout}>
//             <i className="fas fa-sign-out-alt"></i> Logout
//           </button>
//         </div>
//       </div>

//       {/* Main Content */}
//       <div className="main-content">
//         <div className="chat-assistant">
//           <div className="chat-header">
//             <h3>Chat Assistant</h3>
//             <input className="chat-search" type="text" placeholder="Search in chat" />
//           </div>
//           <div className="chat-placeholder">
//             Chat placeholder
//           </div>
//         </div>

//         <div className="map">
//           {mapData ? (
//             <div className="map-content">
//               {/* Replace this with your actual map rendering logic */}
//               <pre>{JSON.stringify(mapData, null, 2)}</pre>
//             </div>
//           ) : (
//             <div className="map-placeholder">
//               Loading map data...
//             </div>
//           )}
//         </div>
//       </div>
//     </div>
//   );
// };

// export default Dashboard;
