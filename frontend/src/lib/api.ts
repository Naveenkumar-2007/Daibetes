import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.PROD ? '' : 'http://localhost:5000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

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
  updateProfile: (data: any) => api.post('/api/user/update_profile', data),
  
  changePassword: (currentPassword: string, newPassword: string) =>
    api.post('/api/user/change_password', {
      current_password: currentPassword,
      new_password: newPassword
    })
}

// Admin APIs
export const adminAPI = {
  getUsers: () => api.get('/api/admin/users'),
  
  getStats: () => api.get('/api/admin/stats')
}

export default api
