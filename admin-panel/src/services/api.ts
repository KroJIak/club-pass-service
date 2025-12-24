import axios from 'axios'

// Use relative path if VITE_API_URL is not set or empty (for production with nginx proxy)
// Otherwise use the provided URL (for development)
const API_URL = import.meta.env.VITE_API_URL || ''
const baseURL = API_URL ? `${API_URL}/api/v1` : '/api/v1'

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api

