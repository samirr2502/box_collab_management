import React, { useState, useEffect } from 'react';
import '../index.css'

const Item = ({folderId}) => {
    const [itemInfo, setItemInfo] = useState({});

    useEffect(() => {
        fetch(`http://127.0.0.1:5000/get_item_info?folderId=${folderId}`)
            .then(res => res.json())
            .then(data => setItemInfo(data))
            .catch(err => console.error("Error fetching item info:", err));
    }, []);
    const [childrenVisible, setChildrenVisible] = useState(false);
    const [collaboratorsVisible, setCollaboratorsVisible] = useState(false);
    const [childrenItems, setChildrenItems] = useState([]);
    const [collaborators, setCollaborators] = useState([]);

    useEffect(() => {
        fetch(`http://127.0.0.1:5000/get_item_info?folderId=${folderId}`)
            .then(res => res.json())
            .then(data => setItemInfo(data))
            .catch(err => console.error("Error fetching item info:", err));
    }, [folderId]);

    const handleShowChildren = () => {
        setChildrenVisible(!childrenVisible);
        if (!childrenItems.length) {
            fetch(`http://127.0.0.1:5000/get_children?folderId=${folderId}`)
                .then(res => res.json())
                .then(data => setChildrenItems(data))
                .catch(err => console.error("Error fetching children items:", err));
        }
    };

    const handleShowCollaborators = () => {
        setCollaboratorsVisible(!collaboratorsVisible);
        if (!collaborators.length) {
            fetch(`http://127.0.0.1:5000/get_collaborators?folderId=${folderId}`)
                .then(res => res.json())
                .then(data => setCollaborators(data))
                .catch(err => console.error("Error fetching collaborators:", err));
        }
    };
    return (
        <>
            <div className="column-even-2">
            <h2>Item Info</h2>
            <p><strong>Name:</strong> {itemInfo.name}</p>
            <p><strong>Item ID:</strong> {itemInfo.id}</p>
            <p><strong>Last Modified:</strong> {itemInfo.last_modified}</p>
            <p><strong>Collaborators:</strong> {itemInfo.collaborators_count}</p>
            <p><strong>Size:</strong> {itemInfo.size} bytes</p>
            <p><strong>Number of Items:</strong> {itemInfo.children_count}</p>

            <button onClick={handleShowChildren}>
                {childrenVisible ? 'Hide' : 'Show'} Children Items
            </button>
            {childrenVisible && (
                <ul>
                    {childrenItems.map(child => (
                        <li key={child.id}>{child.name} (ID: {child.id})</li>
                    ))}
                </ul>
            )}

            <button onClick={handleShowCollaborators}>
                {collaboratorsVisible ? 'Hide' : 'Get'} Collaborators
            </button>
            {collaboratorsVisible && (
                <ul>
                    {collaborators.map(collab => (
                        <li key={collab.id}>{collab.name} ({collab.email})</li>
                    ))}
                </ul>
            )}
            </div>
        </>
    );
};

export default Item;