import axios from "axios";

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 
         (process.env.NODE_ENV === 'production'
           ? "https://finance-backend-9v2i.onrender.com"
           : "http://localhost:8000/api"),
});

apiClient.interceptors.request.use((config) => {
  const token = sessionStorage.getItem("accessToken");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
