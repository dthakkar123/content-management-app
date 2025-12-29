import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor for logging (development only)
apiClient.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      console.log('API Request:', config.method.toUpperCase(), config.url);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    } else {
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// API methods (to be implemented in Phase 9)
const api = {
  // Content endpoints
  content: {
    submitURL: (url) => apiClient.post('/content/url', { url }),
    uploadPDF: (file) => {
      const formData = new FormData();
      formData.append('file', file);
      return apiClient.post('/content/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    },
    getAll: (params = {}) => apiClient.get('/content', { params }),
    getById: (id) => apiClient.get(`/content/${id}`),
    delete: (id) => apiClient.delete(`/content/${id}`),
  },

  // Search endpoints
  search: {
    query: (searchParams) => apiClient.get('/search', { params: searchParams }),
  },

  // Theme endpoints
  themes: {
    getAll: () => apiClient.get('/themes'),
    getById: (id) => apiClient.get(`/themes/${id}`),
    getContent: (themeId, params = {}) =>
      apiClient.get(`/themes/${themeId}/content`, { params }),
    create: (data) => apiClient.post('/themes', data),
    update: (id, data) => apiClient.put(`/themes/${id}`, data),
    delete: (id) => apiClient.delete(`/themes/${id}`),
  },

  // Job status endpoint
  jobs: {
    getStatus: (jobId) => apiClient.get(`/jobs/${jobId}`),
  },

  // Health check
  health: () => apiClient.get('/health', { baseURL: 'http://localhost:8000' }),
};

export default api;
