import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.PROD ? '' : 'http://localhost:5000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 30000, // 30 second timeout
})

// Add retry logic for network errors
let retryCount = 0
const MAX_RETRIES = 3

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => {
    retryCount = 0 // Reset on success
    return response
  },
  async (error) => {
    const config = error.config

    // If it's a network error and we haven't exceeded retries
    if (error.code === 'ECONNABORTED' || error.message === 'Network Error' || !error.response) {
      if (retryCount < MAX_RETRIES && config) {
        retryCount++
        console.log(`Retrying request... Attempt ${retryCount} of ${MAX_RETRIES}`)
        
        // Wait before retrying (exponential backoff)
        await new Promise(resolve => setTimeout(resolve, 1000 * retryCount))
        
        return api(config)
      }
    }
    
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.status, error.response.data)
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error: No response from server')
    } else {
      // Other errors
      console.error('Request Error:', error.message)
    }
    
    retryCount = 0 // Reset for next request
    return Promise.reject(error)
  }
)

// Auth APIs
export const authAPI = {
  login: (username: string, password: string) =>
    api.post('/api/login', { username, password }),
  
  register: (data: { full_name: string; email: string; username: string; password: string }) =>
    api.post('/api/register', data),
  
  logout: () => api.get('/logout'),
  
  getSession: () => api.get('/api/session')
}

// Prediction APIs
export const predictionAPI = {
  predict: (data: {
    name: string
    age: number
    sex: string
    contact: string
    address: string
    pregnancies: number
    glucose: number
    bloodPressure: number
    skinThickness: number
    insulin: number
    bmi: number
    diabetesPedigreeFunction: number
  }) => api.post('/predict', data),
  
  getUserPredictions: () => api.get('/user/predictions'),
  
  getPredictionById: (id: string) => api.get(`/user/prediction/${id}`)
}

// Dashboard APIs
export const dashboardAPI = {
  getUserStats: () => api.get('/api/user/statistics'),
  
  // Use all_predictions instead of history (history is an HTML route, not API)
  getUserHistory: () => api.get('/api/user/all_predictions'),
  
  getLatestPrediction: () => api.get('/api/user/latest_prediction'),
  
  getAllPredictions: () => api.get('/api/user/all_predictions')
}

// Report APIs
export const reportAPI = {
  generateReport: (predictionId: string) =>
    api.post('/api/generate_report', { prediction_id: predictionId }),
  
  generateReportWithData: (data: any) =>
    api.post('/report', data),
  
  downloadReport: (reportId: string) =>
    api.get(`/download_report/${reportId}`, { responseType: 'blob' }),
  
  getUserReports: () => api.get('/api/user/reports'),
  
  downloadReportFile: (filename: string) =>
    api.get(`/reports/${filename}`, { responseType: 'blob' })
}

// User Settings APIs
export const userAPI = {
  updateProfile: (data: any) => api.post('/api/profile/update', data),
  
  changePassword: (currentPassword: string, newPassword: string, confirmPassword: string) =>
    api.post('/api/change_password', {
      current_password: currentPassword,
      new_password: newPassword,
      confirm_password: confirmPassword
    })
}

// Admin APIs
export const adminAPI = {
  getUsers: () => api.get('/api/admin/users'),
  
  getStats: () => api.get('/api/admin/stats'),
  
  deleteUser: (userId: string) => api.delete(`/api/admin/users/${userId}`)
}

export default api
