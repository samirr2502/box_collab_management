import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import Home from './Home'
import Collabs from './Collabs'

// import './index.css'

function App() {
  const [refreshToken, setRefreshToken] = useState('');
  const [accessToken, setAccessToken] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('refreshToken');
    const storedAccess = localStorage.getItem('accessToken');

    if (token) setRefreshToken(token);
    if (storedAccess) setAccessToken(storedAccess);

  }, []);
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const refresh = params.get('refreshToken');
    const access = params.get('accessToken');
  
    if (refresh) {
      localStorage.setItem('refreshToken', refresh);
      setRefreshToken(refresh);
    }
  
    if (access) {
      localStorage.setItem('accessToken', access);
      setAccessToken(access);
    }
  
    // Optional: clean up the URL so tokens aren’t visible
    if (refresh || access) {
      window.history.replaceState({}, '', '/');
    }
  }, []);
  return (
    <Router>

    <div className='body'>
    <header className="top-bar">
        <h1>Box Collab</h1>
    </header>

    <div className="layout">
        <nav className="side-nav">
          <ul>
            <li><Link to="/">Home</Link></li>
            {refreshToken && (
               
              <>
                <li><Link to="/collabs">Get Collabs</Link></li>
                <li><Link to="/remove">Remove User</Link></li>
              </>
            )}
          </ul>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home refreshToken={refreshToken} setRefreshToken={setRefreshToken} 
                                          accessToken={accessToken} setAccessToken={setAccessToken} />} />
            <Route path="/collabs" element={<Collabs refreshToken={refreshToken} accessToken={accessToken}/>} />
            <Route path="/remove" element={<div>Remove User Page</div>} />
          </Routes>
        </main>
      </div>

    <footer className="footer">
        <p>&copy; 2025 Box Collab. All rights reserved.</p>
    </footer>
</div>
</Router>
  )
}

export default App
