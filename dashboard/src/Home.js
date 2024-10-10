// Home.js
import React from 'react';
import './styles.css';

const Home = () => {
  return (
    <div className="home-container">
      <h1>Dashboard Home</h1>
      {/* Move your existing chat assistant, map, etc., here */}
      <div className="chat-assistant">
        {/* Existing chat assistant code from Dashboard.js */}
        {/* Ensure to handle state and functionalities as needed */}
      </div>
      <div className="map">
        {/* Existing map iframe from Dashboard.js */}
      </div>
      { /* Other dashboard elements like plots */ }
    </div>
  );
};

export default Home;
