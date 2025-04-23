import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './index.css'

const Collabs = ({ refreshToken, setRefreshToken, accessToken }) => {
  const navigate = useNavigate();
  const [folderId, setFolderId] = useState('');
  const [excludeFolderIds, setExcludeFolderIds] = useState('');
  const [isCompleted, setIsCompleted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState([]);
  const [mainItems, setMainItems] = useState([]);
  const [openItemId, setOpenItemId] = useState(null);
  const [subfolderItems, setSubfolderItems] = useState([]);
  const [expandedFolders, setExpandedFolders] = useState({});
  const [refreshCount, setRefreshCount] = useState(0); // Triggers refresh
  const [lastClickedId, setLastClickedId] = useState(''); // Triggers refresh

  const handleGetItems = (e) => {
    e.preventDefault();
    if (!folderId) return;

    fetch(`http://127.0.0.1:5000/get_items?folderId=${folderId}&refreshToken=${refreshToken}&accessToken=${accessToken}`, {
      method: 'GET',
    })
      .then(res => res.json())
      .then(data => {
        setItems(data);
        console.log("data: ", data);
      })
      .catch(err => {
        console.error("Error fetching items:", err);
      });
  };


  const handleGetMainItems = (e) => {
    if (e) e.preventDefault();
    fetch(`http://127.0.0.1:5000/get_items?folderId=0&refreshToken=${refreshToken}&accessToken=${accessToken}`, {
      method: 'GET',
    })
      .then(res => res.json())
      .then(data => {
        setMainItems(data);
        console.log("data: ", data);
      })
      .catch(err => {
        console.error("Error fetching items:", err);
      });
  };

  const handleGetItemsInFolder = (folderId) => {
    if (openItemId === folderId) {
      // Clicking again closes it
      setOpenItemId(null);
      setSubfolderItems([]);
      return;
    }

    fetch(`http://127.0.0.1:5000/get_items?folderId=${folderId}&refreshToken=${refreshToken}&accessToken=${accessToken}`)
      .then(res => res.json())
      .then(data => {
        setOpenItemId(folderId);
        setSubfolderItems(data);
      })
      .catch(err => {
        console.error("Error fetching folder items:", err);
      });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setIsCompleted(false);
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
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    // your function here
    console.log("this is being called");
    handleGetMainItems();
  }, []);
  const FolderList = ({ items, resetTrigger }) => {
    const [expandedFolders, setExpandedFolders] = useState({});

    // Reset all open folders when refresh happens
    useEffect(() => {
      setExpandedFolders({});
    }, [resetTrigger]);

    const toggleFolder = (folderId) => {
      if (expandedFolders[folderId]?.open) {
        // Collapse
        setExpandedFolders(prev => ({
          ...prev,
          [folderId]: { ...prev[folderId], open: false }
        }));
      } else {
        // Fetch and expand
        fetch(`http://127.0.0.1:5000/get_items?folderId=${folderId}&refreshToken=${refreshToken}&accessToken=${accessToken}`)
          .then(res => res.json())
          .then(data => {
            setExpandedFolders(prev => ({
              ...prev,
              [folderId]: {
                open: true,
                children: data
              }
            }));
          })
          .catch(err => console.error("Error loading subfolders:", err));
      }
    };

    return (
      <ul>
        {items.map((item, index) => {
          const id = Object.keys(item)[0];
          const name = item[id];
          const isOpen = expandedFolders[id]?.open;
          const children = expandedFolders[id]?.children || [];

          return (
            <li key={index}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <button onClick={() => toggleFolder(id)}>
                  {isOpen ? "➖" : "➕"}
                </button>
                <span >{name} (ID:<span className="link" onClick={() => setFolderId(id)}> {id}</span>)</span>
              </div>

              {isOpen && (
                <div style={{ marginLeft: "1.5em" }}>
                  {children.length > 0 ? (
                    <FolderList items={children} resetTrigger={refreshCount} />
                  ) : (
                    <p style={{ color: "gray" }}>No items found.</p>
                  )}
                </div>
              )}
            </li>
          );
        })}
      </ul>
    );
  };
  useEffect(() => {
    fetch(`http://127.0.0.1:5000/get_items?folderId=0&refreshToken=${refreshToken}&accessToken=${accessToken}`)
      .then(res => res.json())
      .then(data => {
        setMainItems(data);
      })
      .catch(err => {
        console.error("Error fetching main items:", err);
      });
  }, [refreshCount]); // Will re-run when refreshCount changes



  return (
    <>
      <h2>Welcome to Box Collab</h2>

      <div className="collab-layout">
        <div className="form-column">

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
              <button className="btn" onClick={handleGetItems} type="button">
                Get Items
              </button>  </div>

            <div className="form-group">
              <label htmlFor="excludeFolderIds">Exclude Folder IDs (comma separated):</label>
              <input
                id="excludeFolderIds"
                type="text"
                value={excludeFolderIds}
                onChange={(e) => setExcludeFolderIds(e.target.value)}
              />
            </div>

            <button className="btn" type="submit" disabled={loading}>
              {loading ? "Processing..." : "Get Collaborations"}
            </button></form>
          {isCompleted && (
            <div className="checkmark-container">
              <div className="checkmark">✅</div>
              <p>Collaboration Completed!</p>
            </div>
          )}
        </div>
        <div className="item-column">
          <h4>Items in main folder</h4>
          <button
            onClick={() => setRefreshCount(prev => prev + 1)}
            style={{ marginBottom: "1em" }}
          >
            🔄
          </button>

          <div className="items-container">
            <FolderList items={mainItems} />


          </div>

        </div>

      </div>
    </>
  );
};

export default Collabs;
