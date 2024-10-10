import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { getAuth, signOut } from 'firebase/auth';
import './styles.css'; // Assuming the same CSS is used

const Sidebar = () => {
  const navigate = useNavigate();
  const auth = getAuth();

  const handleLogout = () => {
    signOut(auth)
      .then(() => {
        navigate('/login'); // Redirect to login page after logout
      })
      .catch((error) => {
        console.error('Logout error:', error);
      });
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>*Name*</h2>
      </div>

      <div className="menu">
        <Link to="/setup-store" className="menu-item">
          <i className="fas fa-store"></i> Set up a store
        </Link>
        <Link to="/recommended" className="menu-item">
          <i className="fas fa-map-marker-alt"></i> Recommended
        </Link>
        <Link to="/forecast-demand" className="menu-item">
          <i className="fas fa-chart-line"></i> Forecast Demand
        </Link>
        <Link to="/how-to-use" className="menu-item">
          <i className="fas fa-question-circle"></i> How to use
        </Link>
      </div>

      <div className="bottom-menu">
        <button className="settings">
          <i className="fas fa-cog"></i> Settings
        </button>
        <button className="logout" onClick={handleLogout}>
          <i className="fas fa-sign-out-alt"></i> Logout
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
