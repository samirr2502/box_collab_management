import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './index.css'
import config from "../config"
import ItemsList from './collabs/ItemList';
import Item from './collabs/Item';

const Home = ({ sessionUser, setSessionUser }) => {
  const navigate = useNavigate();
  const [folderId, setFolderId] = useState('');
  const [sessionTasks, setSessionTasks] = useState([]);

  useEffect(() => {
    const storedTasks = localStorage.getItem('sessionTasks');
    if (storedTasks) {
      setSessionTasks(JSON.parse(storedTasks));
    }
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const user = params.get('session_user')
    if (user) {
      localStorage.setItem('sessionUser', user);
      setSessionUser(user);
    }
    if (sessionUser) {
      navigate('/'); // Clean up URL
    }
  }, []);

  const handleBoxAccess = () => {
    const clientId = config.client_id;
    const redirectUri = 'http://127.0.0.1:5000/auth'; // must match Box app settings
    const boxAuthUrl = `https://account.box.com/api/oauth2/authorize?response_type=code&client_id=${clientId}&redirect_uri=${encodeURIComponent(redirectUri)}`;

    window.location.href = boxAuthUrl;
  };

  const handleLogout = () => {
    localStorage.removeItem('sessionUser');
    setSessionUser('');
    fetch(`http://127.0.0.1:5000/logout`, {
      method: 'GET',
    })
    navigate('/'); // optional: redirect to home
  };


  return (
    <>
      <h2>Welcome to Box Collab {sessionUser}</h2>
      {!sessionUser ? (
        <button className="btn" onClick={handleBoxAccess}>Get Box Access</button>
      ) : (
        <>
          <button className="btn logout" onClick={handleLogout}>Logout</button>

          <div className="column-layout-two-even">
            <ItemsList setFolderId={setFolderId}/>
            <Item folderId={folderId}/>
          </div>
        </>
      )}
    </>
  );
};

export default Home;
