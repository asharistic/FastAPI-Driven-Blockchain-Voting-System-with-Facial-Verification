import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
})

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle responses and errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle network errors
    if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
      console.error('Backend connection error. Make sure the backend server is running on', API_BASE_URL)
      // Don't redirect on network errors, just log
      return Promise.reject({
        ...error,
        message: 'Cannot connect to backend server. Please ensure the backend is running on http://127.0.0.1:5000'
      })
    }
    
    // Handle 401 unauthorized
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token')
      if (window.location.pathname.startsWith('/admin')) {
        window.location.href = '/admin/login'
      }
    }
    
    return Promise.reject(error)
  }
)

// Connection test utility
export const testConnection = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/health`, { timeout: 5000 })
    return { connected: true, data: response.data }
  } catch (error) {
    return { connected: false, error: error.message }
  }
}

// Voter APIs
export const voterAPI = {
  register: (data) => api.post('/api/register', data),
  verifyFace: (data) => api.post('/api/verify-face', data),
  getAll: () => api.get('/api/voters'),
}

// Vote APIs
export const voteAPI = {
  castVote: (data) => api.post('/api/vote', data),
  getCandidates: () => api.get('/api/candidates'),
}

// Auth APIs
export const authAPI = {
  login: (credentials) => api.post('/api/auth/login', credentials),
  verifyToken: (token) => api.post('/api/auth/verify', { token }),
}

// Admin APIs
export const adminAPI = {
  // Stats
  getStats: () => api.get('/api/admin/stats'),
  
  // Elections
  getElections: () => api.get('/api/admin/elections'),
  createElection: (data) => api.post('/api/admin/elections', data),
  updateElection: (id, data) => api.put(`/api/admin/elections/${id}`, data),
  deleteElection: (id) => api.delete(`/api/admin/elections/${id}`),
  
  // Candidates
  getCandidates: () => api.get('/api/admin/candidates'),
  createCandidate: (data) => api.post('/api/admin/candidates', data),
  updateCandidate: (id, data) => api.put(`/api/admin/candidates/${id}`, data),
  deleteCandidate: (id) => api.delete(`/api/admin/candidates/${id}`),
  
  // Voters
  getVoters: () => api.get('/api/admin/voters'),
  updateVoter: (id, data) => api.put(`/api/admin/voters/${id}`, data),
  deleteVoter: (id) => api.delete(`/api/admin/voters/${id}`),
  
  // Blockchain
  getBlockchain: () => api.get('/api/admin/blockchain'),
  
  // Results
  getResults: () => api.get('/api/admin/results'),
}

// Export API base URL for debugging (use the constant from above)
export const getApiBaseUrl = () => API_BASE_URL

export default api

