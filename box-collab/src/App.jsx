import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import Home from './Home'
import Collabs from './Collabs'

// import './index.css'

function App() {
  const [sessionUser, setSessionUser] = useState('');
  const [sessionTasks, setSessionTasks] = useState([]);

  useEffect(() => {
    const storedUser = localStorage.getItem('sessionUser');
    if (storedUser) setSessionUser(storedUser);
    const storedTasks = JSON.parse(localStorage.getItem('sessionTasks') || '[]');

    if (storedTasks) setSessionTasks(storedTasks);
  }, []);
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const user = params.get('session_user')
    if (user){
      localStorage.setItem('sessionUser', user);
      setSessionUser(user);
    }
    // Optional: clean up the URL so tokens aren’t visible
    if (user) {
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
            {sessionUser && (
               
              <>
                <li><Link to="/collabs">Get Collabs</Link></li>
                <li><Link to="/remove">Remove User</Link></li>
              </>
            )}
          </ul>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home sessionUser={sessionUser} setSessionUser={setSessionUser}
                                            sessionTasks={sessionTasks} setSessionTasks={setSessionTasks}/>} />
            <Route path="/collabs" element={<Collabs/>} />
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
