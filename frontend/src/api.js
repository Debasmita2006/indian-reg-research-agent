import axios from 'axios';

const API_BASE = 'https://indian-reg-research-agent.onrender.com';

export async function runResearch(query) {
  const response = await axios.post(`${API_BASE}/api/research`, { query });
  return response.data;
}
export async function getDashboardData() {
  const response = await axios.get(`${API_BASE}/api/dashboard`);
  return response.data;
}