// frontend/src/api.js
import axios from "axios";

export const fetchNodes = () => axios.get("/api/nodes");
export const fetchTasks = () => axios.get("/api/tasks");