import React,  { useState, useEffect }from 'react';
import { useNavigate } from 'react-router-dom';
import './index.css'

const Collabs = ({ refreshToken, setRefreshToken, accessToken}) => {
  const navigate = useNavigate();
  const [folderId, setFolderId] = useState('');
  const [excludeFolderIds, setExcludeFolderIds] = useState('');
  const [isCompleted, setIsCompleted] = useState(false);

  
  const handleSubmit = (e) => {
    e.preventDefault();

    fetch(`http://127.0.0.1:5000/get_collabs?folderId=${folderId}&excludeFolderIds=${excludeFolderIds}&refreshToken=${refreshToken}&accessToken=${accessToken}`, {
      method: 'GET',
    })
    .then((res) => res.json())
    .then((data) => {
      if (data.status === "success") {
        // If Flask sends a redirect, follow it
        setIsCompleted(true); // Show checkmark
      }
    })
    .catch((err) => {
      console.error("Error:", err);
    });
  };
  return (
    <>
     <h2>Welcome to Box Collab</h2>


     <form onSubmit={handleSubmit} className="collab-form">
  <div className="form-group">
    <label htmlFor="folderId">Folder ID:</label>
    <input
      id="folderId"
      type="text"
      value={folderId}
      onChange={(e) => setFolderId(e.target.value)}
      required
    />
  </div>

  <div className="form-group">
    <label htmlFor="excludeFolderIds">Exclude Folder IDs (comma separated):</label>
    <input
      id="excludeFolderIds"
      type="text"
      value={excludeFolderIds}
      onChange={(e) => setExcludeFolderIds(e.target.value)}
    />
  </div>

  <button className="btn" type="submit">Get Collaborations</button>
</form>
{isCompleted && (
  <div className="checkmark-container">
    <div className="checkmark">✅</div>
    <p>Collaboration Completed!</p>
  </div>
)}

    </>
  );
};

export default Collabs;
