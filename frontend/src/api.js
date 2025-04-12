import axios from "axios";

const BASE = process.env.REACT_APP_BASE_API_URL || "http://localhost:8000";

export const fetchNodes = () => axios.get(`${BASE}/api/nodes`);
export const fetchTasks = () => axios.get(`${BASE}/api/tasks`);