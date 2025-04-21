import React,  { useState, useEffect }from 'react';
import { useNavigate } from 'react-router-dom';
import './index.css'

const Home = ({ refreshToken, setRefreshToken , accessToken,setAccessToken }) => {
  const navigate = useNavigate();

  const handleBoxAccess = () => {
    const clientId = '020r4pyyewrt5si70y5mtvsg4g6kl3qq';
    const redirectUri = 'http://127.0.0.1:5000/auth'; // must match Box app settings
  
    const boxAuthUrl = `https://account.box.com/api/oauth2/authorize?response_type=code&client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}`;
  
    window.location.href = boxAuthUrl;
  };
  const handleLogout = () => {
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('accessToken');
    setRefreshToken('');
    setAccessToken('');
    navigate('/'); // optional: redirect to home
  };

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
  
    if (refresh || access) {
      navigate('/'); // Clean up URL
    }
  }, []);
  

  return (
    <>
      <h2>Welcome to Box Collab</h2>
      {!refreshToken && !accessToken ? (
        <button className="btn" onClick={handleBoxAccess}>Get Box Access</button>
      ) : (
        <>
        <button className="btn" disabled>You are in!</button>
        <button className="btn logout" onClick={handleLogout}>Logout</button>
        </>
      )}
    </>
  );
};

export default Home;
