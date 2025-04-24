import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './index.css'

const Collabs = () => {

  const [folderId, setFolderId] = useState('');
  const [excludeFolderIds, setExcludeFolderIds] = useState('');
  const [isCompleted, setIsCompleted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [items, setItems] = useState([]);
  const [mainItems, setMainItems] = useState([]);
  const [refreshCount, setRefreshCount] = useState(0);

  const [sessionTasks, setSessionTasks] = useState([]);

  const addTask = (newTask) => {
    setSessionTasks((prevTasks) => {
      const updatedTasks = [...prevTasks, newTask];
      localStorage.setItem('sessionTasks', JSON.stringify(updatedTasks)); // Store as string
      return updatedTasks;
    });
  };
  useEffect(() => {
    const storedTasks = localStorage.getItem('sessionTasks');
    if (storedTasks) {
      setSessionTasks(JSON.parse(storedTasks));
    }
  }, []);
  

  // useEffect(() => {
  //   const storedTasks = JSON.parse(localStorage.getItem('sessionTasks') || '[]');
  //   if (storedTasks) setSessionTasks(storedTasks);
  // }, []);
  const handleGetItems = (e) => {
    e.preventDefault();
    if (!folderId) return;

    fetch(`http://127.0.0.1:5000/get_items?folderId=${folderId}`)
      .then(res => res.json())
      .then(data => {
        setItems(data);
        console.log("data: ", data);
      })
      .catch(err => console.error("Error fetching items:", err));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setLoading(true);
    setIsCompleted(false);

    fetch(`http://127.0.0.1:5000/get_collabs?folderId=${folderId}&excludeFolderIds=${excludeFolderIds}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          setIsCompleted(true);
        }
      })
      .catch((err) => console.error("Error:", err))
      .finally(() => setLoading(false));
  };
  const handleSubmitParalell = (e)=> {
    e.preventDefault();
    setLoading(true);
    setIsCompleted(false);
    fetch(`http://127.0.0.1:5000/get_collabs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',

      body: JSON.stringify({
        folderId: folderId,
        excludeFolderIds: excludeFolderIds,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.task_id) {
          console.log(data.task_id);
          addTask(data.task_id);
          console.log(sessionTasks);
        }        
      })
      .catch((err) => {
        console.error("Error:", err);
      })
      .finally(() => {
        setLoading(false);
      });
  }

  useEffect(() => {
    fetch(`http://127.0.0.1:5000/get_items?folderId=0`)
      .then(res => res.json())
      .then(data => setMainItems(data))
      .catch(err => console.error("Error fetching main items:", err));
  }, [refreshCount]);

  const FolderList = ({ items, resetTrigger }) => {
    const [expandedFolders, setExpandedFolders] = useState({});

    useEffect(() => {
      setExpandedFolders({});
    }, [resetTrigger]);

    const toggleFolder = (folderId) => {
      if (expandedFolders[folderId]?.open) {
        setExpandedFolders(prev => ({
          ...prev,
          [folderId]: { ...prev[folderId], open: false }
        }));
      } else {
        fetch(`http://127.0.0.1:5000/get_items?folderId=${folderId}`)
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
          const name = item[id][0];
          const type = item[id][1];
          const isOpen = expandedFolders[id]?.open;
          const children = expandedFolders[id]?.children || [];

          return (
            <li key={index}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {type == "Folder"?
                <button onClick={() => toggleFolder(id)}>
                  {isOpen ? "➖" : "➕"}
                </button>
        : "-"}
                <span>
                  {name} (ID:
                  <span className="link" onClick={() => setFolderId(id)}> {id}</span>)
                </span>
              </div>
              {isOpen && (
                <div style={{ marginLeft: "1.5em" }}>
                  {children.length > 0 ? (
                    <FolderList items={children} resetTrigger={resetTrigger} />
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

  return (
    <>
      <h2>Welcome to Box Collab</h2>
      <div className="collab-layout">
        <div className="form-column">
          <form onSubmit={handleSubmitParalell} className="collab-form">
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
              </button>
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

            <button className="btn" type="submit" disabled={loading}>
              {loading ? "Processing..." : "Get Collaborations"}
            </button>
          </form>

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
            <FolderList items={mainItems} resetTrigger={refreshCount} />
          </div>
        </div>
      </div>
    </>
  );
};

export default Collabs;
