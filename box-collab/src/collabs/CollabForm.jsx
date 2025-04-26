import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../index.css'


const CollabForm = ({ sessionUser, setSessionUser }) => {
    const navigate = useNavigate();

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

    const [excludeFolderIds, setExcludeFolderIds] = useState('');
    const [isCompleted, setIsCompleted] = useState(false);
    const [loading, setLoading] = useState(false);
    const [items, setItems] = useState([]);
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

    const handleSubmitParalell = (e) => {
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


    return (
        <>
            <div className="column-even-2">
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
        </>
    )
};

export default CollabForm;
