import axios from "axios";
const BASE = "https://capsolver.yxschool.cc:8998/api";

export const fetchNodes = () => axios.get(`${BASE}/api/nodes`);
export const fetchTasks = () => axios.get(`${BASE}/api/tasks`);
