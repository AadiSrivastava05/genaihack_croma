// App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { auth } from './firebase';
import { onAuthStateChanged } from 'firebase/auth';
import Login from './Login';
import SetupStore from './SetupStore';
import Recommended from './Recommended';
import ForecastDemand from './ForecastDemand';
import HowToUse from './HowToUse';
import Settings from './Settings';
import Dashboard from './Dashboard';
import BarChart from './BarChart';

function App() {
  const [user, setUser] = React.useState(null);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      setUser(user);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <Router>
      <Routes>
        <Route path="/login" element={user ? <Navigate to="/home" /> : <Login />} />
        
        <Route path="/home" element={user ? <Dashboard /> : <Navigate to="/login" />}>
          <Route path="setup-store" element={<SetupStore />} />
          <Route path="recommended" element={<Recommended />} />
          <Route path="forecast-demand" element={<ForecastDemand />} />
          <Route path="how-to-use" element={<HowToUse />} />
          <Route path="settings" element={<Settings />} />
          <Route path = "barchart" element={<BarChart />} />
        </Route>

        <Route path="/" element={<Navigate to={user ? "/home" : "/login"} />} />
      </Routes>
    </Router>
  );
}

export default App;
