import axios from "axios";

const BASE = import.meta.env.VITE_BASE_API_URL || "http://localhost:8000";

export const fetchNodes = () => axios.get(`${BASE}/api/nodes`);
export const fetchTasks = () => axios.get(`${BASE}/api/tasks`);