import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8000';

export async function runResearch(query) {
  const response = await axios.post(`${API_BASE}/api/research`, { query });
  return response.data;
}
export async function getDashboardData() {
  const response = await axios.get(`${API_BASE}/api/dashboard`);
  return response.data;
}