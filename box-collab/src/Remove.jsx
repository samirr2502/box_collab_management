import React,  { useState, useEffect }from 'react';
import { useNavigate } from 'react-router-dom';
import './index.css'

const Home = ({ refreshToken, setRefreshToken }) => {
  const navigate = useNavigate();

  const handleBoxAccess = () => {
    const clientId = '020r4pyyewrt5si70y5mtvsg4g6kl3qq';
    const redirectUri = 'http://127.0.0.1:5000/auth'; // must match Box app settings
  
    const boxAuthUrl = `https://account.box.com/api/oauth2/authorize?response_type=code&client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}`;
  
    window.location.href = boxAuthUrl;
  };

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get('refreshToken');

    if (token) {
      localStorage.setItem('refreshToken', token);
      setRefreshToken(token);

      // Clean up the URL after storing token
      navigate('/');
    }
  }, []);

  return (
    <>
      <h2>Welcome to Box Collab</h2>
      {!refreshToken ? (
        <button className="btn" onClick={handleBoxAccess}>Get Box Access</button>
      ) : (
        <button className="btn" disabled>You are in!</button>
      )}
    </>
  );
};

export default Home;
