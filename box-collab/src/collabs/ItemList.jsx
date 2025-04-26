import React, { useState, useEffect } from 'react';
import '../index.css'

const ItemsList = ({setFolderId }) => {
  const [mainItems, setMainItems] = useState([]);
  const [refreshCount, setRefreshCount] = useState(0);

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
                {type == "Folder" ?
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
          <div className="column-even-1">
              <h4>Items in main folder</h4>
              {/* <button
                onClick={() => setRefreshCount(prev => prev + 1)}
                style={{ marginBottom: "1em" }}
              >
                🔄
              </button> */}
              <div className="items-container">
                <FolderList items={mainItems} resetTrigger={refreshCount} />
              </div>
            </div>
    </>
  );
};

export default ItemsList;