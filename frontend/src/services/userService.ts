import axios from 'axios';

const API_URL = 'http://localhost:8000/api/token/';

export const loginUser = async (credentials: { username: string; password: string }) => {
  const response = await axios.post(API_URL, credentials);
  return response.data;
};
